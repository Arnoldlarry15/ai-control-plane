"""
Policy Object - Enhanced first-class policy representation.

Policies are the rules that govern AI behavior. Declarative, versioned,
and testable. This extends the existing policy model with full governance.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class PolicyAction(str, Enum):
    """Policy action types."""
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"
    REDACT = "redact"
    WARN = "warn"
    LOG = "log"


class PolicyScope(str, Enum):
    """Policy application scope."""
    GLOBAL = "global"
    AGENT = "agent"
    MODEL = "model"
    USER = "user"
    TEAM = "team"
    ENVIRONMENT = "environment"


class PolicyCondition(BaseModel):
    """
    Policy condition - declarative rule matching.
    
    Conditions are evaluated without code. Pure config.
    """
    
    # Field-based conditions
    field: Optional[str] = Field(None, description="Field to evaluate (e.g., 'model', 'risk_score')")
    
    # Comparison operators
    equals: Optional[Any] = Field(None, description="Exact match")
    not_equals: Optional[Any] = Field(None, description="Not equal")
    in_list: Optional[List[Any]] = Field(None, description="Value in list", alias="in")
    not_in_list: Optional[List[Any]] = Field(None, description="Value not in list", alias="not_in")
    greater_than: Optional[float] = Field(None, description="Greater than")
    less_than: Optional[float] = Field(None, description="Less than")
    greater_or_equal: Optional[float] = Field(None, description="Greater than or equal")
    less_or_equal: Optional[float] = Field(None, description="Less than or equal")
    
    # Pattern matching
    matches_pattern: Optional[str] = Field(None, description="Regex pattern match")
    contains: Optional[str] = Field(None, description="Contains substring")
    contains_any: Optional[List[str]] = Field(None, description="Contains any of these")
    contains_all: Optional[List[str]] = Field(None, description="Contains all of these")
    
    # Logical operators
    and_conditions: Optional[List["PolicyCondition"]] = Field(
        None,
        description="All conditions must match",
        alias="and"
    )
    or_conditions: Optional[List["PolicyCondition"]] = Field(
        None,
        description="Any condition must match",
        alias="or"
    )
    not_condition: Optional["PolicyCondition"] = Field(
        None,
        description="Condition must not match",
        alias="not"
    )
    
    # Always/Never
    always: Optional[bool] = Field(None, description="Always match")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "field": "risk_score",
                "greater_than": 70
            }
        }


class PolicyRule(BaseModel):
    """Policy rule with condition and action."""
    
    name: Optional[str] = Field(None, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    
    # Condition
    when: PolicyCondition = Field(..., description="When to trigger this rule", alias="condition")
    
    # Action
    then: PolicyAction = Field(..., description="Action to take", alias="action")
    
    # Reason
    reason: str = Field(..., description="Human-readable reason for this action")
    
    # Redaction (if action is redact)
    replacement: Optional[str] = Field(None, description="Replacement text for redaction")
    
    # Metadata
    enabled: bool = Field(default=True, description="Rule is enabled")
    priority: int = Field(default=0, description="Rule priority (higher = evaluated first)")
    
    class Config:
        populate_by_name = True


class Policy(BaseModel):
    """
    Policy object - System of record for governance rules.
    
    Policies are declarative, versioned, and testable.
    No Python code required. Pure configuration.
    """
    
    # Identity
    id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    version: str = Field(default="1.0", description="Policy version")
    
    # Rules
    rules: List[PolicyRule] = Field(..., description="Policy rules")
    
    # Scope
    scope: PolicyScope = Field(default=PolicyScope.GLOBAL, description="Policy scope")
    applies_to: List[str] = Field(
        default_factory=list,
        description="What this policy applies to (agent IDs, model names, etc.)"
    )
    
    # Compliance
    compliance_standard: Optional[str] = Field(
        None,
        description="Compliance standard (GDPR, HIPAA, SOC2, etc.)"
    )
    regulatory_reference: Optional[str] = Field(
        None,
        description="Regulatory reference (e.g., 'GDPR Article 22')"
    )
    
    # Lifecycle
    enabled: bool = Field(default=True, description="Policy is enabled")
    enforce: bool = Field(default=True, description="Enforce (true) or monitor only (false)")
    
    # Priority
    priority: int = Field(
        default=100,
        description="Policy priority (higher = evaluated first)"
    )
    
    # Testing
    dry_run: bool = Field(default=False, description="Dry run mode (log only, don't enforce)")
    
    # Metadata
    category: Optional[str] = Field(None, description="Policy category")
    tags: List[str] = Field(default_factory=list, description="Tags for discovery")
    
    # Ownership
    owner: Optional[str] = Field(None, description="Policy owner")
    reviewers: List[str] = Field(default_factory=list, description="Required reviewers")
    last_reviewed_at: Optional[datetime] = Field(None, description="Last review date")
    review_required_by: Optional[datetime] = Field(None, description="Next review due date")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Creator identifier")
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        use_enum_values = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "high-risk-approval",
                "name": "High Risk Approval Required",
                "description": "Require approval for high-risk operations",
                "version": "1.0",
                "rules": [
                    {
                        "when": {"field": "risk_score", "greater_than": 70},
                        "then": "escalate",
                        "reason": "Risk score exceeds threshold"
                    }
                ],
                "scope": "global",
                "enabled": True,
                "enforce": True,
                "priority": 200,
            }
        }
