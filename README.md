# ai-control-plane

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Arnoldlarry15/ai-control-plane/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)](CHANGELOG.md)

**The Operating System for AI Usage in Organizations**

ai-control-plane is not a tool. It's the unavoidable backbone every serious AI deployment runs through.

We don't build AI models. We don't compete with OpenAI, Anthropic, or others.  
We sit above, between, and across all of them.

**Think Salesforce for AI**: The system of record, the control surface, and the default operating layer for how organizations use AI.

## What This Means

- **You keep using your AI models** - GPT-4, Claude, Gemini, whatever you choose
- **Every request flows through here** - The mandatory choke point
- **Every decision is logged** - Immutable, cryptographically verified audit trails
- **Every policy is declarative** - Business rules, not code
- **Every action is explainable** - Trust through transparency

**This is platform infrastructure, not a project.**

---

## 🎉 What's New in v1.0.0 (Production Release)

**From Blueprint to Production Reality** - This release transforms the AI Control Plane from an architectural vision into a fully-functional, production-ready governance platform.

### ✅ Fully Implemented Production Features

1. **Complete Compliance Module System**
   - All 4 compliance standards (GDPR, HIPAA, SOC 2, PCI-DSS) fully implemented with regulatory references
   - Compliance validation API with real-time checking
   - Automated compliance reporting
   - Production-tested policies ready to deploy

2. **Production Dashboard with Real-Time Integration**
   - Live metrics connected to actual system services
   - Real-time activity feed from audit logs
   - Agent status monitoring from registry
   - Compliance status overview
   - Auto-refreshing UI every 5 seconds

3. **Complete RBAC Implementation**
   - 4 distinct roles: Admin, Operator, Developer, Auditor
   - Granular permission system (10+ permission types)
   - API key authentication and management
   - Full user lifecycle support

4. **Package Distribution Ready**
   - Proper package structure with setuptools
   - Built wheel and source distributions
   - Version 1.0.0 with semantic versioning
   - Installation via pip
   - Complete MANIFEST for package data

### 📦 Now Available

- **Installable Package**: `pip install ai_control_plane-1.0.0-py3-none-any.whl`
- **Compliance APIs**: Full REST API for compliance validation
- **Integrated Dashboard**: Mounted at `/dashboard` with real data
- **Production Documentation**: Complete CHANGELOG and package metadata

**This is no longer aspirational. This is production infrastructure.**

---

## Why This Matters: The "Salesforce of AI" Blueprint

Salesforce didn't win because CRM was new. They won because they became:
1. **The System of Record** - Where truth lives
2. **The Control Surface** - How you manage operations
3. **The Default Operating Layer** - The unavoidable backbone

We're doing the same for AI.

### Four Core Principles

#### 1. Declarative Over Imperative ✨
Policies are business rules, not Python code.

```yaml
# This is what users write:
policy:
  name: "High Risk Model Control"
  when:
    and:
      - field: "model"
        equals: "gpt-4"
      - field: "risk_level"
        in: ["high", "critical"]
  then: "escalate"
  reason: "High-risk model requires approval"
```

**Feels like config. That's winning.**

#### 2. System of Record for AI Activity 📋
Every AI decision is logged with cryptographic integrity.

- **Immutable audit trails** - Append-only with hash chaining
- **Chain of custody** - Every decision is traceable
- **Subpoena-ready exports** - Legal compliance built-in
- **Replayable timelines** - Understand what happened, when, and why

**If an AI decision is questioned, this is the source of truth.**

#### 3. Extensibility Is Non-Negotiable 🔌
Platform, not product. Built for customization.

- **Plugin architecture** - Custom policies without touching core
- **Compliance packs** - GDPR, HIPAA, SOC2, PCI-DSS, and yours
- **Risk scoring modules** - Bring your own models
- **Lifecycle hooks** - Intercept and augment at any stage
- **Agent hooks** - pre_execute, post_execute, on_error, on_block

**Think marketplace, not monolith.**

#### 4. Boring Reliability Beats Clever AI 🔒
We're not here to be magical. We're here to be trusted.

- **Deterministic** - Same input = same output, always
- **Explainable** - Every decision has plain English reasoning
- **Fail closed** - Block on error, never silently allow
- **No surprises** - Prefer "no" over "maybe"

**This is boring by design. That's why it works.**

---

## Features

### ✅ Production-Ready Core Features

- 🔐 **Centralized Gateway** - Single choke point for ALL AI execution
- 📋 **Declarative Policies** - Business-readable rules with DSL
- 🔗 **Cryptographic Audit Trail** - Tamper-proof, legally defensible logs
- 🔌 **Plugin System** - Extensible without modifying core
- 👤 **Human-in-the-Loop** - Approval workflows for sensitive operations
- 🛑 **Emergency Kill Switch** - Instant shutdown controls
- 📊 **Policy Explainability** - Every decision has plain English reasoning
- 🔄 **Decision Replay** - Reconstruct any execution timeline

