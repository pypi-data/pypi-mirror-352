from urllib.parse import urlparse
from .httpClient import HTTPClient
from .parsers import HTMLParser

class WebCrawler:
    def __init__(self, http_client=None):
        self.http_client = http_client or HTTPClient()
        self.html_parser = HTMLParser()
        
    def crawl(self, base_url, max_depth=1, max_urls=10, callback=None):
        
     #base_url: starting URL for crawling
     #max_depth: maximum crawl depth
     #max_urls: maximum URLs to visit per level
     #callback: Optional callback function to process each URL ,,,,,, Function signature: callback(url, response)
            
            
        visited_urls = set([base_url])
        urls_to_visit = [base_url]
        all_discovered_urls = []
        base_domain = urlparse(base_url).netloc
        
        for depth in range(max_depth + 1):
            if not urls_to_visit:
                break
                
            current_urls = urls_to_visit[:max_urls]
            urls_to_visit = []
            
            for url in current_urls:
                if url in all_discovered_urls:
                    continue
                    
                all_discovered_urls.append(url)
                
                response, _ = self.http_client.get(url)
                if not response:
                    continue
                
                if callback:
                    callback(url, response)
                
                if depth >= max_depth:
                    continue
                    
                links = self.html_parser.extract_links(response.content, url)
                same_domain_links = self.html_parser.filter_same_domain_links(links, base_url)
                
                for link in same_domain_links:
                    if link not in visited_urls:
                        visited_urls.add(link)
                        urls_to_visit.append(link)
        
        return all_discovered_urls
        
    def get_forms_from_url(self, url):
        response, _ = self.http_client.get(url)
        if not response:
            return []
            
        return self.html_parser.extract_forms(response.content)