# ai-control-plane

**ai-control-plane** is an open, API-first platform for registering, governing, and observing AI systems.

It provides a centralized execution gateway, policy enforcement, audit logging, and human-in-the-loop controls to ensure AI behavior is accountable, interruptible, and safe by default.

**This project does not build AI models. It governs how they are used.**

---

## Features

### Core Capabilities
- 🔐 **Centralized Execution Gateway**: Route all AI model/agent requests through a single control point
- 📋 **Policy Enforcement**: Define and enforce policies on AI behavior before, during, and after execution
- 📝 **Audit Logging**: Complete observability and replay of all AI interactions
- 👤 **Human-in-the-Loop**: Approval queues for sensitive operations
- 🛑 **Kill Switch**: Emergency controls to halt AI agents instantly
- 🔌 **API-First Design**: Simple integration via REST API and Python SDK

### Production-Ready Features ✨
- 🔑 **Role-Based Access Control (RBAC)**: Fine-grained permissions with Admin, Operator, Developer, Auditor, and User roles
- 📜 **Compliance Policy Modules**: Pre-built policies for GDPR, HIPAA, SOC 2, and PCI-DSS
- 📊 **Observability Dashboard**: Real-time web-based monitoring and metrics
- ☸️ **Cloud-Native Deployment**: Kubernetes manifests and Helm charts for production
- 🔄 **CI/CD Pipelines**: GitHub Actions workflows for automated testing and deployment
- 🔒 **Security First**: Multi-stage Docker builds, network policies, and vulnerability scanning

---

## Architecture

The control plane consists of several core modules:

- **Gateway**: API entry point and request routing
- **Registry**: Catalog of registered AI models and agents
- **Policy Engine**: Policy parsing, evaluation, and violation handling with compliance modules
- **Observability**: Event logging, storage, and replay capabilities
- **Approval Service**: Human review queue for flagged operations
- **Kill Switch**: Emergency shutdown and state management
- **Auth**: Role-based access control and identity management
- **Dashboard**: Web-based monitoring and observability UI
- **Compliance**: Pre-built policy modules for GDPR, HIPAA, SOC 2, PCI-DSS

See [docs/architecture.md](docs/architecture.md) for detailed design.

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Arnoldlarry15/ai-control-plane.git
cd ai-control-plane

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e ".[dev]"
```

### Running the Gateway

```bash
# Start the control plane gateway
python -m gateway.main

# Gateway will be available at http://localhost:8000
```

### Using the SDK

```python
from sdk.python.client import ControlPlaneClient

# Initialize client
client = ControlPlaneClient(base_url="http://localhost:8000")

# Register an AI agent
agent = client.register_agent(
    name="my-agent",
    model="gpt-4",
    policies=["no-pii", "require-approval"]
)

# Execute through control plane
response = client.execute(
    agent_id=agent.id,
    prompt="Analyze this data...",
    context={"user": "alice"}
)
```

---

## Documentation

### Core Documentation
- [Architecture Overview](docs/architecture.md) - System design and components
- [Policy Specification](docs/policy-spec.md) - Policy language and rules
- [Threat Model](docs/threat-model.md) - Security considerations
- [Demo Walkthrough](docs/demo-walkthrough.md) - Step-by-step examples

### Production Guides
- [Deployment Guide](docs/deployment-guide.md) - Kubernetes and Helm deployment
- [RBAC Guide](docs/rbac-guide.md) - Role-based access control setup
- [Compliance Guide](docs/compliance-guide.md) - GDPR, HIPAA, SOC 2, PCI-DSS policies

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

---

## Compliance Modules

Pre-built policies for major compliance standards:

```python
from policy.compliance import ComplianceLoader

loader = ComplianceLoader()

# Load GDPR compliance policy
gdpr = loader.load_policy('gdpr')

# Load HIPAA compliance policy
hipaa = loader.load_policy('hipaa')

# Apply to agent
agent = client.register_agent(
    name="healthcare-bot",
    policies=["hipaa-compliance", "gdpr-compliance"]
)
```

Available standards:
- **GDPR**: EU General Data Protection Regulation
- **HIPAA**: US Health Insurance Portability and Accountability Act
- **SOC 2**: Trust Services Criteria
- **PCI-DSS**: Payment Card Industry Data Security Standard

See [Compliance Guide](docs/compliance-guide.md) for details.

---

## Observability Dashboard

Access the web-based dashboard:

```bash
# Start the gateway (includes dashboard)
python -m gateway.main

# Open in browser
open http://localhost:8000/dashboard
```

Dashboard features:
- Real-time metrics and statistics
- Policy violation tracking
- Agent status monitoring
- Audit log viewer
- Kill switch controls

---

## Project Structure

```
ai-control-plane/
├── gateway/              # API gateway and routing
├── registry/             # Agent/model registry
├── policy/               # Policy engine
│   └── compliance/       # Compliance policy modules (GDPR, HIPAA, etc.)
├── observability/        # Logging and audit
├── approval/             # Human-in-the-loop
├── kill_switch/          # Emergency controls
├── auth/                 # RBAC and identity management
├── dashboard/            # Web-based observability UI
├── sdk/                  # Client SDKs
├── deployments/          # Kubernetes and Helm charts
│   ├── kubernetes/       # Raw K8s manifests
│   └── helm/             # Helm chart
├── .github/workflows/    # CI/CD pipelines
├── demo/                 # Example scripts
├── tests/                # Test suite
└── docs/                 # Documentation
```

---

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! This is an open-source project focused on making AI governance accessible and practical.

---

## Disclaimer

This is a governance layer, not an AI model. It does not train, host, or provide AI models. It provides controls over how AI systems are accessed and used.
