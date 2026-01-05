# Quick Start: Platform Features

Welcome to the **Operating System for AI Usage**. This guide shows you how to use the new platform capabilities that make ai-control-plane more than just a tool.

## What's New: "Salesforce of AI" Features

The platform now includes:

1. **Declarative Policy DSL** - Write policies like business rules
2. **Plugin System** - Extend without modifying core
3. **Cryptographic Audit Trail** - Legally defensible logs
4. **Policy Explainability** - Transparent decisions
5. **Lifecycle Hooks** - Intercept execution at any stage

---

## 1. Declarative Policies

**Before (Code):**
```python
def my_policy(request):
    if request.model == "gpt-4" and request.risk == "high":
        return "escalate"
```

**After (Business Rules):**
```yaml
policy:
  name: "High Risk Control"
  when:
    and:
      - field: "model"
        equals: "gpt-4"
      - field: "agent.risk_level"
        equals: "high"
  then: "escalate"
  reason: "High-risk model requires approval"
```

### Using the Policy DSL

```python
from policy.dsl import BusinessPolicy

policy = BusinessPolicy(
    name="Cost Control",
    description="Require approval for expensive operations",
    when={
        "field": "context.estimated_cost",
        "greater_than": 100
    },
    then="escalate",
    reason="Cost exceeds $100 threshold"
)

# Evaluate against context
context = {"context": {"estimated_cost": 150}}
result = policy.evaluate(context)
# result = {"matched": True, "action": "escalate", "reason": "..."}
```

### Policy Templates

```python
from policy.dsl import get_policy_template, POLICY_TEMPLATES

# List available templates
print(POLICY_TEMPLATES.keys())
# ['require_approval_for_model', 'block_pii', 'high_risk_escalation', ...]

# Use a template
policy = get_policy_template(
    "require_approval_for_model",
    MODEL_NAME="gpt-4"
)
```

---

## 2. Plugin System

### Creating a Custom Risk Scorer

```python
from policy.plugins import RiskScorerPlugin

class IndustryRiskScorer(RiskScorerPlugin):
    @property
    def plugin_id(self) -> str:
        return "industry-risk-scorer"
    
    @property
    def plugin_name(self) -> str:
        return "Healthcare Industry Risk Model"
    
    def calculate_risk_score(self, agent_id, prompt, context):
        score = 0
        factors = []
        
        # Your custom logic
        if "PHI" in prompt or "patient" in prompt:
            score += 50
            factors.append("Healthcare data detected")
        
        return {
            "score": score,
            "level": "high" if score > 50 else "medium",
            "factors": factors,
            "recommendations": ["HIPAA review required"]
        }
```

### Registering Plugins

```python
from policy.plugins import PluginRegistry

registry = PluginRegistry()
registry.register(IndustryRiskScorer())

# List plugins
plugins = registry.list_plugins()
```

### Creating Lifecycle Hooks

```python
from policy.plugins import LifecycleHookPlugin

class NotificationHook(LifecycleHookPlugin):
    @property
    def plugin_id(self) -> str:
        return "slack-notification"
    
    @property
    def plugin_name(self) -> str:
        return "Slack Notifications"
    
    @property
    def hook_stage(self) -> str:
        return "on_escalate"
    
    def on_escalate(self, context):
        # Send Slack notification
        send_slack_message(
            channel="#ai-governance",
            message=f"Request escalated: {context['execution_id']}"
        )
        return {"status": "continue"}
```

---

## 3. Cryptographic Audit Trail

### Using the Audit Trail

```python
from observability.audit_trail import AuditTrail

trail = AuditTrail()

# Append events
entry = trail.append(
    event_type="execution_started",
    action="start_execution",
    status="initiated",
    details={"agent_id": "my-agent"},
    execution_id="exec-123",
    agent_id="my-agent",
    user="alice@company.com"
)

# Verify integrity
integrity = trail.verify_integrity()
if integrity["valid"]:
    print("✓ Audit trail integrity verified")
else:
    print("✗ TAMPERING DETECTED")
```

### Chain of Custody

```python
# Get complete chain of custody for an execution
chain = trail.get_chain_of_custody("exec-123")

print(f"Status: {chain['status']}")
print(f"Total events: {chain['total_events']}")

for event in chain['timeline']:
    print(f"  {event['timestamp']}: {event['event_type']}")
    print(f"    Hash verified: {event['hash_verified']}")
```

### Compliance Export

```python
# Export as JSON
json_export = trail.export_for_compliance(
    start_date="2024-01-01",
    end_date="2024-12-31",
    format="json"
)

# Export as CSV
csv_export = trail.export_for_compliance(format="csv")
```

