#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import sys
import time
import asyncio
from rich.console import Console
import datetime

VERSION = "0.1.3"

from openrecon.scanners.portScanner import run_port_scan
from openrecon.scanners.netDisc import live_discovery
from openrecon.scanners.pingSweep import ping_sweep
from openrecon.scanners.subDomainEnum import SubdomainEnumerator, get_fingerprint, recursive_enum

from openrecon.webVulns.SQLiS import SQLiScanner
from openrecon.webVulns.XSSscanner import AsyncXSSScanner
from openrecon.webVulns.csrf import CSRFScanner
from openrecon.webVulns.CMSdetector import CMSDetector
from openrecon.webVulns.graphQL import GraphQLScanner

from openrecon.core.colors import Colors, Messages
from openrecon.core.check_compat import check_payload_file
from openrecon.core.payload_handler import convert_txt_to_json
from openrecon.core.httpClient import HTTPClient
from openrecon.core.reporter import Reporter

console = Console()
reporter = Reporter()

def print_ping_results(results):
    """Print ping sweep results using the new PingSweeper format"""
    pass
            
def create_parser():
    """Create the argument parser"""
    parser = argparse.ArgumentParser(
        prog="openrecon",
        description="OpenRecon — a lightweight, modular cybersecurity scanner"
    )
    parser.add_argument('--version', '-v', '--ver', action='version', version=f'OpenRecon {VERSION}')
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- port scanning ----
    scan_parser = subparsers.add_parser("scan", help="Network and domain reconnaissance modules")
    scan_parser.add_argument("-t", "--target", required=True, help="Target IP, domain, or range (e.g., scanme.nmap.org or 192.168.1.0/24)")
    scan_parser.add_argument("-f", "--flags", help="Nmap flags for port scan (e.g. '-sS -p 80')")
    
    # ---- subdomain scanner ----
    enum_parser = subparsers.add_parser("enum", help="Subdomain enumeration module")
    enum_parser.add_argument("-d", "--domain", help="Target domain (e.g., example.com)")
    enum_parser.add_argument("-r", "--recursive", action="store_true", help="Enable recursive enumeration")
    enum_parser.add_argument("--depth", type=int, default=1, help="Maximum recursion depth (default: 1)")
    enum_parser.add_argument("--no-dns", action="store_true", help="Skip DNS validation")
    enum_parser.add_argument("--clear-cache", action="store_true", help="Clear the subdomain cache")
    enum_parser.add_argument("--show-cache", action="store_true", help="Show the subdomain cache")
    enum_parser.add_argument("--no-cache", action="store_true", help="Disable caching of results")
    enum_parser.add_argument("--sources", help="Comma-separated sources to use (crt,alien,hacker,buffer,threat)")
    enum_parser.add_argument("--threads", type=int, default=5, help="Maximum concurrent threads (default: 5)")
    enum_parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds (default: 15)")
    enum_parser.add_argument("--retries", type=int, default=3, help="Max retries for failed requests (default: 3)")
    enum_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    enum_parser.add_argument("-o", "--output", help="Output file path for results")
    
    # ---- ping and discovery ----
    disc_parser = subparsers.add_parser("disc", help="Network discovery modules")
    disc_parser.add_argument("--range", "-r", default="192.168.1.0/24", help="IP range for discovery (default: 192.168.1.0/24)")
    disc_parser.add_argument("--ping", action="store_true", help="Perform ping sweep")
    disc_parser.add_argument("--arp", action="store_true", help="Perform ARP discovery")
    disc_parser.add_argument("--timeout", type=float, default=1.0, help="Ping timeout in seconds (default: 1.0)")
    disc_parser.add_argument("--retry", type=int, default=2, help="Number of retries for failed pings (default: 2)")
    disc_parser.add_argument("--threads", type=int, default=100, help="Maximum number of concurrent threads (default: 100)")
    disc_parser.add_argument("--dns", action="store_true", help="Perform reverse DNS lookups")
    disc_parser.add_argument("--rate", type=float, default=0.01, help="Delay between pings in seconds (default: 0.01)")
    disc_parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    # ---- SQLi scanner ----
    sqli_parser = subparsers.add_parser("sqli", help="SQL Injection scanner")
    sqli_parser.add_argument("url", help="Target URL (e.g. http://site.com/vuln.php)")
    sqli_parser.add_argument("--type", choices=["error", "union", "time", "classic", "all"], default="classic", help="Scan type: error (Error-Based), union (Union-Based), time (Time-Based), classic (Default), all (All types)")
    sqli_parser.add_argument("--threads", "-t", type=int, default=5, help="Number of threads (default: 5)")
    sqli_parser.add_argument("--crawl", "-c", type=int, default=0, help="Crawl depth (0 to disable, default: 0)")
    sqli_parser.add_argument("--max-urls", type=int, default=10, help="Max URLs to crawl (default: 10)")
    sqli_parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests in seconds (default: 0.5)")
    sqli_parser.add_argument("--output", "-o", help="Output file path for results (without extension)")
    sqli_parser.add_argument("--format", choices=["json", "txt", "html"], default="json", help="Output format (default: json)")
    sqli_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    sqli_parser.add_argument("--cookie", help="Cookie header string (e.g. 'PHPSESSID=xyz')")
    sqli_parser.add_argument("--user-agent", help="Custom User-Agent string")
    sqli_parser.add_argument("--proxy", help="Proxy to use (format: http://proxy:port)")
    sqli_parser.add_argument("--no-forms", action="store_true", help="Skip form scanning")
    sqli_parser.add_argument("--no-params", action="store_true", help="Skip URL parameter scanning")
    sqli_parser.add_argument("--payloads", help="Path to custom payloads file (JSON format)")
    sqli_parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")
    sqli_parser.add_argument("--verify-ssl", action="store_true", help="Verify SSL certificates (disabled by default)")
    
    # ---- XSS scanner ----
    xss_parser = subparsers.add_parser("xss", help="Cross-Site Scripting (XSS) scanner")
    xss_parser.add_argument("url", help="Target URL (e.g. http://site.com/vuln.php)")
    xss_parser.add_argument("--type", choices=["reflected", "dom", "stored", "all"], default="reflected", help="Scan type: reflected (Reflected XSS), dom (DOM XSS), blind (Blind XSS), all (All types)")
    xss_parser.add_argument("--threads", "-t", type=int, default=5, help="Number of threads (default: 5)")
    xss_parser.add_argument("--crawl", "-c", type=int, default=0, help="Crawl depth (0 to disable, default: 0)")
    xss_parser.add_argument("--max-urls", type=int, default=10, help="Max URLs to crawl (default: 10)")
    xss_parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests in seconds (default: 0.5)")
    xss_parser.add_argument("--output", "-o", help="Output file path for results (without extension)")
    xss_parser.add_argument("--format", choices=["json", "txt", "html"], default="json", help="Output format (default: json)")
    xss_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    xss_parser.add_argument("--cookie", help="Cookie header string (e.g. 'PHPSESSID=xyz')")
    xss_parser.add_argument("--user-agent", help="Custom User-Agent string")
    xss_parser.add_argument("--proxy", help="Proxy to use (format: http://proxy:port)")
    xss_parser.add_argument("--no-forms", action="store_true", help="Skip form scanning")
    xss_parser.add_argument("--no-params", action="store_true", help="Skip URL parameter scanning")
    xss_parser.add_argument("--payloads", help="Path to custom payloads file (JSON format)")
    xss_parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")
    xss_parser.add_argument("--verify-ssl", action="store_true", help="Verify SSL certificates (disabled by default)")
    xss_parser.add_argument("--callback-url", help="Callback URL for blind XSS detection")
    
    # ---- CSRF scanner ----
    csrf_parser = subparsers.add_parser("csrf",help='CSRF Vulnerability Scanner')
    csrf_parser.add_argument('url', help='Target URL to scan')
    csrf_parser.add_argument('-c', '--cookies', help='Cookies in name1=value1;name2=value2 format')
    csrf_parser.add_argument('-H', '--headers', help='Additional headers in JSON format')
    csrf_parser.add_argument('-d', '--depth', type=int, default=3, help='Maximum crawl depth')
    csrf_parser.add_argument('-t', '--timeout', type=int, default=15, help='Request timeout in seconds')
    csrf_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    csrf_parser.add_argument('-o', '--output', help='Output results to JSON file')
    
    # ----CMS Detector ----
    cms_parser = subparsers.add_parser('cms', help='Advanced CMS Detector')
    cms_parser.add_argument('url', help='URL of the website to analyze')
    cms_parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    cms_parser.add_argument('--user-agent', help='Custom User-Agent string')
    cms_parser.add_argument('--no-verify', action='store_true', help='Disable SSL verification')
    cms_parser.add_argument('--threads', type=int, default=5, help='Maximum number of threads')
    cms_parser.add_argument('--output', '-o', help='Output file for results (JSON format)')
    cms_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # ---- GraphQL scanner ----
    graphql_parser = subparsers.add_parser("graphql", help="GraphQL API Scanner")
    graphql_parser.add_argument("url", help="Base URL of the target (e.g., https://api.example.com)")
    graphql_parser.add_argument("--headers", help="Additional headers in JSON format")
    graphql_parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")
    graphql_parser.add_argument("--output", "-o", help="Output file for results (JSON format)")
    graphql_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    graphql_parser.add_argument("--verify-ssl", action="store_true", help="Verify SSL certificates (disabled by default)")
    graphql_parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds (default: 1.0)")
    graphql_parser.add_argument("--max-requests", type=int, default=30, help="Maximum requests per minute (default: 30)")
    graphql_parser.add_argument("--retry", type=int, default=3, help="Number of retries for failed requests (default: 3)")
    graphql_parser.add_argument("--retry-delay", type=float, default=5.0, help="Delay between retries in seconds (default: 5.0)")
    
    # ---- Utils ----
    util_parser = subparsers.add_parser("util", help="Utility functions")
    util_subparsers = util_parser.add_subparsers(dest="util_command", required=True)
    compat_parser = util_subparsers.add_parser("check-compat", help="Check payload file compatibility")
    compat_parser.add_argument("payload_file", help="Path to payload file to check")
    convert_parser = util_subparsers.add_parser("convert", help="Convert text payloads to JSON")
    convert_parser.add_argument("input_file", help="Input text file with one payload per line")
    convert_parser.add_argument("-o", "--output", help="Output JSON file (default: same as input with .json extension)")
    
    return parser

