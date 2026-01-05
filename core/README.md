# Core Object Model - The Foundation

## Overview

The Core Object Model is the foundation of the AI Control Plane. Every operation in the system maps to one of these first-class objects. This is the "Salesforce of AI" approach - declarative, traceable, and unavoidable.

## First-Class Objects

### 1. Model
**AI model metadata and capabilities**

Every AI model used in the system must be registered as a Model object. Tracks capabilities, costs, rate limits, and governance requirements.

```python
from core.models import Model, ModelCapability, ModelProvider

model = Model(
    id="gpt-4-turbo",
    name="GPT-4 Turbo",
    provider=ModelProvider.OPENAI,
    capabilities=[ModelCapability.CHAT, ModelCapability.FUNCTION_CALLING],
    context_window=128000,
    default_risk_level="high",
    required_policies=["no-pii", "cost-control"]
)
```

### 2. Agent
**Registered AI agents**

An agent is a configured instance of an AI model with specific policies, risk profiles, and governance requirements.

```python
from core.models import Agent, AgentStatus

agent = Agent(
    id="customer-support-bot",
    name="Customer Support Bot",
    model_id="gpt-4-turbo",
    model="gpt-4",
    status=AgentStatus.ACTIVE,
    risk_level="medium",
    policies=["no-pii", "business-hours"],
    owner="support-team@company.com"
)
```

### 3. Prompt
**Prompt templates and versioning**

Prompts are versioned, templated, and governable artifacts. Track evolution, A/B testing, and compliance.

```python
from core.models import Prompt, PromptVersion, PromptVariable

prompt = Prompt(
    id="customer-greeting",
    name="Customer Greeting Prompt",
    active_version="1.0.0",
    versions=[
        PromptVersion(
            version="1.0.0",
            template="Hello {{customer_name}}, how can I help you today?",
            variables=[
                PromptVariable(name="customer_name", required=True)
            ]
        )
    ]
)
```

### 4. Request
**Execution requests**

Every AI interaction starts with a Request. Complete record of what was asked, by whom, and under what context.

```python
from core.models import Request, RequestStatus

request = Request(
    id="req_abc123",
    agent_id="customer-support-bot",
    user_id="user_123",
    prompt="What are your business hours?",
    model="gpt-4",
    status=RequestStatus.COMPLETED,
    policies_applied=["no-pii", "business-hours"]
)
```

### 5. Decision
**Policy evaluation decisions**

Every policy evaluation produces a Decision. The audit trail of WHY something was allowed, blocked, or escalated.

```python
from core.models import Decision, DecisionOutcome

decision = Decision(
    id="dec_xyz789",
    request_id="req_abc123",
    outcome=DecisionOutcome.ALLOW,
    action="allow",
    reason="All policies passed",
    explanation="Request evaluated against 3 policies. No violations detected.",
    risk_score=15.5,
    risk_level="low"
)
```

### 6. Policy
**Governance rules**

Policies are declarative, versioned, and testable. No Python code required - pure configuration.

```python
from core.models import Policy, PolicyRule, PolicyCondition, PolicyAction

policy = Policy(
    id="high-risk-approval",
    name="High Risk Approval Required",
    version="1.0",
    rules=[
        PolicyRule(
            when=PolicyCondition(field="risk_score", greater_than=70),
            then=PolicyAction.ESCALATE,
            reason="Risk score exceeds threshold"
        )
    ]
)
```

### 7. Risk
**Risk assessment results**

Every request is scored for risk. Complete risk profile with factors, confidence, and recommendations.

```python
from core.models import Risk, RiskLevel, RiskFactor, RiskCategory

risk = Risk(
    id="risk_abc123",
    request_id="req_xyz789",
    score=65.5,
    level=RiskLevel.MEDIUM,
    factors=[
        RiskFactor(
            category=RiskCategory.PII_EXPOSURE,
            name="Potential PII Pattern",
            score=80.0
        )
    ],
    confidence=0.85
)
```

### 8. Approval
**Human approval workflows**

High-risk AI decisions require human judgment. Complete approval workflow with queues, timeouts, and escalation.

```python
from core.models import Approval, ApprovalStatus, ApprovalPriority

approval = Approval(
    id="appr_xyz123",
    request_id="req_abc456",
    agent_id="customer-support-bot",
    prompt="Process sensitive data...",
    reason="High risk score detected",
    status=ApprovalStatus.PENDING,
    priority=ApprovalPriority.HIGH,
    required_approvers=["manager_123"],
    timeout_minutes=30
)
```

### 9. Event
**Immutable audit events**

Events are the immutable audit trail. Hash-chained, cryptographically verifiable, and legally defensible.

```python
from core.models import Event, EventType, EventSeverity

event = Event(
    id="evt_abc123",
    event_type=EventType.REQUEST_COMPLETED,
    severity=EventSeverity.INFO,
    message="AI request completed successfully",
    request_id="req_xyz789",
    agent_id="customer-support-bot",
    hash="abc123...",
    previous_hash="xyz789..."
)
```

## Design Principles

### 1. Declarative Over Imperative
All objects are defined as configuration, not code. Business-readable, version-controlled, and testable.

### 2. Immutability Where It Matters
Events and audit trails are immutable. Requests and decisions are append-only. Changes create new versions.

### 3. Complete Traceability
Every object has creation timestamps, creators, and full history. Chain of custody for compliance.

### 4. Rich Metadata
Every object supports extensible metadata. Custom fields without schema changes.

### 5. Governance-First
Policies, compliance, risk, and approvals are first-class. Not bolted on - built in.

## Usage Patterns

### System of Record
These objects ARE the system of record. Not representations - the actual source of truth.

```python
# Query the system of record
agent = agent_registry.get(agent_id="customer-support-bot")
request = request_store.get(request_id="req_abc123")
decision = decision_store.get(decision_id="dec_xyz789")
```

### Audit Trail
Every object contributes to the audit trail. Complete history of all AI operations.

```python
# Get complete audit trail for a request
events = event_store.query(request_id="req_abc123")
# Returns: [REQUEST_SUBMITTED, POLICY_EVALUATED, RISK_ASSESSED, REQUEST_COMPLETED]
```

### Compliance Reporting
Objects are designed for compliance. Built-in fields for regulatory requirements.

```python
# Compliance report
requests = request_store.query(
    compliance_standards=["GDPR", "HIPAA"],
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## Integration with Existing Code

The core object model integrates with existing components:

- **Registry**: Uses enhanced Agent model
- **Policy Engine**: Uses Policy, PolicyRule, PolicyCondition
- **Observability**: Uses Event model with immutability
- **Approval**: Uses Approval model with workflows
- **Gateway**: Creates Request and Decision objects

## Future Enhancements

- **Object Relationships**: Graph-based relationships between objects
- **Time-Travel Queries**: Query object state at any point in time
- **Change Data Capture**: Stream object changes for real-time sync
- **Object Versioning**: Full version history for all mutable objects
- **Object Permissions**: Fine-grained access control per object

## The "Salesforce of AI" Vision

Just like Salesforce made CRM objects (Account, Contact, Opportunity) the system of record for sales, we're making AI objects (Model, Agent, Request, Decision) the system of record for AI governance.

**Everything in the system maps to one of these objects.**

This is not a library. This is not a framework. This is the operating system for enterprise AI.
