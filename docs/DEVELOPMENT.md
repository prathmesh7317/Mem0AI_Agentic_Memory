# Development Guide

This guide helps developers understand, contribute to, and extend the Mem0 Chatbot application.

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker (for databases)
- Git
- Code editor (VS Code recommended)
- OpenAI API key
- Neo4j Aura account (or local Neo4j)

### Initial Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd git_memo_repos
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
uv sync
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Start databases**
```bash
# Redis Stack
docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest

# Neo4j
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest
```

6. **Run application**
```bash
python main.py
```

---

## Project Structure

### Directory Layout

```
git_memo_repos/
├── app/                    # Main application code
│   ├── api/               # API routes
│   ├── services/          # Business logic
│   ├── models/            # Data models
│   ├── prompts/           # AI prompts
│   ├── utils/             # Utilities
│   ├── constants/         # Constants
│   ├── data/              # Data storage
│   └── core/              # Core infrastructure
│       ├── config/        # Configuration
│       └── logger/        # Logging
├── static/                # Frontend assets
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript
├── templates/             # HTML templates
├── tests/                # Test files
├── docs/                 # Documentation
└── logs/                 # Application logs
```

### Key Files

- `main.py` - Application entry point
- `pyproject.toml` - Dependencies and metadata
- `.env` - Environment variables (not in git)
- `app/api/routes/endpoints.py` - All API endpoints
- `app/services/memory_service.py` - Mem0 integration
- `app/utils/catalog_loader.py` - Domain catalog manager

---

## Code Style

### Python Guidelines

Follow PEP 8 with these specifics:

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `MemoryService`)
- Functions/Methods: `snake_case` (e.g., `get_user_domains`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- Private methods: `_leading_underscore` (e.g., `_load_catalogs`)

**Documentation:**
```python
def function_name(param1: str, param2: int) -> dict:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When validation fails
    """
    pass
```

**Type Hints:**
Always use type hints for parameters and return values.

**Comments:**
Add single-line comments for complex logic blocks.

### JavaScript Guidelines

**Naming:**
- Functions: `camelCase` (e.g., `sendMessage`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)
- Variables: `camelCase` (e.g., `userId`)

**Comments:**
Add concise single-line comments for each code block.

**Async/Await:**
Use async/await for all API calls.

---

## Adding New Features

### Adding a New API Endpoint

1. **Define request/response models** in `app/models/`

```python
# app/models/requests.py
class NewFeatureRequest(BaseModel):
    param1: str
    param2: int
```

2. **Add endpoint** in `app/api/routes/endpoints.py`

```python
@router.post("/new-feature")
async def new_feature(request: NewFeatureRequest):
    """
    Endpoint description.
    """
    try:
        # Implementation
        return {"result": "success"}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

3. **Add constants** if needed in `app/constants/messages.py`

```python
NEW_FEATURE_SUCCESS = "Feature completed successfully"
```

4. **Update frontend** in `static/js/script.js`

```javascript
// Add API call function
async function callNewFeature(param1, param2) {
    const response = await fetch('/new-feature', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({param1, param2})
    });
    return await response.json();
}
```

5. **Document in** `docs/API.md`

### Extending Memory Service

Add new methods in `app/services/memory_service.py`:

```python
def new_memory_operation(self, user_id: str) -> dict:
    """
    Description of operation.
    """
    try:
        # Use self.memory_client for Mem0 operations
        result = self.memory_client.some_operation(user_id)
        return result
    except Exception as e:
        logger.error(f"Error in new_memory_operation: {e}")
        raise
```

### Adding Domain Catalog Features

Extend `app/utils/catalog_loader.py`:

```python
def new_catalog_operation(self, user_id: str, domain_name: str):
    """
    Description of new operation.
    """
    user = self._find_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    # Your logic here
    self._save_catalogs()
```

---

## Testing

### Manual Testing

Use the test script:

```bash
python tests/chatbot_example.py
```

Available commands:
- `domains` - Show user domains
- `clear` - Clear session
- `exit` - Quit

### Testing Neo4j Connection

```bash
python tests/test_neo4j.py
```

### Testing API Endpoints

Using curl:

```bash
# Chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "user_id": "test_user", "session_id": "test_session"}'

