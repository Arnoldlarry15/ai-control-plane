"""
Event Object - Enhanced immutable event representation.

Events are the immutable audit trail. Every action creates an event.
Hash-chained, cryptographically verifiable, and legally defensible.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event type classifications."""
    # Request lifecycle
    REQUEST_SUBMITTED = "request.submitted"
    REQUEST_VALIDATED = "request.validated"
    REQUEST_EXECUTING = "request.executing"
    REQUEST_COMPLETED = "request.completed"
    REQUEST_FAILED = "request.failed"
    REQUEST_BLOCKED = "request.blocked"
    
    # Policy events
    POLICY_EVALUATED = "policy.evaluated"
    POLICY_MATCHED = "policy.matched"
    POLICY_VIOLATED = "policy.violated"
    POLICY_CREATED = "policy.created"
    POLICY_UPDATED = "policy.updated"
    POLICY_DELETED = "policy.deleted"
    
    # Risk events
    RISK_ASSESSED = "risk.assessed"
    RISK_THRESHOLD_EXCEEDED = "risk.threshold_exceeded"
    RISK_ANOMALY_DETECTED = "risk.anomaly_detected"
    
    # Approval events
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_REJECTED = "approval.rejected"
    APPROVAL_TIMEOUT = "approval.timeout"
    APPROVAL_ESCALATED = "approval.escalated"
    
    # Agent events
    AGENT_REGISTERED = "agent.registered"
    AGENT_UPDATED = "agent.updated"
    AGENT_DECOMMISSIONED = "agent.decommissioned"
    AGENT_SUSPENDED = "agent.suspended"
    
    # Model events
    MODEL_REGISTERED = "model.registered"
    MODEL_UPDATED = "model.updated"
    MODEL_DEPRECATED = "model.deprecated"
    
    # Kill switch events
    KILL_SWITCH_ACTIVATED = "kill_switch.activated"
    KILL_SWITCH_DEACTIVATED = "kill_switch.deactivated"
    
    # Auth events
    USER_LOGIN = "auth.login"
    USER_LOGOUT = "auth.logout"
    PERMISSION_DENIED = "auth.permission_denied"
    API_KEY_CREATED = "auth.api_key_created"
    API_KEY_REVOKED = "auth.api_key_revoked"
    
    # Compliance events
    COMPLIANCE_CHECK = "compliance.check"
    COMPLIANCE_VIOLATION = "compliance.violation"
    COMPLIANCE_REPORT = "compliance.report"
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    HEALTH_CHECK = "system.health_check"
    
    # Audit events
    AUDIT_LOG_EXPORT = "audit.export"
    AUDIT_LOG_VERIFIED = "audit.verified"
    AUDIT_LOG_TAMPERED = "audit.tampered"


class EventSeverity(str, Enum):
    """Event severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Event(BaseModel):
    """
    Event object - Immutable audit trail entry.
    
    Every action creates an event. Events are append-only, hash-chained,
    and cryptographically verifiable. This is the legal audit trail.
    """
    
    # Identity
    id: str = Field(..., description="Unique event identifier")
    event_number: Optional[int] = Field(None, description="Sequential event number")
    
    # Classification
    event_type: EventType = Field(..., description="Event type")
    category: Optional[str] = Field(None, description="Event category")
    severity: EventSeverity = Field(default=EventSeverity.INFO, description="Severity")
    
    # Core data
    message: str = Field(..., description="Human-readable event message")
    description: Optional[str] = Field(None, description="Detailed description")
    
    # Associations
    request_id: Optional[str] = Field(None, description="Associated request ID")
    agent_id: Optional[str] = Field(None, description="Associated agent ID")
    user_id: Optional[str] = Field(None, description="Associated user ID")
    policy_id: Optional[str] = Field(None, description="Associated policy ID")
    
    # Context
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data"
    )
    
    # Source
    source: Optional[str] = Field(None, description="Event source (service/component)")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    source_user_agent: Optional[str] = Field(None, description="Source user agent")
    
    # Immutability & verification
    hash: Optional[str] = Field(None, description="Event hash (SHA-256)")
    previous_hash: Optional[str] = Field(None, description="Previous event hash (chain)")
    signature: Optional[str] = Field(None, description="Cryptographic signature")
    
    # Chain verification
    chain_valid: Optional[bool] = Field(None, description="Chain integrity valid")
    verified_at: Optional[datetime] = Field(None, description="Last verification time")
    
    # Timestamps (immutable)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    timestamp_unix: Optional[float] = Field(None, description="Unix timestamp")
    timestamp_iso: Optional[str] = Field(None, description="ISO 8601 timestamp")
    
    # Retention
    retention_days: Optional[int] = Field(None, description="Retention period in days")
    archive_after_days: Optional[int] = Field(None, description="Archive after N days")
    
    # Compliance
    compliance_relevant: bool = Field(
        default=False,
        description="Relevant for compliance reporting"
    )
    compliance_standards: List[str] = Field(
        default_factory=list,
        description="Relevant compliance standards"
    )
    
    # Alerting
    alert_sent: bool = Field(default=False, description="Alert notification sent")
    alert_recipients: List[str] = Field(
        default_factory=list,
        description="Alert recipients"
    )
    
    # Correlation
    correlation_id: Optional[str] = Field(None, description="Correlation ID for related events")
    trace_id: Optional[str] = Field(None, description="Distributed trace ID")
    span_id: Optional[str] = Field(None, description="Span ID for tracing")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    # Indexing hints
    indexed_at: Optional[datetime] = Field(None, description="When indexed for search")
    searchable_text: Optional[str] = Field(None, description="Full-text search content")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "evt_abc123xyz",
                "event_number": 12345,
                "event_type": "request.completed",
                "severity": "info",
                "message": "AI request completed successfully",
                "request_id": "req_xyz789",
                "agent_id": "customer-support-bot",
                "user_id": "user_123",
                "data": {
                    "latency_ms": 1250,
                    "tokens": 150,
                    "cost": 0.0025
                },
                "source": "gateway",
                "hash": "abc123...",
                "previous_hash": "xyz789...",
                "compliance_relevant": True,
                "compliance_standards": ["SOC2", "GDPR"],
            }
        }
