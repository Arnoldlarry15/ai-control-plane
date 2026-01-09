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
