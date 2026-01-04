# Demo Walkthrough

## Overview

This walkthrough demonstrates the core capabilities of **ai-control-plane** in 10 minutes.

You'll see:
1. ✅ Agent registration
2. ✅ Normal execution (allowed)
3. ❌ Policy violation (blocked)
4. ⏸️ Approval workflow (escalated)
5. 🛑 Kill switch (emergency stop)
6. 📜 Audit log replay

---

## Prerequisites

```bash
# Clone and setup
git clone https://github.com/Arnoldlarry15/ai-control-plane.git
cd ai-control-plane
pip install -r requirements.txt

# Set your OpenAI API key (or other provider)
export OPENAI_API_KEY="sk-..."
```

---

## Step 1: Start the Control Plane

```bash
# Terminal 1: Start the gateway
python -m gateway.main

# Expected output:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

The gateway is now running. All AI requests will flow through it.

---

## Step 2: Register an AI Agent

```bash
# Terminal 2: Register an agent
python demo/register_agent.py
```

**What happens**:
- Agent `customer-support-bot` is registered
- Risk level: `medium`
- Policies: `no-pii`, `business-hours`, `rate-limit-standard`
- Model: `gpt-3.5-turbo`

**Output**:
```json
{
  "agent_id": "customer-support-bot",
  "status": "registered",
  "risk_level": "medium",
  "policies": ["no-pii", "business-hours", "rate-limit-standard"]
}
```

**Key concept**: Nothing executes without registration. This prevents shadow AI.

---

## Step 3: Normal Execution (Allowed)

```bash
python demo/run_normal.py
```

**Request**:
```json
{
  "agent_id": "customer-support-bot",
  "prompt": "What are your business hours?",
  "user": "alice@example.com"
}
```

**What happens**:
1. Gateway receives request
2. Checks kill switch (✅ active)
3. Validates agent exists (✅ registered)
4. Evaluates policies (✅ no violations)
5. Executes against OpenAI API
6. Logs everything
7. Returns response

**Output**:
```json
{
  "status": "success",
  "response": "Our business hours are Monday-Friday, 9 AM to 5 PM EST.",
  "execution_id": "exec-1234",
  "latency_ms": 342
}
```

**Check the logs**:
```bash
# Terminal 3: View audit log
curl http://localhost:8000/api/logs/exec-1234
```

You'll see:
- Full request and response
- Policy evaluation results
- Execution metadata
- Timestamps

---

## Step 4: Policy Violation (Blocked)

```bash
python demo/trigger_violation.py
```

**Request**:
```json
{
  "agent_id": "customer-support-bot",
  "prompt": "My SSN is 123-45-6789 and I need help",
  "user": "bob@example.com"
}
```

**What happens**:
1. Gateway receives request
2. Evaluates `no-pii` policy
3. Detects SSN pattern
4. **BLOCKS execution** ❌
5. Logs violation
6. Returns error

**Output**:
```json
{
  "status": "blocked",
  "reason": "Policy violation: PII detected in input",
  "policy_id": "no-pii",
  "execution_id": "exec-1235"
}
```

**Key concept**: The AI model never saw this request. Policy enforcement happens at the gateway.

**Check the logs**:
```bash
curl http://localhost:8000/api/logs/exec-1235
```

You'll see:
- Request (with PII)
- Policy violation details
- NO model response (never executed)

---

## Step 5: Approval Workflow (Escalated)

Now let's trigger an approval requirement:

```bash
# Terminal 2: Send request that requires approval
python demo/request_approval.py
```

**Request**:
```json
{
  "agent_id": "customer-support-bot",
  "prompt": "Cancel my subscription and delete my account",
  "user": "charlie@example.com"
}
```

**What happens**:
1. Gateway evaluates policies
2. `destructive-action` policy triggers
3. Action: **escalate** ⏸️
4. Request queued for human approval
5. Returns 202 Accepted (pending)

**Output**:
```json
{
  "status": "pending_approval",
  "approval_id": "approval-5678",
  "message": "Request queued for human review",
  "estimated_wait": "< 5 minutes"
}
```

**Approve the request**:
```bash
# Terminal 3: View pending approvals
curl http://localhost:8000/api/approvals/pending

# Approve it (requires admin token)
curl -X POST http://localhost:8000/api/approvals/approval-5678/approve \
  -H "Authorization: Bearer <admin-token>" \
  -d '{"reviewer": "manager@example.com", "comment": "Approved per policy"}'
```

**Check approval status**:
```bash
python demo/check_approval_status.py --approval-id approval-5678
```

**Output**:
```json
{
  "approval_id": "approval-5678",
  "status": "approved",
  "reviewer": "manager@example.com",
  "reviewed_at": "2026-01-04T16:30:00Z",
  "execution_id": "exec-1236"
}
```

Now the AI execution proceeds.

**Key concept**: Human-in-the-loop for sensitive operations. No automatic execution of risky actions.

---

## Step 6: Kill Switch (Emergency Stop)

The "oh shit" button. Instant shutdown.

```bash
# Terminal 2: Try to execute
python demo/run_normal.py
# ✅ Works

# Terminal 3: Activate kill switch (global)
curl -X POST http://localhost:8000/api/kill-switch/activate \
  -H "Authorization: Bearer <admin-token>" \
  -d '{"scope": "global", "reason": "Emergency maintenance"}'
