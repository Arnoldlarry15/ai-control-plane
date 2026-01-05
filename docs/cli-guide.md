# CLI Tool Guide

## Overview

The AI Control Plane CLI (`acp`) provides command-line access to all governance operations.

## Installation

### From Package

```bash
pip install ai-control-plane
```

### From Source

```bash
git clone https://github.com/Arnoldlarry15/ai-control-plane.git
cd ai-control-plane
pip install -e .
```

### Make CLI Accessible

Add to your PATH or create an alias:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias acp="python /path/to/ai-control-plane/cli/acp.py"

# Or create symlink
sudo ln -s /path/to/cli/acp.py /usr/local/bin/acp
```

## Configuration

Set environment variables:

```bash
export CONTROL_PLANE_URL="http://localhost:8000"
export CONTROL_PLANE_API_KEY="your-api-key"
```

Or pass as arguments:

```bash
acp --url http://localhost:8000 --api-key your-key [command]
```

## Commands

### Health Check

Check if the control plane is operational:

```bash
acp health
```

Output:
```
Gateway Status: healthy
✓ Control plane is operational
```

### Register Agent

Register a new AI agent:

```bash
acp register my-agent gpt-4 \
  --risk-level medium \
  --policies no-pii,business-hours \
  --environment production \
  --metadata team=engineering \
  --metadata cost_center=ENG-001
```

Output:
```
✓ Agent registered successfully
  Agent ID: agent-abc123
  Name: my-agent
  Model: gpt-4
  Risk Level: medium
```

### Execute Agent

Execute an agent with a prompt:

```bash
acp execute agent-abc123 \
  --prompt "Analyze this data..." \
  --user alice@company.com \
  --context session_id=12345
```

Or from a file:

```bash
acp execute agent-abc123 \
  --prompt-file prompt.txt \
  --user alice@company.com
```

Output:
```
✓ Execution successful
  Execution ID: exec-xyz789
  Status: success

Response:
Here is the analysis...
```

### List Agents

List all registered agents:

```bash
acp list
```

Output:
```
Total agents: 3

• customer-support-bot (agent-123)
  Model: gpt-3.5-turbo
  Risk: low
  Policies: no-pii, business-hours

• data-analyst (agent-456)
  Model: gpt-4
  Risk: high
  Policies: require-approval, no-pii
```

### Get Agent Details

Get detailed information about an agent:

```bash
acp get agent-abc123
```

Output:
```
Agent: my-agent
  ID: agent-abc123
  Model: gpt-4
  Risk Level: medium
  Environment: production
  Policies: no-pii, business-hours
  Created: 2026-01-05T10:00:00Z
```

### Query Logs

Query audit logs:

```bash
# All logs
acp logs --limit 50

# Filter by user
acp logs --user alice@company.com

# Filter by agent
acp logs --agent-id agent-abc123

# Filter by status
acp logs --status blocked
```

Output:
```
Total logs: 25

• Execution: exec-001
  Agent: agent-abc123
  User: alice@company.com
  Status: success
  Time: 2026-01-05T10:15:00Z
```

### Kill Switch

Manage emergency kill switch:

```bash
# Activate global kill switch
acp kill-switch activate \
  --scope global \
  --reason "Security incident"

# Activate for specific agent
acp kill-switch activate \
  --scope agent \
  --agent-id agent-abc123 \
  --reason "Agent compromised"

# Deactivate
acp kill-switch deactivate --scope global

# Check status
acp kill-switch status
```

## JSON Output

Add `--json` flag to any command for JSON output:

```bash
acp list --json
acp get agent-abc123 --json
acp logs --json
```

## Exit Codes

- `0` - Success
- `1` - Error (configuration, network, etc.)
- `2` - Execution blocked
- `3` - Approval pending

Use in scripts:

```bash
if acp execute agent-123 --prompt "test"; then
    echo "Success"
else
    exit_code=$?
    if [ $exit_code -eq 2 ]; then
        echo "Blocked by policy"
    elif [ $exit_code -eq 3 ]; then
        echo "Approval required"
    fi
fi
```

## Examples

### Register and Execute

```bash
# Register agent
AGENT_ID=$(acp register my-bot gpt-4 --json | jq -r '.agent_id')

# Execute
acp execute $AGENT_ID --prompt "Hello, world!"
```

### Batch Operations

```bash
# Register multiple agents from config
for agent in bot1 bot2 bot3; do
    acp register $agent gpt-3.5-turbo --policies no-pii
done
```

### Monitoring Script

```bash
#!/bin/bash
# Monitor for blocked requests

while true; do
    blocked=$(acp logs --status blocked --limit 10 --json)
    if [ $(echo "$blocked" | jq 'length') -gt 0 ]; then
        echo "Alert: Blocked requests detected"
        echo "$blocked" | jq '.[].reason'
    fi
    sleep 60
done
```

### CI/CD Integration

```bash
# In your CI pipeline
acp register ci-agent gpt-4 --environment ci

# Run tests through control plane
acp execute $AGENT_ID --prompt-file test_prompts.txt

# Check compliance
acp logs --agent-id $AGENT_ID --json | \
    jq '[.[] | select(.status == "blocked")] | length' | \
    grep -q "0" || exit 1
```

## Terraform Integration

Use CLI in Terraform null_resource:

```hcl
resource "null_resource" "register_agent" {
  provisioner "local-exec" {
    command = <<-EOT
      acp register ${var.agent_name} ${var.model} \
        --risk-level ${var.risk_level} \
        --policies ${join(",", var.policies)} \
        --environment ${var.environment}
    EOT
  }
}
```

## Configuration File Support (Future)

Coming soon: Load settings from `.acprc`:

```yaml
# ~/.acprc
url: http://localhost:8000
api_key: ${CONTROL_PLANE_API_KEY}
default_risk_level: medium
default_environment: production
```

## Advanced Usage

### Custom Output Formatting

```bash
# Pretty-print JSON
acp list --json | jq '.[] | {name: .name, model: .model}'

# Extract specific fields
acp get agent-123 --json | jq -r '.agent_id'

# CSV output
acp logs --json | jq -r '.[] | [.execution_id, .status] | @csv'
```

### Debugging

```bash
# Verbose output
export DEBUG=1
acp execute agent-123 --prompt "test"

# Check connectivity
curl $CONTROL_PLANE_URL/health
```

## Troubleshooting

### Connection Refused

```bash
# Check if gateway is running
curl http://localhost:8000/health

# Start gateway
python -m gateway.main
```

### Authentication Failed

```bash
# Check API key
echo $CONTROL_PLANE_API_KEY

# Test without auth
acp --url http://localhost:8000 health
```

### Command Not Found

```bash
# Check PATH
which acp

# Use full path
python /path/to/cli/acp.py health
```

## Support

- **Documentation**: https://github.com/Arnoldlarry15/ai-control-plane/docs
- **Issues**: https://github.com/Arnoldlarry15/ai-control-plane/issues
- **Examples**: https://github.com/Arnoldlarry15/ai-control-plane/examples
