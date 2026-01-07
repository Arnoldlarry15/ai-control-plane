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
Request Object - First-class execution request representation.

Every AI execution starts with a Request. This is the complete record
of what was asked, by whom, and under what context.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class RequestStatus(str, Enum):
    """Request status throughout its lifecycle."""
    SUBMITTED = "submitted"
    VALIDATING = "validating"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"


class RequestPriority(str, Enum):
    """Request priority."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Request(BaseModel):
    """
    Request object - System of record for AI execution requests.
    
    Every AI interaction starts here. Immutable, traceable, and governable.
    This is what enterprises audit, what compliance reviews, and what SLAs measure.
    """
    
    # Identity
    id: str = Field(..., description="Unique request identifier (execution_id)")
    request_number: Optional[int] = Field(None, description="Sequential request number")
    
    # Source
    agent_id: str = Field(..., description="Agent executing this request")
    user_id: Optional[str] = Field(None, description="User who initiated the request")
    user_email: Optional[str] = Field(None, description="User email")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    # Content
    prompt: str = Field(..., description="User prompt/input")
    prompt_id: Optional[str] = Field(None, description="Prompt template ID (if templated)")
    prompt_version: Optional[str] = Field(None, description="Prompt template version")
    system_prompt: Optional[str] = Field(None, description="System prompt used")
    
    # Context
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context (metadata, variables, etc.)"
    )
    
    # Model parameters
    model: str = Field(..., description="Model used")
    temperature: Optional[float] = Field(None, description="Temperature parameter")
    max_tokens: Optional[int] = Field(None, description="Max tokens parameter")
    model_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional model parameters"
    )
    
    # Governance
    policies_applied: List[str] = Field(
        default_factory=list,
        description="Policy IDs applied to this request"
    )
    compliance_standards: List[str] = Field(
        default_factory=list,
        description="Compliance standards checked"
    )
    risk_score: Optional[float] = Field(None, description="Calculated risk score (0-100)")
    risk_level: Optional[str] = Field(None, description="Risk level: low, medium, high, critical")
    
    # Status
    status: RequestStatus = Field(
        default=RequestStatus.SUBMITTED,
        description="Current request status"
    )
    priority: RequestPriority = Field(
        default=RequestPriority.NORMAL,
        description="Request priority"
    )
    
    # Approval (if required)
    requires_approval: bool = Field(default=False, description="Requires human approval")
    approval_id: Optional[str] = Field(None, description="Approval request ID")
    approval_status: Optional[str] = Field(None, description="Approval status")
    
    # Response
    response: Optional[str] = Field(None, description="AI response")
    response_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Response metadata (model info, tokens, etc.)"
    )
    
    # Metrics
    latency_ms: Optional[int] = Field(None, description="Total latency in milliseconds")
    tokens_input: Optional[int] = Field(None, description="Input tokens")
    tokens_output: Optional[int] = Field(None, description="Output tokens")
    cost: Optional[float] = Field(None, description="Cost in USD")
    
    # Errors
    error: Optional[str] = Field(None, description="Error message (if failed)")
    error_code: Optional[str] = Field(None, description="Error code")
    error_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed error information"
    )
    
    # Timestamps (immutable audit trail)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution completion time")
    
    # Source tracking
    source_ip: Optional[str] = Field(None, description="Client IP address")
    source_application: Optional[str] = Field(None, description="Source application")
    api_version: Optional[str] = Field(None, description="API version used")
    sdk_version: Optional[str] = Field(None, description="SDK version used")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "req_abc123xyz",
                "request_number": 12345,
                "agent_id": "customer-support-bot",
                "user_id": "user_123",
                "user_email": "alice@company.com",
                "prompt": "What are your business hours?",
                "model": "gpt-4",
                "policies_applied": ["no-pii", "business-hours"],
                "compliance_standards": ["GDPR", "SOC2"],
                "risk_score": 15.5,
                "risk_level": "low",
                "status": "completed",
                "priority": "normal",
                "requires_approval": False,
                "latency_ms": 1250,
                "tokens_input": 50,
                "tokens_output": 100,
                "cost": 0.0025,
            }
        }
