"""
Policy Schemas: Data structures for policies.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PolicyCondition(BaseModel):
    """Policy condition specification."""
    
    # Text matching
    input_contains: Optional[str] = None
    input_contains_any: Optional[List[str]] = None
    input_matches_pattern: Optional[str] = None
    
    # Always trigger
    always: Optional[bool] = None


class PolicyRule(BaseModel):
    """Single policy rule."""
    
    condition: PolicyCondition
    action: str = Field(..., description="Action: allow, block, escalate, redact")
    reason: Optional[str] = Field(None, description="Human-readable reason")
    replacement: Optional[str] = Field(None, description="Replacement text for redact action")


class Policy(BaseModel):
    """Complete policy definition."""
    
    id: str = Field(..., description="Unique policy identifier")
    version: str = Field(default="1.0", description="Policy version")
    name: str = Field(..., description="Human-readable policy name")
    description: Optional[str] = Field(None, description="Policy description")
    rules: List[PolicyRule] = Field(..., description="List of policy rules")
    enabled: bool = Field(default=True, description="Policy enabled status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "no-pii",
                "version": "1.0",
                "name": "Block PII",
                "description": "Prevents PII in prompts",
                "rules": [
                    {
                        "condition": {"input_matches_pattern": "\\d{3}-\\d{2}-\\d{4}"},
                        "action": "block",
                        "reason": "SSN pattern detected",
                    }
                ],
                "enabled": True,
            }
        }
