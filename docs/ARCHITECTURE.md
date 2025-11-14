# System Architecture

This document explains the system design and architecture of the Mem0 Chatbot application.

---

## Overview

The application is a memory-enhanced chatbot built with:
- **FastAPI** - Web framework
- **Mem0** - Memory management system
- **Neo4j** - Graph database for relationships
- **Redis** - Vector database for semantic search
- **OpenAI GPT** - Language model

---

## Architecture Diagram

```
┌─────────────┐
│   Browser   │
│   (User)    │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────────────────┐
│      FastAPI Application        │
│  ┌──────────┐   ┌────────────┐ │
│  │ Endpoints│   │  Templates │ │
│  │   API    │   │   Static   │ │
│  └────┬─────┘   └────────────┘ │
│       │                         │
│  ┌────▼────────────────────┐   │
│  │   Memory Service        │   │
│  │   (Mem0 Integration)    │   │
│  └────┬────────────────────┘   │
│       │                         │
│  ┌────▼──────────┐              │
│  │ Domain Catalog│              │
│  │    Manager    │              │
│  └────┬──────────┘              │
└───────┼─────────────────────────┘
        │
        ├──────────────┬──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐    ┌─────────┐   ┌─────────┐
   │ Neo4j  │    │  Redis  │   │ OpenAI  │
   │ Graph  │    │ Vector  │   │   API   │
   │   DB   │    │  Store  │   │         │
   └────────┘    └─────────┘   └─────────┘
```

---

## Components

### 1. Frontend Layer

**Location:** `templates/`, `static/`

- **HTML Template** (`index.html`)
  - Chat interface
  - Memory management controls
  - Domain catalog modals
  - User/session ID inputs

- **JavaScript** (`static/js/script.js`)
  - API communication
  - DOM manipulation
  - Markdown rendering with marked.js
  - Local storage for user preferences

- **CSS** (`static/css/style.css`)
  - Responsive design
  - Modern UI components
  - Animation effects

### 2. API Layer

**Location:** `app/api/routes/endpoints.py`

Handles HTTP requests and responses:
- Chat endpoint
- Memory management endpoints
- Domain catalog CRUD operations
- Health check

**Technology:** FastAPI with async/await

### 3. Business Logic Layer

**Location:** `app/services/memory_service.py`

Core functionality:
- Chat with memory context
- Memory retrieval (hybrid search)
- Memory storage (automatic extraction)
- Session management

**Technology:** Mem0 with custom configuration

### 4. Domain Catalog System

**Location:** `app/utils/catalog_loader.py`

Manages domain-specific knowledge:
- Add/update/delete catalogs
- Load catalogs for AI prompts
- User-specific catalog management

**Storage:** JSON file (`app/data/domain_catalogs.json`)

### 5. Data Models

**Location:** `app/models/`

- `requests.py` - Request validation models
- `responses.py` - Response format models

**Technology:** Pydantic for validation

### 6. Configuration

**Location:** `app/core/config/config.py`

Environment-based configuration:
- Database connections
- API keys
- Model settings

**Source:** `.env` file

### 7. Constants

**Location:** `app/constants/`

- `messages.py` - Standard response messages
- `status_codes.py` - HTTP status codes

---

## Data Flow

### Chat Request Flow

```
1. User sends message via browser
   ↓
2. Frontend sends POST /chat request
   ↓
3. API endpoint receives request
   ↓
4. Memory Service processes:
   a. Retrieves relevant memories (Redis + Neo4j)
   b. Loads domain catalogs (if applicable)
   c. Constructs prompt with context
   d. Sends to OpenAI
   e. Stores conversation in memory
   ↓
5. Response sent back to frontend
   ↓
6. Frontend renders markdown response
```

### Memory Storage Flow

```
1. User message processed by Mem0
   ↓
2. Mem0 extracts important information
   ↓
3. Information stored in parallel:
   - Redis: Vector embeddings for semantic search
   - Neo4j: Entity relationships (nodes and edges)
   ↓
4. Future queries search both stores
   - Redis: Similarity search using vectors
   - Neo4j: Graph traversal for relationships
```

### Domain Catalog Flow

```
1. User adds domain catalog via UI
   ↓
2. POST /domain/catalog endpoint
   ↓
3. DomainCatalogManager validates and stores
   ↓
4. Saved to domain_catalogs.json
   ↓
5. On next chat:
   a. System loads user's domains
   b. Injects relevant domain content into prompt
   c. AI uses domain knowledge in response
```

---

## Database Schema

### Neo4j Graph Structure

**Nodes:**
- User nodes (user_id)
- Entity nodes (preferences, facts, etc.)

**Relationships:**
- `PREFERS` - User preference relationships
- `HAS_ATTRIBUTE` - User attributes
- `RELATED_TO` - Entity relationships

**Example:**
```
(User:user_123)-[:PREFERS]->(Brand:Nike)
(User:user_123)-[:HAS_ATTRIBUTE {type: "size"}]->(Value:10)
```

### Redis Key Structure

**Key Format:**
```
mem0:{collection}:{user_id}:{memory_id}
```

**Data:**
- Vector embeddings (1536 dimensions for text-embedding-3-large)
- Metadata (timestamp, category, etc.)
- Original text

### Domain Catalog Storage

**File:** `app/data/domain_catalogs.json`

