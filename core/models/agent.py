"""
Agent Object - Enhanced first-class AI agent representation.

Represents a registered AI agent with full governance context.
This extends the existing registry model with the complete object model.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DECOMMISSIONED = "decommissioned"


class AgentEnvironment(str, Enum):
    """Deployment environment."""
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"
    TEST = "test"


class Agent(BaseModel):
    """
    Agent object - System of record for AI agents.
    
    An agent is a configured instance of an AI model with specific policies,
    risk profiles, and governance requirements. This is the entity that executes.
    """
    
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    
    # Model association
    model_id: str = Field(..., description="Model ID this agent uses")
    model: str = Field(..., description="Model name (e.g., gpt-4, claude-3)")
    
    # Environment
    environment: AgentEnvironment = Field(
        default=AgentEnvironment.DEVELOPMENT,
        description="Deployment environment"
    )
    status: AgentStatus = Field(
        default=AgentStatus.ACTIVE,
        description="Agent status"
    )
    
    # Governance
    risk_level: str = Field(
        default="medium",
        description="Risk level: low, medium, high, critical"
    )
    policies: List[str] = Field(
        default_factory=list,
        description="Applied policy IDs"
    )
    compliance_requirements: List[str] = Field(
        default_factory=list,
        description="Required compliance standards (GDPR, HIPAA, etc.)"
    )
    
    # Ownership
    owner: Optional[str] = Field(None, description="Agent owner (user/team)")
    team: Optional[str] = Field(None, description="Team responsible for this agent")
    department: Optional[str] = Field(None, description="Department")
    cost_center: Optional[str] = Field(None, description="Cost center for billing")
    
    # Configuration
    system_prompt: Optional[str] = Field(None, description="System prompt template")
    default_temperature: Optional[float] = Field(None, description="Default temperature")
    default_max_tokens: Optional[int] = Field(None, description="Default max tokens")
    
    # Limits
    rate_limit_rpm: Optional[int] = Field(None, description="Rate limit (requests per minute)")
    daily_cost_limit: Optional[float] = Field(None, description="Daily cost limit (USD)")
    monthly_cost_limit: Optional[float] = Field(None, description="Monthly cost limit (USD)")
    
    # Usage tracking
    total_requests: int = Field(default=0, description="Total requests executed")
    total_cost: float = Field(default=0.0, description="Total cost incurred (USD)")
    last_used_at: Optional[datetime] = Field(None, description="Last execution timestamp")
    
    # Approval requirements
    require_approval: bool = Field(
        default=False,
        description="All requests require human approval"
    )
    approval_policy: Optional[str] = Field(
        None,
        description="Approval policy ID (if custom approval logic)"
    )
    
    # Monitoring
    alert_on_high_cost: bool = Field(default=True, description="Alert on high cost")
    alert_on_policy_violation: bool = Field(default=True, description="Alert on violations")
    alert_recipients: List[str] = Field(
        default_factory=list,
        description="Alert recipient emails"
    )
    
    # Lifecycle
    version: str = Field(default="1.0.0", description="Agent version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Creator identifier")
    
    # Metadata
    description: Optional[str] = Field(None, description="Agent description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional agent-specific metadata"
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "customer-support-bot",
                "name": "Customer Support Bot",
                "model_id": "gpt-4-turbo",
                "model": "gpt-4",
                "environment": "prod",
                "status": "active",
                "risk_level": "medium",
                "policies": ["no-pii", "business-hours", "cost-control"],
                "compliance_requirements": ["GDPR", "SOC2"],
                "owner": "support-team@company.com",
                "team": "Customer Support",
                "department": "Customer Success",
                "require_approval": False,
                "alert_on_high_cost": True,
                "version": "1.0.0",
            }
        }
