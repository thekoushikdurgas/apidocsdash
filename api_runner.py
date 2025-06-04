import requests
import json
import time
import streamlit as st
from typing import Dict, Any, Optional, Tuple, List
import re

class APIRunner:
    def __init__(self):
        self.session = requests.Session()
        self.timeout = 30
    
    def execute_request(self, method: str, url: str, headers: Optional[Dict] = None, 
                       body: Any = None, params: Optional[Dict] = None, 
                       environment_vars: Optional[Dict] = None) -> Tuple[Dict, int]:
        """
        Execute API request and return response data and execution time
        
        Returns:
            Tuple[Dict, int]: (response_data, execution_time_ms)
        """
        try:
            # Replace environment variables in URL and headers
            if environment_vars:
                url = self._replace_variables(url, environment_vars)
                if headers:
                    headers = {k: self._replace_variables(v, environment_vars) 
                             for k, v in headers.items()}
            
            # Prepare request
            start_time = time.time()
            
            # Handle different body types
            if body:
                if isinstance(body, (dict, list)):
                    body = json.dumps(body)
                    if headers is None:
                        headers = {}
                    headers['Content-Type'] = 'application/json'
            
            # Make the request
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                data=body,
                params=params,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            end_time = time.time()
            execution_time = int((end_time - start_time) * 1000)  # Convert to milliseconds
            
            # Parse response
            response_data = self._parse_response(response)
            response_data['execution_time'] = execution_time
            response_data['request_url'] = response.url
            
            return response_data, execution_time
            
        except requests.exceptions.Timeout:
            return {
                'error': 'Request timeout',
                'status_code': 0,
                'headers': {},
                'body': 'Request timed out after 30 seconds',
                'execution_time': 30000
            }, 30000
        except requests.exceptions.ConnectionError:
            return {
                'error': 'Connection error',
                'status_code': 0,
                'headers': {},
                'body': 'Could not connect to the server',
                'execution_time': 0
            }, 0
        except Exception as e:
            return {
                'error': str(e),
                'status_code': 0,
                'headers': {},
                'body': f'Request failed: {str(e)}',
                'execution_time': 0
            }, 0
    
    def _parse_response(self, response: requests.Response) -> Dict:
        """Parse response object into structured data"""
        response_data = {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'body': '',
            'json': None,
            'text': '',
            'size': len(response.content),
            'encoding': response.encoding
        }
        
        # Try to parse JSON
        try:
            response_data['json'] = response.json()
            response_data['body'] = json.dumps(response_data['json'], indent=2)
        except (ValueError, json.JSONDecodeError):
            response_data['text'] = response.text
            response_data['body'] = response.text
        
        return response_data
    
    def _replace_variables(self, text: str, variables: Dict) -> str:
        """Replace environment variables in text using {{variable}} syntax"""
        if not text or not variables:
            return text
        
        # Replace {{variable}} patterns
        for key, value in variables.items():
            pattern = f"{{{{{key}}}}}"
            text = text.replace(pattern, str(value))
        
        return text
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is properly formatted"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
    
    def get_curl_command(self, method: str, url: str, headers: Optional[Dict] = None, 
                        body: Any = None, params: Optional[Dict] = None) -> str:
        """Generate curl command for the request"""
        curl_parts = ['curl', '-X', method.upper()]
        
        # Add URL
        if params:
            url_params = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{url_params}"
        
        curl_parts.extend([f'"{url}"'])
        
        # Add headers
        if headers:
            for key, value in headers.items():
                curl_parts.extend(['-H', f'"{key}: {value}"'])
        
        # Add body
        if body:
            if isinstance(body, (dict, list)):
                body_str = json.dumps(body)
            else:
                body_str = str(body)
            curl_parts.extend(['-d', f"'{body_str}'"])
        
        return ' '.join(curl_parts)
    
    def get_supported_methods(self) -> List[str]:
        """Get list of supported HTTP methods"""
        return ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    
    def get_common_headers(self) -> Dict[str, str]:
        """Get common HTTP headers"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'API-Dashboard/1.0',
            'Authorization': 'Bearer {{token}}',
            'X-API-Key': '{{api_key}}'
        }
    
    def format_response_for_display(self, response_data: Dict) -> Dict:
        """Format response data for display in UI"""
        formatted = {
            'status': response_data.get('status_code', 0),
            'time': response_data.get('execution_time', 0),
            'size': response_data.get('size', 0),
            'headers': response_data.get('headers', {}),
            'body': response_data.get('body', ''),
            'json': response_data.get('json'),
            'is_json': response_data.get('json') is not None
        }
        
        return formatted
    
    def get_status_color(self, status_code: int) -> str:
        """Get color for status code display"""
        if status_code == 0:
            return "red"
        elif 200 <= status_code < 300:
            return "green"
        elif 300 <= status_code < 400:
            return "blue"
        elif 400 <= status_code < 500:
            return "orange"
        elif status_code >= 500:
            return "red"
        else:
            return "gray"
