import time
from urllib.parse import urlparse


from openrecon.core.httpClient import HTTPClient
from openrecon.core.parsers import HTMLParser, ResponseAnalyzer
from openrecon.core.crawler import WebCrawler
from openrecon.core.SQLdetector import SQLiDetector
from openrecon.core.payloadModels import *
from openrecon.core.reporter import Reporter
from openrecon.core.progress import ProgressTracker
from openrecon.core.util import Utils



class SQLiScanner:
    def __init__(self, options=None):
        self.options = options or {}
        self.http_client = HTTPClient(
            user_agent=self.options.get('user_agent'),
            cookies=self.options.get('cookies'),
            proxy=self.options.get('proxy'),
            timeout=self.options.get('timeout', 10),
            verify_ssl=self.options.get('verify_ssl', False)
        )
        self.html_parser = HTMLParser()
        self.response_analyzer = ResponseAnalyzer()
        self.sqli_detector = SQLiDetector(self.http_client)
        self.crawler = WebCrawler(self.http_client)
        self.reporter = Reporter()
        self.progress = ProgressTracker()
        self.utils = Utils()
        
    def get_payloads_for_type(self, scan_type, custom_payloads=None):
        if custom_payloads:
            return custom_payloads
            
        payload_sets = {
            'error': ERROR_BASED_PAYLOADS,
            'union': UNION_BASED_PAYLOADS,
            'time': TIME_BASED_PAYLOADS,
            'classic': CLASSIC_PAYLOADS,
            'all': SQLI_PAYLOADS
        }
        return payload_sets.get(scan_type, CLASSIC_PAYLOADS)
        
    def scan_form(self, url, form_details):
        scan_type = self.options.get('type', 'classic')
        verbose = self.options.get('verbose', False)
        delay = self.options.get('delay', 0.5)
        delay_threshold = max(2.5, delay * 5)
        custom_payloads = self.options.get('custom_payloads', None)
        
        form_url = url if not form_details['action'] else self.http_client.join_url(url, form_details['action'])
        method = form_details['method']
        
        baseline_data = {}
        for input_field in form_details['inputs']:
            if input_field['name'] is None:
                continue
            
            if input_field['type'] == "hidden" or input_field['value']:
                baseline_data[input_field['name']] = input_field['value']
            elif input_field['type'] != "submit":
                baseline_data[input_field['name']] = "baseline123"
        
        baseline_content = self.sqli_detector.get_baseline_response(form_url, method, baseline_data)
        
        vulnerability_details = []
        payloads = self.get_payloads_for_type(scan_type, custom_payloads)
        
        with self.progress.create_progress_bar() as progress:
            task = self.progress.create_task(
                progress, 
                f"Testing payloads on {form_url}", 
                len(form_details['inputs']) * len(payloads)
            )
            
            for input_field in form_details['inputs']:
                if input_field['name'] is None or input_field['type'] == "submit":
                    continue
                    
                for payload in payloads:
                    test_data = baseline_data.copy()
                    test_data[input_field['name']] = payload
                    
                    if delay > 0:
                        time.sleep(delay)
                    
                    if verbose:
                        pass
                    
                    vulnerable, response, details = self.sqli_detector.test_payload(
                        form_url, method, test_data, 
                        f"{payload} in {input_field['name']}", 
                        baseline_content, delay_threshold
                    )
                    
                    if verbose:
                        status = "VULNERABLE" if vulnerable else "NOT vulnerable"
                        self.progress.display_status(
                            f"Result for payload '{payload}' on field '{input_field['name']}': {status}",
                            "success" if vulnerable else "warning"
                        )
                    
                    if vulnerable:
                        vulnerability_details.append({
                            "url": form_url,
                            "method": method,
                            "input_field": input_field['name'],
                            "payload": payload,
                            "details": details
                        })
                            
                    progress.update(task, advance=1)
        
        return vulnerability_details
        
    def scan_url_params(self, url):
        scan_type = self.options.get('type', 'classic')
        verbose = self.options.get('verbose', False)
        delay = self.options.get('delay', 0.5)
        
        params = self.http_client.extract_url_parameters(url)
        if not params:
            return []
            
        vulnerability_details = []
        
        baseline_content = self.sqli_detector.get_baseline_response(url, "get", params)
            
        payloads = self.get_payloads_for_type(scan_type)
            
        with self.progress.create_progress_bar() as progress:
            task = self.progress.create_task(
                progress,
                f"Testing URL parameters on {url}",
                len(params) * len(payloads)
            )
            
            for param_name, param_value in params.items():
                for payload in payloads:
                    test_params = params.copy()
                    test_params[param_name] = payload
                    
                    if delay > 0:
                        time.sleep(delay)
                    
                    vulnerable, response, details = self.sqli_detector.test_payload(
                        url, "get", test_params, 
                        f"{payload} in {param_name}",
                        baseline_content
                    )
                    
                    if vulnerable:
                        vulnerability_details.append({
                            "url": url,
                            "method": "get",
                            "input_field": param_name,
                            "payload": payload,
                            "details": details
                        })
                        if verbose:
                            self.progress.display_status(f"Found vulnerability in parameter {param_name} using {payload}", "success")
                            
                    progress.update(task, advance=1)
        
        return vulnerability_details
        
    def scan_target(self, url):
        self.progress.display_header(f"Starting SQL Injection scan on: {url}")
        
        if not self.http_client.validate_url(url):
            self.progress.display_status("The website is unreachable or invalid. Please check the URL and try again.", "error")
            return []
        
        vulnerabilities = []
        
        # Scan URL parameters if present
        if self.options.get('scan_params', True):
            self.progress.display_status("Scanning URL parameters for SQLi vulnerabilities...", "info")
            if "?" in url:
                param_vulns = self.scan_url_params(url)
                vulnerabilities.extend(param_vulns)
            else:
                self.progress.display_status("No URL parameters found. Try adding parameters like '?id=1'", "warning")
        
        if self.options.get('scan_forms', True):
            self.progress.display_status("Scanning forms for SQLi vulnerabilities...", "info")
            response, _ = self.http_client.get(url)
            
            if response:
                forms = self.html_parser.extract_forms(response.content)
                if forms:
                    self.progress.display_status(f"Found {len(forms)} forms on the page", "info")
                    for i, form in enumerate(forms, 1):
                        self.progress.display_status(f"Testing form #{i}", "info")
                        form_details = self.html_parser.extract_form_details(form)
                        form_vulns = self.scan_form(url, form_details)
                        vulnerabilities.extend(form_vulns)
                else:
                    self.progress.display_status("No forms found on the page", "warning")
        
        # crawl and scan if enabled
        crawl_depth = self.options.get('crawl_depth', 0)
        if crawl_depth > 0:
            self.progress.display_status(f"Starting crawl and scan with depth {crawl_depth}...", "info")
            self._crawl_and_scan(url, vulnerabilities)
        
        # display and save results
        self.reporter.display_scan_summary("SQL Injection", url, vulnerabilities)
        self.reporter.display_vulnerabilities(vulnerabilities)
        
        if self.options.get('output', False):
            output_format = self.options.get('output_format', 'json')
            self.reporter.save_results(url, "sqli", vulnerabilities, formats=[output_format])
        
        return vulnerabilities
        
    def _crawl_and_scan(self, base_url, vulnerabilities):
        max_urls = self.options.get('max_urls', 10)
        crawl_depth = self.options.get('crawl_depth', 1)
        
        def scan_page(url, response):
            if url == base_url:
                return
                
            self.progress.display_status(f"Scanning discovered URL: {url}", "info")
            
            scan_options = self.options.copy()
            scan_options['crawl_depth'] = 0
            
            page_scanner = SQLiScanner(scan_options)
            page_vulns = page_scanner.scan_target(url)
            
            vulnerabilities.extend(page_vulns)
        
        self.progress.display_status(f"Crawling website with depth {crawl_depth}, max {max_urls} URLs per level", "info")
        self.crawler.crawl(base_url, max_depth=crawl_depth, max_urls=max_urls, callback=scan_page)