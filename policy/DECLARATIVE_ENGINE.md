# Declarative Policy Engine v1

## Overview

The Declarative Policy Engine allows you to define governance policies using pure YAML/JSON configuration - **no Python code required**. This is the foundation of the "Salesforce of AI" approach: business-readable rules that anyone can understand and modify.

## Philosophy

**Declarative Over Imperative** - Policies are business rules, not Python code.

```yaml
# This is what users write - pure config
if:
  model: gpt-4
  risk_score: >0.7
then:
  require_approval: true
reason: "High-risk model with elevated risk score"
```

**No code. Just config. That's winning.**

## Basic Syntax

### Simple Field Matching

```yaml
if:
  model: gpt-4
then: escalate
reason: "GPT-4 requires approval"
```

### Comparison Operators

Supported operators: `>`, `>=`, `<`, `<=`

```yaml
if:
  risk_score: >0.7
then: block
reason: "Risk score too high"
```

```yaml
if:
  cost: >=100
then: require_approval
reason: "High cost operation"
```

### Logical Operators

#### AND (all conditions must match)

```yaml
if:
  and:
    - model: gpt-4
    - risk_score: >0.7
then: escalate
reason: "High-risk model with high score"
```

#### OR (any condition must match)

```yaml
if:
  or:
    - estimated_tokens: >10000
    - estimated_cost: >100
then: require_approval
reason: "High tokens or high cost"
```

#### NOT (condition must not match)

```yaml
if:
  not:
    environment: prod
then: allow
reason: "Non-production environment"
```

### List Matching

```yaml
if:
  risk_level:
    - high
    - critical
then: escalate
reason: "High or critical risk detected"
```

### Pattern Matching

#### Contains

```yaml
if:
  prompt: contains:SSN
then: block
reason: "PII detected in prompt"
```

#### Regex

```yaml
if:
  prompt: matches:\d{3}-\d{2}-\d{4}
then: block
reason: "SSN pattern detected"
```

### Nested Fields

Use dot notation for nested fields:

```yaml
if:
  user.role: admin
  context.environment: prod
then: allow
reason: "Admin in production"
```

## Actions

Available actions:
- `allow` - Allow the request
- `block` - Block the request
- `escalate` - Escalate for review
- `require_approval` - Require human approval
- `redact` - Redact sensitive content
- `warn` - Log warning but allow

### Action Flags

You can also use boolean flags in the `then` clause:

```yaml
then:
  require_approval: true
  # or
  block: true
  # or
  allow: true
```

## Real-World Examples

### High Risk Approval

```yaml
name: "High Risk Approval Required"
if:
  model: gpt-4
  risk_score: >0.7
then:
  require_approval: true
reason: "High-risk model with elevated risk score"
```

### Cost Control

```yaml
name: "Cost Control"
if:
  or:
    - estimated_tokens: >10000
    - estimated_cost: >100
then:
  require_approval: true
reason: "High cost operation requires approval"
```

### PII Blocking

```yaml
name: "Block PII"
if:
  prompt: contains:SSN
then: block
reason: "PII detected in prompt"
```

### Production Safety

```yaml
name: "Production Safety"
if:
  and:
    - environment: prod
    - risk_level:
        - high
        - critical
then: escalate
reason: "High-risk operation in production"
```

### Business Hours Only

```yaml
name: "Business Hours"
if:
  and:
    - hour: <9
    - hour: >17
then: block
reason: "Outside business hours"
```

### Model-Specific Rules

```yaml
name: "GPT-4 Restrictions"
if:
  model: gpt-4
then:
  require_approval: true
reason: "GPT-4 requires management approval"
```

## Python API

### Loading Policies

```python
from policy.declarative_engine import DeclarativePolicyEngine, create_policy_from_yaml_style

# Create engine
engine = DeclarativePolicyEngine()

# Load policy from dict
engine.load_policy({
    'name': 'High Risk',
    'if': {'risk_score': '>0.7'},
    'then': 'block',
    'reason': 'Risk too high'
})

# Or use helper
policy = create_policy_from_yaml_style({
    'name': 'Cost Control',
    'if': {'cost': '>=100'},
    'then': {'require_approval': True}
})
engine.load_policy(policy)
```

### Evaluating Policies

```python
# Evaluate against context
result = engine.evaluate({
    'model': 'gpt-4',
    'risk_score': 0.8,
    'cost': 150,
    'environment': 'prod'
})

print(result['action'])  # 'block' (most restrictive wins)
print(result['reason'])  # Why this decision was made
print(result['matched_policies'])  # All policies that matched
```

