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
Decision Model - Canonical policy decision output.

Every policy evaluation produces exactly one of three outcomes:
- ALLOW: Proceed automatically
- DENY: Block immediately  
- REVIEW: Pause and require human approval

Everything else is metadata.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class DecisionType(str, Enum):
    """
    Canonical decision outcomes.
    
    These three values are the only possible outcomes.
    No ambiguity, no "maybe", no "probably allowed".
    """
    ALLOW = "ALLOW"
    DENY = "DENY"
    REVIEW = "REVIEW"


@dataclass
class PolicyDecision:
    """
    Policy decision output.
    
    This is what gets logged, audited, replayed, and simulated.
    Always structured. Always logged. Never ambiguous.
    
    Attributes:
        decision: The final decision (ALLOW, DENY, or REVIEW)
        matched_policies: List of policy IDs that matched
        reason: Human-readable explanation for the decision
    """
    
    decision: DecisionType
    matched_policies: List[str]
    reason: str
    
    def __post_init__(self):
        """Validate decision on initialization."""
        if not isinstance(self.decision, DecisionType):
            raise ValueError(f"decision must be DecisionType, got {type(self.decision)}")
        
        if not isinstance(self.matched_policies, list):
            raise ValueError("matched_policies must be a list")
        
        if not self.reason:
            raise ValueError("reason is required")
