"""
Mem0 Chatbot - FastAPI Application Instance

This FastAPI application provides a memory-powered chatbot interface using:
- Mem0 for long-term memory (LTM) with Neo4j graph storage
- Redis for short-term memory (STM) and message history
- OpenAI for AI responses
"""

import warnings
import uvicorn
warnings.filterwarnings("ignore")

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# from app.api.routes import endpoints


# FastAPI App Initialization
app = FastAPI(
    title="Mem0 Chatbot API",
    description="Memory-powered AI chatbot with Neo4j + Redis backend",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

print("Mem0 Chatbot API Starting...")
print("Memory Service will initialize when first route is imported")
print("API Docs: http://localhost:5000/docs")
print("App running at: http://localhost:5000")


# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Enable CORS for all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Templates Setup
templates = Jinja2Templates(directory="templates")


# Frontend Route
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def index(request: Request):
    """
    Serve the main chatbot HTML page
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        TemplateResponse: Rendered HTML page
    """
    return templates.TemplateResponse(request=request, name="index.html")


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint for Docker healthcheck"""
    return {"status": "healthy", "service": "mem0-chatbot", "version": "1.0.0"}


# Include API Router (lazy load to avoid blocking startup)


# # Include API Router
# # app.include_router(endpoints.router)

# Include API Router (lazy load to avoid startup delays)
@app.on_event("startup")
async def startup_event():
    from app.api.routes import endpoints
    app.include_router(endpoints.router)
    print("✅ API routes loaded successfully")

# Mount Static Files (Must be after routes)
app.mount("/static", StaticFiles(directory="static"), name="static")



if __name__ == '__main__':
    # Run the FastAPI app with Uvicorn server
    uvicorn.run(
        "main:app",  # App is defined in this file
        host="0.0.0.0",  # Listen on all interfaces
        port=5000,  # Port number
        reload=True,  # Auto-reload on code changes
        log_level="info",  # Logging level
        access_log=False  # Disable access logs to reduce clutter
    )

