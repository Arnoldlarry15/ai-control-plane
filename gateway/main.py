"""
Main entry point for the gateway service.

Starts the FastAPI application that serves as the control plane gateway.
"""

import logging
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gateway.routes import router
from gateway.middleware import add_middleware
from gateway.errors import register_error_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Control Plane Gateway",
    description="Centralized execution gateway for AI governance",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
add_middleware(app)

# Register error handlers
register_error_handlers(app)

# Include routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "ai-control-plane-gateway",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "gateway"}


def main(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Start the gateway server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        reload: Enable auto-reload for development
    """
    logger.info(f"Starting AI Control Plane Gateway on {host}:{port}")
    logger.info("The choke point is active. All AI execution flows through here.")
    
    uvicorn.run(
        "gateway.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Control Plane Gateway")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    main(host=args.host, port=args.port, reload=args.reload)
