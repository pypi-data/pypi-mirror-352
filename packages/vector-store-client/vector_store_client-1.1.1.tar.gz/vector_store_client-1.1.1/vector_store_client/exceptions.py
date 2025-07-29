"""Custom exceptions for Vector Store Client.

This module defines exception classes for handling various errors in the Vector Store client.
"""

from typing import Dict, Optional, Any
from pydantic import BaseModel

class VectorStoreError(Exception):
    """Base exception class for Vector Store Client."""
    pass

class ConnectionError(VectorStoreError):
    """Raised when API is unreachable."""
    pass

class TimeoutError(VectorStoreError):
    """Raised when request times out."""
    pass

class ValidationError(VectorStoreError):
    """Raised when input validation fails."""
    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)

class JsonRpcException(VectorStoreError):
    """Raised when API returns an error response.
    
    Standard JSON-RPC error codes:
    * -32700: Parse error - Invalid JSON received
    * -32600: Invalid Request - JSON not conforming to JSON-RPC 2.0 spec
    * -32601: Method not found - Method does not exist / is not available
    * -32602: Invalid params - Invalid method parameters
    * -32603: Internal error - Internal JSON-RPC error
    * -32000 to -32099: Server error - Reserved for implementation-defined server errors
    
    Custom error codes:
    * 404: Resource not found
    * 401: Authentication error
    * 403: Authorization error
    * 409: Conflict (e.g. duplicate resource)
    * 429: Rate limit exceeded
    """
    
    def __init__(self, error, message: Optional[str] = None, code: Optional[int] = None, data: Optional[Any] = None):
        # If already our JsonRpcException, just copy fields
        if isinstance(error, JsonRpcException):
            self.code = error.code
            self.message = error.message
            self.data = getattr(error, 'data', None)
            super().__init__(self.message)
            return
        # If code and message provided directly, use them
        if code is not None:
            self.code = code
            self.message = message or str(error)
            self.data = data
            super().__init__(self.message)
            return
        # If pydantic model
        if isinstance(error, BaseModel):
            error = error.model_dump()
        # If dict
        if isinstance(error, dict):
            self.code = error.get("code")
            self.message = message or error.get("message")
            self.data = error.get("data")
            super().__init__(self.message)
            return
        # If string or other
        self.code = -32603  # Internal error
        self.message = str(error)
        self.data = None
        super().__init__(self.message)

    @classmethod
    def from_code(cls, code: int, message: str, data: Optional[Dict[str, Any]] = None) -> 'JsonRpcException':
        """Create exception from error code and message.
        
        Args:
            code: JSON-RPC error code
            message: Error message
            data: Additional error data
            
        Returns:
            JsonRpcException: Configured exception
        """
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        return cls(error)

class AuthenticationError(VectorStoreError):
    """Raised when authentication fails."""
    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)

class AuthorizationError(VectorStoreError):
    """Raised when user doesn't have permission for the operation."""
    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)

class ResourceNotFoundError(VectorStoreError):
    """Raised when requested resource is not found."""
    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)

class DuplicateError(VectorStoreError):
    """Raised when trying to create duplicate resource."""
    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)

class ServerError(VectorStoreError):
    """Raised when server encounters an error."""
    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)

class RateLimitError(VectorStoreError):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: Optional[str] = None, **kwargs):
        self.message = message
        self.retry_after = retry_after
        self.kwargs = kwargs
        super().__init__(message)

class InvalidRequestError(VectorStoreError):
    """Raised when request is invalid."""
    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)

class ConfigurationError(VectorStoreError):
    """Raised when there's an issue with configuration."""
    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)

class SchemaValidationError(ValidationError):
    """Raised when schema validation fails."""
    pass

class EmbeddingError(VectorStoreError):
    """Raised when embedding generation fails."""
    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(message)

class BadResponseError(VectorStoreError):
    """Raised when server returns an unexpected response format."""
    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs
        super().__init__(message) 