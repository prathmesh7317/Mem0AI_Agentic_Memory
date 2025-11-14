"""
Response Models for FastAPI Endpoints
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint
    
    Attributes:
        response (str): AI-generated response
        user_id (str): User identifier
        session_id (str): Session identifier
    """
    response: str = Field(..., description="AI-generated response")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")


class MemoriesResponse(BaseModel):
    """
    Response model for get memories endpoint
    
    Attributes:
        memories (List[Dict]): List of stored memories
        count (int): Total number of memories
    """
    memories: List[Dict[str, Any]] = Field(..., description="List of stored memories")
    count: int = Field(..., description="Total number of memories")


class ClearResponse(BaseModel):
    """
    Response model for clear operations
    
    Attributes:
        success (bool): Whether operation was successful
        deleted_count (Optional[int]): Number of items deleted (for memory clear)
        message (Optional[str]): Status message (for session clear)
    """
    success: bool = Field(..., description="Operation success status")
    deleted_count: Optional[int] = Field(None, description="Number of deleted memories")
    message: Optional[str] = Field(None, description="Status message")


class ErrorResponse(BaseModel):
    """
    Response model for error responses
    
    Attributes:
        error (str): Error message
    """
    error: str = Field(..., description="Error message")


class DomainCatalogResponse(BaseModel):
    """
    Response model for domain catalog endpoint
    
    Attributes:
        success (bool): Whether operation was successful
        domain_name (str): Name of the domain that was added
        message (str): Status message
    """
    success: bool = Field(..., description="Operation success status")
    domain_name: str = Field(..., description="Name of the domain")
    message: str = Field(..., description="Status message")


class UserDomainsResponse(BaseModel):
    """
    Response model for getting user's domains
    
    Attributes:
        user_id (str): User identifier
        domains (List[str]): List of domain names the user has added
    """
    user_id: str = Field(..., description="User identifier")
    domains: List[str] = Field(..., description="List of domain names")