```

**Output**:
```json
{
  "status": "activated",
  "scope": "global",
  "reason": "Emergency maintenance",
  "activated_by": "admin@example.com",
  "activated_at": "2026-01-04T16:35:00Z"
}
```

**Try to execute again**:
```bash
python demo/run_normal.py
```

**Output**:
```json
{
  "status": "blocked",
  "reason": "Kill switch activated: Emergency maintenance",
  "execution_id": null
}
```

**Key concept**: Instant, reliable shutdown. No bypass. Every request is blocked.

**Deactivate kill switch**:
```bash
curl -X POST http://localhost:8000/api/kill-switch/deactivate \
  -H "Authorization: Bearer <admin-token>"
```

**Try execution again**:
```bash
python demo/run_normal.py
# ✅ Works again
```

**Granular kill switch** (per-agent):
```bash
# Kill just one agent
curl -X POST http://localhost:8000/api/kill-switch/activate \
  -d '{"scope": "agent", "agent_id": "customer-support-bot", "reason": "Agent misbehaving"}'

# Other agents still work, but this one is blocked
```

---

## Step 7: Audit Log Replay

View complete history:

```bash
# Get all executions for a user
curl http://localhost:8000/api/logs?user=alice@example.com

# Get all policy violations
curl http://localhost:8000/api/logs?status=blocked

# Get all kill switch activations
curl http://localhost:8000/api/logs/kill-switch

# Replay a specific execution
curl http://localhost:8000/api/logs/exec-1234/replay
```

**Key concept**: Complete audit trail. Every decision is logged and can be replayed.

---

## Demo Script (All Steps)

Run everything in sequence:

```bash
# Start gateway
python -m gateway.main &

# Wait for startup
sleep 3

# Run demo
./demo/run_full_demo.sh

# Expected output:
# ✅ Step 1: Agent registered
# ✅ Step 2: Normal execution allowed
# ❌ Step 3: PII violation blocked
# ⏸️ Step 4: Approval requested
# ✅ Step 5: Approval granted, execution completed
# 🛑 Step 6: Kill switch activated, execution blocked
# ✅ Step 7: Kill switch deactivated, execution resumed
# 📜 Step 8: Audit logs retrieved
```

---

## Understanding the Value

### Without Control Plane

```python
# Direct OpenAI call
import openai
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}]
)
```

**Problems**:
- ❌ No policy enforcement
- ❌ No audit trail
- ❌ No emergency controls
- ❌ No approval workflow
- ❌ Shadow AI usage

### With Control Plane

```python
# Through control plane
from sdk.python.client import ControlPlaneClient

client = ControlPlaneClient()
response = client.execute(
    agent_id="customer-support-bot",
    prompt=prompt
)
```

**Benefits**:
- ✅ All policies enforced
- ✅ Complete audit trail
- ✅ Kill switch available
- ✅ Approval workflows
- ✅ Centralized governance

**Same API feel, enterprise controls.**

---

## Advanced Demo: Multi-Agent Scenario

```bash
python demo/multi_agent_scenario.py
```

**Scenario**:
- 3 agents: `support-bot`, `sales-bot`, `research-bot`
- Different risk levels and policies
- Simultaneous execution
- One agent gets killed mid-flight

**Demonstrates**:
- Per-agent policies
- Granular kill switch
- Concurrent execution
- Independent governance

---

## Demo for Executives

5-minute version with business value:

```bash
python demo/executive_demo.py
```

**Shows**:
1. **Risk mitigation**: PII blocked automatically
2. **Compliance**: Complete audit trail
3. **Control**: Kill switch stops rogue agents
4. **Productivity**: Fast approval workflows
5. **Visibility**: Real-time monitoring

**Key message**: "AI governance that doesn't slow you down."

---

## Demo for Security Teams

Focus on threat scenarios:

```bash
python demo/security_demo.py
```

**Shows**:
1. **Shadow AI prevention**: Unregistered agents can't run
2. **Data exfiltration**: Policies block sensitive output
3. **Insider threat**: Audit trail catches misuse
4. **Incident response**: Kill switch enables quick containment
5. **Forensics**: Log replay for investigation

---

## Customization

Modify demo scripts to match your use case:

```python
# demo/custom_scenario.py
from sdk.python.client import ControlPlaneClient

client = ControlPlaneClient()

# Register your agent
agent = client.register_agent(
    name="my-custom-agent",
    model="gpt-4",
    risk_level="high",
    policies=["my-custom-policy"]
)

# Execute with your prompt
response = client.execute(
    agent_id=agent.id,
    prompt="Your specific use case...",
    context={"department": "finance"}
)

print(f"Status: {response.status}")
print(f"Response: {response.content}")
```

---

## Troubleshooting

### Gateway won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
python -m gateway.main --port 8080
```

### Agent registration fails
```bash
# Check registry service
curl http://localhost:8000/api/health

# View logs
tail -f logs/gateway.log
```

### Execution blocked unexpectedly
```bash
# Check kill switch status
curl http://localhost:8000/api/kill-switch/status

# Check policy evaluation
curl http://localhost:8000/api/logs/<execution_id>
```

---

## Next Steps

After the demo:

1. **Read the docs**: [architecture.md](architecture.md), [policy-spec.md](policy-spec.md)
2. **Write custom policies**: Add your business rules
3. **Integrate your agents**: Use the SDK
4. **Set up monitoring**: Track violations and usage
5. **Plan rollout**: Start with dev environment, then production

---

## Demo Feedback

This demo proves:
- ✅ Control plane works
- ✅ Policies are enforceable
- ✅ Kill switch is instant
- ✅ Audit trail is complete
- ✅ Integration is simple

**The platform is real. The governance is real. The value is immediate.**
