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
Risk Object - First-class risk assessment representation.

Risk scoring is a first-class operation. Every request gets a risk score.
Track factors, recommendations, and mitigation strategies.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    """Risk category types."""
    PII_EXPOSURE = "pii_exposure"
    DATA_LEAKAGE = "data_leakage"
    COST = "cost"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    BIAS = "bias"
    TOXICITY = "toxicity"
    HALLUCINATION = "hallucination"
    JAILBREAK = "jailbreak"
    PROMPT_INJECTION = "prompt_injection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MODEL_MISUSE = "model_misuse"


class RiskFactor(BaseModel):
    """Individual risk factor contribution."""
    
    category: RiskCategory = Field(..., description="Risk category")
    name: str = Field(..., description="Factor name")
    description: Optional[str] = Field(None, description="Factor description")
    
    score: float = Field(..., description="Factor score (0-100)")
    weight: float = Field(default=1.0, description="Factor weight in overall score")
    confidence: Optional[float] = Field(None, description="Confidence in this assessment (0-1)")
    
    detected_patterns: List[str] = Field(
        default_factory=list,
        description="Patterns that triggered this factor"
    )
    
    class Config:
        use_enum_values = True


class RiskMitigation(BaseModel):
    """Risk mitigation recommendation."""
    
    action: str = Field(..., description="Recommended action")
    reason: str = Field(..., description="Why this mitigation is recommended")
    priority: str = Field(default="normal", description="Priority: low, normal, high, critical")
    automated: bool = Field(default=False, description="Can be automatically applied")


class Risk(BaseModel):
    """
    Risk object - System of record for risk assessments.
    
    Every request is scored for risk. This is the complete risk profile
    with factors, confidence, and recommendations.
    """
    
    # Identity
    id: str = Field(..., description="Unique risk assessment identifier")
    request_id: str = Field(..., description="Associated request ID")
    
    # Overall risk
    score: float = Field(..., description="Overall risk score (0-100)")
    level: RiskLevel = Field(..., description="Risk level classification")
    
    # Factors
    factors: List[RiskFactor] = Field(
        default_factory=list,
        description="Individual risk factors"
    )
    
    # Categories (aggregated)
    category_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Scores by category"
    )
    highest_risk_category: Optional[RiskCategory] = Field(
        None,
        description="Category with highest risk"
    )
    
    # Confidence
    confidence: float = Field(..., description="Overall confidence in assessment (0-1)")
    uncertainty_factors: List[str] = Field(
        default_factory=list,
        description="Factors causing uncertainty"
    )
    
    # Mitigations
    mitigations: List[RiskMitigation] = Field(
        default_factory=list,
        description="Recommended mitigations"
    )
    
    # Context
    agent_id: str = Field(..., description="Agent being assessed")
    model: str = Field(..., description="Model being used")
    user_id: Optional[str] = Field(None, description="User making the request")
    
    # Scoring method
    scorer_id: str = Field(..., description="Risk scorer identifier")
    scorer_version: Optional[str] = Field(None, description="Risk scorer version")
    scoring_method: Optional[str] = Field(None, description="Scoring methodology")
    
    # Comparison
    baseline_score: Optional[float] = Field(
        None,
        description="Baseline/expected risk score for this type of request"
    )
    score_delta: Optional[float] = Field(
        None,
        description="Difference from baseline"
    )
    
    # Historical context
    user_average_risk: Optional[float] = Field(
        None,
        description="User's average risk score"
    )
    agent_average_risk: Optional[float] = Field(
        None,
        description="Agent's average risk score"
    )
    
    # Thresholds
    threshold_low: float = Field(default=30.0, description="Low risk threshold")
    threshold_medium: float = Field(default=50.0, description="Medium risk threshold")
    threshold_high: float = Field(default=70.0, description="High risk threshold")
    
    # Actions triggered
    triggers_approval: bool = Field(
        default=False,
        description="Risk level triggers approval requirement"
    )
    triggers_block: bool = Field(
        default=False,
        description="Risk level triggers automatic block"
    )
    triggers_alert: bool = Field(
        default=False,
        description="Risk level triggers alert"
    )
    
    # Metrics
    calculation_time_ms: Optional[float] = Field(
        None,
        description="Time to calculate risk score (ms)"
    )
    
    # Timestamps
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional risk metadata"
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "risk_abc123",
                "request_id": "req_xyz789",
                "score": 65.5,
                "level": "medium",
                "factors": [
                    {
                        "category": "pii_exposure",
                        "name": "Potential SSN Pattern",
                        "score": 80.0,
                        "weight": 1.5
                    }
                ],
                "confidence": 0.85,
                "agent_id": "customer-support-bot",
                "model": "gpt-4",
                "scorer_id": "default-risk-scorer",
                "triggers_approval": False,
                "triggers_block": False,
                "triggers_alert": True,
            }
        }