### ✅ Enterprise Platform Capabilities (v1.0.0)

- **✅ Compliance Modules**: Pre-built, production-tested policies for GDPR, HIPAA, SOC 2, PCI-DSS
  - Complete policy implementations with regulatory references
  - Compliance validation API
  - Automated compliance reporting
  - All 4 major standards fully implemented and tested
- **✅ Role-Based Access Control**: Full RBAC implementation with 4 roles (Admin, Operator, Developer, Auditor)
  - Granular permission system
  - API key management
  - User lifecycle management
  - Permission enforcement at all endpoints
- **✅ Observability Dashboard**: Real-time web UI for monitoring and control
  - Live metrics and statistics
  - Policy violation tracking
  - Agent status monitoring
  - Kill switch controls
  - Compliance status overview
- **Risk Scoring Framework**: Pluggable risk assessment models
- **Lifecycle Hooks**: Pre/post execution, error handling, blocking events
- **Policy Templates**: Common use cases ready to deploy
- **Dry-Run Mode**: Test policies without executing
- **Conflict Detection**: Identify and resolve policy conflicts
- **Chain of Custody**: Legal-grade audit trail exports

### Production Infrastructure

- 🔑 **Role-Based Access Control**: Complete RBAC with 4 roles and granular permissions
- ☸️ **Cloud-Native**: Kubernetes manifests and Helm charts
- 🔒 **Security First**: Cryptographic integrity, fail-closed architecture
- 📊 **Observability Dashboard**: Real-time monitoring and metrics (fully integrated)
- 🔄 **CI/CD Ready**: GitHub Actions workflows included
- 📦 **PyPI Ready**: Installable via pip (wheel and source distributions available)

---

## Architecture: The Operating System View

```
┌─────────────────────────────────────────────────────┐
│                   Applications                      │
│         (Your AI agents, chatbots, systems)         │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ All AI requests flow through here
                  ▼
┌─────────────────────────────────────────────────────┐
│              AI CONTROL PLANE                       │
│         The Operating System Layer                  │
├─────────────────────────────────────────────────────┤
│  Gateway │ Registry │ Policy │ Audit │ Kill Switch │
│          │          │ Engine │ Trail │             │
├─────────────────────────────────────────────────────┤
│  Plugins │ Compliance │ Hooks │ Explainer │ DSL    │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ Governed requests
                  ▼
┌─────────────────────────────────────────────────────┐
│             AI Model Providers                      │
│      OpenAI │ Anthropic │ Google │ Azure │ ...     │
└─────────────────────────────────────────────────────┘
```

**Core modules**:
- **Gateway**: The mandatory choke point
- **Registry**: System of record for AI agents
- **Policy Engine**: Declarative rule evaluation with DSL
- **Audit Trail**: Cryptographically verified, immutable logs
- **Plugin System**: Extensibility without core changes
- **Explainer**: Makes every decision transparent

See [docs/architecture.md](docs/architecture.md) for detailed design.

## Quick Start

### Installation

#### Option 1: Install from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/Arnoldlarry15/ai-control-plane.git
cd ai-control-plane

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e ".[dev]"
```

#### Option 2: Install from Built Package (Production)

```bash
# Install from local wheel (after building)
pip install dist/ai_control_plane-1.0.0-py3-none-any.whl

# Or install from source distribution
pip install dist/ai_control_plane-1.0.0.tar.gz
```

#### Building the Package

```bash
# Install build tools
pip install build

# Build wheel and source distribution
python -m build

# Outputs:
# - dist/ai_control_plane-1.0.0-py3-none-any.whl
# - dist/ai_control_plane-1.0.0.tar.gz
```

### Running the Control Plane

```bash
# Start the gateway (the choke point)
python -m gateway.main

# Gateway will be available at http://localhost:8000
# API docs at http://localhost:8000/api/docs
```

### 🎯 Quick Start: The 5-Minute Experience

**Option 1: Hello Governance (Fastest)**

The canonical example that shows governance in action:

```bash
python examples/hello_governance.py
```

This demonstrates:
- Agent registration
- Policy-governed execution
- Audit trail preservation
- Clear error messages

**Option 2: Complete SDK Walkthrough**

Full feature demonstration:

```bash
python examples/sdk_walkthrough.py
```

This walks you through:
- Agent registration with governance
- Safe execution with policy enforcement
- Handling blocked requests gracefully
- Approval workflows for high-risk operations
- Audit trail queries and compliance
- Kill switch emergency controls

### Using the Platform

#### 1. Register Your AI Agent

```python
from sdk.python.client import ControlPlaneClient

client = ControlPlaneClient(base_url="http://localhost:8000")

# Register your agent (any model, any provider)
agent = client.register_agent(
    name="my-assistant",
    model="gpt-4",  # or claude-3, gemini, etc.
    risk_level="medium",
    policies=["no-pii", "business-hours", "require-approval-high-cost"]
)
```

#### 2. Execute Through the Control Plane

```python
# Every request flows through here
response = client.execute(
    agent_id=agent.id,
    prompt="Analyze this customer data...",
    context={"user": "alice@company.com"}
)

