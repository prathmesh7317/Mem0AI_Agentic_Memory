"""
Request Models for FastAPI Endpoints
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request model for chat endpoint
    
    Attributes:
        message (str): User's input message
        user_id (str): Unique identifier for the user (default: 'default_user')
        session_id (str): Session identifier for conversation history
        domain_name (Optional[str]): Optional domain name for catalog context
    """
    message: str = Field(..., min_length=1, description="User's input message")
    user_id: str = Field(default="default_user", description="Unique user identifier")
    session_id: str = Field(..., description="Session ID for conversation tracking")
    domain_name: Optional[str] = Field(None, description="Optional domain name to load catalog context")


class ClearMemoryRequest(BaseModel):
    """
    Request model for clearing long-term memories (LTM)
    
    Attributes:
        user_id (str): Unique identifier for the user
    """
    user_id: str = Field(default="default_user", description="User ID whose memories to clear")


class ClearSessionRequest(BaseModel):
    """
    Request model for clearing session history (STM)
    
    Attributes:
        session_id (str): Session ID to clear from Redis
    """
    session_id: str = Field(..., description="Session ID to clear")


class DomainCatalogRequest(BaseModel):
    """
    Request model for adding/updating domain to catalog
    
    Attributes:
        user_id (str): User ID who owns this catalog
        domain_name (str): Name of the domain
        domain_catalog (str): Domain catalog/description
    """
    user_id: str = Field(default="default_user", description="User ID who owns this catalog")
    domain_name: str = Field(..., min_length=1, description="Name of the domain")
    domain_catalog: str = Field(..., min_length=1, description="Domain catalog or description")


class DeleteDomainRequest(BaseModel):
    """
    Request model for deleting domain from catalog
    
    Attributes:
        user_id (str): User ID who owns this catalog
        domain_name (str): Name of the domain to delete
    """
    user_id: str = Field(default="default_user", description="User ID who owns this catalog")
    domain_name: str = Field(..., min_length=1, description="Name of the domain to delete")


class GetMemoriesRequest(BaseModel):
    """
    Request model for retrieving memories
    
    Attributes:
        user_id (str): User ID to retrieve memories for
    """
    user_id: str = Field(default="default_user", description="User ID to retrieve memories for")


class GetUserDomainsRequest(BaseModel):
    """
    Request model for retrieving user domains
    
    Attributes:
        user_id (str): User ID to retrieve domains for
    """
    user_id: str = Field(default="default_user", description="User ID to retrieve domains for")

