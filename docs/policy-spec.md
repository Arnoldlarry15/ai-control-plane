# Policy Specification

## Overview

Policies in **ai-control-plane** are deterministic rules that govern AI behavior. They are:

- **Code, not configuration** - Version controlled and reviewable
- **Declarative** - Express what should happen, not how
- **Composable** - Multiple policies can apply to a single agent
- **Deterministic** - Same input always produces same output

---

## Policy Structure

Policies are defined in YAML format:

```yaml
policy:
  id: "no-pii-policy"
  version: "1.0"
  name: "Block PII in Prompts"
  description: "Prevents personally identifiable information in user prompts"
  
  rules:
    - condition:
        input_contains_any:
          - "ssn"
          - "social security"
          - "credit card"
          - "passport number"
      action: block
      reason: "PII detected in input"
    
    - condition:
        input_matches_pattern: "\\d{3}-\\d{2}-\\d{4}"  # SSN pattern
      action: block
      reason: "SSN pattern detected"
```

---

## Policy Actions

Each policy rule can return one of three actions:

### 1. `allow`
- Request proceeds normally
- Logged as approved
- No human intervention

### 2. `block`
- Request is immediately rejected
- Returns 403 Forbidden
- Logged with reason

### 3. `escalate`
- Request is queued for human approval
- Returns 202 Accepted (pending)
- User can poll for decision

---

## Policy Types

### Input Policies

Evaluate the request before execution.

**Examples**:
- Content filtering (profanity, violence)
- PII detection
- Injection attack prevention
- Rate limiting per user
- Time-based restrictions (business hours only)

```yaml
policy:
  id: "business-hours-only"
  rules:
    - condition:
        time_outside_range:
          start: "09:00"
          end: "17:00"
          timezone: "UTC"
      action: block
      reason: "Execution only allowed during business hours"
```

### Output Policies

Evaluate the response after execution.

**Examples**:
- PII redaction in responses
- Toxicity filtering
- Sensitive data masking
- Compliance validation

```yaml
policy:
  id: "redact-pii-output"
  rules:
    - condition:
        output_contains_pattern: "\\d{3}-\\d{2}-\\d{4}"
      action: redact
      replacement: "[REDACTED-SSN]"
```

### Agent Policies

Apply to specific agents or agent classes.

**Examples**:
- Require approval for high-risk agents
- Limit to specific models
- Environment restrictions

```yaml
policy:
  id: "high-risk-approval"
  applies_to:
    risk_level: ["high", "critical"]
  rules:
    - condition:
        always: true
      action: escalate
      reason: "High-risk agent requires approval"
```

### Rate Limit Policies

Control execution frequency.

```yaml
policy:
  id: "rate-limit-user"
  rules:
    - condition:
        requests_per_minute: 10
        scope: "user"
      action: block
      reason: "Rate limit exceeded"
```

---

## Policy Conditions

### Text Matching

```yaml
condition:
  input_contains: "specific phrase"
  input_contains_any: ["phrase1", "phrase2"]
  input_matches_pattern: "regex pattern"
  input_length_exceeds: 1000
```

### Contextual

```yaml
condition:
  user_role_not_in: ["admin", "developer"]
  environment: "production"
  agent_risk_level: "high"
```

### Temporal

```yaml
condition:
  time_outside_range:
    start: "09:00"
    end: "17:00"
  day_of_week_in: ["saturday", "sunday"]
```

### Rate-based

```yaml
condition:
  requests_per_minute: 10
  requests_per_hour: 100
  requests_per_day: 1000
  scope: "user" | "agent" | "global"
```

---

## Policy Evaluation Order

1. **Kill Switch** (pre-policy check)
2. **Registry Validation** (agent exists?)
3. **Input Policies** (evaluate request)
4. **Rate Limits** (check quotas)
5. **Agent-Specific Policies**
6. **Execution** (if allowed)
7. **Output Policies** (evaluate response)

**Important**: First `block` or `escalate` wins. Evaluation stops immediately.

---

## Policy Assignment

Policies can be assigned at multiple levels:

### Global Policies
Apply to ALL agents.

```yaml
registry:
  global_policies:
    - "no-pii-policy"
    - "business-hours-only"
```

### Agent-Specific Policies

```yaml
agent:
  id: "customer-support-bot"
  policies:
    - "no-pii-policy"
    - "polite-language-only"
    - "rate-limit-user"
```

### Risk-Level Policies

```yaml
policy_assignments:
  risk_level:
    high:
      - "require-approval"
      - "detailed-logging"
    critical:
      - "require-dual-approval"
      - "executive-notification"
```

