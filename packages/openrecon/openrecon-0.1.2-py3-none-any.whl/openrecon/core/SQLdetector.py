import time

from .payloadModels import SQL_ERRORS
from .parsers import ResponseAnalyzer




class SQLiDetector:
    def __init__(self, http_client=None):
        from .httpClient import HTTPClient
        self.http_client = http_client or HTTPClient()
        self.response_analyzer = ResponseAnalyzer()
        
    def test_payload(self, url, method, data, payload_name, baseline_content=None, delay_threshold=2.5):
        try:
            if method.lower() == "post":
                response, response_time = self.http_client.post(url, data=data)
            else:
                response, response_time = self.http_client.get(url, params=data)
            
            if not response:
                return False, None, "Request failed"
            
            if "SLEEP" in str(data) or "WAITFOR" in str(data):
                if response_time > delay_threshold:
                    return True, response, f"Time-based payload succeeded ({response_time:.2f}s): {payload_name}"
            
            if self.is_response_vulnerable(response, baseline_content):
                return True, response, f"Error-based payload succeeded: {payload_name}"
                
            return False, response, None
            
        except Exception as e:
            return False, None, f"Request failed: {e}"
    
    def is_response_vulnerable(self, response, baseline_content=None):
        if not response:
            return False
            
        content = self.response_analyzer.decode_response(response).lower()
        
        for error in SQL_ERRORS:
            if error.lower() in content:
                return True
        
        if baseline_content:
            similarity = self.response_analyzer.calculate_content_similarity(content, baseline_content)
            if similarity < 0.8:
                return True
                
        return False
        
    def get_baseline_response(self, url, method, data):
        try:
            if method.lower() == "post":
                response, _ = self.http_client.post(url, data=data)
            else:
                response, _ = self.http_client.get(url, params=data)
                
            if response:
                return self.response_analyzer.decode_response(response).lower()
        except Exception:
            pass
            
        return None