# Response includes:
# - AI response (if allowed)
# - Execution ID (for audit trail)
# - Decision explanation (why allowed/blocked)
# - Policy chain (what was evaluated)
```

#### 3. Declarative Policy Example

```yaml
# policies/cost-control.yaml
policy:
  name: "High Cost Approval"
  description: "Require approval for expensive operations"
  
  when:
    field: "context.estimated_cost"
    greater_than: 100
  
  then: "escalate"
  reason: "Estimated cost exceeds $100 threshold"
```

#### 4. Query the Audit Trail

```python
# Get complete execution history
logs = client.get_logs(user="alice@company.com", limit=50)

# Get specific execution with full timeline
execution = client.get_execution_log(execution_id)

# Verify cryptographic integrity
integrity = client.verify_audit_integrity()

# Export for compliance (subpoena-ready)
compliance_export = client.export_audit_trail(
    start_date="2024-01-01",
    end_date="2024-12-31",
    format="json"  # or "csv"
)
```

#### 5. Use Plugin System

```python
from policy.plugins import RiskScorerPlugin, PluginRegistry

# Create custom risk scorer
class MyRiskScorer(RiskScorerPlugin):
    @property
    def plugin_id(self) -> str:
        return "my-risk-scorer"
    
    @property
    def plugin_name(self) -> str:
        return "My Industry-Specific Risk Model"
    
    def calculate_risk_score(self, agent_id, prompt, context):
        # Your custom logic
        return {
            "score": 75,
            "level": "high",
            "factors": ["Industry-specific trigger detected"],
            "recommendations": ["Review with domain expert"]
        }

# Register plugin
registry = PluginRegistry()
registry.register(MyRiskScorer())
```

---

## 🚀 New in Phases 4-7: The "Salesforce Moment"

### Phase 4: Trustworthy Systems Are Allowed to Be Slower

**Human-in-the-Loop Workflows That Actually Work**

Certain policies trigger "pause and escalate." A human approves or rejects. The decision is stored forever.

```python
from sdk.python.client import ControlPlaneClient
from sdk.python.exceptions import ApprovalPendingError

client = ControlPlaneClient()

try:
    result = client.execute(
        agent_id=agent_id,
        prompt="Process this high-value transaction",
        context={"estimated_cost": 150}
    )
except ApprovalPendingError as e:
    print(f"Approval required: {e.approval_id}")
    # Human reviews, then:
    # status = client.get_approval_status(e.approval_id)
```

This does two things:
1. **Satisfies real compliance requirements**
2. **Teaches users to think before deploying power**

This is where your product quietly becomes ethical infrastructure.

### Phase 5: Developer Ergonomics

**Safety for Free, Without Slowing Me Down**

Try the canonical "hello governance" example:

```bash
python examples/hello_governance.py
```

Clear error messages that teach:

```python
{
  "error": "Execution Blocked",
  "reason": "PII detected in prompt",
  "what_happened": "Your AI request was blocked by a governance policy.",
  "why_it_happened": "The request contains personally identifiable information (PII)...",
  "how_to_fix": [
    "Remove PII from your prompt (emails, SSNs, phone numbers, etc.)",
    "Use anonymized or synthetic test data",
    "Request a policy exception from your administrator"
  ],
  "examples": {
    "bad": "Process user data: john@example.com, SSN 123-45-6789",
    "good": "Process user data: [USER_EMAIL], [USER_ID]"
  }
}
```

Developers should feel like: **"This tool makes me look responsible without slowing me down."**

### Phase 6: Compliance as Executable Proof

**Compliance Is Not Documents. It's Evidence Generators.**

Instead of saying "GDPR compliant," we provide:

```python
from policy.compliance.evidence import ComplianceEvidence, ComplianceStandard
from datetime import datetime, timedelta

evidence_gen = ComplianceEvidence(audit_logger, policy_evaluator, registry)

# Generate compliance report with evidence
report = evidence_gen.generate_compliance_report(
    standard=ComplianceStandard.GDPR,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31)
)

# Export as certificate
certificate = evidence_gen.export_compliance_certificate(report, format="html")
```

**What you get:**
- "Here is the log that proves data minimization"
- "Here is the policy that enforces retention limits"
- "Here is the audit trail regulators can inspect"

When compliance becomes queryable, you stop selling promises and start selling certainty.

### Phase 7: Opinionated Defaults

**Salesforce Didn't Ask Users to Design CRMs From Scratch. It Shipped Opinions.**

```python
from policy.defaults import PolicyBundle, get_policy_bundle, get_recommended_bundle

# Get recommended bundle based on environment and risk
recommended = get_recommended_bundle(
    environment="production",
    risk_level="high"
)
# Returns: PolicyBundle.SAFE_MODE

