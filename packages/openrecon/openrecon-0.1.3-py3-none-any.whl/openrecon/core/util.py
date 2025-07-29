import os
import json
import time
from datetime import datetime
from urllib.parse import urlparse

class Utils:
    @staticmethod
    def get_domain_from_url(url):
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc.replace(":", "_")
        
    @staticmethod
    def create_directory(directory):
        """Create directory if it doesn't exist."""
        if not os.path.exists(directory):
            os.makedirs(directory)
            
    @staticmethod
    def generate_filename(base_name, target_url):
        """Generate a filename based on target URL and timestamp."""
        domain = Utils.get_domain_from_url(target_url)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{domain}_{timestamp}"
        
    @staticmethod
    def safe_save_json(data, filename):
        """Safely save data as JSON."""
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception:
            return False
            
    @staticmethod
    def safe_save_text(data, filename):
        """Safely save data as text."""
        try:
            with open(filename, "w") as f:
                f.write(data)
            return True
        except Exception:
            return False
            
    @staticmethod
    def safe_request_with_timeout(request_fn, max_retries=3, timeout=10):
        """Make a request with retries and timeout handling."""
        retries = 0
        while retries < max_retries:
            try:
                return request_fn(timeout=timeout)
            except Exception:
                retries += 1
                if retries >= max_retries:
                    return None
                time.sleep(1)
                
    @staticmethod
    def merge_dicts(dict1, dict2):
        """Merge two dictionaries, preferring dict1 values on conflict."""
        result = dict2.copy()
        result.update(dict1)
        return result
        
    @staticmethod
    def format_timestamp():
        """Get formatted timestamp for logging."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")