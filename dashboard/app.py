"""
Dashboard Application

Web-based UI for monitoring AI Control Plane.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)


class DashboardApp:
    """
    Web-based dashboard for AI Control Plane observability.
    
    Provides:
    - Real-time metrics
    - Audit log viewer
    - Policy violation charts
    - Agent status monitor
    - Kill switch controls
    """
    
    def __init__(self, gateway_service=None):
        self.app = FastAPI(title="AI Control Plane Dashboard")
        self.gateway_service = gateway_service
        
        # Set up templates and static files
        base_path = Path(__file__).parent
        self.templates = Jinja2Templates(directory=str(base_path / "templates"))
        
        # Add routes
        self._setup_routes()
        
        logger.info("Dashboard initialized")
    
    def _setup_routes(self):
        """Set up dashboard routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Main dashboard view"""
            stats = self._get_stats()
            return self.templates.TemplateResponse(
                "dashboard.html",
                {"request": request, "stats": stats}
            )
        
        @self.app.get("/api/stats")
        async def get_stats():
            """Get current statistics"""
            return self._get_stats()
        
        @self.app.get("/api/recent_events")
        async def get_recent_events():
            """Get recent audit events"""
            return self._get_recent_events()
        
        @self.app.get("/health")
        async def health():
            """Health check"""
            return {"status": "healthy"}
    
    def _get_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        # Mock data - in production, fetch from observability service
        return {
            "total_executions": 1234,
            "policy_violations": 42,
            "active_agents": 15,
            "kill_switch_active": False,
            "avg_response_time_ms": 245,
            "success_rate": 98.5,
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    def _get_recent_events(self) -> List[Dict[str, Any]]:
        """Get recent audit events"""
        # Mock data - in production, fetch from observability service
        return [
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "event_type": "execution",
                "agent_id": "agent-1",
                "user": "alice@example.com",
                "status": "success",
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                "event_type": "policy_violation",
                "agent_id": "agent-2",
                "user": "bob@example.com",
                "policy": "no-pii",
                "status": "blocked",
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                "event_type": "execution",
                "agent_id": "agent-3",
                "user": "charlie@example.com",
                "status": "success",
            },
        ]


def create_dashboard_app() -> FastAPI:
    """Create and configure dashboard app"""
    dashboard = DashboardApp()
    return dashboard.app