# Health check
curl http://localhost:5000/health
```

Using browser:
- Swagger UI: http://localhost:5000/docs
- Try all endpoints interactively

### Unit Testing (To Be Implemented)

Create tests in `tests/` directory:

```python
# tests/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

Run tests:
```bash
pytest tests/
```

---

## Debugging

### Enable Debug Logging

Set in `.env`:
```bash
LOG_LEVEL=DEBUG
```

### View Logs

```bash
tail -f logs/app.log
```

### Common Issues

**Issue: Connection refused to Redis**
```bash
# Check if Redis is running
docker ps | grep redis-stack

# Restart Redis
docker restart redis-stack
```

**Issue: Neo4j authentication failed**
- Verify credentials in `.env` match Neo4j setup
- Check Neo4j browser: http://localhost:7474

**Issue: OpenAI API errors**
- Verify API key is valid
- Check API quota/billing
- Review rate limits

**Issue: Domain not showing in UI**
- Check browser console for errors
- Verify API endpoint returns data
- Check network tab in DevTools

### Debugging with VS Code

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "5000"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

Set breakpoints and press F5 to debug.

---

## Database Management

### Redis Operations

**Connect to Redis CLI:**
```bash
docker exec -it redis-stack redis-cli
```

**Common commands:**
```bash
KEYS *              # List all keys
KEYS mem0*          # List Mem0 keys
GET key_name        # Get value
DEL key_name        # Delete key
FLUSHALL            # Clear all data (careful!)
```

### Neo4j Operations

**Access Neo4j Browser:** http://localhost:7474

**Common Cypher queries:**

```cypher
// View all nodes
MATCH (n) RETURN n LIMIT 25

// View relationships
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100

// Find user nodes
MATCH (n) WHERE n.user_id = "user_123" RETURN n

// Delete all data (careful!)
MATCH (n) DETACH DELETE n
```

### Backup and Restore

**Redis backup:**
```bash
docker exec redis-stack redis-cli SAVE
docker cp redis-stack:/data/dump.rdb ./backup/
```

**Neo4j backup:**
```bash
docker exec neo4j neo4j-admin dump --database=neo4j --to=/backups/neo4j.dump
```

---

## Configuration Management

### Environment Variables

All configuration in `.env`:

```bash
# Required
OPENAI_API_KEY=sk-...
NEO4J_URL=neo4j+s://...
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
REDIS_URL=redis://localhost:6379

# Optional
LOG_LEVEL=INFO
MAX_TOKENS=4096
TEMPERATURE=0.1
```

### Configuration Loading

Configuration loaded in `app/core/config/config.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ... more config
```

---

## Performance Optimization

### Profiling

Add timing to endpoints:

```python
import time

@router.post("/endpoint")
async def endpoint(request: Request):
    start = time.time()
    
    # Your code here
    
    duration = time.time() - start
    logger.info(f"Endpoint took {duration:.2f}s")
```

### Optimization Tips

1. **Use async/await** for I/O operations
2. **Cache frequent queries** in Redis
3. **Optimize Neo4j queries** with indexes
4. **Limit memory retrieval** to relevant memories only
5. **Use connection pooling** for databases
6. **Monitor with logging** to find bottlenecks

---

## Frontend Development

### JavaScript Structure

**Main file:** `static/js/script.js`

**Key functions:**
- `sendMessage()` - Send chat message
- `addMessage()` - Add message to UI
- `parseMarkdown()` - Render markdown
- `loadUserDomains()` - Load domain list
- `getUserId()` / `getSessionId()` - Get IDs from storage

### CSS Structure

**Main file:** `static/css/style.css`

**Sections:**
- Variables (colors, spacing)
- Layout
- Components (buttons, inputs, modals)
- Animations
- Responsive design

### Making UI Changes

1. Edit HTML in `templates/index.html`
2. Add styles in `static/css/style.css`
3. Add behavior in `static/js/script.js`
4. Test in browser with DevTools open
5. Check responsive design on mobile

---

