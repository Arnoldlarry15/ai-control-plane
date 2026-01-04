"""
Approval Models: Data structures for approval workflows.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ApprovalRequest(BaseModel):
    """Approval request model."""
    
    approval_id: str = Field(..., description="Unique approval ID")
    execution_id: str = Field(..., description="Associated execution ID")
    agent_id: str = Field(..., description="Agent requesting approval")
    user: Optional[str] = Field(None, description="User who made the request")
    prompt: str = Field(..., description="User prompt")
    reason: str = Field(..., description="Reason approval is required")
    policy_id: Optional[str] = Field(None, description="Policy that triggered escalation")
    status: str = Field(default="pending", description="Status: pending, approved, rejected, timeout")
    requested_at: float = Field(..., description="Request timestamp")
    reviewed_at: Optional[float] = Field(None, description="Review timestamp")
    reviewer: Optional[str] = Field(None, description="Reviewer identifier")
    comment: Optional[str] = Field(None, description="Reviewer comment")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
