import requests
import hashlib
import time
import dns.resolver
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import json
import os
from rich.console import Console
from rich.progress import Progress
from datetime import datetime, timedelta

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

console = Console()
CACHE_DIR = os.path.expanduser("~/.openrecon/cache")

#ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

class SubdomainEnumerator:
    def __init__(self, max_retries=3, backoff_factor=2, timeout=15, max_workers=5, cache_time=86400, validate_dns=True, dns_timeout=2, validation_timeout=60, verbose=False):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self.max_workers = max_workers
        self.cache_time = cache_time
        self.validate_dns = validate_dns
        self.dns_timeout = dns_timeout
        self.validation_timeout = validation_timeout
        self.verbose = verbose
        self.user_agent = "OpenRecon/1.0"
        self.headers = {"User-Agent": self.user_agent}
        
    def _get_cache_file(self, domain):
        return os.path.join(CACHE_DIR, "subdomain_cache.json")
    
    def _is_cache_valid(self, cache_file, domain):
        if not os.path.exists(cache_file):
            return False
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            if domain not in data:
                return False
            cache_date = datetime.fromisoformat(data[domain]['timestamp'])
            expire_date = datetime.now() - timedelta(seconds=self.cache_time)
            return cache_date > expire_date
        except Exception:
            return False
    
    def _load_from_cache(self, domain):
        """Load subdomains from cache if available"""
        cache_file = self._get_cache_file(domain)
        if self._is_cache_valid(cache_file, domain):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                if domain in data:
                    console.print(f"[blue]Loading {len(data[domain]['subdomains'])} subdomains from cache[/blue]")
                    return data[domain]['subdomains']
            except Exception as e:
                console.print(f"[yellow]Cache read error: {e}[/yellow]")
        return None
    
    def _save_to_cache(self, domain, subdomains):
        """Save subdomains to cache"""
        cache_file = self._get_cache_file(domain)
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            data[domain] = {
                'timestamp': datetime.now().isoformat(),
                'subdomains': list(subdomains)
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"[yellow][!] Cache write error: {e}[/yellow]")
    
    def _make_request(self, url, params=None):
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                response = requests.get(
                    url, 
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout,
                    verify=False
                )
                
                if response.status_code == 200:
                    return response
                
                if response.status_code == 429:  # Rate limited
                    retry_count += 1
                    sleep_time = self.backoff_factor ** retry_count
                    if self.verbose:
                        console.print(f"[yellow]Rate limited. Retrying in {sleep_time}s ({retry_count}/{self.max_retries})[/yellow]")
                    time.sleep(sleep_time)
                    continue
                  
                console.print(f"[yellow][!] Request failed with status code: {response.status_code}[/yellow]")
                return None
                
            except requests.RequestException as e:
                retry_count += 1
                if retry_count <= self.max_retries:
                    sleep_time = self.backoff_factor ** retry_count
                    if self.verbose:
                        console.print(f"[yellow][!] Request error: {e}. Retrying in {sleep_time}s ({retry_count}/{self.max_retries})[/yellow]")
                    time.sleep(sleep_time)
                else:
                    if self.verbose:
                        console.print(f"[red][!] Max retries reached for {url}: {e}[/red]")
                    return None
    
    def _is_valid_subdomain(self, subdomain):
        if not self.validate_dns:
            return True
            
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.dns_timeout
            resolver.lifetime = self.dns_timeout
            
            
            try:
                resolver.resolve(subdomain, 'A')
                return True
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
                pass
            except dns.exception.Timeout:
                if self.verbose:
                    console.print(f"[yellow][+] DNS timeout for {subdomain} A record[/yellow]")
                return False
                
            try:
                resolver.resolve(subdomain, 'AAAA')
                return True
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
                return False
            except dns.exception.Timeout:
                if self.verbose:
                    console.print(f"[yellow][+] DNS timeout for {subdomain} AAAA record[/yellow]")
                return False
            
        except Exception as e:
            if self.verbose:
                console.print(f"[yellow][!] DNS error for {subdomain}: {e}[/yellow]")
            return False
    
    def _get_from_crtsh(self, domain):
        subdomains = set()
        url = "https://crt.sh/"
        params = {
            'q': f"%.{domain}",
            'output': 'json'
        }
        
        response = self._make_request(url, params)
        if not response:
            return subdomains
            
        try:
            if not response.text.strip().startswith('['):
                console.print(f"[yellow][!] Invalid response format from crt.sh[/yellow]")
                return subdomains
                
            data = response.json()
            for entry in data:
                name = entry.get('name_value', '')
                if not name:
                    continue
                    
                for sub in name.split('\n'):
                    if domain in sub:
                        clean_sub = sub.strip().lower()
                        if clean_sub:
                            subdomains.add(clean_sub)
        except Exception as e:
            console.print(f"[yellow][!] Error parsing crt.sh data: {e}[/yellow]")
            
        console.print(f"[green]Found {len(subdomains)} subdomains from crt.sh[/green]")
        return subdomains
    
    def _get_from_alienvault(self, domain):
        subdomains = set()
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
        
        response = self._make_request(url)
        if not response:
            return subdomains
            
        try:
            data = response.json()
            for entry in data.get('passive_dns', []):
                hostname = entry.get('hostname', '')
                if hostname and domain in hostname:
                    clean_sub = hostname.strip().lower()
                    if clean_sub:
                        subdomains.add(clean_sub)
        except Exception as e:
            console.print(f"[yellow][!] Error parsing AlienVault data: {e}[/yellow]")
            
        console.print(f"[green]Found {len(subdomains)} subdomains from AlienVault[/green]")
        return subdomains
    
    def _get_from_hackertarget(self, domain):
        subdomains = set()
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        
        response = self._make_request(url)
        if not response:
            return subdomains
            
        try:
            content = response.text
            if "API count exceeded" in content:
                console.print("[yellow][!] HackerTarget API limit reached[/yellow]")
                return subdomains
                
            for line in content.splitlines():
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 1:
                        hostname = parts[0]
                        if domain in hostname:
                            clean_sub = hostname.strip().lower()
                            if clean_sub:
                                subdomains.add(clean_sub)
        except Exception as e:
            console.print(f"[yellow][!] Error parsing HackerTarget data: {e}[/yellow]")
            
        console.print(f"[green]Found {len(subdomains)} subdomains from HackerTarget[/green]")
        return subdomains
    
    def _get_from_bufferover(self, domain):
        subdomains = set()
        url = f"https://dns.bufferover.run/dns"
        params = {'q': f'.{domain}'}
        
        response = self._make_request(url, params)
        if not response:
            if self.verbose:
                console.print("[yellow][!] BufferOver.run query failed[/yellow]")
            return subdomains
            
        try:
            data = response.json()
            results = data.get('FDNS_A', []) + data.get('RDNS', [])
            
            for result in results:
                if ',' in result:
                    subdomain = result.split(',')[1]
                    if domain in subdomain:
                        clean_sub = subdomain.strip().lower()
                        if clean_sub:
                            subdomains.add(clean_sub)
        except Exception as e:
            if self.verbose:
                console.print(f"[yellow][!] Error parsing BufferOver data: {e}[/yellow]")
            
        if self.verbose:
            console.print(f"[green]Found {len(subdomains)} subdomains from BufferOver.run[/green]")
        return subdomains
    
    def _get_from_threatcrowd(self, domain):
        subdomains = set()
        url = f"https://threatcrowd.org/searchApi/v2/domain/report/?domain={domain}"
        
        response = self._make_request(url)
        if not response:
            return subdomains
            
        try:
            data = response.json()
            for subdomain in data.get('subdomains', []):
                if domain in subdomain:
                    clean_sub = subdomain.strip().lower()
                    if clean_sub:
                        subdomains.add(clean_sub)
        except Exception as e:
            console.print(f"[yellow][!] Error parsing ThreatCrowd data: {e}[/yellow]")
            
        console.print(f"[green]Found {len(subdomains)} subdomains from ThreatCrowd[/green]")
        return subdomains
    
    def _validate_subdomains(self, subdomains):
        """Validate a list of subdomains using DNS resolution"""
        if not self.validate_dns or not subdomains:
            return subdomains
            
        console.print("[blue]Validating subdomains via DNS resolution...[/blue]")
        valid_subdomains = set()
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Validating...", total=len(subdomains))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_subdomain = {
                    executor.submit(self._is_valid_subdomain, subdomain): subdomain 
                    for subdomain in subdomains
                }
                
                for future in concurrent.futures.as_completed(future_to_subdomain):
                    subdomain = future_to_subdomain[future]
                    try:
                        is_valid = future.result(timeout=self.dns_timeout)
                        if is_valid:
                            valid_subdomains.add(subdomain)
                    except concurrent.futures.TimeoutError:
                        if self.verbose:
                            console.print(f"[yellow]Validation timeout for {subdomain}[/yellow]")
                    except Exception as e:
                        if self.verbose:
                            console.print(f"[yellow]Error validating {subdomain}: {e}[/yellow]")
                    progress.update(task, advance=1)
        
        console.print(f"[green]Validated {len(valid_subdomains)} out of {len(subdomains)} subdomains[/green]")
        return valid_subdomains
    
    def get_subdomains(self, domain, use_all_sources=True):
        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
            
        # Check cache first
        cached_subdomains = self._load_from_cache(domain)
        if cached_subdomains:
            return cached_subdomains
            
        console.print(f"[bold blue][+] Enumerating subdomains for {domain}[/bold blue]")
        all_subdomains = set()
        
        # Set up sources
        sources = [
            ("crt.sh", self._get_from_crtsh),
        ]
        
        if use_all_sources:
            sources.extend([
                ("AlienVault", self._get_from_alienvault),
                ("HackerTarget", self._get_from_hackertarget),
                ("BufferOver", self._get_from_bufferover),
                ("ThreatCrowd", self._get_from_threatcrowd)
            ])
            
        # Query all sources in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_source = {
                executor.submit(source_func, domain): source_name
                for source_name, source_func in sources
            }
            
            for future in concurrent.futures.as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    result = future.result()
                    all_subdomains.update(result)
                    console.print(f"[blue][+] Added {len(result)} subdomains from {source_name}[/blue]")
                except Exception as e:
                    console.print(f"[red][!] Error from {source_name}: {e}[/red]")
        
        # Validate subdomains
        if self.validate_dns and all_subdomains:
            all_subdomains = self._validate_subdomains(all_subdomains)
        
        # Save to cache
        if all_subdomains:
            self._save_to_cache(domain, all_subdomains)
            
        return sorted(all_subdomains)

    def clear_cache(self):
        """Clear the entire subdomain cache file."""
        cache_file = self._get_cache_file(None)
        if os.path.exists(cache_file):
            os.remove(cache_file)
            console.print("[green][+] Cache cleared successfully.[/green]")
        else:
            console.print("[yellow][!] No cache file found.[/yellow]")

    def show_cache(self):
        """Display the contents of the subdomain cache in a visually acceptable way."""
        cache_file = self._get_cache_file(None)
        if not os.path.exists(cache_file):
            console.print("[yellow][!] No cache file found.[/yellow]")
            return
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            console.print("[bold blue]Subdomain Cache:[/bold blue]")
            for domain, info in data.items():
                console.print(f"[bold cyan]Domain: {domain}[/bold cyan]")
                console.print(f"  Timestamp: {info['timestamp']}")
                console.print(f"  Subdomains: {len(info['subdomains'])}")
                for sub in sorted(info['subdomains']):
                    console.print(f"    - {sub}")
        except Exception as e:
            console.print(f"[red]Error reading cache: {e}[/red]")

