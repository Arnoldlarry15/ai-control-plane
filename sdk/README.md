# AI Control Plane SDKs

Enterprise-grade AI governance for multiple programming languages.

## Available SDKs

### Python SDK

Located in `sdk/python/`

**Installation:**
```bash
pip install ai-control-plane
```

**Quick Start:**
```python
from sdk.python.client import ControlPlaneClient

client = ControlPlaneClient(base_url="http://localhost:8000")

# Register agent
agent = client.register_agent(
    name="my-bot",
    model="gpt-4",
    policies=["no-pii"]
)

# Execute
response = client.execute(
    agent_id=agent["agent_id"],
    prompt="Hello, world!"
)
```

**Features:**
- Full API coverage
- Structured exceptions
- Type hints
- Async support (coming soon)

### TypeScript/JavaScript SDK

Located in `sdk/typescript/`

**Installation:**
```bash
npm install @ai-control-plane/sdk
```

**Quick Start:**
```typescript
import { ControlPlaneClient } from '@ai-control-plane/sdk';

const client = new ControlPlaneClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your-key'
});

// Register agent
const agent = await client.registerAgent({
  name: 'my-bot',
  model: 'gpt-4',
  policies: ['no-pii']
});

// Execute
const response = await client.execute({
  agentId: agent.agentId,
  prompt: 'Hello, world!'
});
```

**Features:**
- Full TypeScript support
- Promise-based API
- Type definitions
- Structured errors

See [sdk/typescript/README.md](typescript/README.md) for full documentation.

## CLI Tool

Command-line interface for all governance operations.

**Installation:**
```bash
pip install ai-control-plane
# CLI is available as 'acp' command
```

**Quick Start:**
```bash
# Register agent
acp register my-bot gpt-4 --policies no-pii

# Execute
acp execute agent-123 --prompt "Hello, world!"

# Query logs
acp logs --user alice@example.com
```

See [docs/cli-guide.md](../docs/cli-guide.md) for full CLI documentation.

## Configuration Support

### Terraform-style Configuration

Declarative infrastructure-as-code for AI governance.

**Example:**
```yaml
# agents.yaml
variable "environment" {
  type = string
  default = "production"
}

resource "agent" "support_bot" {
  name = "customer-support"
  model = "gpt-3.5-turbo"
  risk_level = "low"
  policies = ["no-pii", "business-hours"]
  environment = "${var.environment}"
}
```

**Apply:**
```python
from core.config_loader import ConfigApplier
from sdk.python.client import ControlPlaneClient

client = ControlPlaneClient()
applier = ConfigApplier(client)
results = applier.apply("agents.yaml")
```

**Plan:**
```python
applier.plan("agents.yaml")
```

## SDK Comparison

| Feature | Python | TypeScript | CLI |
|---------|--------|-----------|-----|
| Agent Management | ✅ | ✅ | ✅ |
| Execution | ✅ | ✅ | ✅ |
| Audit Logs | ✅ | ✅ | ✅ |
| Kill Switch | ✅ | ✅ | ✅ |
| Type Safety | Type Hints | Full Types | N/A |
| Async Support | Coming Soon | ✅ | N/A |
| Config Files | ✅ | Coming Soon | ✅ |

## Development

### Python SDK

```bash
cd sdk/python
pip install -e .
pytest tests/
```

### TypeScript SDK

```bash
cd sdk/typescript
npm install
npm run build
npm test
```

### CLI

```bash
cd cli
python acp.py --help
```

## Future SDKs

Coming soon:
- Go SDK
- Java SDK
- Ruby SDK
- Rust SDK

## Support

- **Documentation**: https://github.com/Arnoldlarry15/ai-control-plane/docs
- **Issues**: https://github.com/Arnoldlarry15/ai-control-plane/issues
- **Examples**: https://github.com/Arnoldlarry15/ai-control-plane/examples

## License

Apache-2.0