def main():
    """Main entry point for the CLI"""
    print(r"""
 ██████╗ ██████╗ ███████╗███╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
╚██████╔╝██║     ███████╗██║ ╚████║██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
          Github: https://github.com/R0salman
""")
    parser = create_parser()
    args = parser.parse_args()
    
    # ---- scan ----
    if args.command == "scan":
        if not args.flags:
            console.print("[red][!] Provide --flags for port scan[/red]")
            return
        console.print(f"[+] Port scanning {args.target} with flags: {args.flags}")
        result = run_port_scan(args.target, args.flags)
        
    # ---- Enum ----
    elif args.command == "enum":
        # Create enumerator instance for cache operations
        enumerator = SubdomainEnumerator(
            max_retries=args.retries,
            timeout=args.timeout,
            max_workers=args.threads,
            validate_dns=not args.no_dns,
            cache_time=0 if args.no_cache else 86400,
            verbose=args.verbose
        )
        
        if args.clear_cache:
            enumerator.clear_cache()
            return
        elif args.show_cache:
            enumerator.show_cache()
            return
            
        if not args.domain:
            console.print("[red][!] Domain is required for enumeration. Use -d or --domain to specify a target.[/red]")
            return
            
        console.print(f"[green][+] Enumerating subdomains for {args.domain}[/green]")
        
        if not args.recursive:
            fp, fp_info = get_fingerprint(args.domain)
            if fp:
                console.print(f"Fingerprint: [yellow]{fp}[/yellow]")
                if fp_info:
                    console.print(f"Server: {fp_info.get('server', 'unknown')}")
                    console.print(f"Status: {fp_info.get('status', 'unknown')}")

        if args.recursive:
            subs = recursive_enum(
                args.domain,
                depth=args.depth,
                validate=not args.no_dns
            )
        else:
            subs = enumerator.get_subdomains(
                args.domain,
                use_all_sources=not args.sources
            )

        for sub in sorted(subs):
            console.print(f" - [cyan]{sub}[/cyan]")
        
        console.print(f"[green][+] Total subdomains: {len(subs)}[/green]")
        
        if args.output:
            output_path = reporter.get_reports_dir() / args.output
            with open(output_path, 'w') as f:
                f.write('\n'.join(sorted(subs)))
            console.print(f"[green][+] Results saved to {args.output}[/green]")
            
    # ---- Disc ----
    elif args.command == "disc":
        if args.ping:
            console.print(f"[green][+] Ping sweep on {args.range}[/green]")
            results = ping_sweep(
                subnets=[args.range],
                timeout=args.timeout,
                retry_count=args.retry,
                max_threads=args.threads,
                dns_lookup=args.dns,
                rate_limit=args.rate,
                verbose=args.verbose
            )
            print_ping_results(results)
            
        if args.arp:
            console.print(f"[green][+] ARP discovery on {args.range}[/green]")
            for dev in live_discovery(args.range):
                console.print(f"[cyan]{dev['ip']}[/cyan] - {dev['mac']}")

    # ---- SQLi scanner ----
    elif args.command == "sqli":
        console.print(f"[green][+] SQLi scan on: {args.url}[/green]")
        console.print(f"[bold][+] Using {args.type} scan type[/bold]")
        
        #cookies if provided
        cookies = {}
        if args.cookie:
            for cookie_pair in args.cookie.split(';'):
                if '=' in cookie_pair:
                    key, value = cookie_pair.strip().split('=', 1)
                    cookies[key] = value
        
        # Load custom payloads if provided
        custom_payloads = None
        if args.payloads:
            try:
                with open(args.payloads, 'r') as f:
                    custom_payloads = json.load(f)
                console.print(f"[green][+] Loaded {len(custom_payloads)} custom payloads from {args.payloads}[/green]")
            except Exception as e:
                console.print(f"[red][!] Failed to load custom payloads: {e}[/red]")
                return
        
        options = {
            'type': args.type,
            'threads': args.threads,
            'crawl_depth': args.crawl,
            'verbose': args.verbose,
            'output': str(reporter.get_reports_dir() / args.output) if args.output else None,
            'output_format': args.format,
            'scan_forms': not args.no_forms,
            'scan_params': not args.no_params,
            'max_urls': args.max_urls,
            'user_agent': args.user_agent,
            'cookies': cookies,
            'proxy': args.proxy,
            'delay': args.delay,
            'custom_payloads': custom_payloads,
            'timeout': args.timeout,
            'verify_ssl': args.verify_ssl,
        }
        
        try:
            scanner = SQLiScanner(options)  # Initialize scanner with options
            vulnerabilities = scanner.scan_target(args.url)  # Call scan_target with the URL
            if vulnerabilities:
                console.print(f"[green][+] Scan completed. Found {len(vulnerabilities)} potential vulnerabilities[/green]")
            else:
                console.print("[yellow][!] No vulnerabilities found[/yellow]")
        except Exception as e:
            console.print(f"[red][!] SQLi scan failed: {e}[/red]")
        
    # ---- XSS ----
    elif args.command == "xss":
        console.print(f"[green][+] XSS scan on: {args.url}[/green]")
        console.print(f"[bold][+] Using {args.type} scan type[/bold]")

        # Load custom payloads
        custom_payloads = None
        if args.payloads:
            try:
                with open(args.payloads, 'r') as f:
                    custom_payloads = json.load(f) if args.payloads.endswith(".json") else [line.strip() for line in f]
            except Exception as e:
                console.print(f"[red][!] Failed to load payloads: {e}[/red]")
                
        blacklist = {
  "blacklist": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp3", ".mp4", ".avi", ".pdf"]
}

        options = {
            'type': args.type,
            'threads': args.threads,
            'verbose': args.verbose,
            'output': args.output,
            'output_format': args.format,
            'delay': args.delay,
            'custom_payloads': custom_payloads,
            'blacklist': blacklist,
            'user_agent': args.user_agent or 'Mozilla/5.0',
            'cookie':args.cookie if args.cookie else None,
            'timeout': args.timeout
        }

        try:
            scanner = AsyncXSSScanner(options)
            urls = [args.url]
            results = asyncio.run(scanner.run(urls))
            scanner.display_results(results)

            # Save results
            if results and args.output:
                out_path = str(reporter.get_reports_dir() / f"{args.output}.{args.format}")
                with open(out_path, "w") as f:
                    if args.format == "json":
                        json.dump(results, f, indent=2)
                    else:
                        for v in results:
                            f.write(f"URL: {v['url']}\nParam: {v['param_name']}\nPayload: {v['payload']}\nType: {v['type']}\n\n")
                console.print(f"[green][+] Results saved to {out_path}[/green]")

        except Exception as e:
            console.print(f"[red][!] XSS scan failed: {e}[/red]")
    
    # ---- CSRF ----
    elif args.command == "csrf":
        cookies = {}
        if args.cookies:
            for pair in args.cookies.split(';'):
                try:
                    name, value = pair.strip().split('=', 1)
                    cookies[name] = value
                except ValueError:
                    print(f"[!] Invalid cookie format: {pair}")
                    sys.exit(1)
        
        # Parse headers
        headers = {}
        if args.headers:
            try:
                headers = json.loads(args.headers)
            except json.JSONDecodeError:
                print("[!] Invalid headers format. Must be valid JSON.")
                sys.exit(1)
        
        scanner = CSRFScanner(
            url=args.url,
            cookies=cookies,
            headers=headers,
            max_depth=args.depth,
            timeout=args.timeout,
            verbose=args.verbose
        )
        
        results = scanner.scan()
        
        if args.output:
            output_path = reporter.get_reports_dir() / args.output
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
            
    elif args.command == 'cms':
        # Create detector instance with verbose flag
        detector = CMSDetector(
            timeout=args.timeout,
            user_agent=args.user_agent,
            verify_ssl=not args.no_verify,
            max_threads=args.threads,
            verbose=args.verbose
        )
        
        console.print(f"\nAnalyzing {args.url}...")
        start_time = time.time()
        
        # Perform detection
        results = detector.detect(args.url)
        
        elapsed_time = time.time() - start_time
        
        # Print results
        if 'error' in results:
            console.print(f"\n[red]Error: {results['error']}[/red]")
            return 1
        
        console.print(f"\n[green]Results for {results['url']} (completed in {elapsed_time:.2f} seconds):[/green]")
        console.print(f"Status Code: {results['status_code']}")
        console.print(f"Server: {results['server']}")
        console.print(f"Powered By: {results['powered_by']}")
        
        console.print("\n[bold]Detected CMS:[/bold]")
        if 'technologies' in results and 'cms' in results['technologies'] and results['technologies']['cms']:
            for cms_info in results['technologies']['cms']:
                # Color code confidence levels
                confidence_color = (
                    "green" if cms_info['confidence'] > 70 else
                    "yellow" if cms_info['confidence'] > 30 else
                    "red"
                )
                console.print(f"  - [bold]{cms_info['name'].title()}[/bold]: [{confidence_color}]{cms_info['confidence']}%[/{confidence_color}] confidence")
        else:
            console.print("[yellow]  No CMS detected with confidence[/yellow]")
        
        # Display additional technologies in regular output
        if 'technologies' in results:
            console.print("\n[bold]Additional Technologies:[/bold]")
            tech_categories = {
                'web_servers': 'Web Servers',
                'javascript_frameworks': 'JavaScript Frameworks',
                'ui_frameworks': 'UI Frameworks',
                'analytics': 'Analytics',
                'tag_managers': 'Tag Managers',
                'cdn': 'CDN',
                'security': 'Security',
                'miscellaneous': 'Miscellaneous'
            }
            
            for tech_key, tech_name in tech_categories.items():
                if tech_key in results['technologies'] and results['technologies'][tech_key]:
                    techs = results['technologies'][tech_key]
                    if techs:  # Only show if there are technologies in this category
                        tech_list = [f"{tech['name']} ({tech['confidence']}%)" for tech in techs]
                        console.print(f"  - {tech_name}: {', '.join(tech_list)}")

        if args.verbose:
            console.print("\n[bold]Detection Details:[/bold]")
            if 'detection_methods' in results:
                for method, method_results in results['detection_methods'].items():
                    console.print(f"\n  {method.replace('_', ' ').title()}:")
                    if method_results:
                        for cms, matches in method_results.items():
                            console.print(f"    - {cms.title()}: {', '.join(matches)}")
                    else:
                        console.print("[dim]    No matches[/dim]")
            
        # Save results to file if requested
        if args.output:
            output_path = reporter.get_reports_dir() / args.output
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            console.print(f"\n[green]Results saved to {args.output}[/green]")
        
        return 0
            
    # ---- GraphQL ----
    elif args.command == "graphql":
        headers = {}
        if args.headers:
            try:
                headers = json.loads(args.headers)
            except json.JSONDecodeError:
                console.print("[red][!] Invalid headers JSON format[/red]")
                return

        console.print(f"[green][+] Starting GraphQL scan against {args.url}[/green]")
        console.print(f"[cyan][*] Rate limiting: {args.max_requests} requests/minute with {args.delay}s delay[/cyan]")
        
        scanner = GraphQLScanner(
            base_url=args.url,
            headers=headers,
            verbose=args.verbose,
            request_delay=args.delay,
            max_requests_per_minute=args.max_requests,
            max_retries=args.retry,
            retry_delay=args.retry_delay
        )
        
        try:
            results = scanner.scan()
            
            if args.output:
                output_path = reporter.get_reports_dir() / args.output
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2)
                console.print(f"[green][+] Results saved to {args.output}[/green]")
            else:
                # Print summary of results
                if results['discovered_endpoints']:
                    console.print("\n[bold]Discovered Endpoints:[/bold]")
                    for endpoint in results['discovered_endpoints']:
                        console.print(f" - [cyan]{endpoint}[/cyan]")
                
                if results['vulnerabilities']:
                    console.print("\n[bold]Vulnerability Check Results:[/bold]")
                    vulns = results['vulnerabilities']
                    for key, value in vulns.items():
                        if isinstance(value, bool):
                            status = "[green]Enabled[/green]" if value else "[red]Disabled[/red]"
                            console.print(f" - {key}: {status}")
                        elif isinstance(value, list) and value:
                            console.print(f" - {key}:")
                            for item in value:
                                console.print(f"   * [yellow]{item}[/yellow]")
                
                if results['scan_duration']:
                    console.print(f"\n[green][+] Scan completed in {results['scan_duration']:.2f} seconds[/green]")
                    
        except KeyboardInterrupt:
            console.print("\n[yellow][!] Scan interrupted by user[/yellow]")
            return
        except Exception as e:
            console.print(f"[red][!] Scan failed: {str(e)}[/red]")
            if args.verbose:
                import traceback
                console.print(traceback.format_exc())

    # ---- Util ----
    elif args.command == "util":
        if args.util_command == "check-compat":
            console.print(f"[green][+] Checking payload file compatibility: {args.payload_file}[/green]")
            time.sleep(2)
            
            payload_path = os.path.abspath(args.payload_file)
            console.print(f"[green][+] Checking payload file: {payload_path}[/green]")
            time.sleep(1)
            
            if not os.path.exists(payload_path):
                console.print(f"[red][!] File not found: {payload_path}[/red]")
                return
            
            success = check_payload_file(payload_path)
            if success:
                console.print("[green][+] Payload file is compatible[/green]")
            else:
                console.print("[red][!] Payload file is not compatible[/red]")
        
        elif args.util_command == "convert":
            input_path = os.path.abspath(args.input_file)
            console.print(f"[green][+] Converting text file: {input_path}[/green]")
            time.sleep(2)
            
            if not os.path.exists(input_path):
                console.print(f"[red][!] Input file not found: {input_path}[/red]")
                return
            
            if args.output:
                output_path = os.path.abspath(args.output)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            else:
                dir_name = os.path.dirname(input_path)
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(dir_name, f"{base_name}.json")
            
            success = convert_txt_to_json(input_path, output_path)
            if success:
                console.print(f"[green][+] Successfully converted to {output_path}[/green]")
            else:
                console.print("[red][!] Conversion failed[/red]")

def cli_entrypoint():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        if "--debug" in sys.argv:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    cli_entrypoint()