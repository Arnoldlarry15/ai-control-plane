# Copyright 2024 AI Control Plane Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Approval Object - Enhanced first-class approval workflow representation.

Human-in-the-loop is a first-class operation. Every approval request
is tracked, timed, and traceable.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    """Approval request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ApprovalAction(str, Enum):
    """Approval action types."""
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    REQUEST_INFO = "request_info"


class ApprovalPriority(str, Enum):
    """Approval priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ApprovalDecision(BaseModel):
    """Individual approver's decision."""
    
    approver_id: str = Field(..., description="Approver user ID")
    approver_name: Optional[str] = Field(None, description="Approver name")
    approver_email: Optional[str] = Field(None, description="Approver email")
    
    action: ApprovalAction = Field(..., description="Decision action")
    comment: Optional[str] = Field(None, description="Approver comment")
    reason: Optional[str] = Field(None, description="Reason for decision")
    
    decided_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class EscalationRule(BaseModel):
    """Escalation rule definition."""
    
    condition: str = Field(..., description="When to escalate (timeout, rejection, etc.)")
    escalate_to: List[str] = Field(..., description="User IDs to escalate to")
    escalate_after_minutes: Optional[int] = Field(None, description="Auto-escalate after N minutes")


class Approval(BaseModel):
    """
    Approval object - System of record for human-in-the-loop workflows.
    
    High-risk AI decisions require human judgment. This is the complete
    approval workflow with queues, timeouts, and escalation paths.
    """
    
    # Identity
    id: str = Field(..., description="Unique approval identifier")
    request_id: str = Field(..., description="Associated request ID")
    execution_id: Optional[str] = Field(None, description="Execution ID (same as request_id)")
    
    # Source
    agent_id: str = Field(..., description="Agent requesting approval")
    user_id: Optional[str] = Field(None, description="User who made the original request")
    user_email: Optional[str] = Field(None, description="User email")
    
    # Content
    prompt: str = Field(..., description="Prompt requiring approval")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Request context"
    )
    
    # Reason for approval
    reason: str = Field(..., description="Why approval is required")
    policy_id: Optional[str] = Field(None, description="Policy that triggered approval")
    risk_score: Optional[float] = Field(None, description="Risk score")
    risk_level: Optional[str] = Field(None, description="Risk level")
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Risk factors"
    )
    
    # Status
    status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING,
        description="Current status"
    )
    priority: ApprovalPriority = Field(
        default=ApprovalPriority.NORMAL,
        description="Approval priority"
    )
    
    # Approvers
    required_approvers: List[str] = Field(
        default_factory=list,
        description="Required approver IDs"
    )
    optional_approvers: List[str] = Field(
        default_factory=list,
        description="Optional approver IDs"
    )
    approvals_required: int = Field(
        default=1,
        description="Number of approvals required"
    )
    
    # Decisions
    decisions: List[ApprovalDecision] = Field(
        default_factory=list,
        description="Approver decisions"
    )
    
    # Final decision
    final_decision: Optional[ApprovalAction] = Field(
        None,
        description="Final approval decision"
    )
    final_approver: Optional[str] = Field(
        None,
        description="Final approver ID"
    )
    final_comment: Optional[str] = Field(
        None,
        description="Final approver comment"
    )
    
    # Timeouts
    timeout_minutes: int = Field(
        default=60,
        description="Timeout in minutes"
    )
    timeout_action: str = Field(
        default="reject",
        description="Action on timeout: reject, approve, escalate"
    )
    
    # Escalation
    escalation_rules: List[EscalationRule] = Field(
        default_factory=list,
        description="Escalation rules"
    )
    escalated: bool = Field(default=False, description="Was escalated")
    escalated_to: List[str] = Field(
        default_factory=list,
        description="User IDs escalated to"
    )
    escalated_at: Optional[datetime] = Field(None, description="Escalation timestamp")
    escalation_count: int = Field(default=0, description="Number of escalations")
    
    # Queue
    queue_id: Optional[str] = Field(None, description="Approval queue ID")
    queue_position: Optional[int] = Field(None, description="Position in queue")
    
    # Notifications
    notification_sent: bool = Field(default=False, description="Notification sent to approvers")
    notification_sent_at: Optional[datetime] = Field(None, description="When notification sent")
    reminder_count: int = Field(default=0, description="Reminder notifications sent")
    last_reminder_at: Optional[datetime] = Field(None, description="Last reminder timestamp")
    
    # Timestamps
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = Field(None, description="When reviewed")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    
    # Metrics
    time_to_review_seconds: Optional[int] = Field(
        None,
        description="Time from request to first review"
    )
    total_review_time_seconds: Optional[int] = Field(
        None,
        description="Total time from request to completion"
    )
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "appr_xyz123",
                "request_id": "req_abc456",
                "agent_id": "customer-support-bot",
                "user_id": "user_789",
                "prompt": "Process this sensitive customer data...",
                "reason": "High risk score detected",
                "policy_id": "high-risk-approval",
                "risk_score": 85.5,
                "risk_level": "high",
                "status": "pending",
                "priority": "high",
                "required_approvers": ["manager_123"],
                "approvals_required": 1,
                "timeout_minutes": 30,
                "timeout_action": "reject",
            }
        }
