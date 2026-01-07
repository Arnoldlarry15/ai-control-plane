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
Decision Object - First-class policy decision representation.

Every policy evaluation produces a Decision. This is the audit trail
of WHY something was allowed, blocked, or escalated.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class DecisionOutcome(str, Enum):
    """Policy decision outcome."""
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"
    REDACT = "redact"
    WARN = "warn"


class PolicyEvaluation(BaseModel):
    """Individual policy evaluation result."""
    
    policy_id: str = Field(..., description="Policy identifier")
    policy_name: str = Field(..., description="Policy name")
    policy_version: Optional[str] = Field(None, description="Policy version")
    
    matched: bool = Field(..., description="Policy condition matched")
    action: str = Field(..., description="Action: allow, block, escalate, etc.")
    reason: Optional[str] = Field(None, description="Human-readable reason")
    
    # Rule details
    rule_index: Optional[int] = Field(None, description="Rule index that matched")
    condition_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed condition evaluation"
    )
    
    # Timing
    evaluation_time_ms: Optional[float] = Field(None, description="Time to evaluate (ms)")


class Decision(BaseModel):
    """
    Decision object - System of record for policy decisions.
    
    Every AI request gets a decision. This is the "why" behind every allow/block.
    Immutable, explainable, and legally defensible.
    """
    
    # Identity
    id: str = Field(..., description="Unique decision identifier")
    request_id: str = Field(..., description="Associated request ID")
    
    # Final decision
    outcome: DecisionOutcome = Field(..., description="Final decision outcome")
    action: str = Field(..., description="Action taken: allow, block, escalate, etc.")
    
    # Reasoning
    reason: str = Field(..., description="Primary reason for this decision")
    explanation: Optional[str] = Field(
        None,
        description="Detailed plain-English explanation"
    )
    
    # Policy chain
    policies_evaluated: List[PolicyEvaluation] = Field(
        default_factory=list,
        description="All policies evaluated in order"
    )
    triggered_policy_id: Optional[str] = Field(
        None,
        description="Policy that triggered the final decision"
    )
    
    # Risk assessment
    risk_score: Optional[float] = Field(None, description="Risk score (0-100)")
    risk_level: Optional[str] = Field(None, description="Risk level: low, medium, high, critical")
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Factors contributing to risk score"
    )
    
    # Compliance
    compliance_checks: List[str] = Field(
        default_factory=list,
        description="Compliance checks performed"
    )
    compliance_violations: List[str] = Field(
        default_factory=list,
        description="Compliance violations detected"
    )
    
    # Context
    agent_id: str = Field(..., description="Agent for this decision")
    user_id: Optional[str] = Field(None, description="User who made the request")
    model: str = Field(..., description="Model being used")
    
    # Approval (if escalated)
    requires_approval: bool = Field(default=False, description="Decision requires approval")
    approval_id: Optional[str] = Field(None, description="Approval request ID")
    approval_reason: Optional[str] = Field(None, description="Why approval is required")
    
    # Redaction (if applicable)
    redacted_content: List[str] = Field(
        default_factory=list,
        description="Content that was redacted"
    )
    redaction_reasons: List[str] = Field(
        default_factory=list,
        description="Reasons for redaction"
    )
    
    # Metrics
    total_evaluation_time_ms: Optional[float] = Field(
        None,
        description="Total time to evaluate all policies (ms)"
    )
    policies_evaluated_count: int = Field(
        default=0,
        description="Number of policies evaluated"
    )
    
    # Confidence
    confidence: Optional[float] = Field(
        None,
        description="Decision confidence (0.0-1.0)"
    )
    uncertainty_factors: List[str] = Field(
        default_factory=list,
        description="Factors causing uncertainty"
    )
    
    # Overrides
    overridden: bool = Field(default=False, description="Decision was overridden")
    overridden_by: Optional[str] = Field(None, description="Who overrode the decision")
    overridden_at: Optional[datetime] = Field(None, description="When it was overridden")
    override_reason: Optional[str] = Field(None, description="Reason for override")
    original_outcome: Optional[str] = Field(None, description="Original decision outcome")
    
    # Timestamps (immutable)
    decided_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional decision metadata"
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "dec_xyz789",
                "request_id": "req_abc123",
                "outcome": "allow",
                "action": "allow",
                "reason": "All policies passed",
                "explanation": "Request evaluated against 3 policies. No violations detected. Risk score is low.",
                "risk_score": 15.5,
                "risk_level": "low",
                "agent_id": "customer-support-bot",
                "model": "gpt-4",
                "requires_approval": False,
                "total_evaluation_time_ms": 45.2,
                "policies_evaluated_count": 3,
                "confidence": 0.95,
            }
        }