# Apply pre-configured bundle
bundle = get_policy_bundle(PolicyBundle.SAFE_MODE)
# - Maximum safety for production
# - PII blocking enabled
# - High-risk model escalation required
# - Full audit trail
# - GDPR, HIPAA, SOC2, PCI-DSS policies
```

**Available Bundles:**
- **safe_mode**: Maximum safety preset for production. Blocks all high-risk operations.
- **production**: Enterprise-grade governance. Balanced security with usability.
- **development**: Balanced for dev environments. Focus on learning and visibility.
- **permissive**: Minimal restrictions for testing. Not for production use.

**Interactive Configuration Wizard:**

```python
from policy.defaults import configure_agent_interactive

config = configure_agent_interactive()
# Guides you through best practices
# Recommends appropriate bundle
# Explains trade-offs
```

These defaults quietly shape behavior across the industry. That's how platforms bend reality.

---

## The North Star Question

**If someone removed your UI, your SDK, and your branding tomorrow, and only left:**
- Policies
- Logs
- Identity
- Enforcement

**Would enterprises still need it?**

**The answer is yes.** That's what makes this the right thing to build.

---

## Project Structure

```
ai-control-plane/
├── gateway/              # The choke point (API gateway)
├── registry/             # System of record for agents
├── policy/               # Declarative policy engine
│   ├── compliance/       # GDPR, HIPAA, SOC2, PCI-DSS
│   ├── dsl.py           # Business-readable policy DSL
│   ├── plugins.py        # Plugin architecture
│   └── explainer.py      # Decision transparency
├── observability/        # Cryptographic audit trail
│   ├── audit_trail.py   # Immutable, hash-chained logs
│   └── logger.py         # Event capture
├── approval/             # Human-in-the-loop workflows
├── kill_switch/          # Emergency controls
├── auth/                 # RBAC and identity
├── dashboard/            # Observability UI
├── sdk/                  # Client libraries
├── deployments/          # K8s/Helm charts
├── docs/                 # Platform documentation
└── tests/                # Trust through testing
```

---

## Documentation

### Core Platform Docs
- [Architecture Overview](docs/architecture.md) - System design and platform philosophy
- [Policy Specification](docs/policy-spec.md) - Declarative policy DSL guide
- [Threat Model](docs/threat-model.md) - Security considerations
- [Demo Walkthrough](docs/demo-walkthrough.md) - Step-by-step examples

### Adoption Guides
- [Deployment Guide](docs/deployment-guide.md) - Kubernetes and Helm
- [RBAC Guide](docs/rbac-guide.md) - Access control setup
- [Compliance Guide](docs/compliance-guide.md) - GDPR, HIPAA, SOC 2, PCI-DSS
- **[Identity & Observability Guide](docs/identity-and-observability.md)** - Phase 2 & 3: Identity tracking and human-centric observability

### Extensibility (Phase 4 - New! ✨)
- **[Plugin Development Guide](docs/plugin-development.md)** - Creating custom plugins
- **[CLI Guide](docs/cli-guide.md)** - Command-line interface
- **[SDK Documentation](sdk/README.md)** - Python and TypeScript SDKs
- **[Example Plugins](examples/plugins/)** - Risk engines, evaluators, hooks
- **[Config Examples](examples/configs/)** - Terraform-style configuration

---

## Production Deployment

### Docker

```bash
# Build image
docker build -t ai-control-plane:latest .

# Run container
docker run -p 8000:8000 ai-control-plane:latest
```

### Kubernetes

```bash
# Apply manifests
kubectl apply -f deployments/kubernetes/

# Or use Helm
helm install ai-control-plane deployments/helm/ai-control-plane \
  --namespace ai-governance \
  --create-namespace
```

See [Deployment Guide](docs/deployment-guide.md) for complete instructions.

## Compliance Modules

✅ **Production-Ready in v1.0.0** - Pre-built compliance packs for major standards. Load and apply instantly.

```python
from policy.compliance import ComplianceLoader

loader = ComplianceLoader()

# Load GDPR compliance policy
gdpr = loader.load_policy('gdpr')

# Load HIPAA compliance policy
hipaa = loader.load_policy('hipaa')

# Apply to agent
agent = client.register_agent(
    name="healthcare-assistant",
    policies=["hipaa-compliance", "gdpr-compliance"]
)
```

### ✅ Available Standards (Fully Implemented)

- **GDPR**: EU General Data Protection Regulation
  - Right to erasure (Article 17)
  - Automated decision-making (Article 22)
  - Special category data (Article 9)
  - Data minimization (Article 5)
  - Cross-border transfers (Chapter V)
  
- **HIPAA**: US Health Insurance Portability and Accountability Act
  - Protected Health Information (PHI) detection
  - Minimum necessary standard
  - Security Rule compliance
  - Privacy Rule enforcement
  
- **SOC 2**: Trust Services Criteria
  - Security controls (CC6.1, CC7.2, CC8.1)
  - Availability requirements (A1.1)
  - Processing integrity (PI1.1)
  - Confidentiality protection (C1.1)
  - Privacy safeguards (P4.2)
  
- **PCI-DSS**: Payment Card Industry Data Security Standard
  - Cardholder data protection
  - Sensitive authentication data blocking
  - Primary Account Number (PAN) detection
  - CVV/CVC protection
  - Access control requirements

### Compliance Validation API (New in v1.0.0)

```bash
# Validate input against compliance standards
curl -X POST http://localhost:8000/api/compliance/validate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Process this patient record with SSN 123-45-6789",
    "standards": ["hipaa", "gdpr"]
  }'

