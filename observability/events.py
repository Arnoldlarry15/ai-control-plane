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
Observability Events: Structured event definitions.

Every event is logged. Period.

Enhanced for Phase 3: These are now decision records, not just logs.
Answer human questions: Why was this blocked? Who approved this? Which policy fired?
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class Event(BaseModel):
    """Base event structure."""
    
    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Event type")
    timestamp: float = Field(..., description="Unix timestamp")
    iso_timestamp: str = Field(..., description="ISO 8601 timestamp")
    
    # Identity context - WHO did this
    identity: Optional[Dict[str, Any]] = Field(None, description="Identity metadata for this event")


class ExecutionEvent(Event):
    """
    AI execution event - now a decision record.
    
    Answers:
    - What happened?
    - Who initiated it?
    - Why was it allowed/blocked?
    - Which policy fired?
    """
    
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
    
    # Decision record fields - Answer human questions
    decision_reason: Optional[str] = Field(None, description="Human-readable reason for the decision")
    policy_id: Optional[str] = Field(None, description="Policy that made the decision")
    policy_name: Optional[str] = Field(None, description="Human-readable policy name")
    approver_id: Optional[str] = Field(None, description="Who approved this (if escalated)")
    approval_timestamp: Optional[str] = Field(None, description="When was this approved")
    
    def get_decision_summary(self) -> str:
        """Get human-readable decision summary."""
        if self.status == "success":
            return f"Allowed by policy '{self.policy_name or self.policy_id or 'default'}'"
        elif self.status == "blocked":
            return f"Blocked by policy '{self.policy_name or self.policy_id}': {self.decision_reason}"
        elif self.status == "pending_approval":
            return f"Requires approval: {self.decision_reason}"
        else:
            return f"Status: {self.status}"


class PolicyEvent(Event):
    """
    Policy evaluation event - now a decision record.
    
    Answers:
    - Which policy fired?
    - Why did it fire?
    - What was the decision?
    """
    
    event_type: str = "policy"
    execution_id: str
    policy_id: str
    policy_name: Optional[str] = Field(None, description="Human-readable policy name")
    action: str  # allow, block, escalate
    reason: Optional[str] = None
    agent_id: str
    user: Optional[str] = None
    
    # Decision context
    policy_conditions: Optional[List[str]] = Field(None, description="Conditions that were evaluated")
    matched_conditions: Optional[List[str]] = Field(None, description="Conditions that matched")
    
    def get_why_fired(self) -> str:
        """Answer: Why did this policy fire?"""
        if self.matched_conditions:
            return f"Policy '{self.policy_name or self.policy_id}' fired because: {', '.join(self.matched_conditions)}"
        return f"Policy '{self.policy_name or self.policy_id}' fired: {self.reason or 'No specific reason provided'}"


class KillSwitchEvent(Event):
    """Kill switch activation/deactivation event."""
    
    event_type: str = "kill_switch"
    action: str  # activate, deactivate
    scope: str  # global, agent
    agent_id: Optional[str] = None
    reason: str
    activated_by: Optional[str] = None


class ApprovalEvent(Event):
    """
    Approval workflow event - tracks who approved what.
    
    Answers:
    - Who approved this?
    - When was it approved?
    - Under what policy?
    """
    
    event_type: str = "approval"
    approval_id: str
    execution_id: str
    action: str  # requested, approved, rejected, timeout
    reviewer: Optional[str] = None
    reviewer_name: Optional[str] = Field(None, description="Human-readable reviewer name")
    reviewer_role: Optional[str] = Field(None, description="Reviewer's role")
    comment: Optional[str] = None
    
    # Policy context
    policy_id: Optional[str] = Field(None, description="Policy that required approval")
    policy_name: Optional[str] = Field(None, description="Human-readable policy name")
    
    def get_approval_summary(self) -> str:
        """Get human-readable approval summary."""
        if self.action == "approved":
            approver = self.reviewer_name or self.reviewer or "Unknown"
            return f"Approved by {approver} ({self.reviewer_role}) at {self.iso_timestamp}"
        elif self.action == "rejected":
            return f"Rejected by {self.reviewer_name or self.reviewer} at {self.iso_timestamp}"
        elif self.action == "requested":
            return f"Approval requested at {self.iso_timestamp}"
        return f"Status: {self.action}"


class DecisionRecord(BaseModel):
    """
    Complete decision record for a request.
    
    This is what makes the system a "truth oracle for AI behavior".
    
    Answers all human questions:
    - Why was this blocked?
    - Who approved this?
    - Which policy fired?
    - What would have happened under a different policy?
    """
    
    execution_id: str = Field(..., description="Unique execution identifier")
    correlation_id: str = Field(..., description="Correlation ID for tracking across systems")
    
    # Timeline
    request_timestamp: str = Field(..., description="When the request was initiated")
    decision_timestamp: str = Field(..., description="When the decision was made")
    completion_timestamp: Optional[str] = Field(None, description="When the request completed")
    
    # Identity - WHO
    requester_id: str = Field(..., description="Who initiated the request")
    requester_name: Optional[str] = Field(None, description="Requester's name")
    requester_role: str = Field(..., description="Requester's role")
    approver_id: Optional[str] = Field(None, description="Who approved (if escalated)")
    approver_name: Optional[str] = Field(None, description="Approver's name")
    approver_role: Optional[str] = Field(None, description="Approver's role")
    
    # Decision - WHAT and WHY
    decision: str = Field(..., description="Final decision (allow, block, escalate)")
    reason: str = Field(..., description="Human-readable reason")
    
    # Policy - WHICH
    policy_id: Optional[str] = Field(None, description="Policy that made the decision")
    policy_name: Optional[str] = Field(None, description="Human-readable policy name")
    policies_evaluated: List[str] = Field(default_factory=list, description="All policies evaluated")
    
    # Context
    agent_id: str = Field(..., description="Agent involved")
    status: str = Field(..., description="Request status")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    def to_audit_sentence(self) -> str:
        """
        Generate the gold standard audit sentence.
        
        "This model response exists because Alice approved it under policy X at time Y."
        """
        if self.decision == "allow":
            if self.approver_id:
                return (
                    f"This model response exists because {self.approver_name or self.approver_id} "
                    f"approved it under policy '{self.policy_name or self.policy_id}' "
                    f"at {self.completion_timestamp or self.decision_timestamp}."
                )
            else:
                return (
                    f"This model response was automatically allowed for "
                    f"{self.requester_name or self.requester_id} under policy "
                    f"'{self.policy_name or self.policy_id}' at {self.decision_timestamp}."
                )
        elif self.decision == "block":
            return (
                f"This request was blocked for {self.requester_name or self.requester_id} "
                f"by policy '{self.policy_name or self.policy_id}' at {self.decision_timestamp}. "
                f"Reason: {self.reason}"
            )
        else:
            return (
                f"This request is pending approval for {self.requester_name or self.requester_id} "
                f"under policy '{self.policy_name or self.policy_id}'. Reason: {self.reason}"
            )
