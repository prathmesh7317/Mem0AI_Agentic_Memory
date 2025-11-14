"""
Configuration for Mem0 with Neo4j Graph Memory and Qdrant Vector Store
"""

import os
from dotenv import load_dotenv

load_dotenv()


# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM Configuration (for Mem0)
LLM_MODEL = os.getenv("LLM_MODEL")
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 4096

# Neo4j Configuration (for graph memory)
NEO4J_URL = os.getenv("NEO4J_URL")  
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

# Redis Configuration (for vector storage)
REDIS_URL = os.getenv("REDIS_URL")
REDIS_COLLECTION = os.getenv("REDIS_COLLECTION")
REDIS_EMBEDDING_DIMS = int(os.getenv("REDIS_EMBEDDING_DIMS"))
REDIS_MESSAGE_HISTORY_NAME = os.getenv("REDIS_MESSAGE_HISTORY_NAME")
