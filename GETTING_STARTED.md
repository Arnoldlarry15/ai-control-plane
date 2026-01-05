# Getting Started with AI Control Plane

This guide will help you get started with AI Control Plane v1.0.0, the production-ready AI governance platform.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Basic understanding of AI/LLM applications

## Installation

### Option 1: Install from Built Package (Recommended)

```bash
# Download and install the wheel package
pip install ai_control_plane-1.0.0-py3-none-any.whl

# Or from source distribution
pip install ai_control_plane-1.0.0.tar.gz
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/Arnoldlarry15/ai-control-plane.git
cd ai-control-plane

# Install in development mode
pip install -e ".[dev]"
```

### Option 3: Build and Install Locally

```bash
# Clone the repository
git clone https://github.com/Arnoldlarry15/ai-control-plane.git
cd ai-control-plane

# Install build tools
pip install build

# Build the package
python -m build

# Install the built package
pip install dist/ai_control_plane-1.0.0-py3-none-any.whl
```

## Quick Start

### 1. Start the Gateway

The gateway is the central control plane that all AI requests flow through.

```bash
# Start the gateway server
python -m gateway.main

# Or with custom settings
python -m gateway.main --host 0.0.0.0 --port 8000
```

The gateway will start on `http://localhost:8000` with:
- API Documentation at `http://localhost:8000/api/docs`
- Dashboard at `http://localhost:8000/dashboard`

### 2. Register Your First Agent

```python
from sdk.python.client import ControlPlaneClient

# Connect to the control plane
client = ControlPlaneClient(base_url="http://localhost:8000")

# Register an AI agent
agent = client.register_agent(
    name="my-first-agent",
    model="gpt-4",
    risk_level="medium",
    policies=["no-pii"]  # Apply policies
)

print(f"Agent registered: {agent.id}")
```

### 3. Execute Through the Control Plane

```python
# Execute a request through the control plane
response = client.execute(
    agent_id=agent.id,
    prompt="Hello, how are you?",
    context={"user": "alice@company.com"}
)

print(f"Status: {response.status}")
print(f"Response: {response.result}")
```

### 4. Apply Compliance Policies

```python
# Register agent with compliance policies
healthcare_agent = client.register_agent(
    name="healthcare-assistant",
    model="gpt-4",
    risk_level="high",
    policies=["hipaa-compliance", "gdpr-compliance"]
)

# Test compliance validation
try:
    response = client.execute(
        agent_id=healthcare_agent.id,
        prompt="Process patient SSN: 123-45-6789",
        context={"user": "doctor@hospital.com"}
    )
except Exception as e:
    print(f"Blocked by compliance: {e}")
```

### 5. View the Dashboard

Open your browser to `http://localhost:8000/dashboard` to see:

- **Real-time Metrics**: Total executions, violations, success rate
- **Activity Feed**: Recent events and policy decisions
- **Agent Status**: All registered agents and their status
- **Compliance Status**: Overview of all compliance standards
- **Kill Switch**: Emergency shutdown controls

## Using Compliance Modules

### List Available Standards

```bash
# Using curl
curl http://localhost:8000/api/compliance/standards

# Returns: GDPR, HIPAA, SOC 2, PCI-DSS
```

### Validate Input Against Compliance

```bash
curl -X POST http://localhost:8000/api/compliance/validate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Process credit card 4532-1234-5678-9010",
    "standards": ["pci-dss"]
  }'
```

### Generate Compliance Report

```bash
curl http://localhost:8000/api/compliance/report/my-agent \
  ?standards=gdpr,hipaa \
  &start_date=2026-01-01 \
  &end_date=2026-01-31
```

## Using RBAC

### Create Users with Different Roles

```python
from auth.service import AuthService
from auth.models import Role

auth = AuthService()

# Create operator user
operator = auth.create_user(
    user_id="operator1",
    email="operator@company.com",
    full_name="System Operator",
    role=Role.OPERATOR
)

# Create API key for the user
api_key = auth.create_api_key(operator.id, "Operator API Key")
print(f"API Key: {api_key}")
```

### Use API Key for Authentication

```python
client = ControlPlaneClient(
    base_url="http://localhost:8000",
    api_key=api_key
)
```

## Common Use Cases

### 1. Block PII in Prompts

```python
# PII blocking is enabled by default
agent = client.register_agent(
    name="customer-service",
    model="gpt-4",
    policies=["no-pii", "gdpr-compliance"]
)

# This will be blocked
try:
    client.execute(
        agent_id=agent.id,
        prompt="My SSN is 123-45-6789"
    )
except Exception as e:
    print("Blocked: PII detected")
```

### 2. Require Approval for High-Risk Operations

```python
agent = client.register_agent(
    name="database-assistant",
    model="gpt-4",
    risk_level="high",
    policies=["require-approval-high-risk"]
)

# This will be escalated for approval
response = client.execute(
    agent_id=agent.id,
    prompt="Drop the users table"
)

if response.status == "pending_approval":
    print(f"Awaiting approval: {response.approval_id}")
```

### 3. Enable Kill Switch

```python
from kill_switch.service import KillSwitchService

kill_switch = KillSwitchService()

# Activate kill switch for specific agent
kill_switch.activate(
    scope="agent",
    target_id="risky-agent",
    reason="Security incident detected"
)

# All requests to this agent will be blocked
```

## Next Steps

- Read the [Architecture Guide](docs/architecture.md) to understand the design
- Check the [Policy Specification](docs/policy-spec.md) to write custom policies
- Review the [Compliance Guide](docs/compliance-guide.md) for regulatory details
- See the [Deployment Guide](docs/deployment-guide.md) for Kubernetes deployment
- Explore the [Demo Walkthrough](docs/demo-walkthrough.md) for more examples

## Troubleshooting

### Gateway won't start

```bash
# Check if port 8000 is available
lsof -i :8000

# Start on different port
python -m gateway.main --port 8080
```

### Package import errors

```bash
# Reinstall the package
pip uninstall ai-control-plane
pip install -e ".[dev]"
```

### Dashboard not loading

```bash
# Check the gateway logs
python -m gateway.main

# Verify dashboard is mounted
curl http://localhost:8000/dashboard/health
```

## Support

- **Documentation**: [GitHub Docs](https://github.com/Arnoldlarry15/ai-control-plane/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/Arnoldlarry15/ai-control-plane/issues)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

**Welcome to AI Control Plane v1.0.0 - Production-Ready AI Governance**
