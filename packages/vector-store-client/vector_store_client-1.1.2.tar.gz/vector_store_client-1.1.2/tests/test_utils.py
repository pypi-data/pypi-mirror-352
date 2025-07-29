"""Tests for utility functions."""

import pytest
import uuid

from vector_store_client.utils import extract_uuid_from_response, clean_metadata, validate_uuid
from vector_store_client.exceptions import JsonRpcException

def test_extract_uuid_successful_cases():
    """Test extract_uuid_from_response with various valid formats."""
    test_id = str(uuid.uuid4())
    
    # Test direct string
    assert extract_uuid_from_response(test_id) == test_id
    
    # Test dict with record_id
    assert extract_uuid_from_response({"record_id": test_id}) == test_id
    
    # Test dict with id
    assert extract_uuid_from_response({"id": test_id}) == test_id
    
    # Test nested dict
    assert extract_uuid_from_response({"result": {"record_id": test_id}}) == test_id
    assert extract_uuid_from_response({"result": {"id": test_id}}) == test_id

def test_extract_uuid_error_handling():
    """Test that errors in responses raise appropriate exceptions."""
    # Test error response
    error_response = {
        "success": False, 
        "error": {
            "code": -32603, 
            "message": "Missing body field",
            "data": {"details": "Required field is missing"}
        }
    }
    
    with pytest.raises(JsonRpcException) as excinfo:
        extract_uuid_from_response(error_response)
        
    assert excinfo.value.code == -32603
    assert "Missing body field" in excinfo.value.message
    assert excinfo.value.data == {"details": "Required field is missing"}
    
    # Test error without structured data
    simple_error = {"success": False, "error": "Something went wrong"}
    
    with pytest.raises(ValueError) as excinfo:
        extract_uuid_from_response(simple_error)
        
    assert "Error in response" in str(excinfo.value)

def test_clean_metadata():
    """Test that clean_metadata works as expected."""
    # Test with None
    assert clean_metadata(None) == {"body": "No content provided"}
    
    # Test with empty dict
    assert clean_metadata({}) == {"body": "No content provided"}
    
    # Test with valid metadata but without body
    metadata = {"key": "value", "numeric": 123}
    result = clean_metadata(metadata)
    assert result["body"] == "No content provided"
    assert result["key"] == "value"
    assert result["numeric"] == 123
    
    # Test with existing body field
    metadata_with_body = {"key": "value", "body": "This is body content"}
    result = clean_metadata(metadata_with_body)
    assert result["body"] == "This is body content"
    assert result is not metadata_with_body  # Should be a copy

def test_validate_uuid():
    """Test UUID validation."""
    # Valid UUID
    assert validate_uuid(str(uuid.uuid4())) is True
    
    # Invalid UUIDs
    assert validate_uuid("not-a-uuid") is False
    assert validate_uuid("123e4567-e89b-12d3-a456-INVALIDUUID") is False
    assert validate_uuid("") is False 