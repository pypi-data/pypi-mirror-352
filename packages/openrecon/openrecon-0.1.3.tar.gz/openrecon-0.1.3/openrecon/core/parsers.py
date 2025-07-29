from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class HTMLParser:
    @staticmethod
    def parse_html(content):
        return BeautifulSoup(content, "html.parser")
        
    @staticmethod
    def extract_forms(html_content):
        parsed_html = BeautifulSoup(html_content, "html.parser")
        return parsed_html.find_all("form")
        
    @staticmethod
    def extract_form_details(form):
        form_details = {
            "action": form.attrs.get("action", ""),
            "method": form.attrs.get("method", "get").lower(),
            "inputs": []
        }
        
        for input_tag in form.find_all(["input", "textarea", "select"]):
            input_type = input_tag.attrs.get("type", "text") if input_tag.name == "input" else input_tag.name
            input_name = input_tag.attrs.get("name")
            input_value = input_tag.attrs.get("value", "")
            
            if input_name:
                form_details["inputs"].append({
                    "type": input_type,
                    "name": input_name,
                    "value": input_value
                })
        
        for select in form.find_all("select"):
            select_name = select.attrs.get("name")
            options = []
            
            for option in select.find_all("option"):
                options.append(option.attrs.get("value", ""))
            
            if select_name and options:
                form_details["inputs"].append({
                    "type": "select",
                    "name": select_name,
                    "value": options[0] if options else ""
                })

        return form_details
        
    @staticmethod
    def extract_links(html_content, base_url):
        parsed_html = BeautifulSoup(html_content, "html.parser")
        links = []
        
        for a_tag in parsed_html.find_all("a", href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            links.append(full_url)
            
        return links
        
    @staticmethod
    def filter_same_domain_links(links, base_url):
        base_domain = urlparse(base_url).netloc
        return [link for link in links if urlparse(link).netloc == base_domain]

class ResponseAnalyzer:
    @staticmethod
    def decode_response(response):
        if not response:
            return ""
        return response.content.decode(errors="ignore")
        
    @staticmethod
    def calculate_content_similarity(content1, content2):
        if not content1 or not content2:
            return 0
            
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return 0
            
        return len(intersection) / len(union)
        
    @staticmethod
    def contains_patterns(content, patterns):
        if not content:
            return False
            
        content = content.lower()
        return any(pattern.lower() in content for pattern in patterns)