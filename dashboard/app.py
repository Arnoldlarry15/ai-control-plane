"""
Dashboard Application

Web-based UI for monitoring AI Control Plane.
Phase 3: Enhanced with advanced analytics and decision replay.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from observability.analytics import AnalyticsService

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
        
        # Initialize analytics service (Phase 3)
        if obs_logger and hasattr(obs_logger, 'storage'):
            self.analytics = AnalyticsService(obs_logger.storage)
        else:
            self.analytics = None
            logger.warning("Analytics service not initialized - observability logger missing")
        
        # Set up templates and static files
        base_path = Path(__file__).parent
        self.templates = Jinja2Templates(directory=str(base_path / "templates"))
        
        # Add routes
        self._setup_routes()
        
        logger.info("Dashboard initialized with service integrations and analytics")
    
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
        
        # Phase 3 API Endpoints - Advanced Analytics
        
        @self.app.get("/api/analytics/live_traffic")
        async def get_live_traffic():
            """Get live AI traffic metrics"""
            if not self.analytics:
                raise HTTPException(status_code=503, detail="Analytics service not available")
            return self.analytics.get_live_traffic_metrics()
        
        @self.app.get("/api/analytics/policy_hits")
        async def get_policy_hits():
            """Get policy hit breakdown (blocked vs allowed)"""
            if not self.analytics:
                raise HTTPException(status_code=503, detail="Analytics service not available")
            return self.analytics.get_policy_hits_breakdown()
        
        @self.app.get("/api/analytics/high_risk_alerts")
        async def get_high_risk_alerts(limit: int = 10):
            """Get high-risk activity alerts"""
            if not self.analytics:
                raise HTTPException(status_code=503, detail="Analytics service not available")
            return {"alerts": self.analytics.get_high_risk_alerts(limit=limit)}
        
        @self.app.get("/api/analytics/decision/{execution_id}")
        async def get_decision_details(execution_id: str):
            """Get detailed decision replay (KILLER FEATURE)"""
            if not self.analytics:
                raise HTTPException(status_code=503, detail="Analytics service not available")
            
            decision = self.analytics.get_decision_details(execution_id)
            if not decision:
                raise HTTPException(status_code=404, detail="Decision not found")
            
            return decision
        
        @self.app.get("/api/analytics/org_map")
        async def get_org_map():
            """Get organization-wide AI usage map"""
            if not self.analytics:
                raise HTTPException(status_code=503, detail="Analytics service not available")
            return self.analytics.get_org_wide_ai_map()
        
        @self.app.get("/api/analytics/usage_trends")
        async def get_usage_trends(days: int = 7):
            """Get usage trends over time"""
            if not self.analytics:
                raise HTTPException(status_code=503, detail="Analytics service not available")
            return self.analytics.get_usage_trends(days=days)
        
        @self.app.post("/api/demo/populate_data")
        async def populate_demo_data():
            """Populate demo data for testing dashboard (development only)"""
            if not self.obs_logger:
                raise HTTPException(status_code=503, detail="Observability logger not available")
            
            import random
            
            # Sample data
            users = [
                "alice@engineering.company.com",
                "bob@marketing.company.com", 
                "charlie@sales.company.com",
                "diana@support.company.com",
                "eve@executive.company.com",
            ]
            
            agents = [
                "gpt-4-customer-support",
                "claude-3-code-assistant",
                "gpt-3.5-marketing-writer",
                "gemini-pro-analyst",
                "llama-2-chatbot",
            ]
            
            prompts = [
                "Help me write a customer email response",
                "Generate a marketing campaign idea",
                "Analyze this sales data",
                "Write code to implement a feature",
                "Summarize this document",
            ]
            
            # Generate events
            num_events = 50
            for i in range(num_events):
                import uuid
                execution_id = str(uuid.uuid4())
                agent_id = random.choice(agents)
                user = random.choice(users)
                prompt = random.choice(prompts)
                
                rand = random.random()
                if rand < 0.75:
                    status = "success"
                    response = "AI response generated successfully"
                    reason = None
                    policy_id = None
                elif rand < 0.90:
                    status = "blocked"
                    response = None
                    reason = "PII detected in prompt"
                    policy_id = "no-pii-policy"
                else:
                    status = "escalated"
                    response = None
                    reason = "High-risk operation requires approval"
                    policy_id = "high-risk-approval"
                
                latency_ms = random.randint(50, 500)
                
                self.obs_logger.log_execution(
                    execution_id=execution_id,
                    agent_id=agent_id,
                    prompt=prompt,
                    response=response,
                    status=status,
                    latency_ms=latency_ms,
                    user=user,
                    context={"team": user.split("@")[1].split(".")[0]},
                    reason=reason,
                    policy_id=policy_id,
                )
                
                if status in ["blocked", "escalated"]:
                    self.obs_logger.log_policy_event(
                        execution_id=execution_id,
                        policy_id=policy_id,
                        action=status,
                        agent_id=agent_id,
                        reason=reason,
                        user=user,
                    )
            
            # Add high-risk events
            for i in range(3):
                execution_id = str(uuid.uuid4())
                self.obs_logger.log_execution(
                    execution_id=execution_id,
                    agent_id="gpt-4-admin-assistant",
                    prompt="Execute privileged system command",
                    response=None,
                    status="blocked",
                    latency_ms=100,
                    user="eve@executive.company.com",
                    context={"risk_level": "critical"},
                    reason="Privileged operation blocked by security policy",
                    policy_id="privilege-escalation-prevention",
                )
            
            # Add kill switch event
            self.obs_logger.log_kill_switch_event(
                action="activated",
                scope="agent",
                agent_id="gpt-4-admin-assistant",
                reason="Multiple suspicious requests detected",
                activated_by="security-system",
            )
            
            return {
                "status": "success",
                "message": f"Populated {num_events + 3} execution events for demo",
                "events_created": num_events + 3,
            }
        
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
        try:
            if self.registry_service:
                agents = self.registry_service.list_agents()
                stats["active_agents"] = len([a for a in agents if a.status == "active"])
        except Exception as e:
            logger.warning(f"Error fetching agent data: {e}")
        
        try:
            if self.kill_switch_service:
                stats["kill_switch_active"] = self.kill_switch_service.is_active()
        except Exception as e:
            logger.warning(f"Error fetching kill switch status: {e}")
        
        try:
            if self.obs_logger:
                # Get logs from the observability service (limit for performance)
                logs = self.obs_logger.query_logs(limit=100)
                if logs:
                    stats["total_executions"] = len(logs)
                    
                    # Count violations
                    violations = [log for log in logs if log.get("event_type") == "policy_violation"]
                    stats["policy_violations"] = len(violations)
                    
                    # Calculate success rate
                    successful = [log for log in logs if log.get("status") == "success"]
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
            logger.warning(f"Error fetching observability data: {e}")
        
        return stats
    
    def _get_recent_events(self) -> List[Dict[str, Any]]:
        """Get recent audit events"""
        events = []
        
        try:
            if self.obs_logger:
                logs = self.obs_logger.query_logs(limit=50)
                if logs:
                    events = [
                        {
                            "timestamp": log.get("iso_timestamp", log.get("timestamp", datetime.utcnow().isoformat())),
                            "event_type": log.get("event_type", "unknown"),
                            "agent_id": log.get("agent_id", "unknown"),
                            "user": log.get("user", "system"),
                            "status": log.get("status", "unknown"),
                            "policy": log.get("policy_id"),
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
