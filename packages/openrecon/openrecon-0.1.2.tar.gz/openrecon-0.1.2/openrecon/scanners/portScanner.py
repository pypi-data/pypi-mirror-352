import nmap
import json
import os
import re
import sys
import platform
from datetime import datetime
from rich.console import Console
from rich.text import Text
from rich.table import Table
from pathlib import Path
from openrecon.core.reporter import Reporter

console = Console()
reporter = Reporter()

def get_reports_dir():
    reports_dir = Path.home() / "Documents" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    print(f"Reports path used: {reports_dir}")
    return reports_dir

def parse_specified_ports(flags):
    """Parse port specifications from nmap flags"""
    match = re.search(r"-p\s+([0-9,\-]+)", flags)
    if match:
        ports_str = match.group(1)
        if ',' in ports_str:
            return [int(p.strip()) for p in ports_str.split(',') if p.strip().isdigit()]
        elif '-' in ports_str:
            parts = ports_str.split('-')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return list(range(int(parts[0]), int(parts[1]) + 1))
    return None

def is_specific_port_list(flags):
    """Check if flags specify a specific list of ports"""
    match = re.search(r"-p\s+([\d,]+)", flags)
    return bool(match)

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0  # Unix-like systems
    except:
        return False

def run_elevated_scan(scanner, target, flags):
    """Handle elevated scan based on OS"""
    if platform.system() == 'Windows':
        # On Windows, we need to inform the user to run as administrator
        console.print("[yellow][!] This scan requires Administrator privileges.[/yellow]")
        console.print("[yellow][!] Please run the command prompt or PowerShell as Administrator and try again.[/yellow]")
        return None
    else:
        # On Unix-like systems, we can try sudo
        console.print("[yellow][!] Scan requires root privileges. Retrying with sudo...[/yellow]")
        try:
            scanner = nmap.PortScanner()
            scanner.scan(target, arguments=flags, sudo=True)
            return scanner
        except Exception as e:
            console.print(f"[red][!] Failed to run with sudo: {str(e)}[/red]")
            console.print("[red][!] Please run the script with sudo manually.[/red]")
            return None

def display_scan_results(scanner, target):
    """Display scan results in a formatted table"""
    open_ports_found = False
    
    for host in scanner.all_hosts():
        console.print(f"\n[bold green]═══ Scan Results for {host} ═══[/bold green]")
        console.print(f"Host State: [yellow]{scanner[host].state()}[/yellow]")
        
        # Check if host has any protocols
        protocols = scanner[host].all_protocols()
        if not protocols:
            console.print("[dim]No protocols detected[/dim]")
            continue
            
        for proto in protocols:
            ports = scanner[host][proto].keys()
            if not ports:
                continue
                
            # Create table for this protocol
            table = Table(title=f"{proto.upper()} Ports")
            table.add_column("Port", style="cyan", no_wrap=True)
            table.add_column("State", no_wrap=True)
            table.add_column("Service", style="green")
            table.add_column("Product", style="blue")
            table.add_column("Version", style="magenta")
            
            # Sort ports numerically
            sorted_ports = sorted(ports)
            
            for port in sorted_ports:
                port_data = scanner[host][proto][port]
                state = port_data["state"]
                name = port_data.get("name", "unknown")
                product = port_data.get("product", "")
                version = port_data.get("version", "")
                
                # Color code based on state
                if state == "open":
                    state_style = "[bold green]open[/bold green]"
                    open_ports_found = True
                elif state == "closed":
                    state_style = "[red]closed[/red]"
                elif state == "filtered":
                    state_style = "[blue]filtered[/blue]"
                else:
                    state_style = f"[dim]{state}[/dim]"
                
                table.add_row(
                    str(port),
                    state_style,
                    name if name != "unknown" else "[dim]unknown[/dim]",
                    product if product else "[dim]-[/dim]",
                    version if version else "[dim]-[/dim]"
                )
            
            console.print(table)
    
    # Summary
    if open_ports_found:
        console.print(f"\n[bold green]Scan completed! Open ports found above.[/bold green]")
    else:
        console.print(f"\n[yellow]ℹ Scan completed. No open ports detected.[/yellow]")