---

## 4. Policy Explainability

### Explaining Decisions

```python
from policy.explainer import PolicyExplainer

explainer = PolicyExplainer()

explanation = explainer.explain_decision(
    decision="block",
    context={
        "agent_id": "my-agent",
        "model": "gpt-4",
        "user": "alice"
    },
    policies_evaluated=[
        {"name": "PII Protection", "action": "block", "matched": True}
    ],
    final_policy={"name": "PII Protection", "reason": "SSN detected"}
)

# Machine-readable format
print(explanation.to_dict())

# Human-readable format
print(explanation.to_plain_english())
```

### Dry-Run Mode

Test policies without executing:

```python
from policy.explainer import PolicyExplainer

explainer = PolicyExplainer()
report = explainer.generate_dry_run_report(
    context={"model": "gpt-4", "risk": "high"},
    all_policies=loaded_policies
)

print(f"Decision: {report['final_decision']}")
print(f"Policies matched: {report['policies_matched']}")
```

---

## 5. API Endpoints

### New Endpoints Available

**Audit Trail:**
```bash
# Verify audit integrity
curl http://localhost:8000/api/audit/integrity

# Export audit trail
curl http://localhost:8000/api/audit/export?format=json

# Get chain of custody
curl http://localhost:8000/api/audit/chain-of-custody/{execution_id}
```

**Plugins:**
```bash
# List registered plugins
curl http://localhost:8000/api/plugins
```

**Policy Tools:**
```bash
# Dry-run policy evaluation
curl -X POST http://localhost:8000/api/policies/dry-run \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-agent", "prompt": "test"}'

# List policy templates
curl http://localhost:8000/api/policies/templates

# Get specific template
curl http://localhost:8000/api/policies/templates/block_pii
```

---

## 6. Complete Example

```python
from sdk.python.client import ControlPlaneClient
from policy.dsl import BusinessPolicy
from policy.plugins import PluginRegistry, RiskScorerPlugin
from observability.audit_trail import AuditTrail

# 1. Initialize client
client = ControlPlaneClient(base_url="http://localhost:8000")

# 2. Register agent with declarative policies
agent = client.register_agent(
    name="customer-service-bot",
    model="gpt-4",
    risk_level="medium",
    policies=["gdpr-compliance", "pii-protection"]
)

# 3. Create custom policy
custom_policy = BusinessPolicy(
    name="Business Hours Only",
    description="Block requests outside business hours",
    when={
        "or": [
            {"field": "context.hour", "less_than": 9},
            {"field": "context.hour", "greater_than": 17}
        ]
    },
    then="block",
    reason="Requests only allowed during business hours (9-17)"
)

# 4. Execute with full governance
response = client.execute(
    agent_id=agent.id,
    prompt="Help customer with account issue",
    context={
        "user": "alice@company.com",
        "hour": 14  # 2 PM - within business hours
    }
)

# 5. Review explanation
if "explanation" in response:
    print(response["explanation"]["primary_reason"])

# 6. Verify audit trail
integrity = client.verify_audit_integrity()
print(f"Audit trail valid: {integrity['valid']}")

# 7. Export for compliance
export = client.export_audit_trail(
    start_date="2024-01-01",
    format="json"
)
```

---

## Demo Script

Run the comprehensive demo:

```bash
python demo/platform_demo.py
```

This demonstrates all five key capabilities:
1. Declarative Policy DSL
2. Plugin System
3. Cryptographic Audit Trail
4. Policy Explainability
5. Compliance Export

---

## Why This Matters

### Before (Tool)
- Policies in Python code
- Basic logging
- Manual compliance
- Opaque decisions
- Inflexible core

### After (Platform)
- Policies as business rules (YAML)
- Cryptographically verified logs
- Export-ready compliance
- Explained decisions
- Plugin ecosystem

**This is not an incremental improvement. This is a category shift.**

From tool → to platform  
From feature → to infrastructure  
From optional → to inevitable

---

## Next Steps

1. **Review PLATFORM.md** - Understand the philosophy
2. **Run the demo** - See features in action
3. **Read docs/** - Deep dive into architecture
4. **Build a plugin** - Extend with your logic
5. **Deploy to production** - See deployment guide

---

## Support

- Documentation: `docs/`
- Architecture: `docs/architecture.md`
- Platform Philosophy: `PLATFORM.md`
- Issues: GitHub Issues
- Community: (Coming soon)

---

**Remember:** This is not a tool you configure. It's a platform you extend.

🎯 The Salesforce of AI
