"""
VSCode Command Server HTTP Client

A robust Python client for interacting with VSCode Command Server extension.
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List, Callable
from urllib.parse import urljoin


class VSCodeHTTPClient:
    """HTTP client for VSCode Command Server extension."""
    
    def __init__(self, port: int = 3000, host: str = "localhost", timeout: int = 30, auto_retry: bool = False):
        """
        Initialize the VSCode HTTP client.
        
        Args:
            port: Server port (default: 3000)
            host: Server host (default: localhost)
            timeout: Request timeout in seconds (default: 30)
            auto_retry: Enable automatic retry on connection failure (default: False)
        """
        self.port = port
        self.host = host
        self.timeout = timeout
        self.auto_retry = auto_retry
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'vscode-command-client/1.0.0'
        })

    def _make_request_with_retry(self, request_func: Callable, max_retries: int = 3, retry_delay: float = 1.0) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            request_func: Function that makes the actual request
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            
        Returns:
            Response data or error
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return request_func()
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < max_retries:
                    if self.auto_retry:
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        break
        
        return {"success": False, "error": str(last_error), "retries_exhausted": True}

    def check_status(self) -> Dict[str, Any]:
        """
        Check if the server is running.
        
        Returns:
            Dict containing success status and server information
        """
        def _request():
            response = self.session.get(self.base_url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        
        if self.auto_retry:
            return self._make_request_with_retry(_request)
        else:
            try:
                return _request()
            except requests.exceptions.RequestException as e:
                return {"success": False, "error": str(e)}

    def execute_command(self, command: str, args: Optional[List[Any]] = None, retry: bool = None) -> Dict[str, Any]:
        """
        Execute a VSCode command via HTTP.
        
        Args:
            command: VSCode command name
            args: Optional command arguments
            retry: Override auto_retry setting for this request
            
        Returns:
            Dict containing execution result
        """
        def _request():
            payload = {
                "command": command,
                "args": args or []
            }
            
            response = self.session.post(
                urljoin(self.base_url, "/execute"),
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        use_retry = retry if retry is not None else self.auto_retry
        
        if use_retry:
            return self._make_request_with_retry(_request)
        else:
            try:
                return _request()
            except requests.exceptions.RequestException as e:
                return {"success": False, "error": str(e)}

    def get_commands(self) -> Dict[str, Any]:
        """
        Get list of available VSCode commands.
        
        Returns:
            Dict containing list of available commands
        """
        def _request():
            response = self.session.get(
                urljoin(self.base_url, "/commands"),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        if self.auto_retry:
            return self._make_request_with_retry(_request)
        else:
            try:
                return _request()
            except requests.exceptions.RequestException as e:
                return {"success": False, "error": str(e)}

    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information including port, PID, and workspace.
        
        Returns:
            Dict containing server information
        """
        def _request():
            response = self.session.get(
                urljoin(self.base_url, "/info"),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        if self.auto_retry:
            return self._make_request_with_retry(_request)
        else:
            try:
                return _request()
            except requests.exceptions.RequestException as e:
                return {"success": False, "error": str(e)}

    def is_server_running(self) -> bool:
        """
        Quick check if server is running.
        
        Returns:
            True if server is responding, False otherwise
        """
        status = self.check_status()
        return status.get("success", False)

    def wait_for_server(self, max_wait: int = 30, check_interval: float = 1.0) -> bool:
        """
        Wait for server to become available.
        
        Args:
            max_wait: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            True if server becomes available, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.is_server_running():
                return True
            time.sleep(check_interval)
        return False

    def reconnect(self, max_attempts: int = 5, wait_time: int = 2) -> Dict[str, Any]:
        """
        Attempt to reconnect to the server.
        
        Args:
            max_attempts: Maximum reconnection attempts
            wait_time: Time to wait between attempts
            
        Returns:
            Dict with reconnection result
        """
        # Close existing session and create new one
        self.close()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'vscode-command-client/1.0.0'
        })
        
        for attempt in range(1, max_attempts + 1):
            if self.is_server_running():
                return {
                    "success": True,
                    "message": f"Reconnected successfully on attempt {attempt}",
                    "attempts": attempt
                }
            
            if attempt < max_attempts:
                time.sleep(wait_time)
        
        return {
            "success": False,
            "error": f"Failed to reconnect after {max_attempts} attempts",
            "attempts": max_attempts
        }

    def restart_server(self) -> Dict[str, Any]:
        """
        Attempt to restart the VSCode Command Server extension.
        
        Returns:
            Dict with restart result
        """
        # Try to stop the server first
        stop_result = self.execute_command("run-extension.stopServer", retry=False)
        
        # Wait a moment
        time.sleep(1)
        
        # Try to start the server
        start_result = self.execute_command("run-extension.startServer", retry=False)
        
        if start_result.get("success"):
            # Wait for server to be ready
            if self.wait_for_server(max_wait=10):
                return {
                    "success": True,
                    "message": "Server restarted successfully",
                    "stop_result": stop_result.get("success", False),
                    "start_result": True
                }
        
        return {
            "success": False,
            "error": "Failed to restart server",
            "stop_result": stop_result.get("success", False),
            "start_result": start_result.get("success", False)
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check of the server connection.
        
        Returns:
            Dict with detailed health information
        """
        results = {}
        
        # Basic connectivity
        status = self.check_status()
        results["connectivity"] = status.get("success", False)
        results["status_response"] = status
        
        if results["connectivity"]:
            # Server info
            info = self.get_server_info()
            results["server_info"] = info.get("success", False)
            results["info_response"] = info
            
            # Commands availability
            commands = self.get_commands()
            results["commands_available"] = commands.get("success", False)
            results["command_count"] = commands.get("count", 0) if commands.get("success") else 0
            
            # Test command execution
            test_cmd = self.execute_command("run-extension.serverStatus", retry=False)
            results["command_execution"] = test_cmd.get("success", False)
        
        results["overall_health"] = all([
            results["connectivity"],
            results.get("server_info", False),
            results.get("commands_available", False)
        ])
        
        return {
            "success": True,
            "health": results,
            "timestamp": time.time()
        }

    def close(self):
        """Close the HTTP session."""
        if hasattr(self, 'session') and self.session:
            self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        return f"VSCodeHTTPClient(host={self.host}, port={self.port}, auto_retry={self.auto_retry})" 