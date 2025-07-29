"""Data models for Vector Store Client."""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class JsonRpcRequest(BaseModel):
    """Base model for JSON-RPC requests."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    method: str = Field(..., description="Method name to call")
    params: Dict = Field(default_factory=dict, description="Method parameters")
    id: Optional[Union[str, int]] = Field(default=None, description="Request identifier")

class JsonRpcError(BaseModel):
    """JSON-RPC error object."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Dict] = Field(default=None, description="Additional error data")

class JsonRpcResponse(BaseModel):
    """Base model for JSON-RPC responses."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    result: Optional[Union[Dict, List, str, bool, Any]] = Field(default=None, description="Method execution result")
    error: Optional[JsonRpcError] = Field(default=None, description="Error information")
    id: Optional[Union[str, int]] = Field(default=None, description="Request identifier")

class VectorRecord(BaseModel):
    """Model for vector records."""
    id: UUID = Field(..., description="Unique record identifier")
    vector: Optional[List[float]] = Field(default=None, description="Vector data")
    metadata: Dict = Field(default_factory=dict, description="Record metadata")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    text: Optional[str] = Field(default=None, description="Original text if created from text")
    model: Optional[str] = Field(default=None, description="Model used for vectorization")
    session_id: Optional[UUID] = Field(default=None, description="Session identifier")
    message_id: Optional[UUID] = Field(default=None, description="Message identifier")

class SearchResult(BaseModel):
    """Model for search results."""
    id: UUID = Field(..., description="Record identifier")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    vector: Optional[List[float]] = Field(default=None, description="Vector data if requested")
    metadata: Optional[Dict] = Field(default=None, description="Record metadata if requested")
    text: Optional[str] = Field(default=None, description="Original text if available")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str = Field(..., description="Status of service (ok/error)")
    model: str = Field(..., description="Current active model")
    version: str = Field(..., description="Service version")

class CommandSchema(BaseModel):
    """Model for command schema."""
    name: str = Field(..., description="Command name")
    description: str = Field(..., description="Command description")
    params: Dict[str, Dict] = Field(default_factory=dict, description="Parameters schema")

# Parameter models from OpenAPI schema
class ConfigParams(BaseModel):
    """Parameters for config command."""
    operation: str = Field(default="get", description="Operation to perform (get or set)")
    path: Optional[str] = Field(default=None, description="Configuration path in dot notation")
    value: Optional[Any] = Field(default=None, description="Value to set (required for 'set' operation)")

class HelpParams(BaseModel):
    """Parameters for help command."""
    cmdname: Optional[str] = Field(default=None, description="Name of command to get information about")

class GetMetadataParams(BaseModel):
    """Parameters for get_metadata command."""
    record_id: str = Field(..., description="UUID of the record")

class GetTextParams(BaseModel):
    """Parameters for get_text command."""
    record_id: str = Field(..., description="UUID of the record")

class CreateTextRecordParams(BaseModel):
    """Parameters for create_text_record command."""
    text: str = Field(..., description="Text content to store")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional additional metadata")
    session_id: Optional[str] = Field(default=None, description="Optional session UUID")
    message_id: Optional[str] = Field(default=None, description="Optional message UUID")
    model: Optional[str] = Field(default=None, description="Optional embedding model to use")
    timestamp: Optional[str] = Field(default=None, description="Optional ISO 8601 timestamp")

class CreateRecordParams(BaseModel):
    """Parameters for create_record command."""
    vector: List[float] = Field(..., description="Pre-computed embedding vector")
    metadata: Dict[str, Any] = Field(..., description="Metadata to store with record")
    session_id: Optional[str] = Field(default=None, description="UUID of session")
    message_id: Optional[str] = Field(default=None, description="UUID of message")
    timestamp: Optional[str] = Field(default=None, description="ISO 8601 timestamp")

class DeleteParams(BaseModel):
    """Parameters for delete command."""
    filter: Optional[Dict[str, Any]] = Field(default=None, description="Filter criteria for bulk deletion")
    record_id: Optional[str] = Field(default=None, description="Single record ID to delete")
    record_ids: Optional[List[str]] = Field(default=None, description="List of record IDs to delete")
    max_records: int = Field(default=100, description="Maximum records to delete (safety limit)")
    confirm: bool = Field(default=False, description="Confirmation for bulk deletion")

class SearchRecordsParams(BaseModel):
    """Parameters for search_records command."""
    vector: List[float] = Field(..., description="Query vector for similarity search")
    limit: Optional[int] = Field(default=10, description="Maximum number of results to return")
    include_vectors: Optional[bool] = Field(default=False, description="Whether to include vectors in results")
    include_metadata: Optional[bool] = Field(default=True, description="Whether to include metadata in results")
    filter_criteria: Optional[Dict[str, Any]] = Field(default=None, description="Metadata criteria for filtering")

class SearchByVectorParams(BaseModel):
    """Parameters for search_by_vector command."""
    vector: List[float] = Field(..., description="Query vector for similarity search")
    limit: Optional[int] = Field(default=10, description="Maximum number of results to return")
    include_vectors: Optional[bool] = Field(default=False, description="Whether to include vectors in results")
    include_metadata: Optional[bool] = Field(default=True, description="Whether to include metadata in results")

class SearchTextRecordsParams(BaseModel):
    """Parameters for search_text_records command."""
    text: str = Field(..., description="Text query to search for")
    limit: Optional[int] = Field(default=10, description="Maximum number of results")
    model: Optional[str] = Field(default=None, description="Optional embedding model to use")
    include_vectors: Optional[bool] = Field(default=False, description="Whether to include vectors")
    include_metadata: Optional[bool] = Field(default=True, description="Whether to include metadata")
    filter_criteria: Optional[Dict[str, Any]] = Field(default=None, description="Legacy metadata filter")
    metadata_filter: Optional[Dict[str, Any]] = Field(default=None, description="Metadata criteria to filter results")

class FilterRecordsParams(BaseModel):
    """Parameters for filter_records command."""
    metadata_filter: Dict[str, Any] = Field(..., description="Metadata criteria for filtering")
    limit: Optional[int] = Field(default=100, description="Maximum number of results")
    include_vectors: Optional[bool] = Field(default=False, description="Whether to include vectors")
    include_metadata: Optional[bool] = Field(default=True, description="Whether to include metadata") 