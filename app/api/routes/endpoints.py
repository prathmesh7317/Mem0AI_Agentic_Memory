"""
API Endpoints - All routes in one file
Handles chat, memory management, and health check endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import (
    ChatRequest, 
    ChatResponse,
    ClearMemoryRequest, 
    ClearSessionRequest,
    DomainCatalogRequest,
    DeleteDomainRequest,
    GetMemoriesRequest,
    GetUserDomainsRequest,
    MemoriesResponse,
    ClearResponse,
    ErrorResponse,
    DomainCatalogResponse,
    UserDomainsResponse
)
from app.services import MemoryService
from app.utils.catalog_loader import catalog_manager
from app.constants import HTTPStatus, ErrorMessage, SuccessMessage

# router = APIRouter()

# # Create memory service once at module level
# memory_service = MemoryService()

router = APIRouter()

# Memory service instance (lazy-initialized to avoid blocking on import)
_memory_service = None

def get_memory_service() -> MemoryService:
    """
    Lazy-initialize and return the MemoryService singleton.
    Only creates the service when first requested, not at import time.
    This prevents blocking the FastAPI startup event.
    """
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service

# CHAT ENDPOINTS

@router.post(
    "/chat", 
    response_model=ChatResponse, 
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Chat"]
)
async def chat_endpoint(chat_request: ChatRequest):
    """
    Handle chat messages with memory-enhanced context and optional domain catalog.
    
    This endpoint:
    1. Receives user message (with optional domain context)
    2. Retrieves relevant memories (LTM from Neo4j + STM from Redis)
    3. Generates AI response using OpenAI (with domain catalog if provided)
    4. Stores conversation in memory (background process)
    
    Args:
        chat_request (ChatRequest): Chat request with message, user_id, session_id, and optional domain_name
        
    Returns:
        ChatResponse: AI response with user_id and session_id
        
    Raises:
        HTTPException: If message is empty or processing fails
    """
    try:
        # Validate message is not empty
        if not chat_request.message or not chat_request.message.strip():
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorMessage.MESSAGE_EMPTY.value
            )

        # Get response from memory service (async - non-blocking)
        # Pass domain_name to enable domain catalog context if provided
        response = await get_memory_service().chat(
            chat_request.message, 
            chat_request.user_id, 
            chat_request.session_id,
            chat_request.domain_name
        )

        # Return structured response
        return ChatResponse(
            response=response,
            user_id=chat_request.user_id,
            session_id=chat_request.session_id
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_ERROR.value.format(error=str(e))
        )
        
# MEMORY MANAGEMENT ENDPOINTS

@router.get(
    "/memories", 
    response_model=MemoriesResponse,
    responses={500: {"model": ErrorResponse}},
    tags=["Memory Management"]
)
async def get_memories(request: GetMemoriesRequest = Depends()):
    """
    Get all stored long-term memories (LTM) for a user
    
    Retrieves memories stored in Mem0 (backed by Neo4j graph database)
    
    Args:
        request (GetMemoriesRequest): Request with user_id
        
    Returns:
        MemoriesResponse: List of memories and count
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Fetch all memories for the user (async - non-blocking)
        memories = await get_memory_service().get_all_memories(request.user_id)

        # Return memories with count
        return MemoriesResponse(
            memories=memories,
            count=len(memories)
        )

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_ERROR.value.format(error=str(e))
        )


@router.post(
    "/memories/clear", 
    response_model=ClearResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Memory Management"]
)
async def clear_memories(clear_request: ClearMemoryRequest):
    """
    Clear all long-term memories (LTM) for a user
    
    This deletes all memories stored in Mem0/Neo4j for the given user.
    Use with caution - this action cannot be undone!
    
    Args:
        clear_request (ClearMemoryRequest): Request with user_id
        
    Returns:
        ClearResponse: Success status and count of deleted memories
        
    Raises:
        HTTPException: If clearing fails
    """
    try:
        # Delete all memories for the user (async - non-blocking)
        result = await get_memory_service().delete_all_memories(clear_request.user_id)

        # Return result
        return ClearResponse(
            success=result.get('success', False),
            deleted_count=result.get('deleted_count', 0)
        )

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.MEMORY_CLEAR_FAILED.value.format(error=str(e))
        )


@router.post(
    "/session/clear", 
    response_model=ClearResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Session Management"]
)
async def clear_session(clear_request: ClearSessionRequest):
    """
    Clear session history (STM) from Redis for a specific session
    
    This removes conversation history stored in Redis for the given session.
    Does NOT delete long-term memories stored in Mem0/Neo4j.
    
    Args:
        clear_request (ClearSessionRequest): Request with session_id
        
    Returns:
        ClearResponse: Success status and message
        
    Raises:
        HTTPException: If clearing fails
    """
    try:
        # Clear session history from Redis
        result = get_memory_service().clear_session_history(clear_request.session_id)

        # Return result
        return ClearResponse(
            success=result.get('success', False),
            message=result.get('message', '')
        )

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.SESSION_CLEAR_FAILED.value.format(error=str(e))
        )


# DOMAIN CATALOG ENDPOINTS

