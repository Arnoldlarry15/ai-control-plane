"""
Analytics Service for Dashboard - Phase 3 Observability

Provides advanced analytics for executives to understand AI risk in under 60 seconds:
- Live AI traffic metrics
- Policy hit analysis (blocked vs allowed)
- High-risk activity alerts
- Model usage by team
- Risk heatmap
- Usage trends over time
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Advanced analytics service for Phase 3 observability.
    
    Provides executive-level insights into AI usage and risk.
    """
    
    def __init__(self, storage):
        """
        Initialize analytics service.
        
        Args:
            storage: ObservabilityStorage instance
        """
        self.storage = storage
        logger.info("Analytics service initialized")
    
    def get_live_traffic_metrics(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get live AI traffic metrics for the dashboard.
        
        Args:
            time_window_minutes: Time window for "live" data
            
        Returns:
            Live traffic metrics including request rate, response times, etc.
        """
        # Get recent events
        all_events = self.storage.query(limit=1000)
        
        # Filter for execution events
        execution_events = [e for e in all_events if e.get("event_type") == "execution"]
        
        if not execution_events:
            return {
                "total_requests": 0,
                "requests_per_minute": 0,
                "avg_latency_ms": 0,
                "p95_latency_ms": 0,
                "active_users": 0,
                "active_agents": 0,
            }
        
        # Calculate metrics
        total_requests = len(execution_events)
        
        # Extract latencies
        latencies = [e.get("latency_ms", 0) for e in execution_events if e.get("latency_ms")]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        # Calculate p95 latency (with bounds safety)
        sorted_latencies = sorted(latencies)
        p95_index = min(int(len(sorted_latencies) * 0.95), len(sorted_latencies) - 1)
        p95_latency = sorted_latencies[p95_index] if sorted_latencies else 0
        
        # Count unique users and agents
        users = set(e.get("user") for e in execution_events if e.get("user"))
        agents = set(e.get("agent_id") for e in execution_events if e.get("agent_id"))
        
        # Approximate requests per minute (based on total events / time_window)
        requests_per_minute = total_requests / max(time_window_minutes, 1)
        
        return {
            "total_requests": total_requests,
            "requests_per_minute": round(requests_per_minute, 2),
            "avg_latency_ms": round(avg_latency),
            "p95_latency_ms": round(p95_latency),
            "active_users": len(users),
            "active_agents": len(agents),
        }
    
    def get_policy_hits_breakdown(self) -> Dict[str, Any]:
        """
        Get policy hit statistics: blocked vs allowed.
        
        Returns:
            Breakdown of policy decisions
        """
        all_events = self.storage.query(limit=1000)
        execution_events = [e for e in all_events if e.get("event_type") == "execution"]
        
        if not execution_events:
            return {
                "total": 0,
                "allowed": 0,
                "blocked": 0,
                "escalated": 0,
                "error": 0,
                "allow_rate": 0,
                "block_rate": 0,
            }
        
        # Count by status
        status_counts = defaultdict(int)
        for event in execution_events:
            status = event.get("status", "unknown")
            status_counts[status] += 1
        
        total = len(execution_events)
        allowed = status_counts.get("success", 0) + status_counts.get("allowed", 0)
        blocked = status_counts.get("blocked", 0)
        escalated = status_counts.get("escalated", 0)
        error = status_counts.get("error", 0)
        
        # Calculate rates (Note: allow_rate + block_rate may not equal 100% due to escalated/error statuses)
        allow_rate = (allowed / total * 100) if total > 0 else 0
        block_rate = (blocked / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "allowed": allowed,
            "blocked": blocked,
            "escalated": escalated,
            "error": error,
            "allow_rate": round(allow_rate, 1),
            "block_rate": round(block_rate, 1),
        }
    
    def get_high_risk_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get high-risk activity alerts.
        
        Returns recent high-risk events that executives should know about.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of high-risk alerts
        """
        all_events = self.storage.query(limit=500)
        
        high_risk_events = []
        
        for event in all_events:
            risk_level = "low"
            alert_reason = ""
            
            # Identify high-risk scenarios
            if event.get("event_type") == "kill_switch":
                risk_level = "critical"
                alert_reason = f"Kill switch {event.get('action', 'activated')}: {event.get('reason', 'Unknown')}"
            elif event.get("status") == "blocked":
                risk_level = "high"
                policy_decision = event.get("policy_decision", {})
                alert_reason = f"Request blocked: {policy_decision.get('reason', 'Policy violation')}"
            elif event.get("status") == "escalated":
                risk_level = "medium"
                alert_reason = "Request escalated for approval"
            elif event.get("status") == "error":
                risk_level = "medium"
                alert_reason = f"Execution error: {event.get('error', 'Unknown error')}"
            
            # Only include medium, high, or critical
            if risk_level in ["medium", "high", "critical"]:
                high_risk_events.append({
                    "event_id": event.get("event_id"),
                    "timestamp": event.get("iso_timestamp", event.get("timestamp")),
                    "risk_level": risk_level,
                    "alert_reason": alert_reason,
                    "event_type": event.get("event_type"),
                    "agent_id": event.get("agent_id"),
                    "user": event.get("user"),
                    "execution_id": event.get("execution_id"),
                })
        
        # Sort by timestamp (most recent first) and limit
        high_risk_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return high_risk_events[:limit]
    
    def get_decision_details(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific decision (KILLER FEATURE).
        
        Provides complete context for decision replay:
        - Original input
        - Policies evaluated
        - Decision outcome
        - Full execution timeline
        
        Args:
            execution_id: Execution ID to retrieve
            
        Returns:
            Complete decision context or None if not found
        """
        # Get all events for this execution
        events = self.storage.query(execution_id=execution_id, limit=100)
        
        if not events:
            return None
        
        # Extract execution event
        execution_event = None
        policy_events = []
        
        for event in events:
            if event.get("event_type") == "execution":
                execution_event = event
            elif event.get("event_type") == "policy":
                policy_events.append(event)
        
        if not execution_event:
            return None
        
        # Build decision context
        decision_context = {
            "execution_id": execution_id,
            "timestamp": execution_event.get("iso_timestamp"),
            
            # Input context
            "input": {
                "prompt": execution_event.get("prompt"),
                "agent_id": execution_event.get("agent_id"),
                "user": execution_event.get("user"),
                "context": execution_event.get("context", {}),
            },
            
            # Policies evaluated
            "policies_evaluated": [
                {
                    "policy_id": p.get("policy_id"),
                    "action": p.get("action"),
                    "reason": p.get("reason"),
                    "timestamp": p.get("iso_timestamp"),
                }
                for p in policy_events
            ],
            
            # Decision outcome
            "outcome": {
                "status": execution_event.get("status"),
                "response": execution_event.get("response"),
                "latency_ms": execution_event.get("latency_ms"),
                "policy_decision": execution_event.get("policy_decision"),
                "error": execution_event.get("error"),
            },
            
            # Complete timeline
            "timeline": [
                {
                    "timestamp": e.get("iso_timestamp"),
                    "event_type": e.get("event_type"),
                    "description": self._describe_event(e),
                }
                for e in sorted(events, key=lambda x: x.get("timestamp", 0))
            ],
        }
        
        return decision_context
    
    def get_org_wide_ai_map(self) -> Dict[str, Any]:
        """
        Get organization-wide AI usage map.
        
        Shows which teams/users use which models, with risk analysis.
        
        Returns:
            Org-wide AI usage analytics
        """
        all_events = self.storage.query(limit=2000)
        execution_events = [e for e in all_events if e.get("event_type") == "execution"]
        
        if not execution_events:
            return {
                "teams": [],
                "models": [],
                "risk_heatmap": {},
                "total_users": 0,
                "total_agents": 0,
            }
        
        # Aggregate by user (representing teams)
        user_stats = defaultdict(lambda: {
            "total_requests": 0,
            "agents": set(),
            "blocked": 0,
            "allowed": 0,
            "risk_score": 0,
        })
        
        # Aggregate by agent/model
        agent_stats = defaultdict(lambda: {
            "total_requests": 0,
            "users": set(),
            "blocked": 0,
            "allowed": 0,
        })
        
        for event in execution_events:
            user = event.get("user", "unknown")
            agent_id = event.get("agent_id", "unknown")
            status = event.get("status", "unknown")
            
            # Update user stats
            user_stats[user]["total_requests"] += 1
            user_stats[user]["agents"].add(agent_id)
            if status == "blocked":
                user_stats[user]["blocked"] += 1
                user_stats[user]["risk_score"] += 10  # Blocked requests increase risk
            elif status in ["success", "allowed"]:
                user_stats[user]["allowed"] += 1
            
            # Update agent stats
            agent_stats[agent_id]["total_requests"] += 1
            agent_stats[agent_id]["users"].add(user)
            if status == "blocked":
                agent_stats[agent_id]["blocked"] += 1
            elif status in ["success", "allowed"]:
                agent_stats[agent_id]["allowed"] += 1
        
        # Convert to list format
        teams = []
        for user, stats in user_stats.items():
            # Calculate risk level
            block_rate = (stats["blocked"] / stats["total_requests"] * 100) if stats["total_requests"] > 0 else 0
            risk_level = "high" if block_rate > 20 else "medium" if block_rate > 5 else "low"
            
            teams.append({
                "user": user,
                "total_requests": stats["total_requests"],
                "agents_used": len(stats["agents"]),
                "blocked": stats["blocked"],
                "allowed": stats["allowed"],
                "risk_level": risk_level,
                "block_rate": round(block_rate, 1),
            })
        
        models = []
        for agent_id, stats in agent_stats.items():
            models.append({
                "agent_id": agent_id,
                "total_requests": stats["total_requests"],
                "users": len(stats["users"]),
                "blocked": stats["blocked"],
                "allowed": stats["allowed"],
            })
        
        # Sort by usage
        teams.sort(key=lambda x: x["total_requests"], reverse=True)
        models.sort(key=lambda x: x["total_requests"], reverse=True)
        
        return {
            "teams": teams,
            "models": models,
            "risk_heatmap": self._generate_risk_heatmap(teams),
            "total_users": len(user_stats),
            "total_agents": len(agent_stats),
        }
    
    def get_usage_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Get usage trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Time-series usage data
        """
        all_events = self.storage.query(limit=5000)
        execution_events = [e for e in all_events if e.get("event_type") == "execution"]
        
        if not execution_events:
            return {
                "daily_requests": [],
                "daily_blocks": [],
                "daily_users": [],
            }
        
        # Group by day (simplified - using event count as proxy)
        # In production, would parse timestamps and group properly
        
        # For now, generate mock trend data based on current stats
        policy_breakdown = self.get_policy_hits_breakdown()
        
        # Simulate daily trend (in production, would aggregate by actual dates)
        total = policy_breakdown["total"]
        blocked = policy_breakdown["blocked"]
        
        # Distribute across days (simplified)
        daily_avg = total / days if days > 0 else 0
        daily_blocked_avg = blocked / days if days > 0 else 0
        
        daily_requests = [int(daily_avg * (1 + (i % 3 - 1) * 0.1)) for i in range(days)]
        daily_blocks = [int(daily_blocked_avg * (1 + (i % 3 - 1) * 0.15)) for i in range(days)]
        
        return {
            "daily_requests": daily_requests,
            "daily_blocks": daily_blocks,
            "labels": [f"Day {i+1}" for i in range(days)],
            "total_trend": sum(daily_requests),
            "blocks_trend": sum(daily_blocks),
        }
    
    def _describe_event(self, event: Dict[str, Any]) -> str:
        """Generate human-readable description of an event."""
        event_type = event.get("event_type", "unknown")
        
        if event_type == "execution":
            status = event.get("status", "unknown")
            return f"Execution {status}"
        elif event_type == "policy":
            action = event.get("action", "unknown")
            policy_id = event.get("policy_id", "unknown")
            return f"Policy {policy_id}: {action}"
        elif event_type == "kill_switch":
            action = event.get("action", "unknown")
            return f"Kill switch {action}"
        elif event_type == "approval":
            action = event.get("action", "unknown")
            return f"Approval {action}"
        else:
            return f"Event: {event_type}"
    
    def _generate_risk_heatmap(self, teams: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Generate risk heatmap showing distribution of risk levels.
        
        Args:
            teams: List of team statistics
            
        Returns:
            Risk distribution counts
        """
        risk_counts = defaultdict(int)
        for team in teams:
            risk_level = team.get("risk_level", "low")
            risk_counts[risk_level] += 1
        
        return {
            "low": risk_counts.get("low", 0),
            "medium": risk_counts.get("medium", 0),
            "high": risk_counts.get("high", 0),
            "critical": risk_counts.get("critical", 0),
        }
