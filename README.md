# ai-control-plane

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Arnoldlarry15/ai-control-plane/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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
