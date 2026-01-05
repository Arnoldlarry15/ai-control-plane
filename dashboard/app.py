"""
Dashboard Application

Web-based UI for monitoring AI Control Plane.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
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
    - Compliance status
    """
    
    def __init__(self, registry_service=None, obs_logger=None, kill_switch_service=None):
        self.app = FastAPI(title="AI Control Plane Dashboard")
        self.registry_service = registry_service
        self.obs_logger = obs_logger
        self.kill_switch_service = kill_switch_service
        
        # Set up templates and static files
        base_path = Path(__file__).parent
        self.templates = Jinja2Templates(directory=str(base_path / "templates"))
        
        # Add routes
        self._setup_routes()
        
        logger.info("Dashboard initialized with service integrations")
    
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
        
        @self.app.get("/api/agents")
        async def get_agents():
            """Get all registered agents"""
            if self.registry_service:
                agents = self.registry_service.list_agents()
                return {
                    "agents": [
                        {
                            "id": agent.id,
                            "name": agent.name,
                            "model": agent.model,
                            "risk_level": agent.risk_level,
                            "status": agent.status,
                        }
                        for agent in agents
                    ],
                    "total": len(agents),
                }
            return {"agents": [], "total": 0}
        
        @self.app.get("/api/compliance/status")
        async def get_compliance_status():
            """Get compliance status summary"""
            return self._get_compliance_status()
        
        @self.app.get("/health")
        async def health():
            """Health check"""
            return {"status": "healthy"}
    
    def _get_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        stats = {
            "total_executions": 0,
            "policy_violations": 0,
            "active_agents": 0,
            "kill_switch_active": False,
            "avg_response_time_ms": 0,
            "success_rate": 100.0,
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        # Get real data from services if available
        if self.registry_service:
            agents = self.registry_service.list_agents()
            stats["active_agents"] = len([a for a in agents if a.status == "active"])
        
        if self.kill_switch_service:
            stats["kill_switch_active"] = self.kill_switch_service.is_active()
        
        if self.obs_logger:
            try:
                # Get logs from the last 24 hours
                logs = self.obs_logger.get_recent_logs(limit=1000)
                stats["total_executions"] = len(logs)
                
                # Count violations
                violations = [log for log in logs if log.get("event_type") == "policy_violation"]
                stats["policy_violations"] = len(violations)
                
                # Calculate success rate
                successful = [log for log in logs if log.get("status") == "success"]
                if logs:
                    stats["success_rate"] = round((len(successful) / len(logs)) * 100, 1)
                
                # Calculate average response time
                response_times = [
                    log.get("response_time_ms", 0) 
                    for log in logs 
                    if log.get("response_time_ms")
                ]
                if response_times:
                    stats["avg_response_time_ms"] = round(sum(response_times) / len(response_times))
            except Exception as e:
                logger.warning(f"Error fetching logs for stats: {e}")
        
        return stats
    
    def _get_recent_events(self) -> List[Dict[str, Any]]:
        """Get recent audit events"""
        events = []
        
        if self.obs_logger:
            try:
                logs = self.obs_logger.get_recent_logs(limit=50)
                events = [
                    {
                        "timestamp": log.get("timestamp", datetime.utcnow().isoformat()),
                        "event_type": log.get("event_type", "unknown"),
                        "agent_id": log.get("agent_id", "unknown"),
                        "user": log.get("user", "system"),
                        "status": log.get("status", "unknown"),
                        "policy": log.get("policy"),
                    }
                    for log in logs
                ]
            except Exception as e:
                logger.warning(f"Error fetching recent events: {e}")
        
        # Fallback to mock data if no real data available
        if not events:
            events = [
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    "event_type": "execution",
                    "agent_id": "agent-1",
                    "user": "alice@company.test",
                    "status": "success",
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                    "event_type": "policy_violation",
                    "agent_id": "agent-2",
                    "user": "bob@company.test",
                    "policy": "no-pii",
                    "status": "blocked",
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                    "event_type": "execution",
                    "agent_id": "agent-3",
                    "user": "charlie@company.test",
                    "status": "success",
                },
            ]
        
        return events
    
    def _get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status summary"""
        try:
            from policy.compliance.validator import get_compliance_validator
            
            validator = get_compliance_validator()
            standards = validator.get_compliance_standards()
            
            return {
                "standards": [
                    {
                        "id": std_id,
                        "name": std_id.upper(),
                        "status": "active",
                        "description": desc,
                    }
                    for std_id, desc in standards.items()
                ],
                "total_standards": len(standards),
                "compliant": True,
            }
        except Exception as e:
            logger.error(f"Error getting compliance status: {e}")
            return {
                "standards": [],
                "total_standards": 0,
                "compliant": True,
                "error": str(e),
            }


def create_dashboard_app(
    registry_service=None,
    obs_logger=None, 
    kill_switch_service=None
) -> FastAPI:
    """Create and configure dashboard app"""
    dashboard = DashboardApp(
        registry_service=registry_service,
        obs_logger=obs_logger,
        kill_switch_service=kill_switch_service,
    )
    return dashboard.app
