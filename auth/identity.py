"""
Identity Context: Track who does what, when, and why.

This module provides identity metadata tracking for the control plane.
Every request carries identity information for full accountability.

The goal: "This model response exists because Alice approved it under policy X at time Y."
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class IdentityMetadata(BaseModel):
    """
    Identity metadata for a request.
    
    Captures who initiated the action and all relevant context.
    This is what auditors and lawyers need to see.
    """
    user_id: str = Field(..., description="User who initiated the action")
    user_email: Optional[str] = Field(None, description="User email address")
    user_role: str = Field(..., description="User role at time of action")
    user_name: Optional[str] = Field(None, description="User full name")
    
    # Temporal context
    timestamp: str = Field(..., description="ISO 8601 timestamp when action was initiated")
    
    # Request context
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional identity metadata")
    
    @classmethod
    def from_user(
        cls,
        user,  # User model
        request_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "IdentityMetadata":
        """
        Create identity metadata from a user object.
        
        Args:
            user: User object
            request_id: Optional request correlation ID
            source_ip: Optional source IP
            user_agent: Optional user agent
            metadata: Optional additional metadata
            
        Returns:
            IdentityMetadata instance
        """
        return cls(
            user_id=user.id,
            user_email=user.email,
            user_role=user.role.value if hasattr(user.role, 'value') else str(user.role),
            user_name=user.full_name,
            timestamp=datetime.utcnow().isoformat() + "Z",
            request_id=request_id,
            source_ip=source_ip,
            user_agent=user_agent,
            metadata=metadata or {},
        )


class ActionRecord(BaseModel):
    """
    Complete record of an action with identity and decision context.
    
    This is the gold standard audit record.
    "This model response exists because Alice approved it under policy X at time Y."
    """
    # Identity: WHO
    identity: IdentityMetadata = Field(..., description="Who initiated this action")
    
    # Action: WHAT
    action_type: str = Field(..., description="Type of action (execute, approve, block, etc.)")
    action_id: str = Field(..., description="Unique action identifier")
    agent_id: Optional[str] = Field(None, description="Agent involved in the action")
    
    # Decision: WHY
    decision: str = Field(..., description="Decision made (allow, block, escalate)")
    policy_id: Optional[str] = Field(None, description="Policy that made the decision")
    policy_name: Optional[str] = Field(None, description="Human-readable policy name")
    reason: str = Field(..., description="Human-readable reason for decision")
    
    # Temporal: WHEN
    timestamp: str = Field(..., description="ISO 8601 timestamp of action")
    
    # Context: ADDITIONAL INFO
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    def to_audit_sentence(self) -> str:
        """
        Generate the gold standard audit sentence.
        
        Returns:
            Human-readable audit sentence
            
        Example:
            "This model response exists because Alice approved it under policy X at time Y."
        """
        if self.action_type == "approve":
            return (
                f"This response was approved by {self.identity.user_name or self.identity.user_id} "
                f"({self.identity.user_role}) under policy '{self.policy_name or self.policy_id}' "
                f"at {self.timestamp}."
            )
        elif self.action_type == "execute":
            if self.decision == "allow":
                return (
                    f"This response was allowed for {self.identity.user_name or self.identity.user_id} "
                    f"({self.identity.user_role}) under policy '{self.policy_name or self.policy_id}' "
                    f"at {self.timestamp}."
                )
            elif self.decision == "block":
                return (
                    f"This request was blocked for {self.identity.user_name or self.identity.user_id} "
                    f"({self.identity.user_role}) by policy '{self.policy_name or self.policy_id}' "
                    f"at {self.timestamp}. Reason: {self.reason}"
                )
        elif self.action_type == "escalate":
            return (
                f"This request was escalated for approval by {self.identity.user_name or self.identity.user_id} "
                f"({self.identity.user_role}) under policy '{self.policy_name or self.policy_id}' "
                f"at {self.timestamp}. Reason: {self.reason}"
            )
        
        # Default format
        return (
            f"Action '{self.action_type}' performed by {self.identity.user_name or self.identity.user_id} "
            f"({self.identity.user_role}) at {self.timestamp}."
        )
