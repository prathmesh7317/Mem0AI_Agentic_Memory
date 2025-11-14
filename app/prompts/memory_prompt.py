"""
System prompts for the chatbot
Handles base prompt and domain-specific context injection
"""

from typing import Optional
from app.utils.catalog_loader import get_all_user_catalogs
from app.core.logger.logger_config import setup_logger

logger = setup_logger(__name__)

# Base system prompt without domain context (core instructions only)
BASE_SYSTEM_PROMPT = """You are a helpful, intelligent, and conversational AI assistant with memory capabilities.

## CONTEXT FROM PREVIOUS CONVERSATIONS
{context}

## INSTRUCTIONS FOR RESPONSE
1. Review the context above carefully before responding
2. Use information from previous conversations to personalize your response
3. Reference past interactions naturally when relevant to the current question
4. Maintain a consistent and continuous conversation experience
5. Be accurate, helpful, and professional in your responses
6. Keep your answers tone clear, concise, and well-structured like Claude/Cursor AI
7. If the context doesn't contain relevant information, respond based on the current message
8. Acknowledge when you reference information from past conversations
9. For important words, numbers, or phrases, use double asterisks to bold them.
"""



def get_system_prompt(user_id: str, domain_name: Optional[str] = None) -> str:
    """
    Get system prompt, enhanced with ALL domain catalogs if user has any.
    
    Always checks if user has catalogs stored. If yes, includes ALL their catalogs
    in the prompt. If no, returns base prompt only. The domain_name parameter is
    ignored - all catalogs are always included.
    
    Args:
        user_id (str): User ID to get catalogs for
        domain_name (Optional[str]): Ignored - kept for backward compatibility
    
    Returns:
        str: System prompt (base prompt + all user catalogs, or just base prompt)
    
    Example:
        # User has no catalogs
        prompt = get_system_prompt("user_123")
        # Returns: Base prompt only
        
        # User has travel + healthcare catalogs
        prompt = get_system_prompt("user_123")
        # Returns: Base prompt + "\n\nDOMAIN CATALOGS:\n<all catalogs>"
    """
    # Start with base prompt
    system_prompt = BASE_SYSTEM_PROMPT
    
    # Always check if user has ANY catalogs
    all_catalogs = get_all_user_catalogs(user_id)
    
    # If user has catalogs, append ALL of them to the prompt
    if all_catalogs:
        system_prompt += f"""

## DOMAIN CATALOGS
This section provides domain-specific catalogs about the user's industry/field.

{all_catalogs}

## IMPORTANT RULES:
- Only use domain catalogs when the user explicitly asks questions about topics covered in them 
- Do not force domain content into casual conversations or when users are simply sharing personal information
- When the user asks questions related to these domain catalogs, you must use information from the domain catalogs above
- If the question is about topics covered in the domain catalogs, base your answer entirely on the domain catalog information
- Only use general knowledge if the domain catalogs don't contain relevant information
- keep your responses concise and to the point, clear
"""
    
    # Add the standard message and response sections
    system_prompt += """

## CURRENT USER MESSAGE
{message}

## RESPONSE
Provide a helpful, concise and contextually aware response below:
"""

    return system_prompt

