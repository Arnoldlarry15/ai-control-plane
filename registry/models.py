"""
Registry Models: Data structures for AI agents and models.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Agent(BaseModel):
    """Agent registration model."""
    
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    model: str = Field(..., description="AI model (e.g., gpt-3.5-turbo)")
    risk_level: str = Field(default="medium", description="Risk level: low, medium, high, critical")
    policies: List[str] = Field(default_factory=list, description="Applied policy IDs")
    environment: str = Field(default="dev", description="Environment: dev, staging, prod")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: float = Field(..., description="Creation timestamp")
    updated_at: float = Field(..., description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="Creator identifier")
    version: str = Field(default="1.0.0", description="Agent version")
    active: bool = Field(default=True, description="Agent active status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "customer-support-bot",
                "name": "Customer Support Bot",
                "model": "gpt-3.5-turbo",
                "risk_level": "medium",
                "policies": ["no-pii", "business-hours"],
                "environment": "prod",
                "version": "1.0.0",
                "active": True,
            }
        }
