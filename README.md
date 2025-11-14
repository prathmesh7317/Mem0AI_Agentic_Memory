# Mem0 Chatbot with Graph Memory & Redis Vector Store

A production-ready chatbot built with FastAPI demonstrating Mem0's Graph Memory with Redis vector storage:
- ✅ **Redis Stack** (Vector DB) - Semantic search with embeddings & vector storage
- ✅ **Neo4j** (Graph DB) - Relationship graphs & knowledge mapping
- ✅ **OpenAI GPT** - Advanced language model for responses
- ✅ **FastAPI** - Modern, fast web framework with REST APIs
- ✅ **Domain Catalogs** - Context-aware responses with custom domain knowledge
- ✅ **Modal-based UI** - Beautiful interface for catalog management
- ✅ **Logging** - Comprehensive application logs
- ✅ **Clean Architecture** - Class-based design with separation of concerns

Based on:
- [Mem0 Graph Memory Documentation](https://docs.mem0.ai/open-source/features/graph-memory#graph-memory)
- [Mem0 Redis Integration](https://docs.mem0.ai/components/vectordbs/config#redis)

---

## 📁 Project Structure

```
git_memo_repos/
│
├── main.py                          # Application entry point
├── pyproject.toml                   # Project metadata & dependencies (for uv/pip)
├── uv.lock                         # Dependency lock file (uv)
├── .env                            # Environment variables (create this)
├── .gitignore                      # Git ignore rules
├── .python-version                 # Python version specification
│
├── app/                            # Main application package
│   ├── __init__.py                # Package initialization
│   │
│   ├── api/                        # API layer
│   │   ├── __init__.py
│   │   └── routes/                 # Route handlers
│   │       ├── __init__.py
│   │       └── endpoints.py        # All API endpoints (chat, memory, domain catalog)
│   │
│   ├── services/                   # Business logic
│   │   ├── __init__.py
│   │   └── memory_service.py       # Mem0 service (Neo4j + Redis)
│   │
│   ├── models/                     # Pydantic models
│   │   ├── __init__.py
│   │   ├── requests.py             # Request models (ChatRequest, DomainCatalogRequest)
│   │   └── responses.py            # Response models (ChatResponse, DomainCatalogResponse)
│   │
│   ├── prompts/                    # AI prompts
│   │   ├── __init__.py
│   │   └── memory_prompt.py        # Chat system prompts with domain catalog injection
│   │
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   └── catalog_loader.py       # Domain catalog manager (class-based)
│   │
│   ├── constants/                  # Application constants
│   │   ├── __init__.py
│   │   ├── messages.py             # Response messages
│   │   └── status_codes.py         # HTTP status code constants
│   │
│   ├── data/                       # Data storage
│   │   └── domain_catalogs.json    # User domain catalogs storage
│   │
│   └── core/                       # Core infrastructure
│       ├── __init__.py
│       ├── config/                 # Configuration
│       │   ├── __init__.py
│       │   └── config.py           # Environment config
│       └── logger/                 # Logging
│           ├── __init__.py
│           └── logger_config.py    # Logger setup
│
├── static/                         # Frontend assets
│   ├── css/
│   │   └── style.css              # Styling
│   └── js/
│       └── script.js              # Frontend JavaScript
│
├── templates/                      # HTML templates
│   └── index.html                 # Web UI
│
├── tests/                          # Test files
│   ├── chatbot_example.py         # Example chatbot usage
│   └── test_neo4j.py              # Neo4j connection tests
│
└── logs/                          # Application logs
    └── app.log                    # Auto-created log file
```

---

## 🚀 Quick Setup

### **Step 1: Create `.env` File**

Create a `.env` file in the project root and configure:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Required: OpenAI Configuration
EMBEDDING_MODEL=text-embedding-3-large
OPENAI_MODEL=gpt-4o-mini
LLM_MODEL=gpt-4o-mini

# Required: Neo4j Configuration (Get free tier at https://neo4j.com/cloud/aura/)
NEO4J_URL=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

# Required: Redis Configuration (for vector storage)
REDIS_URL=redis://localhost:6379
REDIS_COLLECTION=mem0
REDIS_EMBEDDING_DIMS=1536
```

---

### **Step 2: Install Dependencies**

**Using uv (recommended):**
```bash
uv sync
```
---

### **Step 3: Start Databases with Docker**

#### **A. Redis Stack (Vector DB) - REQUIRED**
```bash
docker run -d --name redis-stack \
  -p 6379:6379 \
  redis/redis-stack:latest
```

#### **B. RedisInsight (Optional - Redis GUI)**
```bash
docker run -d --name redisinsight \
  -p 5540:5540 \
  redis/redisinsight:latest
```

**Access RedisInsight:** http://localhost:5540
- Add database with host: `localhost`, port: `6379`

#### **C. Neo4j (Graph DB) - REQUIRED**
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  -v $(pwd)/neo4j_data:/data \
  neo4j:latest
```

**Access Neo4j Browser:** http://localhost:7474
- Username: `neo4j`
- Password: `password123`

---

### **Step 4: Verify Databases are Running**

```bash
# Check Docker containers
docker ps

# You should see 2-3 containers:
# - redis-stack (port 6379)
# - redisinsight (port 5540) [optional]
# - neo4j (ports 7474, 7687)
```

---

### **Step 5: Run the FastAPI Application**

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
python main.py
```

The app will be available at:
- **Frontend:** http://localhost:5000
- **API Docs:** http://localhost:5000/docs (Swagger UI)
- **API ReDoc:** http://localhost:5000/redoc

---

## 🎯 How It Works

### **1. User sends a message**
```
User: "Hi! I'm John, I love Nike shoes, size 10"
```

### **2. Mem0 automatically extracts memories**
```
✅ "User's name is John"
✅ "User prefers Nike brand"
✅ "User's shoe size is 10"
```

### **3. Mem0 stores in BOTH databases automatically**
```
✅ Redis: Vector embeddings for semantic search
✅ Neo4j: User→PREFERS→Nike relationship
```

### **4. Next query retrieves from both stores**
```
User: "Show me running shoes"

Mem0 hybrid search:
- Redis: Finds "Nike preference" (semantic vector search)
- Neo4j: Finds User→PREFERS→Nike (graph relationships)

Result: Personalized response with user preferences!
```

---

## 🏢 Domain Catalog Feature

### **What is Domain Catalog?**
Domain Catalogs allow you to provide **context-specific knowledge** to the chatbot for different industries or domains (e.g., healthcare, finance, travel, e-commerce).

### **How it Works**

#### **1. Add a Domain Catalog**
```
Domain: travel
Catalog: "TripJack API offers flight bookings, hotel reservations, 
         and holiday packages. Contact support at travel@example.com"
```

#### **2. Chatbot Uses Domain Context**
```
User: "I need to book a flight to Paris"

AI Response (with travel domain catalog):
"I can help you book a flight to Paris using TripJack API! 
 We offer competitive prices and 24/7 support..."
```

### **Domain Catalog Management**

The UI provides a beautiful modal-based interface:

- **ADD** - Create new domain catalog (409 error if already exists)
- **UPDATE** - Modify existing domain catalog (404 error if not found)
- **DELETE** - Remove domain catalog with confirmation

### **Features**

✅ **Multi-Domain Support** - Add unlimited domain catalogs per user
✅ **Auto-Injection** - Catalogs automatically injected into AI prompts
✅ **REST APIs** - Full CRUD operations via FastAPI endpoints
✅ **Class-Based Manager** - Clean, maintainable code architecture
✅ **JSON Storage** - Simple file-based storage (easily replaceable)
✅ **Smart Filtering** - Only uses domain content when relevant to query

---

## 📚 Test Scenarios

Try these conversations to see Mem0 in action:

### **Scenario 1: First Introduction**
```
User: "Hi! I'm Sarah, I'm vegetarian and love Italian food"
```
→ Click "View My Memories" to see what Mem0 stored

### **Scenario 2: Query with Context**
```
User: "Recommend a restaurant"
```
→ AI uses memory to give personalized recommendation

### **Scenario 3: Update/Contradiction**
```
User: "Actually, I'm not vegetarian anymore"
```
→ Mem0 automatically updates in both databases (Redis + Neo4j)!

### **Scenario 4: View Memories**
```
Click "View Memories" button
```
→ See all stored memories for the user

### **Scenario 5: Domain Catalog - Add Travel Domain**
```
1. Click "Domain Catalog" dropdown
2. Click "ADD" button
3. Fill in:
   - Domain Name: travel
   - Catalog: "TripJack API offers flight bookings and hotel reservations"
4. Click "Add Domain"
```
→ Domain catalog added successfully

### **Scenario 6: Query with Domain Context**
```
User: "I need to book a flight to Paris"
```
→ AI uses travel domain catalog for context-aware response

### **Scenario 7: Update Domain Catalog**
```
1. Click "UPDATE" button
2. Fill in:
   - Domain Name: travel
   - New Description: "Updated catalog with new features..."
3. Click "Update Domain"
```
→ Domain catalog updated

### **Scenario 8: Delete Domain Catalog**
```
1. Click "DELETE" button
2. Enter Domain Name: travel
3. Confirm deletion
```
→ Domain catalog removed

---

## 🔧 Configuration

### **Change LLM Model**

Edit `.env` file:
```bash
LLM_MODEL=gpt-3.5-turbo  # Change to cheaper model
# or
LLM_MODEL=gpt-4o         # Use more powerful model
```

Or edit `app/services/memory_service.py`:
```python
"llm": {
    "provider": "openai",
    "config": {
        "model": "gpt-3.5-turbo",  # Change model
        "temperature": 0.1,
        "max_tokens": 4096
    }
}
```

### **Disable Graph DB (Neo4j)**

Comment out in `app/services/memory_service.py`:
```python
# "graph_store": {...},  # Comment to disable Neo4j
```

This will use only Redis for vector storage without graph relationships.

### **Use Different Vector DB**

Change provider in `app/services/memory_service.py`:
```python
"vector_store": {
    "provider": "qdrant",  # Or "pinecone", "weaviate", "chroma"
    "config": {...}
}
```

---

## 🧪 Verify Storage

### **Check Redis (Vector DB)**

#### **Option 1: Using RedisInsight GUI**
1. Open http://localhost:5540
2. Connect to database (host: `localhost`, port: `6379`)
3. Browse keys starting with `mem0`

#### **Option 2: Using Redis CLI**
```bash
# Connect to Redis
docker exec -it redis-stack redis-cli

# List all keys
KEYS *

# List mem0 keys
KEYS mem0*

# Check database size
DBSIZE
```

### **Check Neo4j (Graph DB)**

**Access Neo4j Browser:** http://localhost:7474
- Username: `neo4j`
- Password: `password123` (or your configured password)

**View all nodes and relationships:**
```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 5000;
```

**View all nodes:**
```cypher
MATCH (n) RETURN n LIMIT 25
```

**Delete all relationships (to clean up):**
```cypher
MATCH ()-[r]->()
DELETE r
```

**Delete all nodes and relationships (complete reset):**
```cypher
MATCH (n) DETACH DELETE n
```

---

## 🐛 Troubleshooting

### **Error: Connection refused (Redis)**
```bash
# Check if Redis Stack is running
docker ps | grep redis-stack

# Restart Redis Stack
docker restart redis-stack

# Or start if not running
docker start redis-stack
```

### **Error: ModuleNotFoundError: No module named 'redisvl'**
```bash
# Install redisvl (Redis Vector Library)
source venv/bin/activate
pip install redisvl
```

### **Error: Authentication failed (Neo4j)**
```bash
# Check Neo4j credentials in .env match your setup:
# Default docker credentials:
# NEO4J_USERNAME=neo4j
# NEO4J_PASSWORD=password123
```

### **Error: OpenAI API key not found**
```bash
# Verify .env file exists with:
OPENAI_API_KEY=sk-...

# Restart the app
python main.py
```

### **Error: Port already in use (6379)**
```bash
# Check what's using the port
docker ps -a | grep 6379

# Use different port for Redis
docker run -d --name redis-stack -p 6500:6379 redis/redis-stack:latest

# Update .env file:
REDIS_URL=redis://localhost:6500
```

### **Error: Module not found**
```bash
# Reinstall dependencies using uv
uv sync --reinstall

```

---

## 📊 What Mem0 Does Automatically

✅ **Memory Extraction** - Extracts important info from conversations
✅ **Storage Distribution** - Stores in Vector + Graph DB automatically
✅ **Hybrid Search** - Searches both stores in parallel
✅ **Contradiction Detection** - Updates when info changes
✅ **Multi-User Support** - Separate memories per user
✅ **Categorization** - Auto-categorizes memories

## 🎨 Custom Features Added

✅ **Domain Catalog System** - Context-aware responses with custom knowledge
✅ **Modal-Based UI** - Beautiful interface for catalog management
✅ **Class-Based Architecture** - Clean, maintainable code structure
✅ **RESTful APIs** - Full CRUD operations with proper HTTP status codes
✅ **Smart Context Injection** - Domain catalogs only used when relevant
✅ **Multi-Domain Support** - Unlimited domains per user
✅ **Markdown Rendering** - Full markdown support in chat using marked.js (GitHub Flavored Markdown)
✅ **Constants Management** - Centralized messages and status codes

---

## 🎯 Key Files Explained

### **`main.py`**
- Application entry point
- Creates FastAPI application instance
- Configures CORS middleware
- Mounts static files and templates
- Registers API routes from endpoints.py
- Runs Uvicorn server with hot reload

### **`app/core/config/config.py`**
- Configures Neo4j and Redis connections
- Sets LLM and embedding models
- Loads environment variables from .env
- Provides configuration for memory service

### **`app/services/memory_service.py`**
- Core Mem0 integration
- `chat()` - Main chat interface with memory context
- `_retrieve_memories()` - Hybrid search (Redis + Neo4j)
- `_store_in_memory()` - Store conversations and extract facts
- `get_all_memories()` - Get all user memories
- `delete_all_memories()` - Clear user memories
- `clear_session_history()` - Clear session from Redis

### **`app/api/routes/endpoints.py`**
- **All API endpoints in one file:**
  - `POST /chat` - Chat endpoint with memory context
  - `GET /memories` - Get all memories for a user
  - `POST /memories/clear` - Clear long-term memories (LTM)
  - `POST /session/clear` - Clear session history (STM)
  - `GET /domain/user?user_id={user_id}` - Get user's domain catalog names
  - `POST /domain/catalog` - Add new domain catalog
  - `PUT /domain/catalog` - Update existing domain catalog
  - `DELETE /domain/catalog` - Delete domain catalog
  - `GET /health` - Health check endpoint
- Uses APIRouter for route organization
- Includes request validation and error handling
- RESTful design with proper HTTP status codes

### **`app/models/`**
- **`requests.py`** - Pydantic request models (ChatRequest, ClearMemoryRequest, etc.)
- **`responses.py`** - Pydantic response models (ChatResponse, MemoriesResponse, etc.)
- Provides type safety and automatic validation

### **`app/prompts/memory_prompt.py`**
- System prompts for AI chat
- Defines chatbot personality and behavior
- Memory-aware prompt templates
- **Domain catalog injection** - Automatically includes user's domain catalogs in prompts
- Smart filtering - Only uses domain context when relevant to queries

### **`app/utils/catalog_loader.py`**
- **DomainCatalogManager** class - Manages all domain catalog operations
- **Singleton pattern** - One instance shared across the application
- **Private methods:**
  - `_load_catalogs()` - Load from JSON file
  - `_save_catalogs()` - Save to JSON file
  - `_find_user()` - Find user in data
- **Public methods:**
  - `add_domain()` - Add NEW domain (raises ValueError if exists)
  - `update_domain()` - Update EXISTING domain (raises ValueError if not found)
  - `delete_domain()` - Delete domain (raises ValueError if not found)
  - `get_all_user_catalogs()` - Get all catalogs for AI prompt injection
  - `get_user_domain_names()` - Get list of domain names

### **`app/data/domain_catalogs.json`**
- JSON file storing user domain catalogs
- Structure: `{"users": [{"user_id": "...", "domains": {...}}]}`
- Auto-created on first domain addition
- Simple file-based storage (easily replaceable with database)

### **`templates/index.html` + `static/`**
- Modern, responsive web UI for chatbot
- Real-time chat interface with **Markdown support** (via marked.js CDN)
- Memory management controls
- User/session ID configuration
- **Beautiful modal-based domain catalog management:**
  - ADD modal - Two fields (domain name + catalog description)
  - UPDATE modal - Two fields (domain name + new description)
  - DELETE modal - One field (domain name) + warning message
  - Click outside to close
  - Form validation
  - Smooth animations
- **Frontend Libraries:**
  - `marked.js` (CDN) - Full markdown rendering with GitHub Flavored Markdown support

### **`tests/`**
- **`chatbot_example.py`** - Example usage and testing
- **`test_neo4j.py`** - Neo4j connection verification

---

## 🚀 Next Steps

1. ✅ Test with different users (change User ID in the web UI)
2. ✅ View memories in Neo4j Browser (http://localhost:7474)
3. ✅ Browse embeddings in RedisInsight (http://localhost:5540)
4. ✅ Try contradictions (change preferences and see updates)
5. ✅ Add domain catalogs for your specific use case
6. ✅ Test domain-aware responses
7. ✅ Export data from Redis/Neo4j
8. ✅ Implement conversation history tracking
9. ✅ Add memory analytics and visualization
10. ⬜ Replace JSON storage with database (PostgreSQL/MongoDB)
11. ⬜ Add authentication and user management
12. ⬜ Implement domain catalog versioning

---

## 📝 License

MIT License - Feel free to use for your POC!

---

## 🙋 Need Help?

- **Mem0 Docs:** https://docs.mem0.ai
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Neo4j Docs:** https://neo4j.com/docs
- **Redis Docs:** https://redis.io/docs
- **Redis Vector Search:** https://redis.io/docs/stack/search/reference/vectors/

---

## 📦 Dependencies

**Backend packages** (defined in `pyproject.toml`):
- `mem0ai[graph]` - Memory management with graph support
- `fastapi` - Modern, fast web framework
- `uvicorn[standard]` - ASGI server
- `pydantic` - Data validation using type hints
- `redisvl` - Redis Vector Library for embeddings
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `jinja2` - Template engine for HTML

**Frontend libraries** (loaded via CDN):
- `marked.js` - Markdown parser and compiler for chat message rendering

---

## 🌐 API Endpoints

### Chat
- `POST /chat` - Send message and get AI response with memory context
  - Body: `{"message": "...", "user_id": "...", "session_id": "...", "domain_name": "..."}`
- `GET /` - Web interface

### Memory Management  
- `GET /memories?user_id={id}` - Retrieve all memories for a user
- `POST /memories/clear` - Clear long-term memories (LTM)
  - Body: `{"user_id": "..."}`
- `POST /session/clear` - Clear session history (STM)
  - Body: `{"session_id": "..."}`

### Domain Catalog Management
- `GET /domain/user?user_id={user_id}` - Get list of domain names for a user
  - Returns: `{"user_id": "...", "domains": ["travel", "healthcare"]}`
- `POST /domain/catalog` - Add new domain catalog
  - Body: `{"user_id": "...", "domain_name": "...", "domain_catalog": "..."}`
  - Status: `409 Conflict` if domain already exists
- `PUT /domain/catalog` - Update existing domain catalog
  - Body: `{"user_id": "...", "domain_name": "...", "domain_catalog": "..."}`
  - Status: `404 Not Found` if domain doesn't exist
- `DELETE /domain/catalog?user_id={id}&domain_name={name}` - Delete domain catalog
  - Status: `404 Not Found` if domain doesn't exist

### System
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

---

**Built with modern tech stack: FastAPI + Mem0 + Redis + Neo4j**

