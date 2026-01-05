"""
Approval Workflow Configuration and Escalation

Defines approval workflows, timeout rules, and escalation paths for
human-in-the-loop AI governance.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta


class EscalationLevel(str, Enum):
    """Escalation levels for approvals"""
    L1 = "l1"  # First-level approver
    L2 = "l2"  # Manager/supervisor
    L3 = "l3"  # Director/executive
    L4 = "l4"  # C-level/board


class ApprovalOutcome(str, Enum):
    """Possible outcomes of approval process"""
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class EscalationRule(BaseModel):
    """Rule for when to escalate an approval"""
    
    rule_id: str
    name: str
    description: str
    
    # Conditions for escalation
    timeout_seconds: Optional[int] = Field(
        None,
        description="Escalate if not reviewed within this time"
    )
    rejection_count: Optional[int] = Field(
        None,
        description="Escalate after this many rejections"
    )
    risk_level_threshold: Optional[str] = Field(
        None,
        description="Escalate if risk level is above this (high, critical)"
    )
    
    # Escalation target
    escalate_to_level: EscalationLevel
    escalate_to_roles: List[str] = Field(
        default_factory=list,
        description="Specific roles to escalate to"
    )
    
    # Actions on escalation
    notify_users: List[str] = Field(
        default_factory=list,
        description="Users to notify on escalation"
    )
    
    max_escalation_attempts: int = Field(
        default=3,
        description="Maximum number of escalation attempts before auto-rejection"
    )


class ApprovalWorkflow(BaseModel):
    """
    Approval workflow configuration.
    
    Defines who can approve, timeout rules, and escalation paths.
    """
    
    workflow_id: str
    name: str
    description: str
    
    # Approval requirements
    required_approver_roles: List[str] = Field(
        default_factory=list,
        description="Roles that can approve (e.g., ['approver', 'admin'])"
    )
    required_approvals: int = Field(
        default=1,
        description="Number of approvals required"
    )
    
    # Timeout configuration
    timeout_seconds: int = Field(
        default=3600,  # 1 hour default
        description="Time before approval request times out"
    )
    timeout_action: str = Field(
        default="escalate",
        description="Action on timeout: escalate, reject, or approve"
    )
    
    # Escalation rules
    escalation_rules: List[EscalationRule] = Field(
        default_factory=list,
        description="Rules for escalating approvals"
    )
    
    # Decision rationale
    require_rationale: bool = Field(
        default=True,
        description="Require approvers to provide rationale"
    )
    preserve_full_history: bool = Field(
        default=True,
        description="Preserve complete decision history in audit log"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    def is_user_authorized(self, user_role: str) -> bool:
        """Check if user role is authorized to approve"""
        return user_role in self.required_approver_roles
    
    def is_expired(self, requested_at: datetime) -> bool:
        """Check if approval request has expired"""
        expiry_time = requested_at + timedelta(seconds=self.timeout_seconds)
        return datetime.utcnow() >= expiry_time
    
    def should_escalate(
        self,
        requested_at: datetime,
        rejection_count: int,
        risk_level: Optional[str] = None
    ) -> Optional[EscalationRule]:
        """
        Check if approval should be escalated.
        
        Returns the escalation rule to apply, or None if no escalation needed.
        """
        for rule in self.escalation_rules:
            # Check timeout
            if rule.timeout_seconds:
                timeout_threshold = requested_at + timedelta(seconds=rule.timeout_seconds)
                if datetime.utcnow() >= timeout_threshold:
                    return rule
            
            # Check rejection count
            if rule.rejection_count and rejection_count >= rule.rejection_count:
                return rule
            
            # Check risk level
            if rule.risk_level_threshold and risk_level:
                risk_levels = ["low", "medium", "high", "critical"]
                if risk_levels.index(risk_level) >= risk_levels.index(rule.risk_level_threshold):
                    return rule
        
        return None


class ApprovalDecisionRecord(BaseModel):
    """
    Complete record of an approval decision.
    
    Preserves full rationale and decision chain for compliance.
    """
    
    record_id: str
    approval_id: str
    decision: ApprovalOutcome
    
    # Decision details
    decided_at: datetime
    decided_by: str
    decided_by_role: str
    rationale: str
    
    # Context
    risk_level: Optional[str] = None
    escalation_level: Optional[EscalationLevel] = None
    previous_decisions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="History of previous decisions (rejections, escalations)"
    )
    
    # Supporting information
    reviewed_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context information reviewed by approver"
    )
    supporting_documents: List[str] = Field(
        default_factory=list,
        description="References to supporting documentation"
    )
    
    # Compliance metadata
    workflow_id: str
    compliance_standards: List[str] = Field(
        default_factory=list,
        description="Compliance standards this decision satisfies"
    )
    
    def to_audit_log_entry(self) -> Dict[str, Any]:
        """Convert to audit log entry format"""
        return {
            "record_id": self.record_id,
            "approval_id": self.approval_id,
            "decision": self.decision,
            "decided_at": self.decided_at.isoformat(),
            "decided_by": self.decided_by,
            "decided_by_role": self.decided_by_role,
            "rationale": self.rationale,
            "risk_level": self.risk_level,
            "escalation_level": self.escalation_level,
            "previous_decisions": self.previous_decisions,
            "reviewed_context": self.reviewed_context,
            "supporting_documents": self.supporting_documents,
            "workflow_id": self.workflow_id,
            "compliance_standards": self.compliance_standards,
        }


# Pre-defined workflows
DEFAULT_WORKFLOWS = {
    "standard": ApprovalWorkflow(
        workflow_id="standard",
        name="Standard Approval",
        description="Standard single-approver workflow with 1-hour timeout",
        required_approver_roles=["approver", "admin"],
        required_approvals=1,
        timeout_seconds=3600,
        timeout_action="escalate",
        escalation_rules=[
            EscalationRule(
                rule_id="timeout-escalation",
                name="Timeout Escalation",
                description="Escalate to L2 after 1 hour",
                timeout_seconds=3600,
                escalate_to_level=EscalationLevel.L2,
                escalate_to_roles=["admin"],
                max_escalation_attempts=2,
            )
        ],
    ),
    "high-risk": ApprovalWorkflow(
        workflow_id="high-risk",
        name="High-Risk Approval",
        description="Multi-level approval for high-risk AI operations",
        required_approver_roles=["approver", "admin"],
        required_approvals=2,
        timeout_seconds=1800,  # 30 minutes
        timeout_action="escalate",
        escalation_rules=[
            EscalationRule(
                rule_id="immediate-escalation",
                name="Immediate High-Risk Escalation",
                description="Escalate high-risk immediately to L2",
                risk_level_threshold="high",
                escalate_to_level=EscalationLevel.L2,
                escalate_to_roles=["admin"],
                max_escalation_attempts=3,
            ),
            EscalationRule(
                rule_id="timeout-escalation",
                name="Timeout Escalation to L3",
                description="Escalate to L3 after 30 minutes",
                timeout_seconds=1800,
                escalate_to_level=EscalationLevel.L3,
                escalate_to_roles=["admin"],
                max_escalation_attempts=2,
            ),
        ],
    ),
    "critical": ApprovalWorkflow(
        workflow_id="critical",
        name="Critical System Approval",
        description="Executive-level approval for critical AI systems",
        required_approver_roles=["admin"],
        required_approvals=2,
        timeout_seconds=900,  # 15 minutes
        timeout_action="escalate",
        escalation_rules=[
            EscalationRule(
                rule_id="immediate-executive-escalation",
                name="Immediate Executive Escalation",
                description="Escalate critical systems to L4 immediately",
                risk_level_threshold="critical",
                escalate_to_level=EscalationLevel.L4,
                escalate_to_roles=["admin"],
                max_escalation_attempts=1,
            ),
        ],
    ),
}
