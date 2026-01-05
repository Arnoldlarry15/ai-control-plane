"""
Prompt Object - First-class prompt templates and versioning.

Prompts are versioned, templated, and governable artifacts.
Track prompt evolution, A/B testing, and compliance.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class PromptStatus(str, Enum):
    """Prompt status."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class PromptVariable(BaseModel):
    """Prompt variable definition."""
    
    name: str = Field(..., description="Variable name")
    description: Optional[str] = Field(None, description="Variable description")
    required: bool = Field(default=True, description="Variable is required")
    default_value: Optional[str] = Field(None, description="Default value")
    validation_pattern: Optional[str] = Field(None, description="Regex validation pattern")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "customer_name",
                "description": "Customer's full name",
                "required": True,
                "validation_pattern": "^[A-Za-z\\s]+$"
            }
        }


class PromptVersion(BaseModel):
    """Prompt version with full tracking."""
    
    version: str = Field(..., description="Version identifier (e.g., 1.0.0, 2.1.3)")
    template: str = Field(..., description="Prompt template text")
    variables: List[PromptVariable] = Field(
        default_factory=list,
        description="Variables used in this template"
    )
    
    status: PromptStatus = Field(default=PromptStatus.DRAFT, description="Version status")
    
    # Metrics
    usage_count: int = Field(default=0, description="Number of times used")
    success_rate: Optional[float] = Field(None, description="Success rate (0.0-1.0)")
    average_cost: Optional[float] = Field(None, description="Average cost per execution")
    
    # Metadata
    changelog: Optional[str] = Field(None, description="What changed in this version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Version creator")
    
    class Config:
        use_enum_values = True


class Prompt(BaseModel):
    """
    Prompt object - System of record for prompt templates.
    
    Prompts are first-class artifacts with versioning, A/B testing,
    and governance. Every prompt is tracked, every change is audited.
    """
    
    id: str = Field(..., description="Unique prompt identifier")
    name: str = Field(..., description="Prompt name")
    description: Optional[str] = Field(None, description="Prompt description")
    
    # Versions
    versions: List[PromptVersion] = Field(
        default_factory=list,
        description="All versions of this prompt"
    )
    active_version: str = Field(..., description="Currently active version")
    
    # Association
    agent_ids: List[str] = Field(
        default_factory=list,
        description="Agents using this prompt"
    )
    
    # Categorization
    category: Optional[str] = Field(None, description="Prompt category")
    use_case: Optional[str] = Field(None, description="Primary use case")
    tags: List[str] = Field(default_factory=list, description="Tags for discovery")
    
    # Governance
    requires_approval: bool = Field(
        default=False,
        description="Changes require approval"
    )
    compliance_reviewed: bool = Field(
        default=False,
        description="Has been reviewed for compliance"
    )
    compliance_notes: Optional[str] = Field(None, description="Compliance review notes")
    
    # A/B Testing
    ab_test_enabled: bool = Field(default=False, description="A/B testing enabled")
    ab_test_versions: List[str] = Field(
        default_factory=list,
        description="Versions in A/B test"
    )
    ab_test_split: Optional[Dict[str, float]] = Field(
        None,
        description="Traffic split for A/B test (version -> percentage)"
    )
    
    # Lifecycle
    status: PromptStatus = Field(default=PromptStatus.DRAFT, description="Prompt status")
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
        json_schema_extra = {
            "example": {
                "id": "customer-greeting",
                "name": "Customer Greeting Prompt",
                "description": "Standard greeting for customer interactions",
                "active_version": "1.0.0",
                "agent_ids": ["customer-support-bot"],
                "category": "customer_service",
                "use_case": "greeting",
                "requires_approval": True,
                "status": "active",
            }
        }
