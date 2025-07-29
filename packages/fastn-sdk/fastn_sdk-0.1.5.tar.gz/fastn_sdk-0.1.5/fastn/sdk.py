# fastn/sdk.py
"""
Official Fastn SDK for Python.
This module provides an easy-to-use interface for the Fastn API.
"""

import requests
import json

class FastnAPIError(Exception):
    """Custom exception for Fastn API errors"""
    def __init__(self, status_code, error_data):
        self.status_code = status_code
        self.error_data = error_data
        message = f"API Error (HTTP {status_code}): {self._format_error(error_data)}"
        super().__init__(message)
        
    def _format_error(self, error_data):
        try:
            if isinstance(error_data, str):
                data = json.loads(error_data)
            else:
                data = error_data
                
            if isinstance(data, dict):
                code = data.get('code', 'UNKNOWN_ERROR')
                detail = data.get('datasourceDebug', {})
                datasource_name = detail.get('name', 'unknown')
                datasource_status = detail.get('statusCode', 0)
                
                return f"{code} - Datasource '{datasource_name}' returned status {datasource_status}"
            return str(error_data)
        except:
            return str(error_data)

class FastnSDK:
    def __init__(self, api_key: str, space_id: str, tenant_id: str = None, base_url: str = "https://live.fastn.ai", custom_token: str = None):
        """
        Initialize the Fastn SDK.
        
        Args:
            api_key (str): Your Fastn API key.
            space_id (str): The ID of your Fastn space.
            tenant_id (str, optional): The tenant ID for multi-tenant spaces. Defaults to None.
            base_url (str, optional): The base URL of the Fastn API. Defaults to "https://live.fastn.ai".
            custom_token (str, optional): Custom authentication token for tenant access. Defaults to None.
        """
        self.api_key = api_key
        self.space_id = space_id
        self.tenant_id = tenant_id
        self.base_url = base_url
        self.custom_token = custom_token
        self.endpoint = "/api/ucl/executeActionAgent"
        self.tools_endpoint = "/api/ucl/getTools"
        self.execute_tool_endpoint = "/api/ucl/executeTool"
        self.stage = "LIVE"
        self.headers = {
            "Content-Type": "application/json",
            "stage": self.stage,
            "x-fastn-api-key": self.api_key,
            "x-fastn-space-id": self.space_id
        }
        
        # Add custom token auth if provided
        if self.custom_token:
            self.headers["x-fastn-custom-auth"] = "true"
            self.headers["authorization"] = f"Bearer {self.custom_token}"
            self.headers["x-fastn-space-tenantid"] = self.tenant_id if self.tenant_id else ""

    def execute_action(self, prompt: str, session_id: str = None, debug: bool = False) -> dict:
        """
        Execute an action on the Fastn platform using natural language.
        
        Args:
            prompt (str): The natural language prompt describing the action to execute.
            session_id (str, optional): Session ID for tracking conversations. Defaults to None.
            debug (bool, optional): Enable debug output. Defaults to False.
            
        Returns:
            dict: The response from the Fastn API.
            
        Raises:
            FastnAPIError: If the API returns an error response.
        """
        url = f"{self.base_url}{self.endpoint}"
        payload = {
            "input": {
                "prompt": prompt,
                "env": self.base_url.replace("https://", ""),
            }
        }
        
        # Add sessionId only if it's provided
        if session_id:
            payload["input"]["sessionId"] = session_id

        # Print out the request details if debug is enabled
        if debug:
            print(f"URL: {url}")
            print(f"Headers: {self.headers}")
            print(f"Payload: {payload}")

        response = requests.post(url, json=payload, headers=self.headers)
        
        # Print response status and content if debug is enabled
        if debug:
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text[:500]}...")  # Show first 500 chars
        
        # Handle error responses
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except:
                error_data = response.text
            raise FastnAPIError(response.status_code, error_data)
            
        return response.json()

    def get_tools(self, debug: bool = False) -> dict:
        """
        Fetch available tools from the Fastn platform.
        
        Args:
            debug (bool, optional): Enable debug output. Defaults to False.
            
        Returns:
            dict: List of available tools from the Fastn API.
            
        Raises:
            FastnAPIError: If the API returns an error response.
        """
        url = f"{self.base_url}{self.tools_endpoint}"
        payload = {
            "input": {
                "spaceId": self.space_id
            }
        }
        
        # Print out the request details if debug is enabled
        if debug:
            print(f"URL: {url}")
            print(f"Headers: {self.headers}")
            print(f"Payload: {payload}")

        response = requests.post(url, json=payload, headers=self.headers)
        
        # Print response status and content if debug is enabled
        if debug:
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text[:500]}...")  # Show first 500 chars
        
        # Handle error responses
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except:
                error_data = response.text
            raise FastnAPIError(response.status_code, error_data)
            
        return response.json()
        
    def execute_tool(self, action_id: str, parameters: dict, debug: bool = False) -> dict:
        """
        Execute a specific tool on the Fastn platform.
        
        Args:
            action_id (str): The ID of the action/tool to execute.
            parameters (dict): Parameters required by the tool.
            debug (bool, optional): Enable debug output. Defaults to False.
            
        Returns:
            dict: The response from the Fastn API.
            
        Raises:
            FastnAPIError: If the API returns an error response.
        """
        url = f"{self.base_url}{self.execute_tool_endpoint}"
        payload = {
            "input": {
                "actionId": action_id,
                "parameters": parameters
            }
        }
        
        # Print out the request details if debug is enabled
        if debug:
            print(f"URL: {url}")
            print(f"Headers: {self.headers}")
            print(f"Payload: {payload}")

        response = requests.post(url, json=payload, headers=self.headers)
        
        # Print response status and content if debug is enabled
        if debug:
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text[:500]}...")  # Show first 500 chars
        
        # Handle error responses
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except:
                error_data = response.text
            raise FastnAPIError(response.status_code, error_data)
            
        return response.json()