@router.get(
    "/domain/user",
    response_model=UserDomainsResponse,
    responses={500: {"model": ErrorResponse}},
    tags=["Domain Catalog"]
)
async def get_user_domains(request: GetUserDomainsRequest = Depends()):
    """
    Get all domain names that a user has added.
    
    This endpoint retrieves the list of domain names (not catalog content) 
    that a specific user has registered.
    
    Args:
        request (GetUserDomainsRequest): Request with user_id
        
    Returns:
        UserDomainsResponse: User ID and list of domain names
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Get user domain names using catalog manager
        user_domains = catalog_manager.get_user_domain_names(request.user_id)

        # Return the list of domain names
        return UserDomainsResponse(
            user_id=request.user_id,
            domains=user_domains
        )

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_ERROR.value.format(error=str(e))
        )


@router.post(
    "/domain/catalog",
    response_model=DomainCatalogResponse,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Domain Catalog"]
)
async def add_domain_catalog(domain_request: DomainCatalogRequest):
    """
    Add a new domain name and its catalog/description to JSON storage.
    
    This endpoint only adds new domains. If the domain already exists, 
    it returns a 409 Conflict error. Use PUT endpoint to update existing domains.
    
    Args:
        domain_request (DomainCatalogRequest): Request with user_id, domain_name, and domain_catalog
        
    Returns:
        DomainCatalogResponse: Success status and domain information
        
    Raises:
        HTTPException: If domain_name or domain_catalog is empty, domain already exists, or processing fails
    """
    try:
        # Validate that domain name is not empty
        if not domain_request.domain_name or not domain_request.domain_name.strip():
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorMessage.DOMAIN_NAME_EMPTY.value
            )

        # Validate that domain catalog is not empty
        if not domain_request.domain_catalog or not domain_request.domain_catalog.strip():
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorMessage.DOMAIN_CATALOG_EMPTY.value
            )

        # Clean input values
        user_id = domain_request.user_id.strip()
        domain_name = domain_request.domain_name.strip()
        domain_catalog = domain_request.domain_catalog.strip()

        # Use catalog manager to add domain (raises ValueError if exists)
        result = catalog_manager.add_domain(user_id, domain_name, domain_catalog)

        # Return success response
        return DomainCatalogResponse(
            success=result["success"],
            domain_name=result["domain_name"],
            message=f"{result['message']} for user_id '{user_id}'"
        )

    except ValueError as ve:
        # Domain already exists - return 409 Conflict
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(ve)
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        # Catch any other errors and return 500
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_ERROR.value.format(error=str(e))
        )


@router.put(
    "/domain/catalog",
    response_model=DomainCatalogResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Domain Catalog"]
)
async def update_domain_catalog(domain_request: DomainCatalogRequest):
    """
    Update an existing domain catalog for a user.
    
    This endpoint updates the catalog description for an existing domain.
    If the domain doesn't exist, it returns a 404 error.
    The domain name is normalized (lowercase, trimmed) before updating.
    
    Args:
        domain_request (DomainCatalogRequest): Request with user_id, domain_name, and new domain_catalog
        
    Returns:
        DomainCatalogResponse: Success status and update confirmation message
        
    Raises:
        HTTPException: If domain_name or domain_catalog is empty, domain not found, or update fails
    """
    try:
        # Validate that domain name is not empty
        if not domain_request.domain_name or not domain_request.domain_name.strip():
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorMessage.DOMAIN_NAME_EMPTY.value
            )

        # Validate that domain catalog is not empty
        if not domain_request.domain_catalog or not domain_request.domain_catalog.strip():
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorMessage.DOMAIN_CATALOG_EMPTY.value
            )

        # Clean input values
        user_id = domain_request.user_id.strip()
        domain_name = domain_request.domain_name.strip()
        domain_catalog = domain_request.domain_catalog.strip()

        # Use catalog manager to update domain (raises ValueError if not found)
        result = catalog_manager.update_domain(user_id, domain_name, domain_catalog)

        # Return success response
        return DomainCatalogResponse(
            success=result["success"],
            domain_name=result["domain_name"],
            message=f"{result['message']} for user_id '{user_id}'"
        )

    except ValueError as ve:
        # Domain not found - return 404
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=str(ve)
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        # Catch any other errors and return 500
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_ERROR.value.format(error=str(e))
        )


@router.delete(
    "/domain/catalog",
    response_model=DomainCatalogResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Domain Catalog"]
)
async def delete_domain_catalog(delete_request: DeleteDomainRequest):
    """
    Delete a domain catalog for a specific user.
    
    This endpoint removes a domain and its catalog from the user's storage.
    The domain name is normalized (lowercase, trimmed) before deletion.
    
    Args:
        delete_request (DeleteDomainRequest): Request with user_id and domain_name
        
    Returns:
        DomainCatalogResponse: Success status and deletion confirmation message
        
    Raises:
        HTTPException: If user_id or domain_name is empty, domain not found, or deletion fails
    """
    try:
        # Validate that domain_name is not empty
        if not delete_request.domain_name or not delete_request.domain_name.strip():
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorMessage.DOMAIN_NAME_EMPTY.value
            )

        # Clean inputs
        clean_user_id = delete_request.user_id.strip()
        clean_domain_name = delete_request.domain_name.strip()

        # Use catalog manager to delete domain (raises ValueError if not found)
        result = catalog_manager.delete_domain(clean_user_id, clean_domain_name)

        # Return success response
        return DomainCatalogResponse(
            success=result["success"],
            domain_name=result["domain_name"],
            message=f"{result['message']} for user_id '{clean_user_id}'"
        )

    except ValueError as ve:
        # Domain not found - return 404
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=str(ve)
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        # Catch any other errors and return 500
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessage.INTERNAL_ERROR.value.format(error=str(e))
        )


# SYSTEM ENDPOINTS

@router.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint to verify server is running
    
    Returns:
        dict: Status and service information
    """
    return {
        "status": "healthy",
        "service": "Mem0 Chatbot API",
        "version": "1.0.0"
    }