def save_scan_results(scanner, target):
    """Save scan results to JSON file"""
    result_data = {}
    
    for host in scanner.all_hosts():
        result_data[host] = {
            "state": scanner[host].state(),
            "protocols": {}
        }
        
        for proto in scanner[host].all_protocols():
            ports = scanner[host][proto].keys()
            result_data[host]["protocols"][proto] = {}
            
            for port in ports:
                port_data = scanner[host][proto][port]
                result_data[host]["protocols"][proto][port] = port_data
    
    # Save to file
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Clean target name for filename
        clean_target = re.sub(r'[^\w\.-]', '_', target)
        json_output_file = reporter.get_reports_dir() / f"portscan_{clean_target}_{timestamp}.json"
        
        with open(json_output_file, "w") as json_file:
            json.dump(result_data, json_file, indent=4)
        print(f"Final report path: {json_output_file}")

        return json_output_file
        
    except Exception as e:
        console.print(f"\n[red][!] Failed to save report: {str(e)}[/red]")
        return None

def run_port_scan(target, flags, **kwargs):
    scanner = nmap.PortScanner()
    
    # Validate nmap installation
    try:
        scanner.nmap_version()
    except Exception:
        console.print("[red][!] Nmap is not installed or not found in system PATH.[/red]")
        console.print("[yellow][!] Please install Nmap from https://nmap.org/download.html[/yellow]")
        return None
    
    try:
        console.print(f"[bold]Target:[/bold] [yellow]{target}[/yellow]")
        console.print(f"[bold]Nmap flags:[/bold] [white]{flags}[/white]")
        console.print(f"[bold]Starting scan...[/bold]\n")
        
        # Show privilege status
        if is_admin():
            console.print("[dim]Running with elevated privileges ✓[/dim]")
        else:
            console.print("[dim]Running with standard privileges[/dim]")
        
        # First check if host is up using a quick ping scan
        console.print("[dim]Checking host availability...[/dim]")
        try:
            # Use -sn for ping scan, add -Pn if specified in original flags
            ping_flags = "-sn"
            if "-Pn" in flags:
                ping_flags += " -Pn"
            scanner.scan(target, arguments=ping_flags)
            
            # Check if any hosts are up
            hosts_up = [host for host in scanner.all_hosts() if scanner[host].state() == 'up']
            if not hosts_up:
                console.print(f"[red][!] Host {target} appears to be down or not responding to ping.[/red]")
                console.print("[yellow]Tip: Use -Pn flag to skip host discovery if you're sure the host is up.[/yellow]")
                return None
            else:
                console.print(f"[green]✓ Host is up! Proceeding with port scan...[/green]\n")
        except nmap.nmap.PortScannerError as e:
            # If ping scan fails with privileges error, skip it and proceed with main scan
            if "requires root privileges" not in str(e):
                raise e
        
        try:
            # Main scan
            scanner.scan(target, arguments=flags)
        except nmap.nmap.PortScannerError as e:
            if "requires root privileges" in str(e) or "requires privileged user" in str(e):
                # Try to run with elevated privileges
                scanner = run_elevated_scan(scanner, target, flags)
                if not scanner:
                    return None
            else:
                raise e
        
        # Check if scan was successful
        if not scanner.all_hosts():
            console.print(f"[yellow][!] No hosts found for target: {target}[/yellow]")
            console.print("[yellow][!] The target may be down or not reachable.[/yellow]")
            return None
        
        # Display results
        display_scan_results(scanner, target)
        
        # Save results
        output_file = save_scan_results(scanner, target)
        return {
            "scanner": scanner,
            "output_file": output_file,
            "target": target
        }

    except nmap.nmap.PortScannerError as e:
        console.print(f"[red][!] Nmap Error: {str(e)}[/red]")
        
        if "requires root privileges" in str(e) or "requires privileged user" in str(e):
            if platform.system() == 'Windows':
                console.print("[yellow][!] This scan requires Administrator privileges.[/yellow]")
                console.print("[yellow][!] Please run as Administrator and try again.[/yellow]")
            else:
                console.print("[yellow][!] This scan requires root privileges.[/yellow]")
                console.print("[yellow][!] Please run with sudo and try again.[/yellow]")
        elif "nmap executable not found" in str(e).lower():
            console.print("[red][!] Nmap is not installed or not found in system PATH.[/red]")
            console.print("[yellow][!] Please install Nmap from https://nmap.org/download.html[/yellow]")
        elif "target specification" in str(e).lower():
            console.print(f"[red][!] Invalid target specification: {target}[/red]")
            console.print("[yellow][!] Please check the target format (IP, domain, or CIDR range).[/yellow]")
        else:
            console.print(f"[red][!] Scan failed with error: {str(e)}[/red]")
        
        return None
        
    except KeyboardInterrupt:
        console.print("\n[yellow][!] Scan interrupted by user[/yellow]")
        return None
        
    except Exception as e:
        console.print(f"[red][!] Unexpected error: {str(e)}[/red]")
        if "--debug" in sys.argv:
            import traceback
            console.print(traceback.format_exc())
        return None
