"""Base client implementation for Vector Store API.

This module provides the low-level client functionality for interacting with the Vector Store API.
"""

import logging
import json
import httpx
import jsonschema
from typing import Dict, List, Optional, Any, Union, Type, cast
from uuid import UUID
import time
import asyncio

from .models import JsonRpcRequest, JsonRpcResponse, SearchResult
from .exceptions import (
    ValidationError, 
    JsonRpcException, 
    ConnectionError, 
    TimeoutError, 
    ResourceNotFoundError,
    AuthenticationError, 
    AuthorizationError,
    DuplicateError, 
    RateLimitError,
    ServerError,
    InvalidRequestError,
    BadResponseError,
    SchemaValidationError
)

logger = logging.getLogger(__name__)

# Error code to exception mapping
ERROR_MAP = {
    # Standard JSON-RPC errors
    -32700: InvalidRequestError,  # Parse error
    -32600: InvalidRequestError,  # Invalid Request
    -32601: InvalidRequestError,  # Method not found
    -32602: ValidationError,      # Invalid params
    -32603: ServerError,          # Internal error
    
    # Custom HTTP-like error codes
    400: InvalidRequestError,     # Bad Request
    401: AuthenticationError,     # Unauthorized
    403: AuthorizationError,      # Forbidden
    404: ResourceNotFoundError,   # Not Found
    409: DuplicateError,          # Conflict
    429: RateLimitError,          # Too Many Requests
    500: ServerError,             # Internal Server Error
}

