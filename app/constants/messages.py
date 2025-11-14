"""
Error and Success Message Constants
Use these for all error details and success messages
"""

from enum import Enum


class ErrorMessage(Enum):
    """Centralized error messages organized by category, supports formatting with .format()"""

    # Domain Catalog Errors
    DOMAIN_NOT_FOUND = "Domain '{domain_name}' not found"
    DOMAIN_ALREADY_EXISTS = "Domain '{domain_name}' already exists. Use update to modify it."
    DOMAIN_NAME_EMPTY = "Domain name cannot be empty"
    DOMAIN_CATALOG_EMPTY = "Domain catalog cannot be empty"

    # User Errors
    USER_ID_EMPTY = "User ID cannot be empty"
    USER_NOT_FOUND = "User '{user_id}' not found"

    # Memory Errors
    MEMORY_NOT_FOUND = "Memory not found"
    MEMORY_CLEAR_FAILED = "Failed to clear memories: {error}"

    # Session Errors
    SESSION_NOT_FOUND = "Session '{session_id}' not found"
    SESSION_CLEAR_FAILED = "Failed to clear session: {error}"

    # Chat Errors
    MESSAGE_EMPTY = "Message cannot be empty"
    CHAT_PROCESSING_FAILED = "Failed to process chat: {error}"

    # Validation Errors
    INVALID_INPUT = "Invalid input: {error}"
    VALIDATION_FAILED = "Validation failed: {error}"

    # Generic Errors
    INTERNAL_ERROR = "Internal server error: {error}"
    OPERATION_FAILED = "Operation failed: {error}"

    # Memory Operations Errors
    MEMORY_RETRIEVAL_FAILED = "Failed to retrieve memories: {error}"
    MEMORY_STORAGE_FAILED = "Failed to store memory: {error}"
    MEMORY_DELETION_FAILED = "Failed to delete memories: {error}"
    MEMORY_SEARCH_FAILED = "Failed to search memories: {error}"

    # LLM/OpenAI Errors
    OPENAI_API_FAILED = "OpenAI API request failed: {error}"
    RESPONSE_GENERATION_FAILED = "Failed to generate response: {error}"

    # Redis Message History Errors
    MESSAGE_HISTORY_RETRIEVAL_FAILED = "Failed to retrieve message history: {error}"
    MESSAGE_HISTORY_STORAGE_FAILED = "Failed to store message history: {error}"


class SuccessMessage(Enum):
    """Success messages for operations, supports formatting with .format()"""

    # Domain Catalog Success
    DOMAIN_ADDED = "Domain '{domain_name}' successfully added"
    DOMAIN_UPDATED = "Domain '{domain_name}' successfully updated"
    DOMAIN_DELETED = "Domain '{domain_name}' successfully deleted"

    # Memory Success
    MEMORY_CLEARED = "Successfully cleared {count} memories"

    # Session Success
    SESSION_CLEARED = "Session '{session_id}' successfully cleared"

    # Generic Success
    OPERATION_SUCCESS = "Operation completed successfully"

