"""
Models Package - Pydantic Request and Response Models
"""

from .requests import (
    ChatRequest,
    ClearMemoryRequest,
    ClearSessionRequest,
    DomainCatalogRequest,
    DeleteDomainRequest,
    GetMemoriesRequest,
    GetUserDomainsRequest
)
from .responses import ChatResponse, MemoriesResponse, ClearResponse, ErrorResponse, DomainCatalogResponse, UserDomainsResponse

__all__ = [
    # Request models
    "ChatRequest",
    "ClearMemoryRequest",
    "ClearSessionRequest",
    "DomainCatalogRequest",
    "DeleteDomainRequest",
    "GetMemoriesRequest",
    "GetUserDomainsRequest",
    # Response models
    "ChatResponse",
    "MemoriesResponse",
    "ClearResponse",
    "ErrorResponse",
    "DomainCatalogResponse",
    "UserDomainsResponse"
]

