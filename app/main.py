from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import ocr_controller, prompt_controller
from app.utils.middleware import APIKeyMiddleware

app = FastAPI(
    title="Trade Fast API Backend",
    description="FastAPI backend with LangChain and Gemini integration - Secured with API Key",
    version="1.0.0"
)

# API Key Authentication Middleware (must be added before CORS)
app.add_middleware(APIKeyMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ocr_controller.router)
app.include_router(prompt_controller.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Trade Fast API Backend",
        "version": "1.0.0",
        "security": "API Key authentication required for all endpoints except /, /health, /docs",
        "authentication": {
            "method": "Bearer token",
            "header": "Authorization: Bearer <your_api_key>"
        },
        "agents": {
            "ocr": "Gemini Vision OCR for text extraction and mapping",
            "prompt": "Gemini-powered prompt-based agent"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