## Deployment

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t mem0-chatbot .
docker run -p 5000:5000 --env-file .env mem0-chatbot
```

### Production Checklist

- [ ] Set strong passwords for databases
- [ ] Enable HTTPS/SSL
- [ ] Add authentication
- [ ] Implement rate limiting
- [ ] Set up monitoring
- [ ] Configure logging
- [ ] Use production database instances
- [ ] Set up backups
- [ ] Configure CORS properly
- [ ] Use secrets management
- [ ] Add health checks
- [ ] Set up CI/CD pipeline

---

## Contributing

### Git Workflow

1. **Create feature branch**
```bash
git checkout -b feature/new-feature
```

2. **Make changes and commit**
```bash
git add .
git commit -m "Add new feature: description"
```

3. **Push and create pull request**
```bash
git push origin feature/new-feature
```

### Commit Message Format

```
Type: Brief description

Detailed description of changes.

- Bullet point 1
- Bullet point 2
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

### Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG
5. Request code review
6. Address review comments
7. Merge when approved

---

## Useful Commands

### Development

```bash
# Run app with auto-reload
python main.py

# Check Python version
python --version

# Install new package
uv add package-name

# Update dependencies
uv sync
```

### Database

```bash
# Start all databases
docker start redis-stack neo4j

# Stop all databases
docker stop redis-stack neo4j

# View database logs
docker logs redis-stack
docker logs neo4j
```

### Debugging

```bash
# View application logs
tail -f logs/app.log

# Check Python path
python -c "import sys; print(sys.path)"

# List installed packages
pip list
```

---

## Resources

### Documentation

- Project README: `../README.md`
- API Documentation: `./API.md`
- Architecture: `./ARCHITECTURE.md`

### External Resources

- FastAPI: https://fastapi.tiangolo.com
- Mem0: https://docs.mem0.ai
- Neo4j: https://neo4j.com/docs
- Redis: https://redis.io/docs
- Python: https://docs.python.org

### Community

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share ideas

---

## Troubleshooting Guide

### Port Already in Use

```bash
# Find process using port
lsof -i :5000  # On Linux/Mac
netstat -ano | findstr :5000  # On Windows

# Kill process
kill -9 <PID>  # On Linux/Mac
taskkill /PID <PID> /F  # On Windows
```

### Module Import Errors

```bash
# Reinstall dependencies
uv sync --reinstall

# Check if in virtual environment
which python  # Should show venv path
```

### Database Connection Issues

```bash
# Test Redis connection
docker exec -it redis-stack redis-cli ping

# Test Neo4j connection
python tests/test_neo4j.py
```

---

## Best Practices

### Code Quality

1. Write clear, self-documenting code
2. Add comments for complex logic
3. Use type hints consistently
4. Follow DRY principle
5. Keep functions small and focused
6. Handle errors gracefully
7. Log important operations
8. Write tests for critical code

### Security

1. Never commit `.env` file
2. Validate all user inputs
3. Sanitize outputs
4. Use parameterized queries
5. Keep dependencies updated
6. Review security advisories
7. Implement proper authentication
8. Use HTTPS in production

### Performance

1. Use async operations
2. Implement caching
3. Optimize database queries
4. Monitor performance
5. Profile slow operations
6. Use connection pooling
7. Limit data transfer sizes
8. Implement pagination

---

## Next Steps

After setting up:

1. Read `README.md` for overview
2. Review `ARCHITECTURE.md` for design
3. Try example scenarios
4. Explore API with Swagger
5. Make a small change
6. Add a new feature
7. Write tests
8. Contribute back

---

## Getting Help

### Common Questions

**Q: How do I add a new endpoint?**
A: See "Adding New Features" section above

**Q: Where are memories stored?**
A: In Redis (vectors) and Neo4j (graphs)

**Q: How do I clear all data?**
A: Use Redis CLI `FLUSHALL` and Neo4j `MATCH (n) DETACH DELETE n`

**Q: Can I use a different LLM?**
A: Yes, modify `app/services/memory_service.py` config

### Support

- Check logs: `logs/app.log`
- Review documentation in `docs/`
- Search GitHub issues
- Ask in discussions
- Contact maintainers

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor logs for errors
- Check disk space
- Review performance

**Weekly:**
- Update dependencies
- Review security advisories
- Backup databases

**Monthly:**
- Clean old logs
- Optimize databases
- Review analytics

### Monitoring

Implement monitoring for:
- API response times
- Database performance
- Memory usage
- Error rates
- User activity

---

Happy coding!