**Structure:**
```json
{
  "users": [
    {
      "user_id": "user_123",
      "domains": {
        "travel": "TripJack API catalog...",
        "ecommerce": "Shopping catalog..."
      }
    }
  ]
}
```

---

## Memory System

### Two Types of Memory

**1. Long-Term Memory (LTM)**
- Stored in: Neo4j + Redis
- Contains: User facts, preferences, history
- Persistence: Permanent until cleared
- Retrieval: Hybrid search (vector + graph)

**2. Short-Term Memory (STM)**
- Stored in: Application session
- Contains: Current conversation context
- Persistence: Session only
- Retrieval: Direct access

### Hybrid Search Strategy

Mem0 uses both databases for retrieval:

**Redis (Vector Search):**
- Converts query to embedding
- Finds similar memories by cosine similarity
- Fast semantic search

**Neo4j (Graph Search):**
- Traverses relationship graph
- Finds connected entities
- Contextual relationships

**Combined Result:**
- Merges results from both sources
- Ranks by relevance
- Provides rich context to AI

---

## AI Prompt Construction

### Prompt Components

1. **System Prompt** (`app/prompts/memory_prompt.py`)
   - Chatbot personality
   - Behavior guidelines

2. **Domain Catalogs** (if relevant)
   - Injected automatically
   - User-specific knowledge

3. **Memory Context**
   - Retrieved from Neo4j + Redis
   - User preferences and history

4. **Current Message**
   - User's question or statement

**Final Prompt:**
```
System: You are a helpful AI assistant...
Domain Context: [Travel catalog information...]
Memory Context: User prefers Nike, size 10...
User: Show me running shoes
```

---

## Security Considerations

### Current Implementation

- No authentication (development only)
- No rate limiting
- No input sanitization beyond Pydantic validation
- Markdown rendering with XSS protection

### Production Requirements

**Required for production:**
- Add API authentication (API keys or JWT)
- Implement rate limiting
- Add input validation and sanitization
- Enable CORS with specific origins
- Use HTTPS only
- Encrypt sensitive data
- Add logging for security events
- Implement user session management

---

## Scalability Considerations

### Current Limitations

- Single server instance
- File-based domain catalog storage
- No caching layer
- No load balancing

### Scaling Strategies

**For high traffic:**

1. **Horizontal Scaling**
   - Deploy multiple FastAPI instances
   - Use load balancer (nginx/AWS ALB)
   - Session affinity or shared session store

2. **Database Optimization**
   - Redis cluster for vector store
   - Neo4j cluster for graph database
   - Database connection pooling

3. **Caching**
   - Cache frequent queries
   - Cache domain catalogs in Redis
   - CDN for static assets

4. **Storage Migration**
   - Move domain catalogs to database
   - Use S3 for file storage
   - Implement backup strategy

---

## Design Decisions

### Why Neo4j + Redis?

**Neo4j (Graph DB):**
- Natural fit for relationships
- Powerful graph traversal
- Visual data exploration

**Redis (Vector DB):**
- Fast similarity search
- Low latency
- Built-in vector operations

**Combined:**
- Best of both worlds
- Semantic + relational search
- Rich context for AI

### Why File-Based Domain Catalogs?

**Advantages:**
- Simple implementation
- Easy to debug
- No additional database needed
- Good for POC/MVP

**Disadvantages:**
- Not scalable
- No transactions
- File locking issues with concurrent access

**Future:** Migrate to PostgreSQL or MongoDB

### Why Class-Based Architecture?

**Benefits:**
- Clean separation of concerns
- Easy to test
- Maintainable code
- Follows SOLID principles

---


## Logging

### Implementation

**Location:** `app/core/logger/logger_config.py`

**Features:**
- File-based logging (`logs/app.log`)
- Console output for development
- Timestamp and log levels
- Automatic log rotation

**Logged Information:**
- API requests and responses
- Database operations
- Errors and exceptions
- Performance metrics

---

## Testing Strategy

### Current Tests

**Location:** `tests/`

- `chatbot_example.py` - Manual testing script
- `test_neo4j.py` - Database connection test

### Recommended Tests

**Unit Tests:**
- Memory service functions
- Domain catalog manager
- API endpoints (isolated)

**Integration Tests:**
- Full API workflows
- Database operations
- End-to-end chat flow

**Load Tests:**
- Concurrent user simulation
- Memory retrieval performance
- API response times

---

## Future Enhancements

### Planned Features

1. **Authentication System**
   - User registration/login
   - API key management
   - Role-based access control

2. **Analytics Dashboard**
   - Memory usage statistics
   - Popular domains
   - User engagement metrics

3. **Advanced Memory**
   - Memory prioritization
   - Automatic memory cleanup
   - Memory versioning

4. **Multi-modal Support**
   - Image understanding
   - Voice input/output
   - Document processing

5. **Deployment**
   - Docker containers
   - Kubernetes orchestration
   - CI/CD pipeline
   - Production monitoring

---

## Technology Versions

- Python: 3.11+
- FastAPI: Latest
- Mem0: Latest with graph support
- Neo4j: 5.x
- Redis Stack: Latest
- OpenAI API: Latest

---

## References

- Mem0 Documentation: https://docs.mem0.ai
- FastAPI Documentation: https://fastapi.tiangolo.com
- Neo4j Documentation: https://neo4j.com/docs
- Redis Documentation: https://redis.io/docs