class FastnClient:
    def __init__(self, api_key: str, space_id: str, tenant_id: str = None, base_url: str = "https://live.fastn.ai", auth_token: str = None, custom_token: str = None):
        """
        Initialize the Fastn Client.
        
        Args:
            api_key (str): Your Fastn API key.
            space_id (str): The ID of your Fastn space.
            tenant_id (str, optional): The tenant ID for multi-tenant spaces. Defaults to None.
            base_url (str, optional): The base URL of the Fastn API. Defaults to "https://live.fastn.ai".
            auth_token (str, optional): Authentication token for tenant access. Defaults to None.
            custom_token (str, optional): Alternative custom authentication token. Defaults to None.
        """
        self.api_key = api_key
        self.space_id = space_id
        self.tenant_id = tenant_id
        self.base_url = base_url
        self.auth_token = auth_token or custom_token  # Use either auth_token or custom_token
        self.endpoint = "/api/ucl/executeActionAgent"
        self.tools_endpoint = "/api/ucl/getTools"
        self.execute_tool_endpoint = "/api/ucl/executeTool"
        self.stage = "LIVE"
        self.headers = {
            "Content-Type": "application/json",
            "stage": self.stage,
            "x-fastn-api-key": self.api_key,
            "x-fastn-space-id": self.space_id
        }
        
        # Add auth token if available
        if self.auth_token:
            self.headers["x-fastn-custom-auth"] = "true"
            self.headers["authorization"] = f"Bearer {self.auth_token}"
            self.headers["x-fastn-space-tenantid"] = self.tenant_id if self.tenant_id else ""

    def execute_action(self, prompt: str, session_id: str = None, debug: bool = False) -> dict:
        """
        Execute an action on the Fastn platform using natural language.
        
        Args:
            prompt (str): The natural language prompt describing the action to execute.
            session_id (str, optional): Session ID for tracking conversations. Defaults to None.
            debug (bool, optional): Enable debug output. Defaults to False.
            
        Returns:
            dict: The response from the Fastn API.
            
        Raises:
            FastnAPIError: If the API returns an error response.
        """
        url = f"{self.base_url}{self.endpoint}"
        payload = {
            "input": {
                "prompt": prompt,
                "env": self.base_url.replace("https://", ""),
            }
        }
        
        # Add sessionId only if it's provided
        if session_id:
            payload["input"]["sessionId"] = session_id

        # Print out the request details if debug is enabled
        if debug:
            print(f"URL: {url}")
            print(f"Headers: {self.headers}")
            print(f"Payload: {payload}")

        response = requests.post(url, json=payload, headers=self.headers)
        
        # Print response status and content if debug is enabled
        if debug:
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text[:500]}...")  # Show first 500 chars
        
        # Handle error responses
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except:
                error_data = response.text
            raise FastnAPIError(response.status_code, error_data)
            
        return response.json()

    def get_tools(self, debug: bool = False) -> dict:
        """
        Fetch available tools from the Fastn platform.
        
        Args:
            debug (bool, optional): Enable debug output. Defaults to False.
            
        Returns:
            dict: List of available tools from the Fastn API.
            
        Raises:
            FastnAPIError: If the API returns an error response.
        """
        url = f"{self.base_url}{self.tools_endpoint}"
        payload = {
            "input": {
                "spaceId": self.space_id
            }
        }
        
        # Print out the request details if debug is enabled
        if debug:
            print(f"URL: {url}")
            print(f"Headers: {self.headers}")
            print(f"Payload: {payload}")

        response = requests.post(url, json=payload, headers=self.headers)
        
        # Print response status and content if debug is enabled
        if debug:
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text[:500]}...")  # Show first 500 chars
        
        # Handle error responses
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except:
                error_data = response.text
            raise FastnAPIError(response.status_code, error_data)
            
        return response.json()
        
    def execute_tool(self, action_id: str, parameters: dict, debug: bool = False) -> dict:
        """
        Execute a specific tool on the Fastn platform.
        
        Args:
            action_id (str): The ID of the action/tool to execute.
            parameters (dict): Parameters required by the tool.
            debug (bool, optional): Enable debug output. Defaults to False.
            
        Returns:
            dict: The response from the Fastn API.
            
        Raises:
            FastnAPIError: If the API returns an error response.
        """
        url = f"{self.base_url}{self.execute_tool_endpoint}"
        payload = {
            "input": {
                "actionId": action_id,
                "parameters": parameters
            }
        }
        
        # Print out the request details if debug is enabled
        if debug:
            print(f"URL: {url}")
            print(f"Headers: {self.headers}")
            print(f"Payload: {payload}")

        response = requests.post(url, json=payload, headers=self.headers)
        
        # Print response status and content if debug is enabled
        if debug:
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text[:500]}...")  # Show first 500 chars
        
        # Handle error responses
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except:
                error_data = response.text
            raise FastnAPIError(response.status_code, error_data)
            
        return response.json() 