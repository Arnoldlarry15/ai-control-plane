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
