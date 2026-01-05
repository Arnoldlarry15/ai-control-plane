"""
Model Object - First-class AI model representation.

Represents an AI model with its capabilities, limitations, and governance requirements.
Every AI model used in the system must be registered as a Model object.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ModelCapability(str, Enum):
    """Model capability types."""
    TEXT_GENERATION = "text_generation"
    TEXT_COMPLETION = "text_completion"
    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"
    IMAGE_UNDERSTANDING = "image_understanding"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_GENERATION = "audio_generation"
    FUNCTION_CALLING = "function_calling"
    JSON_MODE = "json_mode"


class ModelProvider(str, Enum):
    """Model provider."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    AWS = "aws"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"
    LOCAL = "local"


class Model(BaseModel):
    """
    Model object - System of record for AI models.
    
    Every AI model has governance requirements, cost implications,
    and risk profiles. This is the first-class representation.
    """
    
    id: str = Field(..., description="Unique model identifier")
    name: str = Field(..., description="Model name (e.g., gpt-4, claude-3)")
    provider: ModelProvider = Field(..., description="Model provider")
    version: Optional[str] = Field(None, description="Model version")
    
    # Capabilities
    capabilities: List[ModelCapability] = Field(
        default_factory=list,
        description="What this model can do"
    )
    
    # Technical specs
    context_window: Optional[int] = Field(None, description="Max context length in tokens")
    max_output_tokens: Optional[int] = Field(None, description="Max output length in tokens")
    supports_streaming: bool = Field(default=True, description="Supports streaming responses")
    supports_functions: bool = Field(default=False, description="Supports function calling")
    
    # Cost (per 1K tokens)
    input_cost_per_1k: Optional[float] = Field(None, description="Input cost per 1K tokens (USD)")
    output_cost_per_1k: Optional[float] = Field(None, description="Output cost per 1K tokens (USD)")
    
    # Governance
    default_risk_level: str = Field(
        default="medium",
        description="Default risk level: low, medium, high, critical"
    )
    required_policies: List[str] = Field(
        default_factory=list,
        description="Policies that must be applied to this model"
    )
    compliance_certifications: List[str] = Field(
        default_factory=list,
        description="Compliance standards this model meets (e.g., HIPAA, SOC2)"
    )
    
    # Limits
    rate_limit_rpm: Optional[int] = Field(None, description="Rate limit (requests per minute)")
    rate_limit_tpm: Optional[int] = Field(None, description="Rate limit (tokens per minute)")
    daily_cost_limit: Optional[float] = Field(None, description="Daily cost limit (USD)")
    
    # Metadata
    description: Optional[str] = Field(None, description="Model description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    endpoint_url: Optional[str] = Field(None, description="API endpoint URL")
    api_key_required: bool = Field(default=True, description="Requires API key")
    
    # Lifecycle
    active: bool = Field(default=True, description="Model is active and available")
    deprecated: bool = Field(default=False, description="Model is deprecated")
    deprecated_reason: Optional[str] = Field(None, description="Deprecation reason")
    sunset_date: Optional[datetime] = Field(None, description="Planned end-of-life date")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Creator identifier")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional model-specific metadata"
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "provider": "openai",
                "version": "gpt-4-1106-preview",
                "capabilities": ["text_generation", "chat", "function_calling", "json_mode"],
                "context_window": 128000,
                "max_output_tokens": 4096,
                "supports_streaming": True,
                "supports_functions": True,
                "input_cost_per_1k": 0.01,
                "output_cost_per_1k": 0.03,
                "default_risk_level": "high",
                "required_policies": ["no-pii", "cost-control"],
                "compliance_certifications": ["SOC2"],
                "rate_limit_rpm": 500,
                "rate_limit_tpm": 150000,
                "active": True,
                "deprecated": False,
            }
        }
