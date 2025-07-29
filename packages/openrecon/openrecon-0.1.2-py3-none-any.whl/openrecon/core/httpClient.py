import requests
import urllib3
import time
from urllib.parse import urljoin, parse_qsl, urlparse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HTTPClient:
    def __init__(self, user_agent=None, cookies=None, proxy=None, timeout=10, verify_ssl=False):
        self.timeout = timeout
        self.session = self._create_session(user_agent, cookies, proxy, verify_ssl)
        
    def _create_session(self, user_agent=None, cookies=None, proxy=None, verify_ssl=False):
        session = requests.Session()
        session.headers["User-Agent"] = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        session.verify = verify_ssl
        
        if cookies:
            if isinstance(cookies, dict):
                # Handle dictionary of cookies
                for name, value in cookies.items():
                    session.cookies.set(name, value)
            elif isinstance(cookies, str):
                # Handle string format cookies
                for cookie_pair in cookies.split(';'):
                    if '=' in cookie_pair:
                        name, value = cookie_pair.strip().split('=', 1)
                        session.cookies.set(name, value)
        
        if proxy:
            session.proxies = {
                "http": proxy,
                "https": proxy
            }
        
        return session
        
    def get(self, url, params=None):
        try:
            start_time = time.time()
            response = self.session.get(url, params=params, timeout=self.timeout)
            response_time = time.time() - start_time
            return response, response_time
        except Exception as e:
            return None, 0
            
    def post(self, url, data=None):
        try:
            start_time = time.time()
            response = self.session.post(url, data=data, timeout=self.timeout)
            response_time = time.time() - start_time
            return response, response_time
        except Exception as e:
            return None, 0
            
    def validate_url(self, url):
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return True
        except Exception:
            return False
            
    def timed_request(self, url, method, data=None, params=None):
        if method.lower() == 'post':
            return self.post(url, data)
        else:
            return self.get(url, params)
            
    @staticmethod
    def extract_url_parameters(url):
        """Extract parameters from URL, including empty ones."""
        parsed_url = urlparse(url)
        query = parsed_url.query
        
        # Handle empty query string
        if not query:
            return {}
            
        # Split by & and handle each parameter
        params = {}
        for param in query.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
            else:
                # Handle parameters without values
                params[param] = ''
                
        return params
        
    @staticmethod
    def join_url(base, path):
        return urljoin(base, path)