"""Utility functions for Vector Store Client.

This module provides helper functions for data processing and manipulation.
"""

import logging
import json
import re
from typing import Any, Dict, Optional
from uuid import UUID
import copy

logger = logging.getLogger(__name__)

def extract_uuid_from_response(response: Any) -> str:
    """Extract UUID from various response formats.
    
    Args:
        response: API response data
        
    Returns:
        UUID as string
        
    Raises:
        ValueError: If UUID can't be extracted
    """
    logger.debug(f"Extracting UUID from: {response}")
    
    # Проверяем на возможную ошибку в ответе
    if isinstance(response, dict) and "success" in response and response.get("success") is False:
        if "error" in response:
            error = response["error"]
            if isinstance(error, dict):
                error_msg = error.get("message", "Unknown error")
                error_code = error.get("code", -1)
                from .exceptions import JsonRpcException
                raise JsonRpcException(message=error_msg, code=error_code, data=error.get("data"), error=error)
            else:
                raise ValueError(f"Error in response: {error}")
    
    # Прямая строка UUID
    if isinstance(response, str):
        return response
        
    # Словарь с полем record_id
    if isinstance(response, dict):
        if "record_id" in response:
            return response["record_id"]
        elif "id" in response:
            return response["id"]
        elif "result" in response and isinstance(response["result"], dict):
            if "record_id" in response["result"]:
                return response["result"]["record_id"]
            elif "id" in response["result"]:
                return response["result"]["id"]
                
    # Попытка преобразования к строке
    try:
        return str(response)
    except Exception as e:
        raise ValueError(f"Failed to extract UUID from response: {e}") from e

def validate_uuid(uuid_str: str) -> bool:
    """Validate if a string is a valid UUID.
    
    Args:
        uuid_str: String to validate
        
    Returns:
        True if the string is a valid UUID, False otherwise
    """
    try:
        UUID(uuid_str)
        return True
    except ValueError:
        return False

def clean_metadata(metadata: Optional[Dict]) -> Dict:
    """Clean and validate metadata dictionary.
    
    Args:
        metadata: Metadata dictionary or None
        
    Returns:
        Cleaned copy of metadata
    """
    if metadata is None:
        return {"body": "No content provided"}
        
    # Deep copy the dictionary to avoid modifying the original
    result = copy.deepcopy(metadata)
    
    # Ensure body field is present and not empty
    if "body" not in result or not result["body"]:
        # Try to use text field if available
        if "text" in result and result["text"]:
            result["body"] = result["text"]
        else:
            # Add a default body if missing
            result["body"] = "No content provided"
    
    return result 