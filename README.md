# ai-control-plane

**ai-control-plane** is an open, API-first platform for registering, governing, and observing AI systems.

It provides a centralized execution gateway, policy enforcement, audit logging, and human-in-the-loop controls to ensure AI behavior is accountable, interruptible, and safe by default.

**This project does not build AI models. It governs how they are used.**

---

## Features

- 🔐 **Centralized Execution Gateway**: Route all AI model/agent requests through a single control point
- 📋 **Policy Enforcement**: Define and enforce policies on AI behavior before, during, and after execution
- 📝 **Audit Logging**: Complete observability and replay of all AI interactions
- 👤 **Human-in-the-Loop**: Approval queues for sensitive operations
- 🛑 **Kill Switch**: Emergency controls to halt AI agents instantly
- 🔌 **API-First Design**: Simple integration via REST API and Python SDK

---

## Architecture

The control plane consists of several core modules:

- **Gateway**: API entry point and request routing
- **Registry**: Catalog of registered AI models and agents
- **Policy Engine**: Policy parsing, evaluation, and violation handling
- **Observability**: Event logging, storage, and replay capabilities
- **Approval Service**: Human review queue for flagged operations
- **Kill Switch**: Emergency shutdown and state management

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

- [Architecture Overview](docs/architecture.md)
- [Policy Specification](docs/policy-spec.md)
- [Threat Model](docs/threat-model.md)
- [Demo Walkthrough](docs/demo-walkthrough.md)

---

## Project Structure

```
ai-control-plane/
├── gateway/          # API gateway and routing
├── registry/         # Agent/model registry
├── policy/           # Policy engine
├── observability/    # Logging and audit
├── approval/         # Human-in-the-loop
├── kill_switch/      # Emergency controls
├── sdk/              # Client SDKs
├── demo/             # Example scripts
├── tests/            # Test suite
└── docs/             # Documentation
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
