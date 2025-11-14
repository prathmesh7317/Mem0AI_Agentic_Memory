# API Documentation

Complete API reference for the Mem0 Chatbot application.

## Base URL

```
http://localhost:5000
```

## Interactive Documentation

- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

---

## Chat Endpoints

### Send Chat Message

Send a message and get AI response with memory context.

**Endpoint:** `POST /chat`

**Request Body:**
```json
{
  "message": "Hi, I'm John and I love Nike shoes",
  "user_id": "user_123",
  "session_id": "session_456",
  "domain_name": "ecommerce"
}
```

**Response:**
```json
{
  "response": "Hello John! I'll remember that you love Nike shoes...",
  "user_id": "user_123",
  "session_id": "session_456"
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

**Example:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me running shoes",
    "user_id": "user_123",
    "session_id": "session_456"
  }'
```

---

## Memory Management Endpoints

### Get All Memories

Retrieve all stored memories for a user.

**Endpoint:** `GET /memories?user_id={user_id}`

**Query Parameters:**
- `user_id` (required) - User identifier

**Response:**
```json
{
  "memories": [
    {
      "id": "mem_123",
      "text": "User's name is John",
      "category": "personal_info"
    },
    {
      "id": "mem_124",
      "text": "User prefers Nike shoes",
      "category": "preferences"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

**Example:**
```bash
curl http://localhost:5000/memories?user_id=user_123
```

---

### Clear Long-Term Memories

Delete all long-term memories for a user.

**Endpoint:** `POST /memories/clear`

**Request Body:**
```json
{
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "message": "All memories cleared successfully for user: user_123"
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

**Example:**
```bash
curl -X POST http://localhost:5000/memories/clear \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123"}'
```

---

### Clear Session History

Clear short-term session history.

**Endpoint:** `POST /session/clear`

**Request Body:**
```json
{
  "session_id": "session_456"
}
```

**Response:**
```json
{
  "message": "Session history cleared successfully for session: session_456"
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

**Example:**
```bash
curl -X POST http://localhost:5000/session/clear \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session_456"}'
```

---

## Domain Catalog Endpoints

### Get User Domains

Get list of all domain names for a user.

**Endpoint:** `GET /domain/user?user_id={user_id}`

**Query Parameters:**
- `user_id` (required) - User identifier

**Response:**
```json
{
  "user_id": "user_123",
  "domains": ["ecommerce", "travel", "healthcare"]
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

**Example:**
```bash
curl http://localhost:5000/domain/user?user_id=user_123
```

---

### Add Domain Catalog

Create a new domain catalog for a user.

**Endpoint:** `POST /domain/catalog`

**Request Body:**
```json
{
  "user_id": "user_123",
  "domain_name": "travel",
  "domain_catalog": "TripJack API offers flight bookings and hotel reservations. Contact: travel@example.com"
}
```

**Response:**
```json
{
  "message": "Domain catalog 'travel' added successfully for user user_123",
  "user_id": "user_123",
  "domain_name": "travel"
}
```

**Status Codes:**
- `201` - Created successfully
- `409` - Domain already exists
- `500` - Server error

**Example:**
```bash
curl -X POST http://localhost:5000/domain/catalog \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "domain_name": "travel",
    "domain_catalog": "TripJack API offers flight bookings..."
  }'
```

---

### Update Domain Catalog

Update an existing domain catalog.

**Endpoint:** `PUT /domain/catalog`

**Request Body:**
```json
{
  "user_id": "user_123",
  "domain_name": "travel",
  "domain_catalog": "Updated travel catalog with new features..."
}
```

**Response:**
```json
{
  "message": "Domain catalog 'travel' updated successfully for user user_123",
  "user_id": "user_123",
  "domain_name": "travel"
}
```

**Status Codes:**
- `200` - Updated successfully
- `404` - Domain not found
- `500` - Server error

**Example:**
```bash
curl -X PUT http://localhost:5000/domain/catalog \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "domain_name": "travel",
    "domain_catalog": "Updated catalog..."
  }'
```

---

### Delete Domain Catalog

Remove a domain catalog.

**Endpoint:** `DELETE /domain/catalog?user_id={user_id}&domain_name={domain_name}`

**Query Parameters:**
- `user_id` (required) - User identifier
- `domain_name` (required) - Domain name to delete

**Response:**
```json
{
  "message": "Domain catalog 'travel' deleted successfully for user user_123",
  "user_id": "user_123",
  "domain_name": "travel"
}
```

**Status Codes:**
- `200` - Deleted successfully
- `404` - Domain not found
- `500` - Server error

**Example:**
```bash
curl -X DELETE "http://localhost:5000/domain/catalog?user_id=user_123&domain_name=travel"
```

---

## System Endpoints

### Health Check

Check if the service is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "message": "Service is running"
}
```

**Status Codes:**
- `200` - Service healthy

**Example:**
```bash
curl http://localhost:5000/health
```

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

- `400` - Bad Request (invalid input)
- `404` - Not Found (resource doesn't exist)
- `409` - Conflict (resource already exists)
- `500` - Internal Server Error

---

## Request/Response Headers

### Required Headers

```
Content-Type: application/json
```

### Response Headers

```
Content-Type: application/json
```

---


## Notes

- All timestamps are in UTC
- User IDs and session IDs are strings (max 255 characters)
- Domain names must be unique per user
- Chat messages support full markdown syntax
- Memories are automatically extracted by Mem0
- Domain catalogs are automatically injected into AI prompts when relevant

