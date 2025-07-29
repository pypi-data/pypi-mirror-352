import re
from .payloadModels import get_payloads_for_context



class XSSContext:
    """Identify and analyze different contexts where XSS might be executed."""
    HTML_CONTEXT = "html"
    ATTR_CONTEXT = "attribute"
    JS_CONTEXT = "javascript"
    URL_CONTEXT = "url"
    CSS_CONTEXT = "css"
    DOM_CONTEXT = "dom"
    
    @staticmethod
    def identify_context(content, injection_point):
        """Identify the context of a potential XSS injection point."""
        if not content or not injection_point:
            return XSSContext.HTML_CONTEXT, {}
            
        try:
            pos = content.find(injection_point)
            if pos == -1:
                return XSSContext.HTML_CONTEXT, {}
                
            window_size = 200
            start = max(0, pos - window_size)
            end = min(len(content), pos + len(injection_point) + window_size)
            window = content[start:end]
            
            # Check for JavaScript context
            js_patterns = [
                r'<script[^>]*>.*?' + re.escape(injection_point),
                r'javascript:.*?' + re.escape(injection_point),
                r'on\w+\s*=\s*[\'"].*?' + re.escape(injection_point)
            ]
            
            for pattern in js_patterns:
                if re.search(pattern, window, re.IGNORECASE | re.DOTALL):
                    quotes = {"'": 0, '"': 0, '`': 0}
                    for i in range(start, pos):
                        if content[i] in quotes:
                            quotes[content[i]] += 1
                    
                    inside_quotes = None
                    for q, count in quotes.items():
                        if count % 2 == 1:
                            inside_quotes = q
                            break
                            
                    return XSSContext.JS_CONTEXT, {"inside_quotes": inside_quotes}
            
            # Check for attribute context
            attr_pattern = r'<[^>]+?(\w+)\s*=\s*([\'"]?).*?' + re.escape(injection_point)
            attr_match = re.search(attr_pattern, window, re.IGNORECASE | re.DOTALL)
            if attr_match:
                attr_name = attr_match.group(1)
                quote_type = attr_match.group(2)
                return XSSContext.ATTR_CONTEXT, {"attr_name": attr_name, "quote_type": quote_type}
            
            # Check for URL context
            url_pattern = r'(href|src|action|data)\s*=\s*([\'"]?).*?' + re.escape(injection_point)
            url_match = re.search(url_pattern, window, re.IGNORECASE)
            if url_match:
                return XSSContext.URL_CONTEXT, {"attr_name": url_match.group(1)}
            
            # Check for CSS context
            css_pattern = r'<style[^>]*>.*?' + re.escape(injection_point)
            if re.search(css_pattern, window, re.IGNORECASE | re.DOTALL):
                return XSSContext.CSS_CONTEXT, {}
                
            return XSSContext.HTML_CONTEXT, {}
            
        except Exception as e:
            print(f"Context analysis error: {e}")
            return XSSContext.HTML_CONTEXT, {}
            
    @staticmethod
    def get_context_specific_payloads(context, context_info):
        return get_payloads_for_context(context, context_info)