# Get compliance standard details
curl http://localhost:8000/api/compliance/standards/gdpr

# Generate compliance report for an agent
curl http://localhost:8000/api/compliance/report/my-agent?standards=gdpr,hipaa
```

**Plugin your own**: Create custom compliance modules without touching core code.

See [Compliance Guide](docs/compliance-guide.md) for details.

---

## Extensibility: The Platform Advantage

This isn't a tool you configure. It's a platform you extend.

### 1. Plugin Architecture

```python
from policy.plugins import PolicyPlugin, PluginType

class MyComplianceChecker(PolicyPlugin):
    @property
    def plugin_id(self) -> str:
        return "my-compliance-checker"
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.COMPLIANCE_MODULE
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Your compliance logic
        return {"compliant": True, "violations": []}
```

### 2. Lifecycle Hooks

Intercept and augment at any stage:

- `pre_execute` - Before AI call
- `post_execute` - After successful execution
- `on_error` - When errors occur
- `on_block` - When request is blocked
- `on_escalate` - When escalated for approval

```python
from policy.plugins import LifecycleHookPlugin

class NotificationHook(LifecycleHookPlugin):
    @property
    def hook_stage(self) -> str:
        return "on_escalate"
    
    def on_escalate(self, context):
        # Send notification to reviewers
        notify_reviewers(context)
        return {"status": "continue"}
```

### 3. Policy Templates

Common patterns ready to use:

```python
from policy.dsl import get_policy_template

# Instant policy from template
policy = get_policy_template(
    "require_approval_for_model",
    MODEL_NAME="gpt-4"
)
```

**Templates included:**
- `require_approval_for_model` - Model-specific approval
- `block_pii` - PII detection and blocking
- `high_risk_escalation` - Risk-based routing
- `business_hours_only` - Time-based restrictions
- `cost_threshold` - Budget controls

### 4. Risk Scoring Framework

Bring your own risk models:

```python
from policy.plugins import RiskScorerPlugin

class MLRiskScorer(RiskScorerPlugin):
    def calculate_risk_score(self, agent_id, prompt, context):
        # Your ML model here
        score = your_model.predict(prompt)
        return {
            "score": score,
            "level": self._score_to_level(score),
            "factors": ["ML model prediction"],
            "recommendations": []
        }
```

---

## Observability Dashboard

✅ **Phase 3 Complete** - Executive-grade dashboard with advanced analytics:

```bash
# Start the gateway (includes dashboard)
python -m gateway.main

# Open in browser
open http://localhost:8000/dashboard
```

### Dashboard Features (Phase 3 - "Salesforce Moment")

**🎯 Executive Overview - Understand AI Risk in 60 Seconds**
- ✅ **6 Key Metrics**: Total executions, violations, agents, success rate, latency, kill switch
- ✅ **High-Risk Activity Alerts**: Critical/High/Medium risk events prominently displayed
- ✅ **Policy Hits Breakdown**: Blocked vs Allowed with percentages
- ✅ **Live AI Traffic**: Requests/min, latency (avg & P95), active users/agents

**🎯 Decision Replay (Killer Feature)**
- ✅ **Click Any Event**: Full decision context in modal view
- ✅ **Complete Timeline**: See inputs, policies evaluated, outcome
- ✅ **Policy Chain**: Every policy decision with reasoning
- ✅ **Audit Trail**: Immutable, timestamped execution history

**🎯 Organization-Wide AI Map**
- ✅ **Team Usage Analytics**: Which teams use which models
- ✅ **Risk Heatmap**: Low/Medium/High/Critical distribution
- ✅ **Usage Trends**: 7-day historical patterns with charts
- ✅ **Top Teams Ranking**: Sorted by usage with risk indicators

**Technical Features**
- ✅ **Real-time Updates**: Auto-refresh every 5 seconds
- ✅ **Interactive Elements**: Click events for detailed investigation
- ✅ **Modern UI**: Dark-themed, responsive, executive-focused
- ✅ **REST APIs**: All analytics available via API endpoints

### Dashboard API Endpoints

**Phase 3 Analytics APIs**

```bash
# Live traffic metrics
curl http://localhost:8000/dashboard/api/analytics/live_traffic

# Policy hits (blocked vs allowed)
curl http://localhost:8000/dashboard/api/analytics/policy_hits

# High-risk activity alerts
curl http://localhost:8000/dashboard/api/analytics/high_risk_alerts

# Decision replay (killer feature)
curl http://localhost:8000/dashboard/api/analytics/decision/{execution_id}