---

## Policy Versioning

All policies are versioned:

```yaml
policy:
  id: "no-pii-policy"
  version: "2.0"
  replaces: "1.0"
  effective_date: "2026-01-15T00:00:00Z"
```

**Rules**:
- Version increments on any change
- Old versions remain for audit purposes
- Active version is clearly marked
- Changes are logged in observability

---

## Built-in Policies

The control plane ships with standard policies:

- `allow-all`: Permissive mode for testing
- `block-all`: Emergency lockdown
- `require-approval`: Force human review
- `no-pii-basic`: Basic PII detection
- `rate-limit-standard`: Sensible defaults

---

## Custom Policy Development

### Step 1: Define Policy YAML

```yaml
policy:
  id: "my-custom-policy"
  version: "1.0"
  name: "My Custom Policy"
  rules:
    - condition:
        input_contains: "forbidden"
      action: block
```

### Step 2: Register Policy

```bash
curl -X POST http://localhost:8000/api/policies \
  -H "Content-Type: application/yaml" \
  --data-binary @my-policy.yaml
```

### Step 3: Assign to Agent

```bash
curl -X POST http://localhost:8000/api/agents/{agent_id}/policies \
  -d '{"policy_id": "my-custom-policy"}'
```

---

## Policy Testing

Before deploying policies to production:

```python
from policy.evaluator import PolicyEvaluator

evaluator = PolicyEvaluator()
policy = evaluator.load_policy("no-pii-policy")

# Test case
result = evaluator.evaluate(
    policy=policy,
    input_text="My SSN is 123-45-6789",
    context={}
)

assert result.action == "block"
assert "SSN" in result.reason
```

---

## Best Practices

1. **Start Permissive**: Begin with `allow-all`, add restrictions gradually
2. **Test Thoroughly**: Use demo scripts to validate policies
3. **Version Everything**: Never modify policies in place
4. **Document Reasons**: Clear explanations for each rule
5. **Monitor Impact**: Track block/escalate rates
6. **Fail Closed**: When in doubt, block

---

## Policy Language Grammar (Formal)

```
Policy ::= {
  id: String,
  version: SemVer,
  name: String,
  rules: [Rule+]
}

Rule ::= {
  condition: Condition,
  action: Action,
  reason?: String
}

Condition ::= 
  | { input_contains: String }
  | { input_matches_pattern: Regex }
  | { time_outside_range: TimeRange }
  | { requests_per_minute: Integer }
  | ...

Action ::= "allow" | "block" | "escalate" | "redact"
```

---

## Example: Complete Policy File

```yaml
policy:
  id: "production-safe-agent"
  version: "1.0"
  name: "Production Safety Policy"
  description: "Comprehensive safety policy for production agents"
  
  rules:
    # Block obvious PII
    - condition:
        input_matches_pattern: "\\d{3}-\\d{2}-\\d{4}"
      action: block
      reason: "SSN pattern detected"
    
    # Block after hours
    - condition:
        time_outside_range:
          start: "06:00"
          end: "22:00"
          timezone: "UTC"
      action: block
      reason: "Outside operational hours"
    
    # Rate limit aggressive users
    - condition:
        requests_per_minute: 20
        scope: "user"
      action: block
      reason: "Rate limit exceeded"
    
    # Escalate high-value requests
    - condition:
        input_contains_any:
          - "delete"
          - "remove"
          - "cancel subscription"
      action: escalate
      reason: "Destructive action requires approval"
    
    # Default: allow
    - condition:
        always: true
      action: allow
```

---

## Advanced: Custom Evaluators

For complex logic beyond YAML, implement custom evaluators in Python:

```python
from policy.evaluator import CustomPolicyEvaluator

class SentimentPolicyEvaluator(CustomPolicyEvaluator):
    def evaluate(self, input_text, context):
        sentiment_score = self.analyze_sentiment(input_text)
        
        if sentiment_score < -0.5:
            return PolicyDecision(
                action="block",
                reason="Negative sentiment detected"
            )
        
        return PolicyDecision(action="allow")
```

---

## FAQ

**Q: What happens if policies conflict?**
A: First match wins. Order matters.

**Q: Can policies call external services?**
A: Not recommended. Keep policies fast and deterministic.

**Q: How do I temporarily disable a policy?**
A: Use the kill switch or deactivate the policy version.

**Q: What's the performance impact?**
A: Sub-millisecond for simple rules. Complex regex may add latency.
