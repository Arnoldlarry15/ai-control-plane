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
Tests for core object models.

Validates that all first-class objects work correctly and maintain
the "Salesforce of AI" principles.
"""

import pytest
from datetime import datetime
from core.models import (
    Model, ModelCapability, ModelProvider,
    Agent, AgentStatus, AgentEnvironment,
    Prompt, PromptVersion, PromptVariable, PromptStatus,
    Request, RequestStatus, RequestPriority,
    Decision, DecisionOutcome, PolicyEvaluation,
    Policy, PolicyRule, PolicyCondition, PolicyAction, PolicyScope,
    Risk, RiskLevel, RiskFactor, RiskCategory, RiskMitigation,
    Approval, ApprovalStatus, ApprovalPriority, ApprovalDecision, ApprovalAction,
    Event, EventType, EventSeverity,
)


class TestModelObject:
    """Test Model object."""
    
    def test_create_model(self):
        """Test creating a model."""
        model = Model(
            id="gpt-4-turbo",
            name="GPT-4 Turbo",
            provider=ModelProvider.OPENAI,
            version="gpt-4-1106-preview",
            capabilities=[ModelCapability.CHAT, ModelCapability.FUNCTION_CALLING],
            context_window=128000,
            max_output_tokens=4096,
            input_cost_per_1k=0.01,
            output_cost_per_1k=0.03,
            default_risk_level="high",
            required_policies=["no-pii"],
        )
        
        assert model.id == "gpt-4-turbo"
        assert model.provider == ModelProvider.OPENAI
        assert ModelCapability.CHAT in model.capabilities
        assert model.active is True
        assert model.deprecated is False
    
    def test_model_with_compliance(self):
        """Test model with compliance certifications."""
        model = Model(
            id="hipaa-model",
            name="HIPAA Compliant Model",
            provider=ModelProvider.AZURE,
            compliance_certifications=["HIPAA", "SOC2"],
            default_risk_level="medium",
        )
        
        assert "HIPAA" in model.compliance_certifications
        assert model.active is True


class TestAgentObject:
    """Test Agent object."""
    
    def test_create_agent(self):
        """Test creating an agent."""
        agent = Agent(
            id="customer-support-bot",
            name="Customer Support Bot",
            model_id="gpt-4-turbo",
            model="gpt-4",
            environment=AgentEnvironment.PRODUCTION,
            status=AgentStatus.ACTIVE,
            risk_level="medium",
            policies=["no-pii", "business-hours"],
            owner="support-team@company.com",
        )
        
        assert agent.id == "customer-support-bot"
        assert agent.status == AgentStatus.ACTIVE
        assert agent.environment == AgentEnvironment.PRODUCTION
        assert "no-pii" in agent.policies
    
    def test_agent_with_limits(self):
        """Test agent with usage limits."""
        agent = Agent(
            id="test-agent",
            name="Test Agent",
            model_id="gpt-4",
            model="gpt-4",
            rate_limit_rpm=100,
            daily_cost_limit=50.0,
            monthly_cost_limit=1000.0,
        )
        
        assert agent.rate_limit_rpm == 100
        assert agent.daily_cost_limit == 50.0


class TestPromptObject:
    """Test Prompt object."""
    
    def test_create_prompt(self):
        """Test creating a prompt."""
        prompt = Prompt(
            id="greeting",
            name="Customer Greeting",
            active_version="1.0.0",
            versions=[
                PromptVersion(
                    version="1.0.0",
                    template="Hello {{name}}!",
                    variables=[
                        PromptVariable(name="name", required=True)
                    ],
                    status=PromptStatus.ACTIVE,
                )
            ],
        )
        
        assert prompt.id == "greeting"
        assert prompt.active_version == "1.0.0"
        assert len(prompt.versions) == 1
        assert prompt.versions[0].variables[0].name == "name"
    
    def test_prompt_ab_testing(self):
        """Test prompt with A/B testing."""
        prompt = Prompt(
            id="test-prompt",
            name="Test Prompt",
            active_version="1.0.0",
            ab_test_enabled=True,
            ab_test_versions=["1.0.0", "2.0.0"],
            ab_test_split={"1.0.0": 0.5, "2.0.0": 0.5},
        )
        
        assert prompt.ab_test_enabled is True
        assert len(prompt.ab_test_versions) == 2


class TestRequestObject:
    """Test Request object."""
    
    def test_create_request(self):
        """Test creating a request."""
        request = Request(
            id="req_123",
            agent_id="customer-support-bot",
            user_id="user_456",
            prompt="What are your hours?",
            model="gpt-4",
            status=RequestStatus.SUBMITTED,
            priority=RequestPriority.NORMAL,
        )
        
        assert request.id == "req_123"
        assert request.status == RequestStatus.SUBMITTED
        assert request.priority == RequestPriority.NORMAL
    
    def test_request_with_governance(self):
        """Test request with governance data."""
        request = Request(
            id="req_789",
            agent_id="test-agent",
            user_id="user_123",
            prompt="Test prompt",
            model="gpt-4",
            policies_applied=["no-pii", "cost-control"],
            compliance_standards=["GDPR", "SOC2"],
            risk_score=45.5,
            risk_level="medium",
            requires_approval=False,
        )
        
        assert "no-pii" in request.policies_applied
        assert "GDPR" in request.compliance_standards
        assert request.risk_score == 45.5


class TestDecisionObject:
    """Test Decision object."""
    
    def test_create_decision(self):
        """Test creating a decision."""
        decision = Decision(
            id="dec_123",
            request_id="req_456",
            outcome=DecisionOutcome.ALLOW,
            action="allow",
            reason="All policies passed",
            agent_id="test-agent",
            model="gpt-4",
            policies_evaluated=[
                PolicyEvaluation(
                    policy_id="no-pii",
                    policy_name="No PII",
                    matched=False,
                    action="allow",
                )
            ],
        )
        
        assert decision.outcome == DecisionOutcome.ALLOW
        assert len(decision.policies_evaluated) == 1
    
    def test_decision_with_escalation(self):
        """Test decision requiring approval."""
        decision = Decision(
            id="dec_789",
            request_id="req_123",
            outcome=DecisionOutcome.ESCALATE,
            action="escalate",
            reason="High risk detected",
            agent_id="test-agent",
            model="gpt-4",
            requires_approval=True,
            approval_reason="Risk score exceeds threshold",
        )
        
        assert decision.requires_approval is True
        assert decision.outcome == DecisionOutcome.ESCALATE


class TestPolicyObject:
    """Test Policy object."""
    
    def test_create_policy(self):
        """Test creating a policy."""
        policy = Policy(
            id="high-risk-policy",
            name="High Risk Approval",
            version="1.0",
            rules=[
                PolicyRule(
                    when=PolicyCondition(field="risk_score", greater_than=70),
                    then=PolicyAction.ESCALATE,
                    reason="Risk too high",
                )
            ],
        )
        
        assert policy.id == "high-risk-policy"
        assert len(policy.rules) == 1
        assert policy.enabled is True
    
    def test_policy_with_compliance(self):
        """Test policy with compliance reference."""
        policy = Policy(
            id="gdpr-policy",
            name="GDPR Compliance",
            version="1.0",
            rules=[
                PolicyRule(
                    when=PolicyCondition(contains="personal data"),
                    then=PolicyAction.BLOCK,
                    reason="GDPR violation",
                )
            ],
            compliance_standard="GDPR",
            regulatory_reference="Article 22",
        )
        
        assert policy.compliance_standard == "GDPR"


class TestRiskObject:
    """Test Risk object."""
    
    def test_create_risk(self):
        """Test creating a risk assessment."""
        risk = Risk(
            id="risk_123",
            request_id="req_456",
            score=65.5,
            level=RiskLevel.MEDIUM,
            confidence=0.85,
            agent_id="test-agent",
            model="gpt-4",
            scorer_id="default-scorer",
        )
        
        assert risk.score == 65.5
        assert risk.level == RiskLevel.MEDIUM
        assert risk.confidence == 0.85
    
    def test_risk_with_factors(self):
        """Test risk with multiple factors."""
        risk = Risk(
            id="risk_789",
            request_id="req_123",
            score=85.0,
            level=RiskLevel.HIGH,
            confidence=0.90,
            agent_id="test-agent",
            model="gpt-4",
            scorer_id="ml-scorer",
            factors=[
                RiskFactor(
                    category=RiskCategory.PII_EXPOSURE,
                    name="SSN Pattern",
                    score=90.0,
                    weight=1.5,
                ),
                RiskFactor(
                    category=RiskCategory.COST,
                    name="High Token Count",
                    score=60.0,
                    weight=0.8,
                ),
            ],
            mitigations=[
                RiskMitigation(
                    action="Redact PII",
                    reason="Remove sensitive data",
                    priority="high",
                )
            ],
        )
        
        assert len(risk.factors) == 2
        assert len(risk.mitigations) == 1


class TestApprovalObject:
    """Test Approval object."""
    
    def test_create_approval(self):
        """Test creating an approval request."""
        approval = Approval(
            id="appr_123",
            request_id="req_456",
            agent_id="test-agent",
            prompt="Sensitive operation",
            reason="High risk score",
            status=ApprovalStatus.PENDING,
            priority=ApprovalPriority.HIGH,
            required_approvers=["manager_1"],
            timeout_minutes=30,
        )
        
        assert approval.status == ApprovalStatus.PENDING
        assert approval.priority == ApprovalPriority.HIGH
        assert "manager_1" in approval.required_approvers
    
    def test_approval_with_decisions(self):
        """Test approval with approver decisions."""
        approval = Approval(
            id="appr_789",
            request_id="req_123",
            agent_id="test-agent",
            prompt="Test",
            reason="Test reason",
            decisions=[
                ApprovalDecision(
                    approver_id="manager_1",
                    action=ApprovalAction.APPROVE,
                    comment="Looks good",
                )
            ],
            final_decision=ApprovalAction.APPROVE,
        )
        
        assert len(approval.decisions) == 1
        assert approval.final_decision == ApprovalAction.APPROVE


class TestEventObject:
    """Test Event object."""
    
    def test_create_event(self):
        """Test creating an event."""
        event = Event(
            id="evt_123",
            event_type=EventType.REQUEST_COMPLETED,
            severity=EventSeverity.INFO,
            message="Request completed",
            request_id="req_456",
            agent_id="test-agent",
        )
        
        assert event.event_type == EventType.REQUEST_COMPLETED
        assert event.severity == EventSeverity.INFO
    
    def test_event_with_chain(self):
        """Test event with hash chain."""
        event = Event(
            id="evt_789",
            event_type=EventType.POLICY_EVALUATED,
            severity=EventSeverity.INFO,
            message="Policy evaluated",
            hash="abc123",
            previous_hash="xyz789",
            chain_valid=True,
        )
        
        assert event.hash == "abc123"
        assert event.previous_hash == "xyz789"
        assert event.chain_valid is True
    
    def test_event_compliance_relevant(self):
        """Test compliance-relevant event."""
        event = Event(
            id="evt_111",
            event_type=EventType.COMPLIANCE_VIOLATION,
            severity=EventSeverity.WARNING,
            message="Compliance violation detected",
            compliance_relevant=True,
            compliance_standards=["GDPR", "HIPAA"],
        )
        
        assert event.compliance_relevant is True
        assert "GDPR" in event.compliance_standards


class TestObjectIntegration:
    """Test integration between objects."""
    
    def test_request_decision_chain(self):
        """Test request-decision relationship."""
        request = Request(
            id="req_integration",
            agent_id="test-agent",
            user_id="user_1",
            prompt="Test",
            model="gpt-4",
        )
        
        decision = Decision(
            id="dec_integration",
            request_id=request.id,
            outcome=DecisionOutcome.ALLOW,
            action="allow",
            reason="All clear",
            agent_id=request.agent_id,
            model=request.model,
        )
        
        assert decision.request_id == request.id
        assert decision.agent_id == request.agent_id
    
    def test_request_risk_decision_chain(self):
        """Test request-risk-decision chain."""
        request = Request(
            id="req_chain",
            agent_id="test-agent",
            user_id="user_1",
            prompt="Test",
            model="gpt-4",
        )
        
        risk = Risk(
            id="risk_chain",
            request_id=request.id,
            score=75.0,
            level=RiskLevel.HIGH,
            confidence=0.9,
            agent_id=request.agent_id,
            model=request.model,
            scorer_id="default",
        )
        
        decision = Decision(
            id="dec_chain",
            request_id=request.id,
            outcome=DecisionOutcome.ESCALATE,
            action="escalate",
            reason="High risk",
            agent_id=request.agent_id,
            model=request.model,
            risk_score=risk.score,
            risk_level=risk.level,
        )
        
        assert risk.request_id == request.id
        assert decision.request_id == request.id
        assert decision.risk_score == risk.score