# Organization-wide AI map
curl http://localhost:8000/dashboard/api/analytics/org_map

# Usage trends (7 days)
curl http://localhost:8000/dashboard/api/analytics/usage_trends

# Basic endpoints
curl http://localhost:8000/dashboard/api/stats
curl http://localhost:8000/dashboard/api/recent_events
curl http://localhost:8000/dashboard/api/agents
curl http://localhost:8000/dashboard/api/compliance/status
```

**Demo Data (Development)**

```bash
# Populate sample data for testing
curl -X POST http://localhost:8000/dashboard/api/demo/populate_data
```

## Development

```bash
# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .

# Linting
flake8 .

# Run locally
python -m gateway.main
```

---

## What Makes This The "Salesforce of AI"

### 1. Inevitable Adoption
Once you need governance (and you will), this becomes mandatory infrastructure.

### 2. Network Effects
More plugins → More value → More adoption → More plugins

### 3. Lock-In Through Trust
- All your audit history lives here
- All your compliance evidence lives here
- All your policy logic lives here
- **You can't switch because this IS your system of record**

### 4. Boring = Reliable = Enterprise
Not the sexiest product. That's exactly why it wins.

---

## 📚 Complete Feature Reference

### Core Platform Components

#### 🎯 9 First-Class AI Objects (Phase 1)
The system of record for AI governance:
1. **Model** - AI model metadata, capabilities, costs
2. **Agent** - Registered AI agents with policies and risk levels
3. **Prompt** - Versioned prompt templates with A/B testing
4. **Request** - Complete execution requests with traceability
5. **Decision** - Policy evaluation decisions with full reasoning
6. **Policy** - Declarative governance rules (YAML/JSON, not code)
7. **Risk** - Comprehensive risk assessments with factors
8. **Approval** - Human-in-the-loop workflows with escalation
9. **Event** - Immutable audit events with hash chaining

See: `core/models/` for implementation

#### 🔐 Authentication & Authorization (Phase 2)
- **RBAC System**: 4 roles (Admin, Operator, Developer, Auditor, Approver)
- **Granular Permissions**: 10+ permission types
- **API Key Management**: Generate, rotate, revoke
- **OIDC/SSO Integration**: Auth0, Okta, Azure AD, Google Workspace
- **User Lifecycle**: Create, update, suspend, delete
- **Identity Tracking**: Complete user attribution for all actions

See: `auth/` directory, `docs/rbac-guide.md`

#### 📋 Declarative Policy Engine (Phases 1-2)
- **No Code Required**: Pure YAML/JSON policies
- **Business-Readable**: Compliance officers can review without developers
- **Operators**: Field comparison, pattern matching, list operations
- **Actions**: block, allow, escalate, audit, warn
- **Nested Logic**: Complex AND/OR conditions
- **Policy Bundles**: Pre-configured safe_mode, production, development, permissive

See: `policy/dsl.py`, `policy/defaults.py`, `docs/policy-spec.md`

#### 🔍 Compliance Modules (Phase 2 & 6)
Pre-built compliance packs with regulatory references:
- **GDPR**: Articles 5, 9, 17, 22, Chapter V
- **HIPAA**: Privacy Rule, Security Rule, PHI protection
- **SOC 2**: Trust Services Criteria (Security, Availability, Processing Integrity)
- **PCI-DSS**: Requirements 3, 7, 10 (cardholder data protection)
- **NIST AI RMF**: 4 core functions (GOVERN, MAP, MEASURE, MANAGE)
- **EU AI Act**: Risk categorization (unacceptable, high, limited, minimal)

**New: Compliance Evidence Generators** - Queryable proof instead of documents
- Generate compliance reports with evidence
- Export certificates (HTML, JSON)
- Query specific requirements
- Automated compliance reporting

See: `policy/compliance/`, `docs/compliance-guide.md`

#### ✅ Human-in-the-Loop Workflows (Phases 2 & 4)
- **Multi-Level Approvals**: L1 → L2 → L3 → L4 escalation
- **Configurable Workflows**: Standard, high-risk, critical
- **Timeout Handling**: Auto-escalate, reject, or approve
- **Decision Rationale**: Mandatory reasoning for compliance
- **Permanent History**: All decisions stored forever
- **Escalation Rules**: Based on timeout, risk level, rejection count

See: `approval/`, gateway routes `/approvals/*`

#### 🔒 Immutable Audit Trail (Phase 1)
- **Hash Chaining**: Every entry linked to previous
- **HMAC Signatures**: Cryptographically verified
- **Tamper Detection**: Mathematically provable integrity
- **Append-Only**: Cannot modify or delete
- **Chain of Custody**: Complete request timelines
- **Decision Replay**: Click any event to see full context
- **Compliance Exports**: Subpoena-ready, legally defensible

See: `observability/audit_trail.py`, `observability/immutable_audit.py`

#### 📊 Executive Dashboard (Phase 3)
Real-time observability with auto-refresh:
- **Live Traffic**: Requests/min, latency (avg & P95), active users/agents
- **Policy Hits**: Blocked vs Allowed breakdown with percentages
- **High-Risk Alerts**: Critical/High/Medium risk event feed
- **Decision Replay**: Click any event for complete timeline (killer feature)
- **Org-Wide AI Map**: Team usage, model distribution, risk heatmap
- **Usage Trends**: 7-day historical charts
- **Kill Switch Status**: Emergency control visibility

See: `dashboard/`, `observability/analytics.py`

#### 🛑 Kill Switch (Phase 1)
Emergency shutdown controls:
- **Global Kill Switch**: Stop all AI operations instantly
- **Agent-Scoped**: Disable specific agents
- **Reason Tracking**: All activations logged with rationale
- **Status API**: Check kill switch state
- **Fail-Closed**: Blocks all requests when active

See: `kill_switch/`, gateway routes `/kill-switch/*`

#### 🔌 Plugin System (Phase 4)
Extend without touching core code:
- **6 Plugin Types**: Policy evaluators, risk engines, risk scorers, lifecycle hooks, compliance modules, data sanitizers
- **8 Lifecycle Hooks**: pre_request, pre_execute, post_decision, post_execute, on_error, on_block, on_escalate, on_incident
- **Dynamic Loading**: Auto-discovery from directories
- **Example Plugins**: Risk engines, evaluators, hooks

See: `policy/plugins.py`, `policy/plugin_loader.py`, `docs/plugin-development.md`, `examples/plugins/`

#### 💻 SDKs & CLI (Phases 4 & 5)
- **Python SDK**: Full-featured client with helpful exceptions
- **TypeScript SDK**: Type-safe with IntelliSense support
- **CLI Tool**: `acp` command with full feature parity
- **Error Messages**: Clear guidance on what/why/how to fix
- **Examples**: hello_governance.py, sdk_walkthrough.py

See: `sdk/python/`, `sdk/typescript/`, `cli/acp.py`, `docs/cli-guide.md`

#### 🏗️ Infrastructure as Code (Phase 4)
- **Terraform-Style Config**: Declarative YAML/JSON
- **Variable Substitution**: Reusable configurations
- **Resource Blocks**: Agents, policies, compliance
- **Plan & Apply**: Preview before deployment

See: `core/config_loader.py`, `examples/configs/`

#### 🚀 Deployment Ready
- **Docker**: Multi-stage builds, optimized images
- **Kubernetes**: Complete manifests (deployment, service, configmap, HPA, ingress)
- **Helm Charts**: Parameterized deployments
- **CI/CD**: GitHub Actions workflows
- **Health Checks**: Liveness and readiness probes

See: `deployments/`, `Dockerfile`, `.github/workflows/`

---

## 📖 Documentation

### Getting Started
- [GETTING_STARTED.md](GETTING_STARTED.md) - First steps with the platform
- [QUICKSTART.md](QUICKSTART.md) - Quick reference guide
- [PLATFORM_QUICKSTART.md](PLATFORM_QUICKSTART.md) - Platform overview

### Core Documentation
- [docs/architecture.md](docs/architecture.md) - System design and philosophy
- [docs/policy-spec.md](docs/policy-spec.md) - Policy language reference
- [docs/threat-model.md](docs/threat-model.md) - Security considerations
- [docs/demo-walkthrough.md](docs/demo-walkthrough.md) - Step-by-step examples

### Adoption Guides
- [docs/deployment-guide.md](docs/deployment-guide.md) - Kubernetes and Helm
- [docs/rbac-guide.md](docs/rbac-guide.md) - Access control setup
- [docs/compliance-guide.md](docs/compliance-guide.md) - Regulatory standards
- [docs/identity-and-observability.md](docs/identity-and-observability.md) - Phase 2 & 3 features

### Developer Guides
- [docs/plugin-development.md](docs/plugin-development.md) - Creating custom plugins
- [docs/cli-guide.md](docs/cli-guide.md) - Command-line interface
- [sdk/README.md](sdk/README.md) - Python and TypeScript SDKs
- [control_plane/policy/INTEGRATION_GUIDE.md](control_plane/policy/INTEGRATION_GUIDE.md) - Integration patterns

### Phase Documentation
- [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) - Foundation implementation
- [docs/PHASE_2_COMPLETE.md](docs/PHASE_2_COMPLETE.md) - Trust & Compliance
- [PHASE_3_COMPLETE.md](PHASE_3_COMPLETE.md) - Observability & UX
- [PHASE_4_COMPLETE.md](PHASE_4_COMPLETE.md) - Extensibility ecosystem

---

## 📚 Examples & Demos

### Getting Started Examples

**Hello Governance** - The canonical 5-minute example:
```bash
python examples/hello_governance.py
```
Shows: Agent registration, policy enforcement, audit trails, error handling

**Complete SDK Walkthrough** - End-to-end feature tour:
```bash
python examples/sdk_walkthrough.py
```
Demonstrates: Registration, execution, policy blocking, approval workflows, audit queries, kill switch

### Demo Scripts

Located in `demo/` directory:

- **platform_demo.py** - Complete platform capabilities demonstration
- **production_features.py** - Production-ready features showcase
- **register_agent.py** - Simple agent registration
- **run_normal.py** - Normal execution flow
- **trigger_violation.py** - Policy violation examples
- **kill_agent.py** - Kill switch demonstration

### Plugin Examples

Located in `examples/plugins/`:

- **risk_engine_example.py** - Custom risk assessment engine
- **evaluator_example.py** - Custom policy evaluators
- **hooks_example.py** - Lifecycle hook implementations

### Configuration Examples

Located in `examples/configs/`:

- **agents.yaml** - Terraform-style agent configuration

### Test Scripts

Located in `scripts/`:

- **populate_test_data.py** - Generate test data for development
- **seed_demo_data.py** - Seed demo data for dashboard
- **reset_env.py** - Reset environment state

---

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions welcome. This is platform infrastructure for AI governance.

**Particularly interested in:**
- Additional compliance modules (regional standards)
- Plugin implementations (risk scorers, hooks, sanitizers)
- Policy templates for common use cases
- Integration examples with major AI providers
- Performance optimizations for scale

---

## Roadmap

### ✅ V1: Production Ready (Complete)
- [x] Core governance features
- [x] Compliance modules (GDPR, HIPAA, SOC 2, PCI-DSS)
- [x] RBAC system
- [x] Observability dashboard
- [x] Production deployment

### ✅ Phase 4: Extensibility (Complete)
- [x] **Policy Plugin Framework** - Drop-in evaluators, external risk engines
- [x] **Lifecycle Hooks** - Pre-request, post-decision, incident triggers
- [x] **SDK Expansion** - TypeScript/JavaScript SDK, CLI tool
- [x] **Terraform Config** - Declarative infrastructure-as-code
- [x] **Plugin Ecosystem** - Examples, documentation, testing

### ✅ Phases 4-7: The "Salesforce Moment" (Complete)

**Phase 4: Human-in-the-Loop That Actually Slows Things Down (On Purpose)**
- [x] **Approval Workflows** - Explicit "pause and escalate" triggers
- [x] **Decision Permanence** - Every approval decision stored forever
- [x] **Compliance-Grade Rationale** - Required reasoning for all decisions
- [x] **Escalation Paths** - Multi-level approval chains with timeout handling

**Phase 5: Developer Ergonomics (The Salesforce Trapdoor)**
- [x] **Hello Governance Example** - Canonical end-to-end example in under 50 lines
- [x] **Helpful Error Messages** - Clear guidance on what happened, why, and how to fix
- [x] **SDK Walkthrough** - Complete feature demonstration with examples
- [x] **"Safety for Free"** - Governance that doesn't feel like friction

**Phase 6: Compliance as Executable Proof**
- [x] **Evidence Generators** - Turn compliance into queryable proof
- [x] **Compliance Reports** - Generate reports with evidence for GDPR, HIPAA, SOC2, PCI-DSS
- [x] **Certificate Exports** - HTML/JSON compliance certificates
- [x] **Audit Trail Queries** - Query specific compliance evidence by standard and requirement

**Phase 7: Opinionated Defaults (This Is How You Win the Category)**
- [x] **Policy Bundles** - Pre-configured: safe_mode, production, development, permissive
- [x] **Recommended Enforcement** - Intelligent defaults based on environment and risk
- [x] **Configuration Wizard** - Interactive setup with best practices
- [x] **"Safe Mode" Presets** - Maximum safety for production out of the box

### V2: Production Scale
- [ ] Persistent storage (PostgreSQL for audit, Redis for state)
- [ ] Distributed tracing for policy evaluation
- [ ] Advanced policy engine (rate limiting, quotas, time windows)
- [ ] Real-time approval notifications (WebSockets)
- [ ] Multi-tenancy with organization isolation

### V3: Ecosystem
- [ ] Plugin marketplace
- [ ] Visual policy builder
- [ ] Compliance certification workflows
- [ ] Integration with major AI platforms
- [ ] Advanced analytics and reporting

### V4: Intelligence
- [ ] ML-powered risk scoring
- [ ] Anomaly detection in usage patterns
- [ ] Policy recommendation engine
- [ ] Automated compliance gap analysis

---

## The Reality Check

**Right now, this repo feels like:**
"A very smart engineer's blueprint for AI governance"

**To become the Salesforce of AI, it needs to feel like:**
"The unavoidable backbone every serious AI deployment runs through"

**We're building the bones, not the skin.**

The direction is correct. The distance is measurable. The north star is clear.

**This is not a criticism. This is a roadmap.**

---

## Disclaimer

This is a governance layer, not an AI model provider.

- We don't train models
- We don't host models  
- We don't compete with OpenAI, Anthropic, Google, or Microsoft

**We govern how AI is used. That's the entire business.**
