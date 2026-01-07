# Policy Engine - Making Governance Real

## Overview

The Policy Engine is the beating heart of AI Control Plane governance. It transforms governance from aspirational declarations into **enforceable, testable, and undeniable reality**.

This is not a compliance checklist. This is **authoritative control**.

## The Mental Model

A real policy engine answers exactly one question:

> **"Given this request, under these policies, what must happen?"**

And it must answer it **deterministically**.

- Not vibes
- Not best effort  
- Not "probably allowed"

The engine outputs one of **three canonical outcomes**:

- **ALLOW** – proceed automatically
- **DENY** – block immediately
- **REVIEW** – pause and require human approval

Everything else is metadata.

## Why This Matters

**Before**: "We enforce policies."  
**Now**: "Here is the exact function where enforcement happens, and here are the test cases that prove it."

This is your **"no means no"** moment.

## Architecture

The policy engine consists of four core primitives:

### 1. Policy

A policy is a rule with intent.

```yaml
id: "prod_pii_requires_review"
version: "1.0.0"
description: "Access to PII in production requires human approval"

scope:
  environment: ["production"]
  resource_type: ["model", "agent"]

conditions:
  tags: ["pii"]

effect: "REVIEW"
priority: 100
```

**Structure:**
- `scope`: What it applies to (environment, resource type, actor role)
- `conditions`: When it triggers (tags, metadata, intent)
- `effect`: What happens (ALLOW, DENY, REVIEW)
- `priority`: Conflict resolution order (higher = evaluated first)

### 2. Request Context

The truth payload being judged. **Immutable** once created.

```python
from control_plane.policy.schemas.context import RequestContext

context = RequestContext(
    actor_id="user_123",
    actor_role="developer",
    resource_id="model_gpt4",
    resource_type="model",
    environment="production",
    intent="data_access",
    tags=["pii"],
    metadata={"department": "finance"}
)
```

**Immutability prevents shenanigans.** Context is frozen and cannot be modified during evaluation.

### 3. Decision

The output. Always structured. Always logged. Never ambiguous.

```python
from control_plane.policy.schemas.decision import PolicyDecision, DecisionType

decision = PolicyDecision(
    decision=DecisionType.REVIEW,
    matched_policies=["prod_pii_requires_review"],
    reason="Review required by policy prod_pii_requires_review: Access to PII in production requires human approval"
)
```

This is what gets logged, audited, replayed, and simulated.

### 4. Engine

A **pure evaluator**. No side effects. No database writes. No API calls.

```python
from control_plane.policy.engine.evaluator import evaluate_policies
from control_plane.policy.engine.loader import load_policies_from_directory

# Load policies
policies = load_policies_from_directory("/path/to/policies")

# Evaluate
decision = evaluate_policies(policies, context)

# Branch on decision
if decision.decision == DecisionType.DENY:
    # Block request
    return {"error": "Request denied", "reason": decision.reason}
elif decision.decision == DecisionType.REVIEW:
    # Enqueue for approval
    approval_id = enqueue_approval_workflow(context, decision)
    return {"status": "pending_review", "approval_id": approval_id}
else:  # ALLOW
    # Proceed with request
    return execute_request(context)
```

**This purity is what makes it trustworthy.**

## Usage

### Basic Evaluation

```python
from control_plane.policy.schemas.context import RequestContext
from control_plane.policy.schemas.policy_schema import PolicySchema
from control_plane.policy.engine.evaluator import evaluate_policies

# Define policy
policy = PolicySchema({
    "id": "prod_pii_requires_review",
    "version": "1.0.0",
    "description": "PII in production requires review",
    "scope": {"environment": ["production"]},
    "conditions": {"tags": ["pii"]},
    "effect": "REVIEW",
    "priority": 100
})

# Create context
context = RequestContext(
    actor_id="user_123",
    actor_role="developer",
    resource_id="model_gpt4",
    resource_type="model",
    environment="production",
    intent="data_access",
    tags=["pii"],
    metadata={}
)

# Evaluate
decision = evaluate_policies([policy], context)

print(f"Decision: {decision.decision}")
print(f"Reason: {decision.reason}")
```

### Loading Policies from Files

```python
from control_plane.policy.engine.loader import load_policies_from_directory

# Load all policies from directory
policies = load_policies_from_directory("/etc/ai-control-plane/policies")

# Evaluate
decision = evaluate_policies(policies, context)
```

### Loading Example Policies

```python
from control_plane.policy.engine.loader import load_example_policies

# Load built-in example policies
policies = load_example_policies()

# These include:
# - prod_pii_requires_review: PII in production requires approval
# - dev_pii_allow: PII allowed in development
# - prod_banned_deny: Banned content blocked in production
# - high_risk_review: High-risk operations require review
# - financial_prod_review: Financial data requires approval
```

