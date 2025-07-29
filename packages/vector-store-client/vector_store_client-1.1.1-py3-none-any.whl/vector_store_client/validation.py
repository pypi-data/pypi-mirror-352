"""Validation functions for Vector Store Client parameters.

This module provides functions for validating input parameters before making API requests.
"""

import logging
from typing import Dict, Optional
from uuid import UUID
from datetime import datetime

from .exceptions import ValidationError

logger = logging.getLogger(__name__)

def validate_session_id(session_id: Optional[str], params: Dict) -> None:
    """Validates session_id and adds it to params if valid.
    
    Args:
        session_id: Session ID to validate (UUID)
        params: Parameters dictionary to update
        
    Raises:
        ValidationError: If session_id format is invalid
    """
    if session_id:
        try:
            UUID(session_id)
            params["session_id"] = session_id
        except ValueError:
            raise ValidationError("Invalid session_id format")

def validate_message_id(message_id: Optional[str], params: Dict) -> None:
    """Validates message_id and adds it to params if valid.
    
    Args:
        message_id: Message ID to validate (UUID)
        params: Parameters dictionary to update
        
    Raises:
        ValidationError: If message_id format is invalid
    """
    if message_id:
        try:
            UUID(message_id)
            params["message_id"] = message_id
        except ValueError:
            raise ValidationError("Invalid message_id format")

def validate_timestamp(timestamp: Optional[str], params: Dict) -> None:
    """Validates timestamp and adds it to params if valid.
    
    Args:
        timestamp: Timestamp to validate (ISO 8601 format)
        params: Parameters dictionary to update
        
    Raises:
        ValidationError: If timestamp format is invalid
    """
    if timestamp:
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            params["timestamp"] = timestamp
        except ValueError:
            raise ValidationError("Invalid timestamp format")

def validate_create_record_params(
    metadata: Dict,
    session_id: Optional[str] = None,
    message_id: Optional[str] = None,
    timestamp: Optional[str] = None
) -> Dict:
    """Validates parameters for record creation.
    
    Args:
        metadata: Metadata dictionary
        session_id: Optional session ID (UUID)
        message_id: Optional message ID (UUID)
        timestamp: Optional timestamp (ISO 8601 format)
        
    Returns:
        Validated parameters dict
        
    Raises:
        ValidationError: If any parameter is invalid
    """
    params = {"metadata": metadata or {}}
    
    validate_session_id(session_id, params)
    validate_message_id(message_id, params)
    validate_timestamp(timestamp, params)
    
    return params

def validate_limit(limit: int, min_value: int = 1, max_value: int = 100) -> int:
    """Validates limit parameter for search and filter operations.
    
    Args:
        limit: The limit value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Validated limit value
        
    Raises:
        ValidationError: If limit is outside allowed range
    """
    if limit < min_value or limit > max_value:
        raise ValidationError(f"Limit must be between {min_value} and {max_value}")
    return limit

def validate_server_response(response: dict, expected: str = None) -> None:
    """Validates the structure and content of the server response.
    Args:
        response: The response dictionary from the server
        expected: The expected key or type in the response (e.g., 'record_id', 'metadata', 'result', 'success')
    Raises:
        ValidationError: If the response is missing required fields, has wrong types, or is otherwise invalid
    """
    if not isinstance(response, dict):
        raise ValidationError(f"Server response is not a dictionary: {type(response)}")
    # JSON-RPC 2.0: must have 'result' or 'error'
    if "result" not in response and "error" not in response:
        raise ValidationError("Server response missing both 'result' and 'error' fields")
    # If error present, must be a dict or string
    if "error" in response and response["error"] is not None:
        if not isinstance(response["error"], (dict, str)):
            raise ValidationError("'error' field in server response must be dict or string")
    # If result present, check expected content
    if "result" in response:
        result = response["result"]
        # If expected is a key, check for it in result or nested result/data
        if expected:
            def has_expected_key(obj):
                if isinstance(obj, dict):
                    if expected in obj:
                        return True
                    # Check nested 'result' or 'data'
                    for nested_key in ("result", "data"):
                        if nested_key in obj and isinstance(obj[nested_key], dict):
                            if has_expected_key(obj[nested_key]):
                                return True
                return False
            if not has_expected_key(result):
                raise ValidationError(f"Server response 'result' missing expected key: '{expected}'")
    # If success/error pattern is used
    if "result" in response and isinstance(response["result"], dict):
        r = response["result"]
        if "success" in r:
            if not isinstance(r["success"], bool):
                raise ValidationError("'success' field in server response must be boolean")
            if not r["success"] and "error" not in r:
                raise ValidationError("Server response with success=false must contain 'error' field")
    # Optionally, add more checks for nested data, etc. 