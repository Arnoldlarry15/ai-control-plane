"""
Observability Events: Structured event definitions.

Every event is logged. Period.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Event(BaseModel):
    """Base event structure."""
    
    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Event type")
    timestamp: float = Field(..., description="Unix timestamp")
    iso_timestamp: str = Field(..., description="ISO 8601 timestamp")


class ExecutionEvent(Event):
    """AI execution event."""
    
    event_type: str = "execution"
    execution_id: str
    agent_id: str
    user: Optional[str] = None
    prompt: str
    response: Optional[str] = None
    status: str  # success, blocked, pending_approval, error
    latency_ms: int
    policy_decision: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PolicyEvent(Event):
    """Policy evaluation event."""
    
    event_type: str = "policy"
    execution_id: str
    policy_id: str
    action: str  # allow, block, escalate
    reason: Optional[str] = None
    agent_id: str
    user: Optional[str] = None


class KillSwitchEvent(Event):
    """Kill switch activation/deactivation event."""
    
    event_type: str = "kill_switch"
    action: str  # activate, deactivate
    scope: str  # global, agent
    agent_id: Optional[str] = None
    reason: str
    activated_by: Optional[str] = None


class ApprovalEvent(Event):
    """Approval workflow event."""
    
    event_type: str = "approval"
    approval_id: str
    execution_id: str
    action: str  # requested, approved, rejected, timeout
    reviewer: Optional[str] = None
    comment: Optional[str] = None
