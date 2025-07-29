import re
import sys
import os
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.CMSfingerprints import load_cms_fingerprints
from core.colors import Colors, Messages

import requests
from bs4 import BeautifulSoup

# Suppress only the InsecureRequestWarning from urllib3 needed for some sites
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CMSDetector:
    def __init__(self, timeout=10, user_agent=None, verify_ssl=True, max_threads=5, verbose=False):
        """Initialize the CMS detector with configuration options."""
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_threads = max_threads
        self.verbose = verbose
        self.headers = {
            'User-Agent': user_agent or 'OpenRecon/1.0'
        }
        
        self.cms_fingerprints = load_cms_fingerprints()
        # Add modern framework fingerprints if not already in fingerprints
        self._add_modern_framework_fingerprints()

    def _add_modern_framework_fingerprints(self):
        if 'Next.js' not in self.cms_fingerprints:
            self.cms_fingerprints['Next.js'] = {
                'headers': [
                    'X-Powered-By: Next.js',
                    'Server: Next.js'
                ],
                'meta_tags': [
                    'next-head-count',
                    'next-head'
                ],
                'paths': [
                    '_next/static',
                    '_next/data',
                    '__next'
                ],
                'html_patterns': [
                    '__NEXT_DATA__',
                    'next-head-count',
                    'next-error'
                ],
                'js_patterns': [
                    'next/router',
                    'next/link',
                    'next/head',
                    'next/script'
                ],
                'cookies': []
            }

    def _print_verbose(self, message, color=Colors.VERBOSE):
        if self.verbose:
            print(color.render(f"[VERBOSE] {message}"))

    def _check_website_accessible(self, url):
        try:
            self._print_verbose(f"Checking website accessibility: {url}", Colors.CHECKING)
            
            # First try HEAD request to check if server responds
            try:
                head_response = requests.head(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                    allow_redirects=True
                )
            except requests.RequestException:
                head_response = None

            # If HEAD fails or gives non-200, try GET
            if not head_response or head_response.status_code >= 400:
                self._print_verbose("HEAD request failed, trying GET...", Colors.WARNING)
                response = self._fetch_url(url)
                if not response:
                    return False
                
                content_type = response.headers.get('Content-Type', '').lower()
                if not any(x in content_type for x in ['text/html', 'application/xhtml+xml']):
                    self._print_verbose(f"Non-web content type detected: {content_type}", Colors.ERROR)
                    return False
                    
                return True
            return True
            
        except Exception as e:
            self._print_verbose(f"Accessibility check failed: {str(e)}", Colors.ERROR)
            return False

    def detect(self, url):
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Check if website is accessible before scanning
        if not self._check_website_accessible(url):
            return {'error': f"Target {url} is not accessible or doesn't appear to be a web application"}

        try:
            self._print_verbose(f"Starting CMS detection for: {url}", Colors.INFO)
            start_time = time.time()
            
            # Fetch main page content
            response = self._fetch_url(url)
            if not response:
                return {'error': f"Failed to fetch {url}"}

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Collect all detection results
            results = {
                'url': url,
                'status_code': response.status_code,
                'server': response.headers.get('Server', 'Unknown'),
                'powered_by': response.headers.get('X-Powered-By', 'Unknown'),
                'detection_time': None,  # Will be filled at the end
                'technologies': {
                    'cms': [],
                    'web_servers': [],
                    'programming_languages': [],
                    'javascript_frameworks': [],
                    'ui_frameworks': [],
                    'analytics': [],
                    'tag_managers': [],
                    'cdn': [],
                    'security': [],
                    'miscellaneous': []
                }
            }
            
            # Run all detection methods
            self._print_verbose("Running header analysis...")
            header_results = self._analyze_headers(response.headers)
            
            self._print_verbose("Running meta tag analysis...")
            meta_results = self._analyze_meta_tags(soup)
            
            self._print_verbose("Running path analysis...")
            path_results = self._analyze_paths(url, response)
            
            self._print_verbose("Running HTML pattern analysis...")
            html_results = self._analyze_html_patterns(response.text)
            
            self._print_verbose("Running JavaScript analysis...")
            js_results = self._analyze_js_patterns(soup, url)
            
            self._print_verbose("Running cookie analysis...")
            cookie_results = self._analyze_cookies(response.cookies)
            
            # Aggregate all detection results for confidence calculation
            detection_results = {
                'header_analysis': header_results,
                'meta_analysis': meta_results,
                'path_analysis': path_results,
                'html_analysis': html_results,
                'js_analysis': js_results,
                'cookie_analysis': cookie_results
            }
            
            # Calculate confidence scores
            cms_confidence = self._calculate_confidence(detection_results)
            
            # Add CMS detections to results
            for cms, details in cms_confidence.items():
                results['technologies']['cms'].append({
                    'name': cms,
                    'confidence': details['confidence'],
                    'version': None,  # Could be enhanced to detect versions
                    'categories': ['CMS']
                })
            
            # Detect additional technologies
            tech_results = self._detect_technologies(response, soup)
            
            # Map technology results to Wappalyzer-like categories
            if 'web_server' in tech_results:
                results['technologies']['web_servers'].append({
                    'name': tech_results['web_server'],
                    'confidence': 100,
                    'categories': ['Web servers']
                })
            
            if 'frameworks' in tech_results:
                for framework in tech_results['frameworks']:
                    if framework in ['React', 'Angular', 'Vue.js', 'Next.js']:
                        results['technologies']['javascript_frameworks'].append({
                            'name': framework,
                            'confidence': 100,
                            'categories': ['JavaScript frameworks']
                        })
                    else:
                        results['technologies']['ui_frameworks'].append({
                            'name': framework,
                            'confidence': 100,
                            'categories': ['UI frameworks']
                        })
            
            if 'analytics' in tech_results:
                for analytic in tech_results['analytics']:
                    if 'Tag Manager' in analytic:
                        results['technologies']['tag_managers'].append({
                            'name': analytic,
                            'confidence': 100,
                            'categories': ['Tag managers']
                        })
                    else:
                        results['technologies']['analytics'].append({
                            'name': analytic,
                            'confidence': 100,
                            'categories': ['Analytics']
                        })
            
            if 'security' in tech_results:
                for security in tech_results['security']:
                    results['technologies']['security'].append({
                        'name': security,
                        'confidence': 100,
                        'categories': ['Security']
                    })
            
            # Calculate and format detection time
            elapsed_time = time.time() - start_time
            results['detection_time'] = f"{elapsed_time:.2f} seconds"
            
            self._print_verbose(f"CMS detection completed in {results['detection_time']}", Colors.SUCCESS)
            
            return results
            
        except Exception as e:
            error_msg = f"Error detecting CMS: {str(e)}"
            self._print_verbose(error_msg, Colors.CRITICAL)
            return {'error': error_msg}

    def _fetch_url(self, url, allow_redirects=True):
        try:
            self._print_verbose(f"Fetching URL: {url}")
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                allow_redirects=allow_redirects
            )
            self._print_verbose(f"Received response: {response.status_code}")
            return response
        except requests.RequestException as e:
            self._print_verbose(f"Failed to fetch {url}: {str(e)}", Colors.ERROR)
            return None

    def _analyze_headers(self, headers):
        """Analyze HTTP headers for CMS indicators."""
        results = {}
        headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
        
        for cms, fingerprint in self.cms_fingerprints.items():
            matches = []
            for header_pattern in fingerprint['headers']:
                if ':' in header_pattern:
                    header_name, header_value = header_pattern.split(':', 1)
                    header_name = header_name.strip().lower()
                    header_value = header_value.strip().lower()
                    
                    if header_name in headers_lower and header_value in headers_lower[header_name]:
                        matches.append(header_pattern)
                else:
                    for header_name, header_value in headers_lower.items():
                        if header_pattern.lower() in header_name or header_pattern.lower() in header_value:
                            matches.append(f"{header_name}: {header_value}")
                            
            if matches:
                results[cms] = matches
                
        return results

    def _analyze_html_patterns(self, html_content):
        results = {}
        html_content = html_content.lower()
        
        for cms, fingerprint in self.cms_fingerprints.items():
            matches = []
            for pattern in fingerprint['html_patterns']:
                if pattern.lower() in html_content:
                    matches.append(pattern)
                    
            if matches:
                results[cms] = matches
                
        return results

    def _analyze_meta_tags(self, soup):
        results = {}
        
        for cms, fingerprint in self.cms_fingerprints.items():
            if not fingerprint['meta_tags']:
                continue
                
            matches = []
            meta_tags = soup.find_all('meta')
            
            for meta_tag in meta_tags:
                name = meta_tag.get('name', '').lower()
                content = meta_tag.get('content', '').lower()
                
                for pattern in fingerprint['meta_tags']:
                    if pattern.lower() in name or pattern.lower() in content:
                        matches.append(f"{name}: {content}")
                        
            if matches:
                results[cms] = matches
                
        return results

    def _analyze_paths(self, base_url, main_response):
        results = {}
        parsed_url = urlparse(base_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        headers_lower = {k.lower(): v.lower() for k, v in main_response.headers.items()}
        if 'x-powered-by' in headers_lower and 'next.js' in headers_lower['x-powered-by']:
            self._print_verbose("Skipping extensive path analysis due to Next.js detection", Colors.INFO)
            return results
            
        def check_path(cms, path):
            # Skip checking paths for modern frameworks we've already detected
            if cms in ['Next.js', 'React']:
                return None
                
            url = urljoin(base_url, path)
            try:
                response = requests.head(
                    url,
                    headers=self.headers,
                    timeout=2,  # Shorter timeout for paths
                    verify=self.verify_ssl,
                    allow_redirects=False
                )
                # Only consider 200-399 responses as valid matches
                if 200 <= response.status_code < 400:
                    # Additional verification for admin paths
                    if any(admin_path in path for admin_path in ['/wp-admin/', '/administrator/']):
                        if 'login' in response.headers.get('Content-Type', '').lower():
                            return path
                        return None
                    return path
                return None
            except:
                return None
                
        modern_frameworks = ['Next.js', 'React', 'Gatsby', 'Nuxt']
        for cms in modern_frameworks:
            if cms in self.cms_fingerprints:
                with ThreadPoolExecutor(max_workers=min(self.max_threads, 3)) as executor:
                    futures = [executor.submit(check_path, cms, path) 
                             for path in self.cms_fingerprints[cms]['paths']]
                    matches = [future.result() for future in futures if future.result()]
                    if matches:
                        results[cms] = matches
                        return results

        #Check traditional CMS paths ONLY if no modern framework detected
        traditional_cms = [cms for cms in self.cms_fingerprints.keys() if cms not in modern_frameworks]
        for cms in traditional_cms:
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                futures = [executor.submit(check_path, cms, path) 
                         for path in self.cms_fingerprints[cms]['paths']]
                matches = [future.result() for future in futures if future.result()]
                if matches:
                    results[cms] = matches

        # will Also look for path patterns in the main response
        html_content = main_response.text.lower()
        for cms, fingerprint in self.cms_fingerprints.items():
            matches = []
            for path in fingerprint['paths']:
                if path.lower() in html_content:
                    # Additional verification
                    if any(admin_path in path for admin_path in ['/wp-admin/', '/administrator/']):
                        if f'href="{path}' in html_content or f'src="{path}' in html_content:
                            matches.append(path)
                    else:
                        matches.append(path)
                        
            if matches and cms not in results:
                results[cms] = matches
                
        return results

    def _analyze_js_patterns(self, soup, url):
        results = {}
        
        scripts = soup.find_all('script')
        script_texts = []
        
        for script in scripts:
            if script.string:
                script_text = script.string.lower()
                script_texts.append(script_text)
                if '__next_data__' in script_text:
                    results['Next.js'] = ['__NEXT_DATA__']
        
        script_srcs = [script.get('src', '') for script in scripts if script.get('src')]
        
        if script_srcs:
            for src in script_srcs[:5]:
                if src.startswith(('http://', 'https://')):
                    script_url = src
                else:
                    script_url = urljoin(url, src)
                    
                script_response = self._fetch_url(script_url)
                if script_response and script_response.status_code == 200:
                    script_text = script_response.text.lower()
                    script_texts.append(script_text)
                    
                    if '_next/static/chunks/' in src and ('next' in script_text or 'webpack' in script_text):
                        results['Next.js'] = ['_next/static/chunks']
        
        for cms, fingerprint in self.cms_fingerprints.items():
            matches = []
            for script_text in script_texts:
                for pattern in fingerprint['js_patterns']:
                    if cms == 'Magento' and pattern.lower() == 'mage':
                        if 'mage' in script_text and ('mage.cookies' in script_text or 'mage.translate' in script_text):
                            matches.append('Magento-specific JS patterns')
                            break
                    elif pattern.lower() in script_text:
                        matches.append(pattern)
                        break
            
            if matches:
                results[cms] = list(set(matches))  # Remove duplicates
                
        return results

    def _detect_technologies(self, response, soup):
        """Detect additional technologies with improved framework detection."""
        technologies = {}
        
        # Detect web server
        server = response.headers.get('Server')
        if server:
            technologies['web_server'] = server
        
        # Detect frameworks and libraries from scripts and HTML
        frameworks = set()
        html_content = response.text.lower()
        
        # Next.js detection
        if '__next_data__' in html_content or '_next/static' in html_content:
            frameworks.add('Next.js')
        
        # React detection
        if 'react' in html_content or any('react' in script.get('src', '').lower() for script in soup.find_all('script')):
            frameworks.add('React')
        
        # Other framework detections
        script_srcs = [script.get('src', '').lower() for script in soup.find_all('script')]
        
        if any('jquery' in src for src in script_srcs):
            frameworks.add('jQuery')
        if any('bootstrap' in src for src in script_srcs):
            frameworks.add('Bootstrap')
        if any('angular' in src for src in script_srcs):
            frameworks.add('Angular')
        if any('vue' in src for src in script_srcs):
            frameworks.add('Vue.js')
        
        if frameworks:
            technologies['frameworks'] = sorted(frameworks)
        
        # Detect analytics tools with more patterns
        analytics = set()
        
        if 'google-analytics.com' in html_content or 'gtag' in html_content or 'ga(' in html_content:
            analytics.add('Google Analytics')
        if 'facebook.net/en_US/fbevents' in html_content or 'fbq(' in html_content:
            analytics.add('Facebook Pixel')
        if 'googletagmanager.com' in html_content or 'gtm.js' in html_content:
            analytics.add('Google Tag Manager')
        if 'plausible.io' in html_content:
            analytics.add('Plausible')
        
        if analytics:
            technologies['analytics'] = sorted(analytics)
        
        # Detect security headers
        security = set()
        if 'strict-transport-security' in response.headers:
            security.add('HSTS')
        if 'x-content-type-options' in response.headers and 'nosniff' in response.headers['x-content-type-options'].lower():
            security.add('NoSniff')
        
        if security:
            technologies['security'] = sorted(security)
        
        return technologies
    
    def _analyze_cookies(self, cookies):
        results = {}
        
        cookies_dict = {name: cookies[name] for name in cookies.keys()}
        
        for cms, fingerprint in self.cms_fingerprints.items():
            matches = []
            for pattern in fingerprint['cookies']:
                for cookie_name, cookie_value in cookies_dict.items():
                    if (pattern.lower() in cookie_name.lower() or 
                        (isinstance(cookie_value, str) and pattern.lower() in cookie_value.lower())):
                        matches.append(cookie_name)
                        
            if matches:
                results[cms] = matches
                
        return results
    
    def _calculate_confidence(self, detection_results):
        """Calculate confidence scores for each detected CMS."""
        # Assign weights to different detection methods
        weights = {
            'header_analysis': 3,
            'meta_analysis': 2,
            'path_analysis': 4,
            'html_analysis': 3,
            'js_analysis': 3,
            'cookie_analysis': 2
        }
        
        #Collect all CMS mentions
        cms_mentions = Counter()
        for method, results in detection_results.items():
            method_weight = weights.get(method, 1)
            for cms in results:
                cms_mentions[cms] += method_weight * len(results[cms])
        
        #Calculate confidence percentages
        total_score = sum(cms_mentions.values())
        confidence_scores = {}
        
        if total_score > 0:
            for cms, score in cms_mentions.items():
                confidence = (score / total_score) * 100
                confidence_scores[cms] = {
                    'score': score,
                    'confidence': round(confidence, 2)
                }
                
        #sort by confidence
        sorted_cms = sorted(confidence_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        return {cms: details for cms, details in sorted_cms}