import json
import streamlit as st
from typing import Dict, List, Any, Optional

class APIParser:
    def __init__(self, api_doc: Dict):
        self.api_doc = api_doc
        self.parsed_endpoints = []
        self.navigation_tree = {}
    
    def parse_document(self):
        """Parse the API documentation JSON structure"""
        try:
            if 'toc_dictionary' in self.api_doc:
                self.navigation_tree = self._parse_toc_dictionary(self.api_doc['toc_dictionary'])
                self.parsed_endpoints = self._extract_endpoints(self.api_doc['toc_dictionary'])
            else:
                st.error("Invalid API documentation format. Missing 'toc_dictionary' key.")
                return False
            return True
        except Exception as e:
            st.error(f"Error parsing API documentation: {str(e)}")
            return False
    
    def _parse_toc_dictionary(self, toc_dict: Dict, parent_path: str = "") -> Dict:
        """Recursively parse the table of contents dictionary"""
        navigation = {}
        
        for key, value in toc_dict.items():
            current_path = f"{parent_path}/{key}" if parent_path else key
            
            navigation[key] = {
                'level': value.get('level', 1),
                'is_last': value.get('is_last', False),
                'path': current_path,
                'section': value.get('section', {}),
                'api_endpoints': value.get('api_endpoints', []),
                'children': {},
                'has_endpoints': len(value.get('api_endpoints', [])) > 0,
                'has_children': 'children' in value and bool(value['children'])
            }
            
            if 'children' in value and value['children']:
                navigation[key]['children'] = self._parse_toc_dictionary(
                    value['children'], current_path
                )
        
        return navigation
    
    def _extract_endpoints(self, toc_dict: Dict, parent_path: str = "") -> List[Dict]:
        """Extract all API endpoints from the documentation"""
        endpoints = []
        
        for key, value in toc_dict.items():
            current_path = f"{parent_path} > {key}" if parent_path else key
            
            # Extract endpoints from current level
            if 'api_endpoints' in value and value['api_endpoints']:
                for endpoint in value['api_endpoints']:
                    endpoint_info = {
                        'category': current_path,
                        'endpoint': endpoint.get('endpoint', ''),
                        'method': self._extract_method_from_endpoint(endpoint.get('endpoint', '')),
                        'url': self._extract_url_from_endpoint(endpoint.get('endpoint', '')),
                        'description': value.get('section', {}).get('content_text', ''),
                        'request_body': endpoint.get('request_body', {}),
                        'curl_command': endpoint.get('curl_command', ''),
                        'responses': endpoint.get('responses', {}),
                        'raw_endpoint': endpoint
                    }
                    endpoints.append(endpoint_info)
            
            # Recursively extract from children
            if 'children' in value and value['children']:
                endpoints.extend(self._extract_endpoints(value['children'], current_path))
        
        return endpoints
    
    def _extract_method_from_endpoint(self, endpoint: str) -> str:
        """Extract HTTP method from endpoint string"""
        if not endpoint:
            return 'GET'
        
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        for method in methods:
            if endpoint.upper().startswith(method):
                return method
        
        return 'GET'
    
    def _extract_url_from_endpoint(self, endpoint: str) -> str:
        """Extract URL from endpoint string"""
        if not endpoint:
            return ''
        
        parts = endpoint.split(' ', 1)
        if len(parts) > 1:
            return parts[1]
        return endpoint
    
    def get_navigation_tree(self) -> Dict:
        """Get the navigation tree structure"""
        return self.navigation_tree
    
    def get_endpoints(self) -> List[Dict]:
        """Get all parsed endpoints"""
        return self.parsed_endpoints
    
    def get_endpoint_by_path(self, endpoint_path: str) -> Optional[Dict]:
        """Get specific endpoint by its path"""
        for endpoint in self.parsed_endpoints:
            if endpoint['endpoint'] == endpoint_path:
                return endpoint
        return None
    
    def search_endpoints(self, query: str) -> List[Dict]:
        """Search endpoints by query string"""
        if not query:
            return self.parsed_endpoints
        
        query = query.lower()
        filtered_endpoints = []
        
        for endpoint in self.parsed_endpoints:
            # Search in endpoint URL, method, category, and description
            if (query in endpoint['endpoint'].lower() or
                query in endpoint['method'].lower() or
                query in endpoint['category'].lower() or
                query in endpoint['description'].lower()):
                filtered_endpoints.append(endpoint)
        
        return filtered_endpoints
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        categories = set()
        for endpoint in self.parsed_endpoints:
            categories.add(endpoint['category'])
        return sorted(list(categories))
    
    def get_endpoints_by_category(self, category: str) -> List[Dict]:
        """Get endpoints filtered by category"""
        return [ep for ep in self.parsed_endpoints if ep['category'] == category]
    
    def format_endpoint_for_display(self, endpoint: Dict) -> str:
        """Format endpoint for display in UI"""
        method = endpoint['method']
        url = endpoint['url']
        return f"{method} {url}"
    
    def get_request_example(self, endpoint: Dict) -> Dict:
        """Get request example for an endpoint"""
        return {
            'method': endpoint['method'],
            'url': endpoint['url'],
            'headers': self._extract_headers_from_curl(endpoint.get('curl_command', '')),
            'body': endpoint.get('request_body', {})
        }
    
    def _extract_headers_from_curl(self, curl_command: str) -> Dict:
        """Extract headers from curl command"""
        headers = {}
        if not curl_command:
            return headers
        
        # Simple parsing of curl headers
        parts = curl_command.split(' -H ')
        for part in parts[1:]:  # Skip the first part (curl -X POST...)
            if '"' in part:
                header_part = part.split('"')[1]
                if ':' in header_part:
                    key, value = header_part.split(':', 1)
                    headers[key.strip()] = value.strip()
        
        return headers
    
    def get_response_examples(self, endpoint: Dict) -> Dict:
        """Get response examples for an endpoint"""
        return endpoint.get('responses', {})
