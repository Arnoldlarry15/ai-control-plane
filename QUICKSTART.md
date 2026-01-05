# AI Control Plane - Quick Start Guide

## What Is This?

**ai-control-plane** is a governance layer for AI systems. It sits between your application and AI models (OpenAI, Anthropic, etc.) to provide:

- ✅ Policy enforcement (block PII, rate limits, etc.)
- ✅ Complete audit trail (every request logged)
- ✅ Emergency controls (kill switch)
- ✅ Human approval workflows
- ✅ Centralized registration (no shadow AI)

## Installation

```bash
git clone https://github.com/Arnoldlarry15/ai-control-plane.git
cd ai-control-plane
pip install -r requirements.txt
```

## Running the System

### 1. Start the Gateway

```bash
python -m gateway.main
```

The gateway will start on `http://localhost:8000`

### 2. Register an AI Agent

```bash
python demo/register_agent.py
```

This registers a customer support bot with PII protection policies.

### 3. Run a Normal Execution

```bash
python demo/run_normal.py
```

This shows a successful AI execution through the control plane.

### 4. Test Policy Enforcement

```bash
python demo/trigger_violation.py
```

This demonstrates how policies block prohibited content (PII detection).

### 5. Test Kill Switch

```bash
python demo/kill_agent.py
```

This shows instant emergency shutdown capabilities.

## Using the SDK

```python
from sdk.python.client import ControlPlaneClient

# Initialize client
client = ControlPlaneClient(base_url="http://localhost:8000")

# Register an agent
agent = client.register_agent(
    name="my-agent",
    model="gpt-3.5-turbo",
    policies=["no-pii"]
)

# Execute through control plane
response = client.execute(
    agent_id=agent["agent_id"],
    prompt="What are your business hours?",
    user="user@company.test"
)

print(response["response"])
```

## Running Tests

```bash
pytest tests/ -v
```

All 22 tests should pass.

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│    Gateway       │  ← The Choke Point
│  (Enforces All)  │
└──────┬───────────┘
       │
   ┌───┴───┬─────────┬──────────┬───────┐
   ▼       ▼         ▼          ▼       ▼
Registry Policy  Kill    Audit  Approval
         Engine  Switch   Log
```

## Key Features

### 1. Fail Closed
If any component fails, execution is blocked. No bypass.

### 2. Everything Logged
Complete audit trail of all requests, decisions, and responses.

### 3. Policies are Code
Policies are YAML files in version control, reviewed like code.

### 4. Gateway is Mandatory
All AI calls flow through the gateway. No direct access.

### 5. Kill Switch is Instant
Emergency shutdown in sub-millisecond timeframes.

### 6. No Hidden Magic
Transparent, deterministic behavior. No ML in the control plane.

## What This Is NOT

- ❌ Not an AI model (we don't train models)
- ❌ Not a vector database
- ❌ Not a prompt management system
- ❌ Not an observability platform (for monitoring apps)

## What This IS

✅ A governance layer for AI systems
✅ Ensures AI behavior is accountable
✅ Makes AI usage interruptible and safe
✅ Provides compliance and audit capabilities

## Next Steps

1. Read `docs/architecture.md` for system design
2. Read `docs/policy-spec.md` to write custom policies
3. Read `docs/threat-model.md` for security considerations
4. Read `docs/demo-walkthrough.md` for detailed usage

## Support

This is an open-source project focused on making AI governance accessible and practical.

**The platform is real. The governance is real. The value is immediate.**
