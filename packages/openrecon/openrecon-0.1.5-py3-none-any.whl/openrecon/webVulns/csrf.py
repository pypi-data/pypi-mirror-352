import json
import math
import re
import sys
import time
from urllib.parse import urljoin, urlparse, urldefrag
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from openrecon.core.colors import Colors, Messages

class CSRFScanner:
    def __init__(self, url: str, cookies: Optional[Dict] = None, headers: Optional[Dict] = None, max_depth: int = 3, timeout: int = 15, verbose: bool = False):
        self.console = Console()
        self.base_url = self._normalize_url(url)
        self.session = requests.Session()
        self.max_depth = max_depth
        self.timeout = timeout
        self.verbose = verbose
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CSRF-Scanner/2.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            **({'Cookie': '; '.join(f"{k}={v}" for k, v in cookies.items())} if cookies else {})
        })
        
        if headers:
            self.session.headers.update(headers)

        self.token_patterns = [
            'csrf', 'csrftoken', 'xsrf', 'xsrftoken', '_csrf', '_csrftoken',
            'authenticity_token', '_token', 'token', 'csrf_token', 'xsrf_token',
            'anti_csrf', '__requestverificationtoken', 'requesttoken',
            'nonce', 'form_key', 'csrf-param', 'csrf-token', 'csrfmiddlewaretoken',
            'laravel-token', 'symfony_token', 'django-csrftoken'
        ]

        self.visited_urls = set()
        self.results = {
            'forms': [],
            'endpoints': [],
            'meta_tags': [],
            'csp_policies': [],
            'cookies': [],
            'statistics': {
                'forms_analyzed': 0,
                'protected_forms': 0,
                'vulnerable_forms': 0,
                'endpoints_analyzed': 0,
                'protected_endpoints': 0,
                'vulnerable_endpoints': 0,
                'secure_cookies': 0,
                'insecure_cookies': 0,
                'meta_tags_found': 0,
                'csp_policies_analyzed': 0
            },
            'vulnerabilities': [],
            'validation': {
                'is_accessible': False,
                'response_time': None,
                'status_code': None
            }
        }

    def _normalize_url(self, url: str) -> str:
        """Ensure URL has proper scheme"""
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'
        return url.rstrip('/')

    def _validate_website(self) -> bool:
        """Check if website is accessible before scanning"""
        self.console.print("\n[+] Validating website accessibility...", style=Colors.CHECKING)
        
        try:
            start_time = time.time()
            response = self.session.head(
                self.base_url, 
                timeout=self.timeout,
                allow_redirects=True
            )
            elapsed = (time.time() - start_time) * 1000
            
            self.results['validation'].update({
                'is_accessible': True,
                'response_time': f"{elapsed:.2f}ms",
                'status_code': response.status_code
            })
            
            self.console.print(
                Messages.SITE_UP + 
                f" (Status: {response.status_code}, Response: {elapsed:.2f}ms)",
                style=Colors.VALID
            )
            return True
            
        except requests.RequestException as e:
            self.results['validation']['is_accessible'] = False
            self.console.print(
                Messages.SITE_DOWN + f" - {str(e)}", 
                style=Colors.INVALID
            )
            return False

    def scan(self) -> Optional[Dict]:
        if not self._validate_website():
            self.console.print(
                "[!] Aborting scan due to website accessibility issues",
                style=Colors.CRITICAL
            )
            return None
        
        self._analyze_page(self.base_url, 0, task=None)
        
        self._check_cookie_security()
        
        self._print_report()
        return self.results

    def _analyze_csp(self, csp_policy: str, page_url: str) -> None:
        csp_data = {
            'page_url': page_url,
            'policy': csp_policy,
            'findings': []
        }
        
        if "'unsafe-inline'" in csp_policy:
            csp_data['findings'].append(
                "CSP allows unsafe-inline which could weaken CSRF protections"
            )
        
        if "form-action" not in csp_policy:
            csp_data['findings'].append(
                "Missing form-action directive in CSP"
            )
        
        self.results['csp_policies'].append(csp_data)
        
        if csp_data['findings'] and self.verbose:
            for finding in csp_data['findings']:
                self._log_warning(f"CSP issue on {page_url}: {finding}")
                
    def _analyze_page(self, url: str, depth: int, task) -> None:
        if depth > self.max_depth or url in self.visited_urls:
            if self.verbose:
                self._log_debug(f"Skipping {url} (already visited or max depth reached)")
            return

        self.visited_urls.add(url)
        
        try:
            # First make a HEAD request to check content type
            head_response = self.session.head(url, timeout=self.timeout)
            content_type = head_response.headers.get('Content-Type', '').lower()
            
            if self.verbose:
                self._log_debug(f"Initial HEAD request to {url}")
                self._log_debug(f"Content-Type: {content_type}")
                self._log_debug(f"Headers: {dict(head_response.headers)}")

            # Only proceed with GET if it's HTML or we don't know the type
            if 'text/html' in content_type or not content_type:
                rendered_html = self._render_with_playwright(url)
                if not rendered_html:
                    return

                
                if self.verbose:
                    self._log_debug(f"GET response from {url}")
                    self._log_debug(f"Content length: {len(rendered_html)} bytes")
                    self._log_debug(f"First 200 chars: {rendered_html[:200]}...")

                soup = BeautifulSoup(rendered_html, 'html.parser')
                
                forms = soup.find_all('form')
                if self.verbose:
                    self._log_info(f"Found {len(forms)} forms at {url}")
                    for i, form in enumerate(forms, 1):
                        self._log_debug(f"Form {i}: Method={form.get('method', 'GET')}, Action={form.get('action', url)}")
                
                self._check_forms(rendered_html, url)
                
                self._check_api_endpoints(rendered_html, url)
                
                self._check_meta_tags(rendered_html, url)
                
                script_tags = soup.find_all('script')
                if self.verbose:
                    self._log_info(f"Found {len(script_tags)} script tags at {url}")
                    for script in script_tags:
                        if script.get('src'):
                            self._log_debug(f"External script: {script.get('src')}")
                
                links = []
                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(url, link.get('href'))
                    links.append(absolute_url)
                    if self.verbose:
                        self._log_debug(f"Found link: {absolute_url} (from {url})")
                
                if self.verbose:
                    self._log_info(f"Found {len(links)} total links at {url}")
                
                for link in links:
                    parsed = urlparse(link)
                    if parsed.netloc == urlparse(self.base_url).netloc:
                        self._analyze_page(urldefrag(link)[0], depth + 1, task)
            
            elif self.verbose:
                self._log_info(f"Skipping non-HTML content at {url} (Content-Type: {content_type})")

        except requests.RequestException as e:
            self._log_error(f"Error accessing {url}: {str(e)}")

    def _check_meta_tags(self, html: str, page_url: str) -> None:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            meta_tags = soup.find_all('meta')
            
            for meta in meta_tags:
                meta_name = meta.get('name', '').lower()
                meta_content = meta.get('content', '')
                
                if any(pattern in meta_name for pattern in self.token_patterns):
                    token_value = meta_content
                    entropy = self._calculate_entropy(token_value)
                    
                    protection_status = 'protected' if entropy > 3.5 else 'weak_token'
                    
                    self.results['meta_tags'].append({
                        'url': page_url,
                        'type': 'meta_tag',
                        'name': meta_name,
                        'protection': protection_status,
                        'token_entropy': entropy
                    })
                    
                    self.results['statistics']['meta_tags_found'] += 1
                    
                    if self.verbose:
                        if protection_status == 'protected':
                            self._log_success(f"Found protected CSRF token in meta tag '{meta_name}' at {page_url}")
                        else:
                            self._log_warning(f"Weak CSRF token in meta tag '{meta_name}' at {page_url} (entropy: {entropy:.2f})")
        
        except Exception as e:
            self._log_error(f"Error analyzing meta tags at {page_url}: {str(e)}")

    def _analyze_json_endpoint(self, url: str, json_data: dict) -> None:
        token_fields = [field for field in json_data.keys() 
                    if any(pattern in field.lower() for pattern in self.token_patterns)]
        
        for field in token_fields:
            token_value = str(json_data[field])
            entropy = self._calculate_entropy(token_value)
            
            self.results['endpoints'].append({
                'url': url,
                'type': 'api',
                'protection': 'protected' if entropy > 3.5 else 'weak_token',
                'token_field': field,
                'token_entropy': entropy
            })
            
            if self.verbose:
                if entropy > 3.5:
                    self._log_success(f"Found protected CSRF token in API response at {url} (field: {field})")
                else:
                    self._log_warning(f"Weak CSRF token in API response at {url} (field: {field}, entropy: {entropy:.2f})")
                    
    def _check_forms(self, html: str, page_url: str) -> None:
        soup = BeautifulSoup(html, 'html.parser')
        forms = soup.find_all('form')
        
        for i, form in enumerate(forms):
           self._log_debug(f"Raw form HTML [{i}]: {str(form)[:200]}")

        for form in forms:
            form_method = form.get('method', 'get').lower()
            form_action = urljoin(page_url, form.get('action', ''))
            form_id = form.get('id', 'unnamed_form')
            
            self.results['statistics']['forms_analyzed'] += 1
            
            # Only check state-changing methods
            if form_method not in ('post', 'put', 'patch', 'delete'):
                continue
                
            token_found, token_name, token_value = self._detect_csrf_token(form)
            protection_status = self._evaluate_protection(form_method, token_found, token_value)
            
            form_data = {
                'url': form_action,
                'method': form_method.upper(),
                'form_id': form_id,
                'protection': protection_status,
                'token_name': token_name,
                'token_entropy': self._calculate_entropy(token_value) if token_value else None,
                'page_url': page_url
            }
            
            self.results['forms'].append(form_data)
            
            if protection_status == 'protected':
                self.results['statistics']['protected_forms'] += 1
                if self.verbose:
                    self._log_success(f"Form {form_id} at {form_action} has CSRF protection")
            else:
                self.results['statistics']['vulnerable_forms'] += 1
                self.results['vulnerabilities'].append({
                    'type': 'form',
                    'url': form_action,
                    'method': form_method.upper(),
                    'risk': 'high',
                    'description': 'Form lacks CSRF protection'
                })
                self._log_warning(f"Potential CSRF vulnerability in form {form_id} at {form_action}")

    def _check_api_endpoints(self, html: str, page_url: str) -> None:
        # Look for fetch/XHR calls
        js_patterns = [
            r'fetch\(["\'](.+?)["\']',
            r'\.ajax\([\s\S]*?url:\s*["\'](.+?)["\']',
            r'axios\.(get|post|put|delete|patch)\(["\'](.+?)["\']'
        ]
        
        for pattern in js_patterns:
            for match in re.finditer(pattern, html):
                endpoint = urljoin(page_url, match.group(1))
                self._analyze_api_endpoint(endpoint)

    def _analyze_api_endpoint(self, endpoint: str) -> None:
        self.results['statistics']['endpoints_analyzed'] += 1
        
        try:
            # First check for CORS headers
            cors_response = self.session.options(endpoint, timeout=self.timeout)
            cors_headers = cors_response.headers
            
            # Then check actual request
            test_response = self.session.get(endpoint, timeout=self.timeout)
            headers = test_response.headers
            
            # Check for CSRF protections
            protection_found = False
            protection_methods = []
            
            # Check for custom headers
            if 'x-csrf-token' in self.session.headers:
                protection_found = True
                protection_methods.append('custom_header')
                
            # Check for token in cookies
            if any(t in cookie.name.lower() for cookie in self.session.cookies for t in self.token_patterns):
                protection_found = True
                protection_methods.append('cookie_token')
                
            # Check CORS settings
            if cors_headers.get('Access-Control-Allow-Origin') != '*':
                protection_found = True
                protection_methods.append('cors_restricted')
                
            endpoint_data = {
                'url': endpoint,
                'protection': 'protected' if protection_found else 'unprotected',
                'methods': protection_methods,
                'cors': dict(cors_headers)
            }
            
            self.results['endpoints'].append(endpoint_data)
            
            if protection_found:
                self.results['statistics']['protected_endpoints'] += 1
                if self.verbose:
                    self._log_success(f"API endpoint {endpoint} has CSRF protection via {', '.join(protection_methods)}")
            else:
                self.results['statistics']['vulnerable_endpoints'] += 1
                self.results['vulnerabilities'].append({
                    'type': 'api',
                    'url': endpoint,
                    'risk': 'high',
                    'description': 'API endpoint lacks CSRF protection'
                })
                self._log_warning(f"Potential CSRF vulnerability in API endpoint {endpoint}")
                
        except requests.RequestException as e:
            self._log_error(f"Error testing API endpoint {endpoint}: {str(e)}")

    def _check_cookie_security(self) -> None:
        for cookie in self.session.cookies:
            cookie_data = {
                'name': cookie.name,
                'secure': cookie.secure,
                'httponly': 'HttpOnly' in cookie._rest,
                'samesite': getattr(cookie, 'samesite', None)
            }
            
            self.results['cookies'].append(cookie_data)
            
            if cookie_data['secure'] and cookie_data['httponly'] and cookie_data['samesite'] in ('Lax', 'Strict'):
                self.results['statistics']['secure_cookies'] += 1
                if self.verbose:
                    self._log_success(f"Cookie {cookie.name} has secure attributes")
            else:
                self.results['statistics']['insecure_cookies'] += 1
                self.results['vulnerabilities'].append({
                    'type': 'cookie',
                    'name': cookie.name,
                    'risk': 'medium',
                    'description': 'Cookie missing security attributes'
                })
                self._log_warning(f"Insecure cookie {cookie.name}")

    def _extract_window_tokens(self, html: str, page_url: str) -> None:
        matches = re.findall(r'window\.(\w+)\s*=\s*[\'"]([^\'"]+)[\'"]', html)
        for name, value in matches:
            if any(t in name.lower() for t in self.token_patterns):
                entropy = self._calculate_entropy(value)
                self.results['meta_tags'].append({
                    'url': page_url,
                    'type': 'js_token',
                    'name': name,
                    'protection': 'protected' if entropy > 3.5 else 'weak_token',
                    'token_entropy': entropy
                })
                if self.verbose:
                    self._log_info(f"[Window] Detected JS token: {name} (entropy={entropy:.2f})")

    # will add Later
    def _analyze_javascript(self) -> None:
        # This would be expanded to analyze SPA frameworks
        pass

    def _detect_csrf_token(self, form) -> Tuple[bool, Optional[str], Optional[str]]:
        """Detect CSRF tokens in a form"""
        # Check hidden inputs
        for input_tag in form.find_all('input', type='hidden'):
            input_name = input_tag.get('name', '').lower()
            if any(pattern in input_name for pattern in self.token_patterns):
                return True, input_tag.get('name'), input_tag.get('value', '')
                
        # Check meta tags (common in SPAs)
        meta_tags = form.find_all('meta', attrs={'name': lambda x: x and any(p in x.lower() for p in self.token_patterns)})
        for meta in meta_tags:
            return True, meta.get('name'), meta.get('content', '')
            
        return False, None, None

    def _evaluate_protection(self, method: str, token_found: bool, token_value: Optional[str]) -> str:
        if method.lower() == 'get':
            return 'get_method'
            
        if not token_found:
            return 'unprotected'
            
        if not token_value or len(token_value) < 16:
            return 'weak_token'
            
        entropy = self._calculate_entropy(token_value)
        if entropy < 3.5:  # Low entropy threshold
            return 'weak_token'
            
        return 'protected'

    def _calculate_entropy(self, token: str) -> float:
        if not token:
            return 0.0
        prob = [float(token.count(c)) / len(token) for c in dict.fromkeys(list(token))]
        entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy
    
    def _render_with_playwright(self, url: str) -> Optional[str]:
        try:
            from playwright.sync_api import sync_playwright
            import time

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto(url, timeout=self.timeout * 1000)

                try:
                    page.wait_for_selector("form", timeout=5000)
                except:
                    time.sleep(2)  # fallback delay

                page.wait_for_load_state("networkidle", timeout=self.timeout * 1000)
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            self._log_error(f"[Playwright] Failed to render {url}: {e}")
            return None

    
    def _print_report(self) -> None:
        # Summary table
        summary_table = Table(title="CSRF Scan Summary", show_header=True, header_style="white")
        summary_table.add_column("Category", style="cyan")
        summary_table.add_column("Count", justify="right")
        
        stats = self.results['statistics']
        summary_table.add_row("Forms Analyzed", str(stats['forms_analyzed']))
        summary_table.add_row("Protected Forms", str(stats['protected_forms']))
        summary_table.add_row("Vulnerable Forms", str(stats['vulnerable_forms']), style="red" if stats['vulnerable_forms'] > 0 else "green")
        summary_table.add_row("API Endpoints Analyzed", str(stats['endpoints_analyzed']))
        summary_table.add_row("Protected Endpoints", str(stats['protected_endpoints']))
        summary_table.add_row("Vulnerable Endpoints", str(stats['vulnerable_endpoints']), style="red" if stats['vulnerable_endpoints'] > 0 else "green")
        summary_table.add_row("Secure Cookies", str(stats['secure_cookies']))
        summary_table.add_row("Insecure Cookies", str(stats['insecure_cookies']), style="red" if stats['insecure_cookies'] > 0 else "green")
        
        self.console.print(summary_table)
        
        # Vulnerabilities section
        if self.results['vulnerabilities']:
            vuln_table = Table(title="CSRF Vulnerabilities Found", show_header=True, header_style="bold red")
            vuln_table.add_column("Type")
            vuln_table.add_column("Location")
            vuln_table.add_column("Risk")
            vuln_table.add_column("Description")
            
            for vuln in self.results['vulnerabilities']:
                vuln_table.add_row(
                    vuln['type'],
                    vuln.get('url', vuln.get('name', 'N/A')),
                    vuln['risk'],
                    vuln['description']
                )
            
            self.console.print(vuln_table)

    def _log_success(self, message: str) -> None:
        self.console.print(f"[+] {message}", style="green")

    def _log_warning(self, message: str) -> None:
        self.console.print(f"[!] {message}", style="yellow")

    def _log_error(self, message: str) -> None:
        self.console.print(f"[!] {message}", style="red")
    
    def _log_info(self, message: str) -> None:
        self.console.print(f"[*] {message}", style="white")
    
    def _log_debug(self, message: str) -> None:
        self.console.print(f"[DEBUG] {message}", style="white")