import os
import requests
import time
import json
import logging
import warnings
from typing import Dict, Any, Optional, Union, BinaryIO, Callable
import mimetypes
from pathlib import Path
from urllib.parse import urlencode
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .types import (
    HealthCheckResponse,
    QueueResponse,
    ExecuteWorkflowResponse,
    GetOutputResponse,
    RunDetailResponse,
    RunListResponse,
    CancelRunResponse,
    FlowscaleConfig,
    WorkflowResponse,
    WebSocketOptions,
    WebSocketMessage,
)

class FlowscaleAPI:
    def __init__(self, config: FlowscaleConfig):
        """
        Initialize the Flowscale API client.
        
        Args:
            config: Configuration dictionary containing api_key, base_url, and optional settings
        """
        self.api_key = config['api_key']
        self.base_url = config['base_url']
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1000)  # milliseconds
        
        # Set up the requests session with retry strategy
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=self.retry_delay / 1000.0  # Convert to seconds
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default timeout
        self.timeout = config.get('timeout', 6000)  # Default 6000 seconds
        
        # Set default headers
        self.session.headers.update({
            'X-API-KEY': self.api_key
        })
        
        # WebSocket properties (Note: WebSocket functionality would require additional dependencies)
        self.ws = None
        self.ws_connected = False
        self.reconnect_attempts = 0
        
        # Set up logging
        self.logger = logging.getLogger('flowscale')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[Flowscale %(levelname)s] %(asctime)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def check_health(self) -> HealthCheckResponse:
        """
        Checks the health status of all ComfyUI instances within the specified cluster.
        
        Returns:
            The health status response
        """
        return self._make_request('GET', '/api/v1/comfy/health')

    def get_workflows(self) -> WorkflowResponse:
        """
        Retrieves the list of workflows available in the cluster.
        
        Returns:
            The workflows response
        """
        return self._make_request('GET', '/api/v1/comfy/workflows')

    def get_queue(self) -> QueueResponse:
        """
        Retrieves the queue data for all ComfyUI instances in the cluster.
        
        Returns:
            The queue status response
        """
        return self._make_request('GET', '/api/v1/comfy/queue')

    def execute_workflow(
        self, 
        workflow_id: str, 
        data: Dict[str, Any], 
        group_id: Optional[str] = None
    ) -> ExecuteWorkflowResponse:
        """
        Executes a specified workflow by processing dynamic form data.
        
        Args:
            workflow_id: The ID of the workflow to execute
            data: Form data including text fields and file uploads
            group_id: Optional group ID
            
        Returns:
            The workflow execution response
        """
        files = {}
        form_data = {}
        
        # Process the data into files and form fields
        for key, value in data.items():
            if isinstance(value, list):
                # Handle arrays (for multiple files)
                for item in value:
                    self._append_form_data(form_data, files, key, item)
            else:
                self._append_form_data(form_data, files, key, value)
        
        # Construct the URL with query parameters
        params = {'workflow_id': workflow_id}
        if group_id:
            params['group_id'] = group_id
        
        url = f"/api/v1/runs?{urlencode(params)}"
        
        # Make the request with multipart/form-data
        headers = {'Content-Type': 'multipart/form-data'}
        
        try:
            response = self.session.post(
                f"{self.base_url}{url}",
                data=form_data,
                files=files,
                timeout=self.timeout,
                headers={k: v for k, v in headers.items() if k != 'Content-Type'}  # Let requests set Content-Type for multipart
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)
        finally:
            # Close any opened files
            for file_obj in files.values():
                if hasattr(file_obj, 'close'):
                    file_obj.close()
                elif isinstance(file_obj, tuple) and len(file_obj) > 1 and hasattr(file_obj[1], 'close'):
                    file_obj[1].close()

    def execute_workflow_async(
        self,
        workflow_id: str,
        data: Dict[str, Any],
        group_id: Optional[str] = None,
        poll_interval_ms: int = 2000,
        timeout_ms: int = 600000
    ) -> GetOutputResponse:
        """
        Executes a workflow and waits for the output by polling.
        
        Args:
            workflow_id: The ID of the workflow to execute
            data: Form data including text fields and file uploads
            group_id: Optional group ID
            poll_interval_ms: Optional polling interval in milliseconds (default: 2000)
            timeout_ms: Optional timeout in milliseconds (default: 600000 - 10 minutes)
            
        Returns:
            The output response
        """
        start_time = time.time() * 1000  # Convert to milliseconds
        
        # Execute the workflow first
        execute_response = self.execute_workflow(workflow_id, data, group_id)
        
        # If there are no output names, throw an error
        if not execute_response.get('data', {}).get('output_names'):
            raise Exception('No output names returned from workflow execution')
        
        # Get the first output name
        output_name = execute_response['data']['output_names'][0]
        attempts = 0
        
        # Poll until we get a result or timeout
        while True:
            if (time.time() * 1000) - start_time > timeout_ms:
                raise Exception(f'Workflow execution timed out after {timeout_ms}ms')
            
            try:
                output = self.get_output(output_name)
                self._log_debug("Polling workflow output:", output)
                
                if output is None:
                    self._log_warn(f"No output found for {output_name}, retrying...")
                    # Continue polling - output is not ready yet
                    time.sleep(poll_interval_ms / 1000.0)
                    continue
                
                # Only return if status is 'success'
                if output.get('status') == 'success':
                    return output
                
                # Continue polling if status is 'in_progress'
                if output.get('status') == 'in_progress':
                    self._log_debug(f"Workflow still in progress (status: {output.get('status')}), continuing to poll...")
                    time.sleep(poll_interval_ms / 1000.0)
                    continue
                
                # If we get an error status, throw an error
                if output.get('status') in ['error', 'failed']:
                    raise Exception(f"Workflow execution failed with status: {output.get('status')}")
                
                # For any other status, continue polling but log it
                self._log_warn(f"Unexpected status: {output.get('status')}, continuing to poll...")
                time.sleep(poll_interval_ms / 1000.0)
                continue
            
            except Exception as error:
                # Log the error but continue polling
                self._log_warn(f"Error polling for output (attempt {attempts}):", error)
                # After several failures, increase polling interval to avoid excessive requests
                if attempts > 5:
                    poll_interval_ms = min(poll_interval_ms * 1.5, 10000)  # Increase interval, max 10s
                # Wait before retrying
                time.sleep(poll_interval_ms / 1000.0)
            
            attempts += 1

    def get_output(self, filename: str) -> Optional[GetOutputResponse]:
        """
        Retrieves the output of a specific run by providing the filename.
        
        Args:
            filename: The filename of the output to retrieve
            
        Returns:
            The output response or None if no output is found
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/runs/output",
                params={"filename": filename},
                timeout=self.timeout
            )
            
            if response.status_code == 204:
                return None
            elif response.status_code == 504:
                self._log_warn('Received 504 Gateway Timeout, retrying...')
                # For 504 errors specifically, we'll return None to allow the polling to continue
                return None
            elif response.status_code == 408:
                raise Exception("Run Timeout")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as error:
            if error.response and error.response.status_code == 204:
                return None
            elif error.response and error.response.status_code == 504:
                self._log_warn('Received 504 Gateway Timeout, retrying...')
                return None
            elif error.response and error.response.status_code == 408:
                raise Exception("Run Timeout")
            else:
                raise error
        except Exception as error:
            raise error

    def cancel_run(self, run_id: str) -> CancelRunResponse:
        """
        Cancels a specific run using its unique run ID.
        
        Args:
            run_id: The ID of the run to cancel
            
        Returns:
            The cancellation response
        """
        return self._make_request('POST', f'/api/v1/runs/{run_id}/cancel')

    def get_run(self, run_id: str) -> RunDetailResponse:
        """
        Retrieves detailed information about a specific run using its unique run ID.
        
        Args:
            run_id: The ID of the run to retrieve
            
        Returns:
            The run details response
        """
        return self._make_request('GET', f'/api/v1/runs/{run_id}')

    def get_runs(self, group_id: Optional[str] = None) -> RunListResponse:
        """
        Retrieves a list of all runs associated with a specific group ID.
        If no group ID is provided, all runs will be returned.
        
        Args:
            group_id: The group ID to filter runs
            
        Returns:
            The list of runs response
        """
        params = {'group_id': group_id} if group_id else {}
        return self._make_request('GET', '/api/v1/runs', params=params)

    def _append_form_data(self, form_data: Dict, files: Dict, key: str, value: Any):
        """
        Helper method to append data to form data and files dictionaries.
        """
        if hasattr(value, "read") and callable(value.read):
            # It's a file-like object
            files[key] = value
        elif isinstance(value, (bytes, bytearray)):
            # It's binary data
            files[key] = value
        elif isinstance(value, str) and os.path.isfile(value):
            # It's a file path
            file_name = os.path.basename(value)
            files[key] = (file_name, open(value, "rb"), 
                          mimetypes.guess_type(value)[0] or 'application/octet-stream')
        elif isinstance(value, dict):
            # Handle plain objects by stringifying
            form_data[key] = json.dumps(value)
        else:
            # Handle primitive values
            form_data[key] = str(value)

    def _handle_error(self, error: Exception) -> None:
        """
        Error handling helper.
        
        Args:
            error: The exception to handle
        """
        if isinstance(error, requests.exceptions.HTTPError):
            response = error.response
            try:
                error_data = response.json()
                error_message = json.dumps(error_data)
            except:
                error_data = response.text
                error_message = error_data
            
            raise Exception(
                f"Error: {response.status_code} {response.reason} - {error_message}"
            )
        elif isinstance(error, requests.exceptions.RequestException):
            raise Exception(f"No response received from API server: {str(error)}")
        else:
            print(error)
            raise Exception(f"Error: {str(error)}")

    def _log(self, level: str, message: str, *args):
        """
        Internal logging method
        """
        if level == 'debug':
            self.logger.debug(message, *args)
        elif level == 'info':
            self.logger.info(message, *args)
        elif level == 'warn':
            self.logger.warning(message, *args)
        elif level == 'error':
            self.logger.error(message, *args)

    def _log_debug(self, message: str, *args):
        self._log('debug', message, *args)

    def _log_info(self, message: str, *args):
        self._log('info', message, *args)

    def _log_warn(self, message: str, *args):
        self._log('warn', message, *args)

    def _log_error(self, message: str, *args):
        self._log('error', message, *args)

    def _make_request(self, method: str, url: str, params: Optional[Dict] = None, data: Any = None) -> Any:
        """
        Makes API request with retry capability
        """
        full_url = f"{self.base_url}{url}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(full_url, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(full_url, params=params, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    # WebSocket methods (Note: These would require additional dependencies like websocket-client)
    def connect_websocket(self, options: WebSocketOptions = None) -> Callable[[], None]:
        """
        Connects to the WebSocket API endpoint and sets up event handlers.
        Note: This requires the 'websocket-client' package to be installed.
        
        Args:
            options: Configuration options for the WebSocket connection
            
        Returns:
            A function that can be called to disconnect the WebSocket
        """
        warnings.warn(
            "WebSocket functionality requires the 'websocket-client' package. "
            "Install it with: pip install websocket-client",
            UserWarning
        )
        
        # This is a placeholder implementation
        # In a real implementation, you would use websocket-client library
        def disconnect():
            pass
        
        return disconnect

    def disconnect_websocket(self) -> None:
        """
        Disconnects the WebSocket connection if it exists.
        """
        if self.ws:
            self.ws = None
            self.ws_connected = False

    def send_websocket_message(self, message: Any) -> bool:
        """
        Sends a message through the WebSocket connection.
        
        Args:
            message: The message to send
            
        Returns:
            Whether the message was sent successfully
        """
        if not self.ws or not self.ws_connected:
            self._log_error('WebSocket is not connected')
            return False
        
        # This is a placeholder implementation
        return False

    def is_websocket_connected(self) -> bool:
        """
        Checks if the WebSocket connection is currently open.
        
        Returns:
            True if the WebSocket is connected, false otherwise
        """
        return self.ws_connected and self.ws is not None