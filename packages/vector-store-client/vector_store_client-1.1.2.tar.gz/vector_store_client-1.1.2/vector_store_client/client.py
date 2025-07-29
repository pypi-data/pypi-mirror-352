"""Vector Store Client implementation.

This module provides the main client class for interacting with the Vector Store API.
"""

import logging
from typing import Dict, List, Optional, Union, Any
from uuid import UUID
import datetime
import json

from .models import (
    SearchResult, 
    ConfigParams,
    CreateRecordParams,
    CreateTextRecordParams,
    DeleteParams,
    FilterRecordsParams,
    GetMetadataParams,
    GetTextParams,
    SearchByVectorParams,
    SearchRecordsParams,
    SearchTextRecordsParams,
    HealthResponse
)
from .exceptions import (
    ValidationError,
    JsonRpcException,
    ResourceNotFoundError,
    AuthenticationError,
    DuplicateError,
    RateLimitError,
    ServerError,
    BadResponseError
)
from .base_client import BaseVectorStoreClient
from .utils import extract_uuid_from_response, clean_metadata
from .validation import (
    validate_session_id, 
    validate_message_id, 
    validate_timestamp,
    validate_create_record_params,
    validate_limit,
    validate_server_response
)

logger = logging.getLogger(__name__)

class VectorStoreClient(BaseVectorStoreClient):
    """Client for interacting with Vector Store API."""

    def extract_from_nested_result(self, obj: dict, key: str):
        """Recursively extract a value by key from nested dicts (result/data)."""
        if not isinstance(obj, dict):
            return None
        if key in obj:
            return obj[key]
        for nested_key in ("result", "data"):
            if nested_key in obj and isinstance(obj[nested_key], dict):
                found = self.extract_from_nested_result(obj[nested_key], key)
                if found is not None:
                    return found
        return None

    async def create_record(
        self,
        vector: List[float],
        metadata: Dict,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        raw_response: bool = False,
    ) -> Dict:
        """Creates a new record with vector and metadata.
        
        Args:
            vector: Vector data as list of floats (must be 384-dim)
            metadata: Metadata dictionary (must contain 'body' field)
            session_id: Optional session ID (UUID)
            message_id: Optional message ID (UUID)
            timestamp: Optional timestamp (ISO 8601 format)
            raw_response: If True, return full server response (dict), else return dict with record_id (default: False)
        
        Returns:
            Dict with record_id (default) or full server response (dict) if raw_response=True
        
        Raises:
            ValidationError: If parameters are invalid (unless raw_response=True)
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        # Validate vector dimension
        if not isinstance(vector, list) or len(vector) != 384:
            raise ValidationError(f"Vector must be a list of 384 floats, got {len(vector) if isinstance(vector, list) else type(vector)}")
        # Validate metadata
        if not isinstance(metadata, dict):
            raise ValidationError("Metadata must be a dictionary")
        metadata_copy = clean_metadata(metadata.copy() if metadata else {})
        if 'body' not in metadata_copy or not metadata_copy['body']:
            metadata_copy['body'] = metadata_copy.get('text', "Vector record created with no text content")
        params = CreateRecordParams(
            vector=vector,
            metadata=metadata_copy,
        ).model_dump(exclude_none=True)
        validate_session_id(session_id, params)
        validate_message_id(message_id, params)
        validate_timestamp(timestamp, params)
        try:
            response = await self._make_request(
                "create_record",
                params
            )
            result = response.get("result", {})
            if isinstance(result, dict) and result.get("success") is False:
                if raw_response:
                    return response
                error = result.get("error", {})
                error_msg = error.get("message", str(error))
                error_code = error.get("code", -1)
                raise JsonRpcException(message=error_msg, code=error_code, data=error.get("data"), error=error)
            validate_server_response(response, expected="record_id")
            logger.debug(f"Raw create_record response: {response!r}")
            record_id = self.extract_from_nested_result(result, "record_id")
            return {"record_id": record_id}
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if e.code == 409:
                raise DuplicateError(f"Record with these parameters already exists: {e.message}")
            if e.code in (-32602, -32600):
                raise ValidationError(f"Invalid parameters: {e.message}")
            raise

    async def create_text_record(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        model: Optional[str] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        raw_response: bool = False,
    ) -> Dict:
        """Creates a new record from text with automatic vectorization.
        
        Args:
            text: Text to vectorize
            metadata: Optional metadata dictionary (must contain 'body' field)
            model: Optional model name for vectorization
            session_id: Optional session ID (UUID)
            message_id: Optional message ID (UUID)
            timestamp: Optional timestamp (ISO 8601 format)
            raw_response: If True, return full server response (dict), else return dict with record_id (default: False)
        
        Returns:
            Dict with record_id (default) or full server response (dict) if raw_response=True
        
        Raises:
            ValidationError: If parameters are invalid (unless raw_response=True)
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        if not isinstance(text, str) or not text:
            raise ValidationError("Text must be a non-empty string")
        metadata_copy = clean_metadata(metadata or {})
        if "body" not in metadata_copy or not metadata_copy["body"]:
            metadata_copy["body"] = text
        params = CreateTextRecordParams(
            text=text,
            metadata=metadata_copy,
        ).model_dump(exclude_none=True)
        if model:
            params["model"] = model
        validate_session_id(session_id, params)
        validate_message_id(message_id, params)
        validate_timestamp(timestamp, params)
        try:
            response = await self._make_request(
                "create_text_record",
                params
            )
            result = response.get("result", {})
            if isinstance(result, dict) and result.get("success") is False:
                if raw_response:
                    return response
                error = result.get("error", {})
                error_msg = error.get("message", str(error))
                error_code = error.get("code", -1)
                raise JsonRpcException(message=error_msg, code=error_code, data=error.get("data"), error=error)
            validate_server_response(response, expected="record_id")
            logger.debug(f"Raw create_text_record response: {response!r}")
            record_id = self.extract_from_nested_result(result, "record_id")
            return {"record_id": record_id}
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if e.code == 409:
                raise DuplicateError(f"Record with this text already exists: {e.message}")
            if e.code in (-32602, -32600):
                raise ValidationError(f"Invalid parameters: {e.message}")
            raise

    async def search_by_vector(
        self,
        vector: List[float],
        limit: int = 10,
        include_vectors: bool = False,
        include_metadata: bool = True,
        raw_response: bool = False,
    ) -> Union[List[SearchResult], Dict]:
        """Search for records by vector similarity.
        
        Args:
            vector: Vector to search with (must be 384-dim)
            limit: Maximum number of results to return
            include_vectors: Whether to include vectors in results
            include_metadata: Whether to include metadata in results
            raw_response: If True, return full server response (dict), else return list of SearchResult (default: False)
        
        Returns:
            List of search results (default) or full server response (dict) if raw_response=True
        
        Raises:
            ValidationError: If parameters are invalid (unless raw_response=True)
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        if not isinstance(vector, list) or len(vector) != 384:
            raise ValidationError(f"Vector must be a list of 384 floats, got {len(vector) if isinstance(vector, list) else type(vector)}")
        params = SearchByVectorParams(
            vector=vector,
            limit=validate_limit(limit),
            include_vectors=include_vectors,
            include_metadata=include_metadata,
        ).model_dump(exclude_none=True)
        try:
            response = await self._make_request(
                "search_by_vector",
                params
            )
            validate_server_response(response, expected="records")
            if raw_response:
                return response
            return self._process_search_results(response)
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if "dimension mismatch" in e.message.lower():
                raise ValidationError(f"Vector dimension mismatch: {e.message}")
            raise

    async def search_text_records(
        self,
        text: str,
        limit: int = 10,
        model: Optional[str] = None,
        include_vectors: bool = False,
        include_metadata: bool = True,
        metadata_filter: Optional[Dict] = None,
        raw_response: bool = False,
    ) -> Union[List[SearchResult], Dict]:
        """Search for records by text similarity.
        
        Args:
            text: Query text
            limit: Maximum number of results
            model: Optional embedding model
            include_vectors: Whether to include vectors in results
            include_metadata: Whether to include metadata in results
            metadata_filter: Optional metadata filter
            raw_response: If True, return full server response (dict), else return list of SearchResult (default: False)
        
        Returns:
            List of search results (default) or full server response (dict) if raw_response=True
        
        Raises:
            ValidationError: If parameters are invalid (unless raw_response=True)
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        if not isinstance(text, str) or not text:
            raise ValidationError("Text must be a non-empty string")
        params = SearchTextRecordsParams(
            text=text,
            limit=validate_limit(limit),
            model=model,
            include_vectors=include_vectors,
            include_metadata=include_metadata,
            metadata_filter=metadata_filter,
        ).model_dump(exclude_none=True)
        try:
            response = await self._make_request(
                "search_text_records",
                params
            )
            validate_server_response(response, expected="records")
            if raw_response:
                return response
            return self._process_search_results(response)
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            raise

    async def search_by_text(self, *args, **kwargs):
        """Alias for search_text_records (for compatibility and coverage)."""
        return await self.search_text_records(*args, **kwargs)

    async def filter_records(
        self,
        metadata_filter: Dict,
        limit: int = 100,
        include_vectors: bool = False,
        include_metadata: bool = True,
        raw_response: bool = False,
    ) -> Union[List[SearchResult], Dict]:
        """Filter records by metadata criteria.
        
        Args:
            metadata_filter: Filter criteria for metadata
            limit: Maximum number of results (1-1000)
            include_vectors: Whether to include vectors in results
            include_metadata: Whether to include metadata in results
            raw_response: If True, return full server response (dict), else return list of SearchResult (default: False)
        
        Returns:
            List of filtered results (default) or full server response (dict) if raw_response=True
        
        Raises:
            ValidationError: If parameters are invalid (unless raw_response=True)
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        if not isinstance(metadata_filter, dict):
            raise ValidationError("metadata_filter must be a dictionary")
        params = FilterRecordsParams(
            metadata_filter=metadata_filter,
            limit=validate_limit(limit, max_value=1000),
            include_vectors=include_vectors,
            include_metadata=include_metadata
        ).model_dump(exclude_none=True)
        logger.debug(f"filter_records request params: {params}")
        try:
            response = await self._make_request(
                "filter_records",
                params
            )
            validate_server_response(response, expected="records")
            if raw_response:
                return response
            return self._process_search_results(response)
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if e.code in (-32602, -32600):
                raise ValidationError(f"Invalid parameters: {e.message}")
            raise

    async def get_metadata(self, record_id: str, raw_response: bool = False) -> Union[Dict, Dict]:
        """Get metadata for a record by ID.
        
        Args:
            record_id: Record ID (UUID)
            raw_response: If True, return full server response (dict), else return metadata dict (default: False)
        
        Returns:
            Metadata dictionary (default) or full server response (dict) if raw_response=True
        
        Raises:
            ValidationError: If record_id is invalid (unless raw_response=True)
            ResourceNotFoundError: If record not found (unless raw_response=True)
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        if not isinstance(record_id, str) or not record_id:
            raise ValidationError("record_id must be a non-empty string")
        params = GetMetadataParams(record_id=record_id).model_dump(exclude_none=True)
        try:
            response = await self._make_request("get_metadata", params)
            validate_server_response(response, expected="metadata")
            if raw_response:
                return response
            metadata = self.extract_from_nested_result(response["result"], "metadata")
            return metadata
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if e.code == 404:
                raise ResourceNotFoundError(f"Record not found: {record_id}")
            raise

    async def get_text(self, record_id: str, raw_response: bool = False) -> Union[str, Dict]:
        """Get text for a record by ID.
        
        Args:
            record_id: Record ID (UUID)
            raw_response: If True, return full server response (dict), else return text (default: False)
        
        Returns:
            Text string (default) or full server response (dict) if raw_response=True
        
        Raises:
            ValidationError: If record_id is invalid (unless raw_response=True)
            ResourceNotFoundError: If record not found (unless raw_response=True)
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        if not isinstance(record_id, str) or not record_id:
            raise ValidationError("record_id must be a non-empty string")
        params = GetTextParams(record_id=record_id).model_dump(exclude_none=True)
        try:
            response = await self._make_request("get_text", params)
            validate_server_response(response, expected="text")
            if raw_response:
                return response
            text = self.extract_from_nested_result(response["result"], "text")
            return text
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if e.code == 404:
                raise ResourceNotFoundError(f"Record not found: {record_id}")
            raise

    async def delete(
        self,
        record_id: Optional[str] = None,
        record_ids: Optional[List[str]] = None,
        filter: Optional[Dict] = None,
        max_records: int = 100,
        confirm: bool = False,
        raw_response: bool = False,
    ) -> Union[bool, Dict]:
        """Delete records by ID, list of IDs, or filter.
        
        Args:
            record_id: Single record ID to delete
            record_ids: List of record IDs to delete
            filter: Metadata filter for bulk delete
            max_records: Max records to delete (with filter)
            confirm: Must be True for bulk delete
            raw_response: If True, return full server response (dict), else return bool (default: False)
        
        Returns:
            True if delete succeeded (default) or full server response (dict) if raw_response=True
        
        Raises:
            ValidationError: If parameters are invalid (unless raw_response=True)
            ResourceNotFoundError: If record not found (unless raw_response=True)
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        params = {}
        # Усиленная валидация: только один из record_id, record_ids, filter
        specified = [x is not None for x in (record_id, record_ids, filter)]
        if sum(specified) != 1:
            raise ValidationError("Must specify exactly one of record_id, record_ids, or filter")
        if record_id:
            params["record_id"] = record_id
        elif record_ids:
            if not confirm and len(record_ids) > 1:
                raise ValidationError("Must set confirm=True when deleting multiple records")
            params["record_ids"] = record_ids
            params["confirm"] = confirm
        elif filter:
            if not confirm:
                raise ValidationError("Must set confirm=True when deleting by filter")
            params["filter"] = filter
            params["max_records"] = max_records
            params["confirm"] = confirm
        try:
            response = await self._make_request(
                "delete",
                params
            )
            validate_server_response(response, expected="success")
            if raw_response:
                return response
            return True
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if e.code == 404:
                raise ResourceNotFoundError(f"Record not found")
            if e.code in (-32602, -32600):
                raise ValidationError(f"Invalid parameters: {e.message}")
            raise

    async def search_records(
        self,
        vector: List[float],
        limit: int = 10,
        include_vectors: bool = False,
        include_metadata: bool = True,
        filter_criteria: Optional[Dict] = None,
        raw_response: bool = False,
    ) -> Union[List[SearchResult], Dict]:
        """Search for records by vector similarity with optional filtering.
        
        Args:
            vector: Query vector (must be 384-dim)
            limit: Maximum number of results
            include_vectors: Whether to include vectors in results
            include_metadata: Whether to include metadata in results
            filter_criteria: Optional metadata criteria to filter results
            raw_response: If True, return full server response (dict), else return list of SearchResult (default: False)
        
        Returns:
            List of search results (default) or full server response (dict) if raw_response=True
        
        Raises:
            ValidationError: If parameters are invalid (unless raw_response=True)
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        if not isinstance(vector, list) or len(vector) != 384:
            raise ValidationError(f"Vector must be a list of 384 floats, got {len(vector) if isinstance(vector, list) else type(vector)}")
        params = SearchRecordsParams(
            vector=vector,
            limit=validate_limit(limit),
            include_vectors=include_vectors,
            include_metadata=include_metadata
        ).model_dump(exclude_none=True)
        if filter_criteria:
            params["filter_criteria"] = filter_criteria
        try:
            response = await self._make_request(
                "search_records",
                params
            )
            validate_server_response(response, expected="records")
            if raw_response:
                return response
            return self._process_search_results(response)
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if e.code in (-32602, -32600):
                raise ValidationError(f"Invalid parameters: {e.message}")
            raise

    async def health(self, raw_response: bool = False) -> Union[Dict, Dict]:
        """Check service health.
        
        Args:
            raw_response: If True, return full server response (dict), else return health dict (default: False)
        
        Returns:
            Health dictionary (default) or full server response (dict) if raw_response=True
        
        Raises:
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        try:
            response = await self._make_request("health", {})
            validate_server_response(response, expected="status")
            if raw_response:
                return response
            return response["result"]
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if e.code == 500:
                raise ServerError(f"Health check failed: {e.message}")
            raise

    async def config(
        self,
        operation: str = "get",
        path: Optional[str] = None,
        value: Optional[Any] = None,
        raw_response: bool = False,
    ) -> Union[Any, Dict]:
        """Access or modify service configuration.
        
        Args:
            operation: Operation type (get/set)
            path: Configuration path (dot-separated)
            value: Optional value to set
            raw_response: If True, return full server response (dict), else return config value (default: False)
        
        Returns:
            Configuration value or status (default) or full server response (dict) if raw_response=True
        
        Raises:
            ValidationError: If parameters are invalid (unless raw_response=True)
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        params = ConfigParams(
            operation=operation
        ).model_dump(exclude_none=True)
        if path:
            params["path"] = path
        if value is not None:
            params["value"] = value
        try:
            response = await self._make_request("config", params)
            if operation == "set":
                validate_server_response(response, expected="success")
            else:
                validate_server_response(response, expected="result")
            if raw_response:
                return response
            return response["result"]
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if e.code in (-32602, -32600):
                raise ValidationError(f"Invalid configuration parameters: {e.message}")
            if e.code == 403:
                raise AuthenticationError("Not authorized to access configuration")
            raise

    async def help(self, cmdname: Optional[str] = None, raw_response: bool = False) -> Union[Dict, Dict]:
        """Get help information about API commands.
        
        Args:
            cmdname: Optional command name
            raw_response: If True, return full server response (dict), else return help dict (default: False)
        
        Returns:
            Help dictionary (default) or full server response (dict) if raw_response=True
        
        Raises:
            ConnectionError: If API is unreachable
            JsonRpcException: If API returns an error (unless raw_response=True)
        """
        params = {"cmdname": cmdname} if cmdname else {}
        try:
            response = await self._make_request("help", params)
            validate_server_response(response, expected="result")
            if raw_response:
                return response
            return response["result"]
        except JsonRpcException as e:
            if raw_response and hasattr(e, 'error'):
                return {"success": False, "error": getattr(e, 'error', str(e))}
            if e.code == 404 and cmdname:
                raise ResourceNotFoundError(f"Command '{cmdname}' not found")
            raise 