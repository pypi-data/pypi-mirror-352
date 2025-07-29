import requests
import json
from urllib.parse import urljoin
import time
from datetime import timedelta
from typing import Optional, Dict, Any, List
from core.colors import Colors, Messages

class GraphQLScanner:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, verbose: bool = False, request_delay: float = 1.0, max_requests_per_minute: int = 30, max_retries: int = 3, retry_delay: float = 5.0):
        self.base_url = base_url
        self.headers = headers or {
            'User-Agent': 'OpenRecon-GraphQL-Scanner/1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.endpoints = self._get_default_endpoints()
        self.timeout = 10
        self.verbose = verbose
        self.scan_start_time = None
        self.scan_end_time = None
        
        self.request_delay = request_delay
        self.max_requests_per_minute = max_requests_per_minute
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.request_timestamps = []
        
        self.header_tests = {
            'apollo': {
                'apollo-require-preflight': 'true',
                'apollo-operation-name': 'TestOperation',
                'apollo-operation-type': 'query',
                'apollo-query-hash': 'test-hash',
                'apollo-client-name': 'test-client',
                'apollo-client-version': '1.0.0'
            },
            'graphql': {
                'x-graphql-operation': 'query',
                'x-graphql-operation-name': 'TestOperation',
                'x-graphql-variables': '{"test":"value"}',
                'x-graphql-extensions': '{"persistedQuery":{"version":1,"sha256Hash":"test"}}'
            },
            'batching': {
                'content-type': 'application/json',
                'accept': 'application/json',
                'x-batch-size': '10',
                'x-batch-id': 'test-batch',
                'x-batch-priority': 'high'
            }
        }
        
        # GraphQL-specific test payloads
        self.graphql_payloads = {
            'introspection': [
                '{__schema{types{name,fields{name}}}}',
                '{__type(name:"User"){name,fields{name,type{name}}}}',
                'mutation{__typename}',
                'query{__schema{queryType{name}}}',
                '{__type(name:"Query"){name,fields{name,args{name,type{name}}}}}',
                '{__schema{types{name,fields{name,args{name,type{name}}}}}}',
                '{__schema{queryType{name,fields{name,args{name,type{name}}}}}}',
                '{__schema{mutationType{name,fields{name,args{name,type{name}}}}}}',
                '{__schema{subscriptionType{name,fields{name,args{name,type{name}}}}}}',
                '{__schema{directives{name,description,locations,args{name,type{name}}}}}'
            ],
            'depth_attacks': [
                '{' + 'user {' * 5 + 'id' + '}' * 5 + '}',
                '{' + 'user {' * 10 + 'id' + '}' * 10 + '}',
                '{' + 'user {' * 20 + 'id' + '}' * 20 + '}',
                '{' + 'user {' * 50 + 'id' + '}' * 50 + '}',
                '{' + 'user {' * 100 + 'id' + '}' * 100 + '}'
            ],
            'batch_attacks': [
                [{'query': '{__typename}'}, {'query': '{__schema{types{name}}}'}],
                [{'query': '{__typename}'} for _ in range(10)],
                [{'query': '{__typename}'} for _ in range(50)],
                [{'query': '{__typename}'} for _ in range(100)],
                [{'query': '{__typename}'} for _ in range(1000)]
            ],
            'aliases': [
                '{a:__typename b:__typename c:__typename}',
                '{a:__schema{types{name}} b:__schema{types{name}} c:__schema{types{name}}}',
                '{a:__type(name:"User"){name} b:__type(name:"User"){name} c:__type(name:"User"){name}}'
            ],
            'fragments': [
                'fragment X on Query { __typename } { ...X }',
                'fragment X on Query { __typename ...X } { ...X }',
                'fragment X on Query { __typename ...Y } fragment Y on Query { __typename ...X } { ...X }'
            ],
            'cost_analysis': [
                # Simple nested query
                '{user{posts{comments{user{posts{comments{id}}}}}}}',
                # Multiple nested fields
                '{user{posts{comments{user{profile{settings{preferences{notifications{email}}}}}}}}}',
                # List with nested objects
                '{users{posts{comments{reactions{user{profile{settings{preferences{id}}}}}}}}}',
                # Multiple root queries
                '{users{id} posts{id} comments{id} reactions{id} settings{id}}',
                # Complex nested lists
                '{users{posts{comments{reactions{user{posts{comments{reactions{id}}}}}}}}}',
                # Multiple fragments with nesting
                '''
                fragment UserFields on User {
                    id
                    posts {
                        comments {
                            user {
                                profile {
                                    settings {
                                        id
                                    }
                                }
                            }
                        }
                    }
                }
                {
                    users {
                        ...UserFields
                        ...UserFields
                        ...UserFields
                    }
                }
                '''
            ]
        }
    
    def _print_status(self, message: str, status_type: str = "info"):
        elapsed = ""
        if self.scan_start_time:
            elapsed = f" [{timedelta(seconds=time.time()-self.scan_start_time)}]"
        
        prefixes = {
            "info": ("[*]", Colors.INFO),
            "success": ("[+]", Colors.SUCCESS),
            "warning": ("[!]", Colors.WARNING),
            "error": ("[×]", Colors.ERROR),
            "critical": ("[!]", Colors.CRITICAL)
        }
        
        prefix, color = prefixes.get(status_type.lower(), ("[*]", Colors.INFO))
        print(f"{color.render(prefix)}{elapsed} {message}")

    def _print_verbose(self, message: str):
        if self.verbose:
            print(f"{Colors.VERBOSE.render('  [DEBUG]')} {Colors.VERBOSE_HIGHLIGHT.render(message)}")

    def _print_test_result(self, test_name: str, result: bool, time_taken: float):
        status = Colors.VALID.render("PASS") if result else Colors.INVALID.render("FAIL")
        time_str = Colors.PORT.render(f"{time_taken:.3f}s")
        print(f"  {Colors.CHECKING.render('→')} {test_name:<40} {status} {time_str}")

    def _get_default_endpoints(self) -> List[str]:
        return [
            '/graphql',
            '/graphql/',
            '/api',
            '/api/graphql',
            '/query',
            '/gql',
            '/graphql-api',
            '/v1/graphql',
            '/v2/graphql',
            '/graphql/v1',
            '/graphql/v2'
        ]
    
    def _wait_for_rate_limit(self):
        if self.max_requests_per_minute == 0:
            return
            
        current_time = time.time()
        
        self.request_timestamps = [ts for ts in self.request_timestamps if current_time - ts < 60]
        
        # If we've hit the rate limit, wait
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - self.request_timestamps[0])
            if wait_time > 0:
                if self.verbose:
                    print(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.request_timestamps = []
        
        # Add delay between requests if delay is not 0
        if self.request_delay > 0 and self.request_timestamps:
            time.sleep(self.request_delay)
        
        self.request_timestamps.append(current_time)

    def _send_request(self, url: str, query: str, variables: Optional[Dict[str, Any]] = None, custom_headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Send a GraphQL request with rate limiting and retries"""
        self._print_verbose(f"Sending request to {Colors.URL.render(url)}")
        self._print_verbose(f"Query: {Colors.VERBOSE_HIGHLIGHT.render(query)}")
        
        if variables:
            self._print_verbose(f"Variables: {Colors.VERBOSE_HIGHLIGHT.render(str(variables))}")
        
        payload = {'query': query}
        if variables:
            payload['variables'] = variables
            
        # Use custom headers if provided, otherwise use default headers
        headers = custom_headers if custom_headers is not None else self.headers
            
        start_time = time.time()
        retries = 0
        
        while retries <= self.max_retries:
            try:
                # Apply rate limiting
                self._wait_for_rate_limit()
                
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                    verify=False
                )
                elapsed = time.time() - start_time
                
                self._print_verbose(f"Response ({elapsed:.3f}s): Status {response.status_code}")
                if self.verbose and response.text:
                    self._print_verbose(f"Response body: {Colors.VERBOSE_HIGHLIGHT.render(response.text[:200])}{'...' if len(response.text) > 200 else ''}")
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Too Many Requests
                    retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                    if self.verbose:
                        self._print_status(f"Rate limited. Waiting {retry_after}s before retry...", "warning")
                    time.sleep(retry_after)
                    retries += 1
                    continue
                else:
                    self._print_status(f"Request failed with status {response.status_code}", "warning")
                    if retries < self.max_retries:
                        retries += 1
                        time.sleep(self.retry_delay)
                        continue
                    break
                    
            except requests.exceptions.RequestException as e:
                elapsed = time.time() - start_time
                self._print_status(f"Request failed: {str(e)}", "error")
                self._print_verbose(f"Failed after {elapsed:.3f}s")
                if retries < self.max_retries:
                    retries += 1
                    time.sleep(self.retry_delay)
                    continue
                break
                
        return None
    
    def discover_graphql_endpoints(self) -> List[str]:
        discovered = []
        for endpoint in self.endpoints:
            url = urljoin(self.base_url, endpoint)
            query = '{__schema {types {name}}}'
            response = self._send_request(url, query)
            if response and not response.get('errors'):
                discovered.append(url)
        return discovered
    
    def introspect_schema(self, endpoint_url: str) -> Optional[Dict[str, Any]]:
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                    ...FullType
                }
                directives {
                    name
                    description
                    locations
                    args {
                        ...InputValue
                    }
                }
            }
        }
        
        fragment FullType on __Type {
            kind
            name
            description
            fields(includeDeprecated: true) {
                name
                description
                args {
                    ...InputValue
                }
                type {
                    ...TypeRef
                }
                isDeprecated
                deprecationReason
            }
            inputFields {
                ...InputValue
            }
            interfaces {
                ...TypeRef
            }
            enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
            }
            possibleTypes {
                ...TypeRef
            }
        }
        
        fragment InputValue on __InputValue {
            name
            description
            type {
                ...TypeRef
            }
            defaultValue
        }
        
        fragment TypeRef on __Type {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                    ofType {
                                        kind
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        return self._send_request(endpoint_url, introspection_query)
    
    def analyze_query_cost(self, endpoint_url: str) -> Dict[str, Any]:
        """Analyze query cost and complexity"""
        results = {
            'cost_limiting_enabled': False,
            'expensive_queries_allowed': False,
            'cost_analysis': [],
            'suggestions': []
        }
        
        self._print_status("Analyzing query cost and complexity...")
        
        for i, payload in enumerate(self.graphql_payloads['cost_analysis']):
            start_time = time.time()
            response = self._send_request(endpoint_url, payload)
            elapsed = time.time() - start_time
            
            complexity = self._estimate_query_complexity(payload)
            
            analysis = {
                'query': payload,
                'complexity': complexity,
                'response_time': elapsed,
                'success': response is not None and not response.get('errors'),
                'error': response.get('errors', [])[0].get('message') if response and response.get('errors') else None
            }
            
            results['cost_analysis'].append(analysis)
            
            if complexity > 1000 and analysis['success']:
                results['expensive_queries_allowed'] = True
                results['suggestions'].append(
                    f"Expensive query allowed (complexity: {complexity}, time: {elapsed:.2f}s)"
                )
            
            if response and response.get('errors'):
                error_msg = str(response['errors'][0].get('message', '')).lower()
                if any(term in error_msg for term in ['cost', 'complexity', 'limit', 'threshold']):
                    results['cost_limiting_enabled'] = True
                    results['suggestions'].append(
                        f"Cost limiting detected (complexity: {complexity}, error: {error_msg})"
                    )
        
        if not results['cost_limiting_enabled']:
            results['suggestions'].append(
                "No query cost limiting detected. Implement query complexity analysis and limits."
            )
        if results['expensive_queries_allowed']:
            results['suggestions'].append(
                "Expensive queries are allowed. Implement query cost thresholds."
            )
        
        return results
    
    def _estimate_query_complexity(self, query: str) -> int:
        """Estimate the complexity of a GraphQL query"""
        complexity = 0
        
        # Count nested levels
        nested_level = 0
        for char in query:
            if char == '{':
                nested_level += 1
                complexity += nested_level
            elif char == '}':
                nested_level -= 1
        
        # Count fields
        fields = query.count('{') - query.count('fragment')
        complexity += fields * 2
        
        fragments = query.count('fragment')
        complexity += fragments * 10
        
        aliases = query.count(':')
        complexity += aliases * 5
        
        list_indicators = ['s]', 's{', 's ', 's\n']
        for indicator in list_indicators:
            complexity += query.count(indicator) * 20
        
        return complexity

    def test_headers(self, endpoint_url: str) -> Dict[str, Any]:
        """Test GraphQL-specific headers and their handling"""
        results = {
            'apollo_headers': {
                'supported': False,
                'details': []
            },
            'graphql_headers': {
                'supported': False,
                'details': []
            },
            'batching_headers': {
                'supported': False,
                'details': []
            },
            'vulnerabilities': [],
            'suggestions': []
        }
        
        self._print_status("Testing GraphQL-specific headers...")
        
        self._print_status("Testing Apollo-specific headers...")
        original_headers = self.headers.copy()
        for header, value in self.header_tests['apollo'].items():
            test_headers = original_headers.copy()
            test_headers[header] = value
            
            response = self._send_request(
                endpoint_url,
                '{__typename}',
                custom_headers=test_headers
            )
            
            if response and not response.get('errors'):
                results['apollo_headers']['supported'] = True
                results['apollo_headers']['details'].append(f"Header {header} is supported")
            elif response and response.get('errors'):
                error_msg = str(response['errors'][0].get('message', '')).lower()
                if 'apollo' in error_msg:
                    results['apollo_headers']['details'].append(f"Header {header} is recognized but rejected")
        
        self._print_status("Testing GraphQL-specific headers...")
        for header, value in self.header_tests['graphql'].items():
            test_headers = original_headers.copy()
            test_headers[header] = value
            
            response = self._send_request(
                endpoint_url,
                '{__typename}',
                custom_headers=test_headers
            )
            
            if response and not response.get('errors'):
                results['graphql_headers']['supported'] = True
                results['graphql_headers']['details'].append(f"Header {header} is supported")
            elif response and response.get('errors'):
                error_msg = str(response['errors'][0].get('message', '')).lower()
                if 'graphql' in error_msg or 'operation' in error_msg:
                    results['graphql_headers']['details'].append(f"Header {header} is recognized but rejected")
        
        self._print_status("Testing batching headers...")
        for header, value in self.header_tests['batching'].items():
            test_headers = original_headers.copy()
            test_headers[header] = value
            
            batch_payload = [
                {'query': '{__typename}'},
                {'query': '{__schema{types{name}}}'}
            ]
            
            try:
                response = requests.post(
                    endpoint_url,
                    headers=test_headers,
                    json=batch_payload,
                    timeout=self.timeout,
                    verify=False
                )
                
                if response.status_code == 200:
                    batch_response = response.json()
                    if isinstance(batch_response, list) and len(batch_response) > 1:
                        results['batching_headers']['supported'] = True
                        results['batching_headers']['details'].append(
                            f"Batching possible with header {header}"
                        )
                        
                        if header == 'x-batch-size' and int(value) > 100:
                            results['vulnerabilities'].append(
                                f"Large batch size ({value}) allowed via header"
                            )
                        elif header == 'x-batch-priority' and value == 'high':
                            results['vulnerabilities'].append(
                                "High priority batching allowed"
                            )
            except:
                continue
        
        if results['apollo_headers']['supported']:
            results['suggestions'].append(
                "Apollo headers are supported. Consider implementing strict header validation."
            )
        if results['graphql_headers']['supported']:
            results['suggestions'].append(
                "GraphQL-specific headers are supported. Consider implementing strict header validation."
            )
        if results['batching_headers']['supported']:
            results['suggestions'].append(
                "Batching headers are supported. Consider implementing strict batching limits."
            )
        if results['vulnerabilities']:
            results['suggestions'].append(
                "Implement strict header validation and batching limits to prevent abuse."
            )
        
        return results

    def test_graphql_vulnerabilities(self, endpoint_url: str) -> Dict[str, Any]:
        results = {
            'introspection_abuse': False,
            'depth_attack_vulnerable': False,
            'batch_attack_vulnerable': False,
            'alias_abuse': False,
            'fragment_abuse': False,
            'cost_analysis': {},
            'header_analysis': {},
            'vulnerability_details': [],
            'suggestions': []
        }
        
        self._print_status("Testing for introspection abuse...")
        for payload in self.graphql_payloads['introspection']:
            response = self._send_request(endpoint_url, payload)
            if self._check_injection_success(response, 'introspection'):
                results['introspection_abuse'] = True
                results['vulnerability_details'].append(f"Introspection possible with payload: {payload}")
                break
        
        self._print_status("Testing for query depth vulnerabilities...")
        for payload in self.graphql_payloads['depth_attacks']:
            start_time = time.time()
            response = self._send_request(endpoint_url, payload)
            elapsed = time.time() - start_time
            
            if response and not response.get('errors'):
                results['depth_attack_vulnerable'] = True
                results['vulnerability_details'].append(
                    f"Depth attack possible with {payload.count('{')} levels (took {elapsed:.2f}s)"
                )
                break
        
        self._print_status("Testing for batch query vulnerabilities...")
        for payload in self.graphql_payloads['batch_attacks']:
            try:
                response = requests.post(
                    endpoint_url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout,
                    verify=False
                )
                if response.status_code == 200:
                    batch_response = response.json()
                    if isinstance(batch_response, list) and len(batch_response) > 1:
                        results['batch_attack_vulnerable'] = True
                        results['vulnerability_details'].append(
                            f"Batch attack possible with {len(payload)} queries"
                        )
                        break
            except:
                continue
        
        self._print_status("Testing for alias abuse...")
        for payload in self.graphql_payloads['aliases']:
            response = self._send_request(endpoint_url, payload)
            if response and not response.get('errors'):
                results['alias_abuse'] = True
                results['vulnerability_details'].append(f"Alias abuse possible with payload: {payload}")
                break
        
        self._print_status("Testing for fragment abuse...")
        for payload in self.graphql_payloads['fragments']:
            response = self._send_request(endpoint_url, payload)
            if response and not response.get('errors'):
                results['fragment_abuse'] = True
                results['vulnerability_details'].append(f"Fragment abuse possible with payload: {payload}")
                break
        
        self._print_status("Performing query cost analysis...")
        cost_results = self.analyze_query_cost(endpoint_url)
        results['cost_analysis'] = cost_results
        
        results['suggestions'].extend(cost_results['suggestions'])
        
        self._print_status("Testing GraphQL-specific headers...")
        header_results = self.test_headers(endpoint_url)
        results['header_analysis'] = header_results
        
        results['suggestions'].extend(header_results['suggestions'])
        
        return results

    def _check_injection_success(self, response: Optional[Dict[str, Any]], test_type: str) -> bool:
        """Check if a GraphQL-specific test was successful"""
        if not response:
            return False
            
        if test_type == 'introspection':
            return 'data' in response and '__schema' in str(response)
            
        return 'data' in response and not response.get('errors')

    def check_vulnerabilities(self, endpoint_url: str) -> Dict[str, Any]:
        results = {
            'introspection_enabled': False,
            'debug_mode_enabled': False,
            'csrf_protection': True,
            'batch_requests_enabled': False,
            'information_disclosure': [],
            'query_depth_analysis': None,
            'graphql_vulnerabilities': {},
            'suggestions': []
        }
        
        schema = self.introspect_schema(endpoint_url)
        if schema:
            results['introspection_enabled'] = True
            results['suggestions'].append(
                "Introspection is enabled. Consider disabling in production."
            )
        
        debug_query = '{__typename}'
        debug_headers = {'X-Debug-Mode': 'true'}
        original_headers = self.headers.copy()
        self.headers.update(debug_headers)
        response = self._send_request(endpoint_url, debug_query)
        self.headers = original_headers
        
        if response and 'extensions' in response and 'debug' in response['extensions']:
            results['debug_mode_enabled'] = True
            results['suggestions'].append(
                "Debug mode appears to be enabled. Disable in production."
            )
        
        csrf_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        original_headers = self.headers.copy()
        self.headers.update(csrf_headers)
        response = self._send_request(
            endpoint_url,
            'mutation { __typename }'
        )
        self.headers = original_headers
        
        if response and not response.get('errors'):
            results['csrf_protection'] = False
            results['suggestions'].append(
                "CSRF protection might be missing. Implement CSRF tokens."
            )
        
        batch_payload = [
            {'query': '{__typename}'},
            {'query': '{__schema{types{name}}}'}
        ]
        try:
            response = requests.post(
                endpoint_url,
                headers=self.headers,
                json=batch_payload,
                timeout=self.timeout,
                verify=False
            )
            if response.status_code == 200:
                batch_response = response.json()
                if isinstance(batch_response, list) and len(batch_response) > 1:
                    results['batch_requests_enabled'] = True
                    results['suggestions'].append(
                        "Batch requests are enabled. Consider rate limiting."
                    )
        except:
            pass
        
        error_query = '{ nonExistentField }'
        response = self._send_request(endpoint_url, error_query)
        if response and 'errors' in response:
            for error in response['errors']:
                if 'message' in error and 'stack trace' in error['message'].lower():
                    results['information_disclosure'].append(
                        "Stack traces exposed in error messages"
                    )
                if 'message' in error and any(word in error['message'].lower() 
                                           for word in ['sql', 'syntax', 'database']):
                    results['information_disclosure'].append(
                        "Database information exposed in error messages"
                    )
        
        if results['information_disclosure']:
            results['suggestions'].append(
                "Sensitive information exposed in errors. Configure error masking."
            )
        
        deep_query = '{' + 'user {' * 10 + 'id' + '}' * 10 + '}'
        start_time = time.time()
        response = self._send_request(endpoint_url, deep_query)
        elapsed = time.time() - start_time
        
        results['query_depth_analysis'] = {
            'depth': 10,
            'response_time': elapsed,
            'success': response is not None
        }
        
        if response and not response.get('errors'):
            results['suggestions'].append(
                "No query depth limiting detected. Implement depth limiting."
            )
        
        self._print_status("Testing GraphQL-specific vulnerabilities...")
        graphql_results = self.test_graphql_vulnerabilities(endpoint_url)
        results['graphql_vulnerabilities'] = graphql_results
        results['suggestions'].extend(graphql_results['suggestions'])
        
        return results
    
    def scan(self) -> Dict[str, Any]:
        self.scan_start_time = time.time()
        self._print_status(f"Starting GraphQL scan against {Colors.URL.render(self.base_url)}")
        
        # Print rate limiting configuration
        if self.max_requests_per_minute == 0:
            self._print_status("Rate limiting: Disabled")
        else:
            self._print_status(f"Rate limiting: {self.max_requests_per_minute} requests/minute with {self.request_delay}s delay")
        
        self._print_status("Discovering GraphQL endpoints...")
        
        results = {
            'base_url': self.base_url,
            'discovered_endpoints': [],
            'vulnerabilities': {},
            'schema': None,
            'timestamp': time.time(),
            'scan_duration': 0
        }
        
        # Endpoint discovery
        discovery_start = time.time()
        endpoints = self.discover_graphql_endpoints()
        discovery_time = time.time() - discovery_start
        
        if not endpoints:
            self._print_status("No GraphQL endpoints discovered", "warning")
            return results
            
        self._print_status(f"Discovered {len(endpoints)} endpoints", "success")
        for i, endpoint in enumerate(endpoints, 1):
            self._print_status(f"  {i}. {Colors.URL.render(endpoint)}")
        results['discovered_endpoints'] = endpoints
        
        main_endpoint = endpoints[0]
        self._print_status(f"Scanning primary endpoint: {Colors.URL.render(main_endpoint)}")
        
        self._print_status("Performing schema introspection...")
        schema_start = time.time()
        schema = self.introspect_schema(main_endpoint)
        schema_time = time.time() - schema_start
        
        if schema:
            self._print_status("Successfully retrieved schema", "success")
            results['schema'] = schema
            self._print_verbose(f"Schema contains {len(schema['data']['__schema']['types'])} types")
        else:
            self._print_status("Schema introspection failed", "warning")
        
        self._print_status("Running vulnerability checks...")
        vuln_start = time.time()
        vuln_results = self.check_vulnerabilities(main_endpoint)
        vuln_time = time.time() - vuln_start
        
        # Print vulnerability results
        self._print_status("Vulnerability check results:", "info")
        self._print_test_result("Introspection enabled", vuln_results['introspection_enabled'], schema_time)
        self._print_test_result("Debug mode enabled", vuln_results['debug_mode_enabled'], 0)
        self._print_test_result("CSRF protection", vuln_results['csrf_protection'], 0)
        self._print_test_result("Batch requests enabled", vuln_results['batch_requests_enabled'], 0)
        
        if vuln_results['information_disclosure']:
            self._print_status("Information disclosure issues found:", "warning")
            for issue in vuln_results['information_disclosure']:
                print(f"  {Colors.VULNERABLE.render('!')} {issue}")

        self._print_test_result("Query depth protection", not vuln_results['query_depth_analysis']['success'], vuln_results['query_depth_analysis']['response_time'])
        
        if vuln_results['suggestions']:
            self._print_status("Security suggestions:", "info")
            for suggestion in vuln_results['suggestions']:
                print(f"  {Colors.WARNING.render('•')} {suggestion}")
        
        results['vulnerabilities'] = vuln_results
        self.scan_end_time = time.time()
        results['scan_duration'] = self.scan_end_time - self.scan_start_time
        
        self._print_status(f"Scan completed in {results['scan_duration']:.2f} seconds", "success")
        return results