## Policy Evaluation Rules

1. **Policies are sorted by priority** (highest first)
2. **For each policy:**
   - Check if scope matches
   - Check if conditions match
   - If both match, record the match
   - **If effect is DENY, return immediately**
   - **If effect is REVIEW, return immediately**
3. **If no DENY or REVIEW matched, return ALLOW**

### Priority Precedence

- **DENY** > **REVIEW** > **ALLOW**
- Higher priority policies are evaluated first
- First matching DENY or REVIEW wins

## Example Policies

### Production PII Requires Review

```yaml
id: "prod_pii_requires_review"
version: "1.0.0"
description: "Access to PII in production requires human approval"

scope:
  environment: ["production"]
  resource_type: ["model", "agent"]

conditions:
  tags: ["pii"]

effect: "REVIEW"
priority: 100
```

**Result**: `prod + pii → REVIEW`

### Development PII Allowed

```yaml
id: "dev_pii_allow"
version: "1.0.0"
description: "PII access allowed in development environment"

scope:
  environment: ["development", "dev"]

conditions:
  tags: ["pii"]

effect: "ALLOW"
priority: 50
```

**Result**: `dev + pii → ALLOW`

### Production Banned Content Denied

```yaml
id: "prod_banned_deny"
version: "1.0.0"
description: "Block banned content in production immediately"

scope:
  environment: ["production"]

conditions:
  tags: ["banned"]

effect: "DENY"
priority: 200
```

**Result**: `prod + banned → DENY`

## Testing

The policy engine includes comprehensive tests that prove:

✅ `prod + pii → REVIEW`  
✅ `dev + pii → ALLOW`  
✅ `prod + banned → DENY`  
✅ Priority-based conflict resolution  
✅ Deterministic evaluation  
✅ Immutability guarantees  

Run tests:

```bash
pytest tests/test_policy_engine.py -v
```

## Integration

### Gateway Integration

```python
from gateway.routes import router
from control_plane.policy.engine.evaluator import evaluate_policies
from control_plane.policy.engine.loader import load_policies_from_directory
from control_plane.policy.schemas.context import RequestContext
from control_plane.policy.schemas.decision import DecisionType

# Load policies once at startup
policies = load_policies_from_directory("/etc/policies")

@router.post("/execute")
async def execute_request(request: ExecutionRequest):
    # Build context from request
    context = RequestContext(
        actor_id=request.user_id,
        actor_role=request.user_role,
        resource_id=request.agent_id,
        resource_type="agent",
        environment=os.getenv("ENVIRONMENT", "production"),
        intent=request.intent,
        tags=request.tags,
        metadata=request.metadata
    )
    
    # Evaluate policies
    decision = evaluate_policies(policies, context)
    
    # Branch on decision
    if decision.decision == DecisionType.DENY:
        return {
            "status": "denied",
            "reason": decision.reason,
            "matched_policies": decision.matched_policies
        }
    
    elif decision.decision == DecisionType.REVIEW:
        approval_id = await create_approval_request(context, decision)
        return {
            "status": "pending_review",
            "approval_id": approval_id,
            "reason": decision.reason
        }
    
    else:  # ALLOW
        result = await execute_ai_request(request)
        return {
            "status": "completed",
            "result": result
        }
```

## Key Principles

### 1. Deterministic

Same input **always** produces same output. No randomness, no ML, no guessing.

### 2. Auditable

Every decision is logged with:
- Which policies matched
- Why they matched
- What the decision was
- When it happened

### 3. Extensible

Add new policies without changing code. Just add YAML files.

### 4. Human-Legible

Policies are readable by auditors, compliance teams, and business stakeholders.

### 5. Enterprise-Credible

Production-ready with proper testing, documentation, and error handling.

## Benefits

### Before This Engine

- Governance was theoretical
- Policies were documented, not enforced
- No way to prove compliance
- Manual approval processes
- Inconsistent decisions

### With This Engine

- ✅ **Governance is code** - Policies are executed, not just described
- ✅ **Provable enforcement** - Tests prove policies work
- ✅ **Automatic compliance** - Policies enforce regulations
- ✅ **Auditable decisions** - Every decision is logged
- ✅ **Consistent behavior** - Deterministic evaluation

## Next Steps

Once this exists, the Control Plane stops being theoretical. It becomes authoritative.

This is your **"no means no"** moment.

Future enhancements:
- Policy simulation (what-if analysis)
- Policy versioning and rollback
- Real-time policy updates
- Policy conflict detection
- Advanced condition matching (regex, ranges, etc.)
- Integration with compliance frameworks
