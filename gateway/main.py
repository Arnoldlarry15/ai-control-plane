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
    description="Production-Grade AI Governance Platform - The Operating System for Enterprise AI",
    version="1.0.0",
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

# Mount dashboard
try:
    from dashboard.app import create_dashboard_app
    from gateway.services import get_registry, get_observability_logger, get_kill_switch
    
    dashboard_app = create_dashboard_app(
        registry_service=get_registry(),
        obs_logger=get_observability_logger(),
        kill_switch_service=get_kill_switch(),
    )
    app.mount("/dashboard", dashboard_app)
    logger.info("Dashboard mounted at /dashboard")
except Exception as e:
    logger.warning(f"Dashboard not mounted: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "ai-control-plane-gateway",
        "version": "1.0.0",
        "status": "operational",
        "description": "Production-Grade AI Governance Platform",
        "endpoints": {
            "api_docs": "/api/docs",
            "dashboard": "/dashboard",
            "health": "/health",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "gateway", "version": "1.0.0"}


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
