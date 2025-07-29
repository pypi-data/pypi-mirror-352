"""Vector Store Client library.

Provides client for interacting with Vector Store API.
"""

from .client import VectorStoreClient
from .models import SearchResult, VectorRecord
from .exceptions import (
    ValidationError, 
    JsonRpcException, 
    ConnectionError, 
    TimeoutError,
    ResourceNotFoundError,
    AuthenticationError,
    AuthorizationError,
    DuplicateError,
    ServerError,
    RateLimitError
)
from .base_client import BaseVectorStoreClient
from .utils import extract_uuid_from_response, validate_uuid, clean_metadata
from .validation import (
    validate_session_id, 
    validate_message_id, 
    validate_timestamp,
    validate_create_record_params,
    validate_limit
)

__version__ = '1.1.2'
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Импортируем типы
from .types import (
    MetadataDict, 
    FilterCriteria, 
    SearchOptions, 
    MessageStructure, 
    Vector, 
    RecordId, 
    JsonRpcId, 
    JsonRpcParams, 
    JsonRpcResult, 
    JsonRpcError as JsonRpcErrorType
)

__all__ = [
    # Client
    'VectorStoreClient',
    'BaseVectorStoreClient',
    'create_client',
    
    # Models
    'SearchResult',
    'VectorRecord',
    
    # Exceptions
    'ValidationError',
    'JsonRpcException',
    'ConnectionError',
    'TimeoutError',
    'ResourceNotFoundError',
    'AuthenticationError',
    'AuthorizationError',
    'DuplicateError',
    'ServerError',
    'RateLimitError',
    
    # Types
    'MetadataDict',
    'FilterCriteria',
    'SearchOptions',
    'MessageStructure',
    'Vector',
    'RecordId',
    'JsonRpcId',
    'JsonRpcParams',
    'JsonRpcResult',
    'JsonRpcErrorType',
    
    # Utils
    'extract_uuid_from_response',
    'validate_uuid',
    'clean_metadata',
    
    # Validation
    'validate_session_id',
    'validate_message_id',
    'validate_timestamp',
    'validate_create_record_params',
    'validate_limit'
]

async def create_client(*args, **kwargs):
    """Async factory function for creating a client instance.
    
    This is a convenience wrapper around VectorStoreClient.create()
    """
    return await VectorStoreClient.create(*args, **kwargs) 