class BaseVectorStoreClient:
    """Base client with low-level API functionality."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8007",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        async_client: Optional[httpx.AsyncClient] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_on_status_codes: Optional[List[int]] = None
    ):
        """Initialize Vector Store client.
        
        Args:
            base_url: Base URL of the Vector Store API
            timeout: Request timeout in seconds
            headers: Optional custom headers
            async_client: Optional pre-configured async HTTP client
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
            retry_on_status_codes: HTTP status codes to retry on
        """
        self.base_url = base_url.rstrip('/')
        self._timeout = timeout
        self._headers = headers or {"Content-Type": "application/json"}
        self._client = async_client or httpx.AsyncClient(
            timeout=timeout,
            headers=self._headers
        )
        self.schema = None
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._retry_on_status_codes = retry_on_status_codes or [408, 429, 500, 502, 503, 504]
        self._request_id = 0

    async def load_schema(self) -> Dict:
        """Loads the API command schema from the server.
        
        Returns:
            Dict containing API command schema
            
        Raises:
            ConnectionError: If schema couldn't be loaded
            ValidationError: If schema is invalid
        """
        try:
            # Try to get detailed command schema first
            resp = await self._client.get(f"{self.base_url}/api/commands")
            
            if resp.status_code != 200:
                # Fallback to help command if /api/commands not available
                logger.debug("Falling back to help command for schema")
                help_resp = await self._make_request("help", {})
                self.schema = help_resp["result"]
                return self.schema
                
            schema_data = resp.json()
            
            # Verify schema structure
            if not isinstance(schema_data, dict):
                raise ConnectionError("Invalid API schema: not a dictionary")
                
            if "commands" not in schema_data and "methods" in schema_data:
                # Rename methods to commands for consistency
                schema_data["commands"] = schema_data.pop("methods")
                
            if "commands" not in schema_data:
                # Try to construct schema from OpenAPI specification
                logger.debug("Trying to extract schema from OpenAPI spec")
                openapi_resp = await self._client.get(f"{self.base_url}/openapi.json")
                if openapi_resp.status_code == 200:
                    openapi_data = openapi_resp.json()
                    schema_data = self._extract_schema_from_openapi(openapi_data)
                    if "commands" not in schema_data:
                        raise ConnectionError("API schema doesn't contain commands and couldn't be extracted from OpenAPI spec")
                else:
                    raise ConnectionError("API schema doesn't contain commands and OpenAPI spec not available")
            
            self.schema = schema_data
            return self.schema
            
        except httpx.HTTPError as e:
            raise ConnectionError(f"Failed to load API schema: {e}")
        except ValidationError as e:
            # Re-throw validation errors as is
            raise
        except Exception as e:
            raise ConnectionError(f"Failed to process API schema: {e}")

    def _extract_schema_from_openapi(self, openapi_data: Dict) -> Dict:
        """Extract command schema from OpenAPI specification.
        
        Args:
            openapi_data: OpenAPI specification dictionary
            
        Returns:
            Extracted schema in our format
        """
        schema = {"commands": {}}
        
        # Get available commands from enum values in CommandRequest
        if "components" in openapi_data and "schemas" in openapi_data["components"]:
            schemas = openapi_data["components"]["schemas"]
            
            if "CommandRequest" in schemas and "properties" in schemas["CommandRequest"]:
                cmd_props = schemas["CommandRequest"]["properties"]
                
                if "command" in cmd_props and "enum" in cmd_props["command"]:
                    commands = cmd_props["command"]["enum"]
                    
                    # Create basic command entries
                    for cmd in commands:
                        schema["commands"][cmd] = {
                            "name": cmd,
                            "description": f"Command {cmd}"
                        }
                        
                        # Find parameter schema if available
                        param_schema_name = f"{cmd.title().replace('_', '')}Params"
                        if param_schema_name in schemas:
                            params_info = {}
                            if "properties" in schemas[param_schema_name]:
                                for param_name, param_info in schemas[param_schema_name]["properties"].items():
                                    params_info[param_name] = {
                                        "type": param_info.get("type", "string"),
                                        "description": param_info.get("description", ""),
                                        "required": param_name in schemas[param_schema_name].get("required", [])
                                    }
                            schema["commands"][cmd]["params"] = params_info
        
        return schema

    @classmethod
    async def create(cls, *args, **kwargs) -> 'BaseVectorStoreClient':
        """Async factory method that loads schema and returns ready client.
        
        Returns:
            Initialized client instance with loaded schema
        """
        self = cls(*args, **kwargs)
        await self.load_schema()
        return self

    async def _make_request(
        self,
        method: str,
        params: Dict,
        request_id: Optional[int] = None
    ) -> Dict:
        """Make JSON-RPC request to API.
        
        Args:
            method: RPC method name
            params: Method parameters
            request_id: Optional request ID (auto-generated if None)
            
        Returns:
            Response data
            
        Raises:
            ConnectionError: If API is unreachable
            TimeoutError: If request times out
            JsonRpcException: If API returns an error
        """
        if request_id is None:
            self._request_id += 1
            request_id = self._request_id
            
        request = JsonRpcRequest(
            method=method,
            params=params,
            id=request_id
        )
        
        request_data = request.model_dump()
        
        for attempt in range(self._max_retries):
            try:
                logger.debug(f"Making request to {self.base_url}/cmd: {request_data}")
                
                response = await self._client.post(
                    f"{self.base_url}/cmd",
                    json=request_data
                )
                
                # Handle HTTP-level errors
                if response.status_code >= 400:
                    # Check if we should retry
                    if response.status_code in self._retry_on_status_codes and attempt < self._max_retries - 1:
                        retry_after = response.headers.get('Retry-After')
                        delay = float(retry_after) if retry_after and retry_after.isdigit() else self._retry_delay
                        logger.warning(f"Request failed with status {response.status_code}, retrying in {delay}s")
                        await asyncio.sleep(delay * (attempt + 1))  # Exponential backoff
                        continue
                    
                    # If we get a 429, raise RateLimitError
                    if response.status_code == 429:
                        retry_after = response.headers.get('Retry-After')
                        raise RateLimitError(
                            f"Too many requests, retry after {retry_after}s if provided",
                            retry_after=retry_after
                        )
                        
                    # Map HTTP status codes to exceptions
                    if response.status_code in ERROR_MAP:
                        exc_class = ERROR_MAP[response.status_code]
                        raise exc_class(f"HTTP error: {response.status_code} {response.reason_phrase}")
                    
                    # Generic HTTP error
                    raise ConnectionError(f"HTTP error: {response.status_code} {response.reason_phrase}")
                
                # Parse JSON response
                try:
                    response_data = response.json()
                    logger.debug(f"Received response: {response_data}")
                except Exception as e:
                    raise BadResponseError(f"Invalid JSON response: {e}")
                
                # Validate JSON-RPC format
                if not isinstance(response_data, dict):
                    raise BadResponseError("Response is not a dictionary")
                
                # Handle adapted format where result is nested in a data field
                if "result" in response_data and isinstance(response_data["result"], dict) and "data" in response_data["result"]:
                    # Format: {"result": {"success": true, "data": {...}}}
                    if response_data["result"].get("success", True) == True:
                        data_response = response_data.copy()
                        data_response["result"] = response_data["result"]["data"]
                        response_data = data_response
                        logger.debug(f"Processed nested data format: {response_data}")
                
                # Check for JSON-RPC error
                if "error" in response_data:
                    self._handle_error_response(response_data["error"])
                
                # Check expected fields
                if "jsonrpc" not in response_data:
                    logger.warning("Response missing jsonrpc field")
                    
                if "id" not in response_data:
                    logger.warning("Response missing id field")
                    
                # Поддержка нестандартных форматов ответа без поля result
                if "result" not in response_data:
                    # Если это прямой ответ (без оболочки jsonrpc)
                    if "data" in response_data:
                        modified_data = response_data.copy()
                        modified_data["result"] = response_data["data"]
                        modified_data["jsonrpc"] = "2.0"
                        modified_data["id"] = request_id
                        response_data = modified_data
                        logger.debug(f"Fixed missing result field with data: {response_data}")
                    else:
                        # Если в данных нет ни result, ни data - создаем ответ из всех данных
                        logger.warning(f"Response missing result field, using entire response as result: {response_data}")
                        modified_data = {"result": response_data, "jsonrpc": "2.0", "id": request_id}
                        response_data = modified_data
                
                # Validate that response ID matches request ID
                resp_id = response_data.get("id")
                if resp_id is not None and resp_id != request_id:
                    logger.warning(f"Response ID {resp_id} doesn't match request ID {request_id}")
                
                return response_data
                
            except httpx.TimeoutException as e:
                if attempt < self._max_retries - 1:
                    logger.warning(f"Request timed out, retrying ({attempt+1}/{self._max_retries})")
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                    continue
                raise TimeoutError(f"Request timed out after {self._max_retries} attempts: {e}")
                
            except httpx.HTTPError as e:
                if attempt < self._max_retries - 1:
                    logger.warning(f"HTTP error occurred, retrying ({attempt+1}/{self._max_retries}): {e}")
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                    continue
                raise ConnectionError(f"HTTP error occurred: {e}")
                
            except (ConnectionError, TimeoutError, JsonRpcException):
                # Re-throw these exceptions without modification
                raise
                
            except Exception as e:
                # For unexpected errors, log and convert to ConnectionError
                logger.exception("Unexpected error during request")
                raise ConnectionError(f"Request failed: {e}")
    
    def _handle_error_response(self, error: Any) -> None:
        """Process error response from API.
        
        Args:
            error: Error object from response
            
        Raises:
            JsonRpcException: With translated error info
            ServerError: If error format is not recognized
        """
        try:
            if isinstance(error, dict):
                # Handle standard JSON-RPC error format
                if "code" in error and "message" in error:
                    code = error["code"]
                    message = error["message"]
                    data = error.get("data")
                    
                    # Map to appropriate exception type
                    exc_class = ERROR_MAP.get(code, JsonRpcException)
                    
                    # Если это ошибка связанная с неверной размерностью - преобразуем в ValidationError
                    if "dimension mismatch" in message.lower() or "vector dimension" in message.lower():
                        exc_class = ValidationError
                        
                    # Генерируем соответствующее исключение с дополнительными параметрами
                    if exc_class is JsonRpcException:
                        raise exc_class(message=message, code=code, data=data)
                    else:
                        # Для других типов исключений передаем сообщение как есть
                        raise exc_class(message)
                
                # Handle nested error structure
                if "error" in error and isinstance(error["error"], dict):
                    return self._handle_error_response(error["error"])
                
                # Handle server's success=False format
                if "success" in error and error["success"] is False:
                    if "error" in error and isinstance(error["error"], dict):
                        return self._handle_error_response(error["error"])
            
            # Default error handler
            raise ServerError(f"Unrecognized error format: {error}")
        except Exception as e:
            if isinstance(e, (JsonRpcException, ValidationError, ResourceNotFoundError)):
                # Re-raise JSON-RPC exceptions and другие специфические исключения как есть
                raise
            # Wrap other errors
            raise ServerError(f"Error handling response: {e}") from e
            
    async def __aenter__(self) -> 'BaseVectorStoreClient':
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self._client.aclose()

    async def call_command(self, command: str, **params) -> Any:
        """Call a command defined in the loaded schema with parameter validation.
        
        Args:
            command: Command name (as in schema)
            **params: Parameters for the command
            
        Returns:
            Result of the command
            
        Raises:
            ValidationError: If command or parameters are invalid
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error
        """
        if not self.schema:
            try:
                await self.load_schema()
            except Exception as e:
                raise ValidationError(f"Failed to load API schema: {e}")
                
        if "commands" not in self.schema:
            raise ValidationError("API schema does not contain commands")
            
        if command not in self.schema["commands"]:
            raise ValidationError(f"Unknown command: {command}")
        
        # Create JSON Schema for parameters
        cmd_info = self.schema["commands"][command]
        param_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Extract parameter information if available
        if "params" in cmd_info and isinstance(cmd_info["params"], dict):
            for pname, pinfo in cmd_info["params"].items():
                param_type = pinfo.get("type", "string")
                param_schema["properties"][pname] = {"type": param_type}
                
                if pinfo.get("required", False):
                    param_schema["required"].append(pname)
                    
        # Validate parameters against schema
        try:
            jsonschema.validate(instance=params, schema=param_schema)
        except jsonschema.ValidationError as e:
            raise SchemaValidationError(f"Parameter validation error for command '{command}': {e.message}")
            
        # Send command
        response = await self._make_request(command, params)
        return response["result"]
        
    def _process_search_results(self, response: Dict) -> List[SearchResult]:
        """Process search results from API response.
        
        Args:
            response: API response dictionary
            
        Returns:
            List of SearchResult objects
        """
        if "result" not in response:
            # Если это уже список записей, обработаем его напрямую
            if isinstance(response, list):
                records = response
            elif isinstance(response, dict):
                # Проверяем разные форматы ответа
                if "records" in response:
                    records = response["records"]
                elif "matches" in response:
                    records = response["matches"]
                elif "data" in response and isinstance(response["data"], list):
                    records = response["data"]
                else:
                    logger.warning(f"No records found in search results: {response}")
                    return []
            else:
                logger.warning(f"No records found in search results: {response}")
                return []
        else:
            result = response["result"]
            
            # Handle nested data format
            if isinstance(result, dict) and "data" in result and "success" in result and result["success"]:
                result = result["data"]
                
            # Try to parse string result as JSON
            if isinstance(result, str):
                try:
                    parsed = json.loads(result)
                    if isinstance(parsed, list):
                        result = parsed
                    elif isinstance(parsed, dict) and "records" in parsed:
                        result = parsed["records"]
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse string result as JSON: {result}")
                
            # Convert result to list if it's not already
            records = []
            if isinstance(result, dict):
                # Handle more complex nested formats
                if "result" in result and isinstance(result["result"], dict) and "records" in result["result"]:
                    records = result["result"]["records"]
                elif "records" in result:
                    records = result["records"]
                elif "matches" in result:
                    records = result["matches"]
                elif "data" in result and isinstance(result["data"], list):
                    records = result["data"]
            elif isinstance(result, list):
                records = result
                
        if not records:
            logger.warning(f"No records found in search results: {result}")
            return []
        
        results = []
        
        # Log extracted result data
        logger.debug(f"Processing search results: {records}")
        
        # Handle different result item formats
        if isinstance(records, list):
            for item in records:
                if isinstance(item, dict):
                    # Map fields from server response to SearchResult format
                    try:
                        record_id = item.get("record_id") or item.get("id")
                        if not record_id:
                            logger.warning(f"Record missing ID: {item}")
                            continue
                            
                        score = item.get("score", 1.0)
                        metadata = item.get("metadata", {})
                        vector = item.get("vector", None)
                        
                        search_result = SearchResult(
                            id=record_id,
                            score=score,
                            metadata=metadata,
                            vector=vector
                        )
                        
                        results.append(search_result)
                    except (KeyError, ValueError, TypeError) as e:
                        logger.error(f"Failed to create SearchResult: {e}, data: {item}")
                elif isinstance(item, SearchResult):
                    # Already in the right format
                    results.append(item)
                elif isinstance(item, str):
                    # Если элемент - просто строка (ID записи)
                    search_result = SearchResult(
                        id=item,
                        score=1.0,
                        metadata={},
                        vector=None
                    )
                    results.append(search_result)
                else:
                    logger.warning(f"Unrecognized search result item: {item}")
        
        return results 