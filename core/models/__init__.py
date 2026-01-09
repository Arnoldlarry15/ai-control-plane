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
AI Object Model - First-class objects for the AI Control Plane.

Everything in the system maps to one of these core objects:
- Model: AI model metadata and capabilities
- Agent: Registered AI agents
- Prompt: Prompt templates and versioning
- Request: Execution requests
- Decision: Policy evaluation decisions
- Policy: Governance rules
- Risk: Risk assessment results
- Approval: Human approval workflows
- Event: Immutable audit events

This is the "Salesforce of AI" object model - declarative, traceable, and unavoidable.
"""

from core.models.model import Model, ModelCapability, ModelProvider
from core.models.agent import Agent, AgentStatus, AgentEnvironment
from core.models.prompt import Prompt, PromptVersion, PromptVariable, PromptStatus
from core.models.request import Request, RequestStatus, RequestPriority
from core.models.decision import Decision, DecisionOutcome, PolicyEvaluation
from core.models.policy import Policy, PolicyRule, PolicyCondition, PolicyAction, PolicyScope
from core.models.risk import Risk, RiskLevel, RiskFactor, RiskCategory, RiskMitigation
from core.models.approval import Approval, ApprovalStatus, ApprovalAction, ApprovalDecision, ApprovalPriority
from core.models.event import Event, EventType, EventSeverity

__all__ = [
    # Model
    "Model",
    "ModelCapability",
    "ModelProvider",
    # Agent
    "Agent",
    "AgentStatus",
    "AgentEnvironment",
    # Prompt
    "Prompt",
    "PromptVersion",
    "PromptVariable",
    "PromptStatus",
    # Request
    "Request",
    "RequestStatus",
    "RequestPriority",
    # Decision
    "Decision",
    "DecisionOutcome",
    "PolicyEvaluation",
    # Policy
    "Policy",
    "PolicyRule",
    "PolicyCondition",
    "PolicyAction",
    "PolicyScope",
    # Risk
    "Risk",
    "RiskLevel",
    "RiskFactor",
    "RiskCategory",
    "RiskMitigation",
    # Approval
    "Approval",
    "ApprovalStatus",
    "ApprovalAction",
    "ApprovalDecision",
    "ApprovalPriority",
    # Event
    "Event",
    "EventType",
    "EventSeverity",
]