def get_subdomains(domain, validate=False, use_cache=True, use_all_sources=True):
    enumerator = SubdomainEnumerator(
        validate_dns=validate,
        cache_time=86400 if use_cache else 0,
        verbose=True
    )
    return enumerator.get_subdomains(domain, use_all_sources=use_all_sources)

def recursive_enum(domain, depth=1, validate=False):
    if depth <= 0:
        return set()
    
    seen = set()
    all_subdomains = set()
    
    def _enum_recursive(current_domain, current_depth):
        if current_depth <= 0 or current_domain in seen:
            return set()
            
        seen.add(current_domain)
        
        enumerator = SubdomainEnumerator(validate_dns=validate, verbose=True)
        subdomains = enumerator.get_subdomains(current_domain)
        result_set = set(subdomains)
        
        console.print(f"[blue][+] Found {len(subdomains)} subdomains for {current_domain}[/blue]")
        
        if current_depth > 1:
            for subdomain in subdomains:
                console.print(f"[blue][+] Searching deeper: {subdomain} (level {current_depth-1})[/blue]")
                deeper = _enum_recursive(subdomain, current_depth-1)
                result_set.update(deeper)
                
        return result_set
    
    return _enum_recursive(domain, depth)

def get_fingerprint(domain):
    try:
        url = f"https://{domain}"
        headers = {"User-Agent": "OpenRecon/1.0"}
        
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True, verify=False)
            header_string = str(response.headers)
            server_info = response.headers.get('Server', '')
            content_type = response.headers.get('Content-Type', '')
            
            fingerprint_data = f"{response.status_code}|{server_info}|{content_type}|{header_string}"
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            additional_info = {
                'server': server_info,
                'status': response.status_code,
                'content_type': content_type,
                'protocol': 'https'
            }
            
            return fingerprint, additional_info
        except requests.exceptions.SSLError:
            console.print(f"[yellow][!] HTTPS failed for {domain}, trying HTTP...[/yellow]")
            url = f"http://{domain}"
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            header_string = str(response.headers)
            server_info = response.headers.get('Server', '')
            content_type = response.headers.get('Content-Type', '')
            
            fingerprint_data = f"{response.status_code}|{server_info}|{content_type}|{header_string}"
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            additional_info = {
                'server': server_info,
                'status': response.status_code,
                'content_type': content_type,
                'protocol': 'http'
            }
            
            return fingerprint, additional_info
    except Exception as e:
        console.print(f"[yellow][+] Could not get fingerprint for {domain}: {e}[/yellow]")
        return None, None