### Result Structure

```python
{
    'action': 'block',
    'reason': 'Risk too high',
    'policy_id': 'high-risk-policy',
    'policy_name': 'High Risk Policy',
    'matched_policies': ['high-risk-policy', 'cost-control'],
    'all_results': [...]  # All policy evaluation results
}
```

## Policy Resolution

When multiple policies match, the **most restrictive** action wins:

1. `block` (highest priority)
2. `require_approval` / `escalate`
3. `redact`
4. `warn`
5. `allow` (lowest priority)

Example:
```python
# Both policies match
engine.load_policy({'if': {'model': 'gpt-4'}, 'then': 'allow'})
engine.load_policy({'if': {'model': 'gpt-4'}, 'then': 'block'})

result = engine.evaluate({'model': 'gpt-4'})
# result['action'] == 'block'  # Most restrictive wins
```

## Loading from YAML Files

```python
import yaml
from policy.declarative_engine import DeclarativePolicyEngine, create_policy_from_yaml_style

# Load from YAML file
with open('policies/high-risk.yaml', 'r') as f:
    policy_spec = yaml.safe_load(f)

engine = DeclarativePolicyEngine()
engine.load_policy(create_policy_from_yaml_style(policy_spec))
```

## Example YAML File

```yaml
# policies/production-safety.yaml
name: "Production Safety Controls"
description: "Enhanced safety for production environment"

if:
  and:
    - environment: prod
    - or:
        - risk_level: [high, critical]
        - model: gpt-4
        - estimated_cost: >1000
then:
  require_approval: true

reason: "Production environment requires approval for high-risk operations"
enabled: true
priority: 100
```

## Best Practices

### 1. Keep Policies Simple
One policy, one concern. Easier to understand and maintain.

✅ Good:
```yaml
if:
  risk_score: >0.7
then: block
```

❌ Bad:
```yaml
if:
  and:
    - risk_score: >0.7
    - model: gpt-4
    - environment: prod
    - user.role: developer
    - cost: >100
then: maybe_escalate_sometimes
```

### 2. Use Descriptive Names and Reasons
```yaml
name: "GDPR Article 22 - Automated Decision Making"
reason: "Automated processing of personal data requires explicit consent (GDPR Art. 22)"
```

### 3. Test Policies in Dry-Run First
```yaml
enabled: true
enforce: false  # Monitor only, don't enforce yet
```

### 4. Version Your Policies
```yaml
name: "Cost Control"
version: "2.0"
description: "Updated thresholds for 2024"
```

### 5. Document Compliance References
```yaml
compliance_standard: "HIPAA"
regulatory_reference: "Privacy Rule § 164.502(a)"
```

## Advantages Over Code

### Before (Code-Based)
```python
def evaluate_policy(agent, prompt, context):
    if agent.model == "gpt-4":
        risk = calculate_risk(prompt)
        if risk > 0.7:
            if context.get("environment") == "prod":
                return {"action": "escalate", "reason": "..."}
    return {"action": "allow"}
```

### After (Declarative)
```yaml
if:
  and:
    - model: gpt-4
    - risk_score: >0.7
    - environment: prod
then: escalate
```

**Benefits:**
- ✅ Non-technical users can read and modify
- ✅ No code deployment required
- ✅ Version controlled as config
- ✅ Testable without execution
- ✅ Auditable by compliance teams
- ✅ No security vulnerabilities from code

## Integration with Existing System

The declarative engine integrates seamlessly:

```python
from policy.declarative_engine import DeclarativePolicyEngine
from policy.evaluator import PolicyEvaluator

# Use alongside existing evaluator
declarative_engine = DeclarativePolicyEngine()
traditional_evaluator = PolicyEvaluator()

# Load declarative policies
declarative_engine.load_policy(my_declarative_policy)

# Evaluate
declarative_result = declarative_engine.evaluate(context)
traditional_result = traditional_evaluator.evaluate(agent, prompt, context, user)

# Combine results (most restrictive wins)
```

## Future Enhancements

- [ ] Policy testing framework
- [ ] Visual policy builder
- [ ] Policy templates library
- [ ] Policy conflict detection
- [ ] Policy simulation mode
- [ ] Policy impact analysis

## The "Salesforce of AI" Vision

Just like Salesforce lets business users create validation rules without code, we let compliance teams create AI governance policies without code.

**This is configuration, not customization. That's how you scale.**
