"""
FastAPI application for WhatsApp Lead Collection Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes
from app.routes.whatsapp_webhook import router as whatsapp_router

# Create FastAPI application
app = FastAPI(
    title="Dream Axis Travel Solutions - WhatsApp Lead Collection",
    description="GDPR-compliant WhatsApp chatbot for collecting truck driver leads",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(whatsapp_router, prefix="/api", tags=["whatsapp"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dream Axis Travel Solutions - WhatsApp Lead Collection API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )

