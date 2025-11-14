"""
Memory Service using Mem0 with Neo4j Graph Memory and Redis Vector Store

This module provides a chatbot service that leverages Mem0's memory capabilities
with Neo4j for graph-based memory storage and Redis for vector-based semantic search.

Uses AsyncMemory for non-blocking operations with FastAPI.
"""

import json
import time
import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI
from mem0 import AsyncMemory
from mem0.configs.base import MemoryConfig
from redisvl.extensions.message_history.message_history import MessageHistory

# Import from the new structure
from app.core.config import (
    NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE,
    REDIS_URL, REDIS_COLLECTION, REDIS_EMBEDDING_DIMS, REDIS_MESSAGE_HISTORY_NAME,
    OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
)
from app.prompts.memory_prompt import get_system_prompt
from app.core.logger.logger_config import setup_logger
from app.constants import ErrorMessage

# Initialize logger for this module
logger = setup_logger(__name__)


class MemoryService:
    """
    Async chatbot service with persistent memory using Mem0, Neo4j, and Redis.
    
    This service provides a complete chatbot solution with:
    - Memory storage and retrieval via AsyncMemory (non-blocking)
    - Graph-based relationships via Neo4j
    - Vector similarity search via Redis
    - OpenAI LLM for response generation (async)
    
    Attributes:
        client (AsyncOpenAI): Async OpenAI API client for LLM calls
        memory (AsyncMemory): Async Mem0 memory instance with Neo4j and Redis backends
    """
    
    def __init__(self):
        """
        Initialize the MemoryService with all required components.
        
        Sets up:
        1. AsyncOpenAI client for non-blocking LLM responses
        2. AsyncMemory system with Neo4j graph store and Redis vector store
        
        Configuration is loaded from environment variables via config.py
        
        Raises:
            Exception: If initialization of any component fails
        """
        logger.info("Initializing AsyncMemoryService with Mem0, Neo4j, and Redis...")
        
        # Initialize AsyncOpenAI client for non-blocking response generation
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

        self.message_history = MessageHistory(name=REDIS_MESSAGE_HISTORY_NAME, redis_url=REDIS_URL)
        logger.info("Message history initialized successfully")
        
        # Build Mem0 configuration combining Neo4j and Redis using MemoryConfig
        config = MemoryConfig(
            # Vector store configuration (Redis)
            # Used for semantic similarity search over memories
            vector_store={
                "provider": "redis",
                "config": {
                    "collection_name": REDIS_COLLECTION,         # Collection name (mem0)
                    "embedding_model_dims": REDIS_EMBEDDING_DIMS, # Embedding dimensions (1536)
                    "redis_url": REDIS_URL                        # Redis connection URL
                }
            },
            # Graph store configuration (Neo4j)
            # Used for relationship-based memory connections
            graph_store={
                "provider": "neo4j",
                "config": {
                    "url": NEO4J_URL,                       # Neo4j connection URL
                    "username": NEO4J_USERNAME,             # Neo4j username
                    "password": NEO4J_PASSWORD,             # Neo4j password
                    "database": NEO4J_DATABASE,             # Neo4j database name
                }
            },
            # LLM configuration for Mem0's internal operations
            # Used by Mem0 for memory extraction and processing
            llm={
                "provider": "openai",
                "config": {
                    "model": LLM_MODEL,                     # OpenAI model to use
                    "temperature": LLM_TEMPERATURE,         # Response randomness
                    "max_tokens": LLM_MAX_TOKENS,           # Max response length
                }
            },
            reranker={
                "provider": "llm_reranker",
                "config": {
                    "llm": {
                        "provider": "openai",
                        "config": {
                            "model": LLM_MODEL,
                            "temperature": LLM_TEMPERATURE,  # For consistency
                            "max_tokens": LLM_MAX_TOKENS    # Limit response length
                        }
                    },
                    "top_k": 5,              # Fewer results = faster
                    "batch_ranking": True,   # YES - rank multiple at once
                }
            },
            version="v1.1"                              # Mem0 configuration version
        )
        
        # Initialize AsyncMemory with the MemoryConfig object
        self.memory = AsyncMemory(config=config)
        
        logger.info("AsyncMemory system initialized")
        
        logger.info(f"AsyncMemoryService ready! Using {LLM_MODEL} with Neo4j + Redis backends")
    
    async def chat(self, message: str, user_id: str, session_id: str, domain_name: str = None) -> str:
        """
        Main chat interface - processes user message with memory-enhanced context.
        
        This async method orchestrates the entire conversation flow:
        1. Retrieves relevant memories for context (non-blocking)
        2. Builds context string from memories
        3. Generates AI response using OpenAI with context (non-blocking)
        4. Stores the conversation in memory (background task - non-blocking)
        
        Args:
            message (str): The user's input message
            user_id (str): Unique identifier for the user
            session_id (str): Session identifier for conversation history
            domain_name (str, optional): Domain name to load catalog context for
            
        Returns:
            str: The AI-generated response
            
        Raises:
            Exception: If there's an error in the chat flow
        """        
        try:
            logger.info(f"\n\n\nProcessing message for user id:- '{user_id}'\n\nuser_query:- '{message}'...\n\n")
            
            # Log if domain context is being used
            if domain_name:
                logger.info(f"Using domain context: '{domain_name}'")
            
            # Step 1: Retrieve relevant memories from Mem0 (non-blocking)
            memory_results = await self._retrieve_memories(user_id, message, session_id)
            
            # Step 2: Generate AI response using OpenAI with memory context (non-blocking)
            # Pass user_id and domain_name to use domain-specific catalog if available
            answer = await self._generate_response(message, memory_results, user_id, domain_name)
            
            # Step 3: Store in memory (background async task - non-blocking)
            asyncio.create_task(self._store_in_memory(message, answer, user_id, session_id))
            
            logger.info(f"Successfully processed message for user '{user_id}' (memory storage running in background)")
            return answer

        except Exception as e:
            error_msg = ErrorMessage.RESPONSE_GENERATION_FAILED.value.format(error=str(e))
            logger.error(f"User '{user_id}': {error_msg}")
            raise
    
    async def _retrieve_memories(self, user_id: str, query: str, session_id: str) -> str:
        """
        Retrieve relevant memories for a user based on the query (async).
        
        Uses Mem0's hybrid search combining:
        - Vector similarity search (Redis) for semantic matching
        - Graph relationships (Neo4j) for contextual connections
        
        Args:
            user_id (str): Unique identifier for the user
            query (str): Search query (typically the user's current message)
            session_id (str): Session identifier for conversation history
            
        Returns:
            str: Combined context string from memories and history
        """
        start_time = time.time()
        
        # Step 1: Search memories using AsyncMemory (non-blocking)
        mem0_start = time.time()
        memories = await self.memory.search(query, user_id=user_id, rerank=True, limit=5)
        mem0_time = time.time() - mem0_start
        logger.info(f"\n\n## MEM0 SEARCH TIME: {mem0_time:.3f}s")

        memory_results = memories.get('results', []) if memories else []
        logger.info(f"Found {len(memory_results)} relevant memories")

        context = "\n".join([f"- {m['memory']}" for m in memory_results if 'memory' in m])

        # Step 2: Retrieve recent messages from Redis for context
        redis_start = time.time()
        history = self.message_history.get_recent(top_k=20, session_tag=session_id)
        redis_time = time.time() - redis_start
        logger.info(f"\n\n## REDIS GET HISTORY TIME: {redis_time:.3f}s")

        # Step 3: Combine memories and recent messages for context
        history_context = context + "\n\n" + str(history)

        total_time = time.time() - start_time
        logger.info(f"\n\n#RETRIEVE_MEMORIES_END - Total time: {total_time:.3f}s\nMem0 context: {context}\nRedis history: {json.dumps(history, indent=4, ensure_ascii=False)}\n")
        return history_context

    async def _generate_response(self, message: str, context: str, user_id: str, domain_name: str = None) -> str:
        """
        Generate AI response using OpenAI with memory context (async).
        
        Constructs a prompt using the system prompt template (optionally enhanced with domain catalog),
        combining the user's message with retrieved memory context.
        
        Args:
            message (str): The user's input message
            context (str): Formatted memory context string
            user_id (str): User ID to get catalog for
            domain_name (str, optional): Domain name to load catalog context for
            
        Returns:
            str: The AI-generated response
            
        Raises:
            Exception: If OpenAI API call fails
        """        
        # Get system prompt (enhanced with domain catalog if domain_name provided for this user)
        system_prompt_template = get_system_prompt(user_id, domain_name)
        
        # Build the prompt using the template from prompts/memory_prompt.py
        prompt = system_prompt_template.format(context=context, message=message)
        logger.info(f"\n\nSystem prompt: \n\n{prompt}\n\n")
        # Log if domain context was added
        if domain_name:
            logger.info(f"Using enhanced prompt with domain catalog for user '{user_id}', domain: '{domain_name}'")
        
        # Call AsyncOpenAI API with the constructed prompt (non-blocking)
        openai_start = time.time()
        response = await self.client.chat.completions.create(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        openai_time = time.time() - openai_start
        
        # Extract the response content
        answer = response.choices[0].message.content

        logger.info(f"\n\n#OPENAI_API_TIME: {openai_time:.3f}s\n")
        
        return answer
    
    async def _store_in_memory(self, user_message: str, ai_response: str, user_id: str, session_id: str) -> None:
        """
        Store the complete conversation turn (user message + AI response) in Mem0 memory (async).
        
        Mem0 automatically:
        - Extracts relevant information from the conversation
        - Creates embeddings for vector search (stored in Redis)
        - Builds graph relationships (stored in Neo4j)
        
        Args:
            user_message (str): The user's input message
            ai_response (str): The AI's response to the user
            user_id (str): Unique identifier for the user
            session_id (str): Session identifier for conversation history
            
        Raises:
            Exception: If memory storage fails
        """
        start_time = time.time()
        
        # Create a formatted conversation turn with both user and AI messages
        conversation_turn = f"User: {user_message}\nAssistant: {ai_response}"
        
         # Store the conversation in message history of redis for future retrieval
        redis_start = time.time()
        self.message_history.add_messages([{"role": "user", "content": user_message}, {"role": "assistant", "content": ai_response}], session_tag=session_id)
        redis_time = time.time() - redis_start
        logger.info(f"\n\n## REDIS ADD TIME: {redis_time:.3f}s")

        # Add to AsyncMemory (non-blocking - automatically handles Redis + Neo4j storage)
        mem0_start = time.time()
        await self.memory.add(conversation_turn, user_id=user_id)
        mem0_time = time.time() - mem0_start
        logger.info(f"\n\n## MEM0 ADD TIME: {mem0_time:.3f}s")
            
        total_time = time.time() - start_time
        logger.info(f"\n#STORE_MEMORY_END - Complete conversation turn stored successfully in {total_time:.3f}s\n")
    
    
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all stored memories for a specific user (async).
        
        Unlike search_memories(), this returns ALL memories without filtering
        or ranking. Useful for memory management, exports, or debugging.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            List[Dict[str, Any]]: Complete list of all memory objects for the user
        """
        logger.info(f"Retrieving all memories for user '{user_id}'...")
        
        # Fetch all memories from AsyncMemory (non-blocking)
        results = await self.memory.get_all(user_id=user_id)
        
        # Extract the memories list
        memory_list = results.get("results", [])
        
        logger.info(f"Retrieved {len(memory_list)} total memories for user '{user_id}'")
        logger.debug(f"All memories: {results}")
        
        return memory_list
    
    
    async def delete_all_memories(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all memories for a specific user (async).
        
        This is a bulk operation that removes all stored memories from both
        Redis and Neo4j for the given user. Use with caution!
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            Dict[str, Any]: Summary of deletion operation containing:
                - success (bool): Overall operation success status
                - deleted_count (int): Number of successfully deleted memories
        """
        logger.info(f"Deleting all memories for user '{user_id}'...")
        
        try:
            # Get all memories first to count them (non-blocking)
            all_memories = await self.memory.get_all(user_id=user_id)
            memory_list = all_memories.get("results", [])
            memory_count = len(memory_list)
            
            logger.info(f"Found {memory_count} memories to delete for user '{user_id}'")
            
            # Delete all memories for this user using AsyncMemory (non-blocking)
            await self.memory.delete_all(user_id=user_id)
            
            # Log final results
            logger.info(f"Successfully deleted {memory_count} memories for user '{user_id}'")
            
            # Return summary of deletion operation
            return {
                "success": True,
                "deleted_count": memory_count
            }

        except Exception as e:
            error_msg = ErrorMessage.MEMORY_DELETION_FAILED.value.format(error=str(e))
            logger.error(f"User '{user_id}': {error_msg}")
            return {
                "success": False,
                "deleted_count": 0
            }
    
    
    def clear_session_history(self, session_id: str) -> Dict[str, Any]:
        """
        Clear all message history (STM) for a specific session from Redis.
        
        This removes the conversation history stored in Redis for the given session,
        but does NOT delete long-term memories stored in Mem0/Neo4j.
        
        Args:
            session_id (str): Session identifier for the conversation history
            
        Returns:
            Dict[str, Any]: Summary of deletion operation containing:
                - success (bool): Overall operation success status
                - message (str): Status message
        """
        logger.info(f"Clearing session history for session '{session_id}'...")
        
        try:
            # Create a MessageHistory instance bound to this specific session
            session_history = MessageHistory(
                name=REDIS_MESSAGE_HISTORY_NAME, 
                redis_url=REDIS_URL, 
                session_tag=session_id
            )
            
            # Clear all messages for this session using the clear() method
            session_history.clear()
            
            logger.info(f"Successfully cleared all messages for session '{session_id}'")

            return {
                "success": True,
                "message": f"Session history cleared for session: {session_id}"
            }

        except Exception as e:
            error_msg = ErrorMessage.SESSION_CLEAR_FAILED.value.format(error=str(e))
            logger.error(f"Session '{session_id}': {error_msg}")
            return {
                "success": False,
                "message": error_msg
            }

