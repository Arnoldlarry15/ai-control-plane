# Integration Guide - Wiring the Policy Engine into the Gateway

This guide shows how to integrate the deterministic policy engine into the existing AI Control Plane gateway.

## Overview

The new policy engine can work **alongside** the existing policy evaluator, providing a migration path without breaking existing functionality.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Gateway Request                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                      Executor                            │
│  - Check kill switch                                     │
│  - Validate agent                                        │
│  - Evaluate policies  ←─────┐                           │
│  - Execute or block          │                           │
└──────────────────────────────┼───────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ↓                     ↓
         ┌──────────────────┐  ┌──────────────────┐
         │  Old Evaluator   │  │  New Engine      │
         │  (Existing)      │  │  (Deterministic) │
         └──────────────────┘  └──────────────────┘
```

## Integration Options

### Option 1: Side-by-Side (Recommended for Migration)

Run both evaluators in parallel. Use the new engine for new policies, keep old evaluator for existing policies.

```python
# gateway/executor.py

from control_plane.policy.engine.adapter import PolicyEngineAdapter

class Executor:
    def __init__(self, ...):
        # Existing evaluator
        self.policy_evaluator = policy_evaluator
        
        # New deterministic engine
        self.policy_engine = PolicyEngineAdapter(
            policies_directory="/etc/ai-control-plane/policies"
        )
    
    async def execute(self, agent_id, prompt, context, user):
        # ... kill switch check, agent validation ...
        
        # Option 1: Try new engine first, fall back to old
        if self.policy_engine.policies:
            decision = self.policy_engine.evaluate(agent, prompt, context, user)
        else:
            decision = self.policy_evaluator.evaluate(agent, prompt, context, user)
        
        # Handle decision
        if decision["action"] == "block":
            raise PolicyViolationError(decision["reason"])
        elif decision["action"] == "escalate":
            # Queue for approval
            return await self._handle_escalation(...)
        else:  # allow
            # Execute the request
            return await self._execute_request(...)
```

### Option 2: Full Replace

Replace the old evaluator entirely with the new engine.

```python
# gateway/executor.py

from control_plane.policy.engine.adapter import PolicyEngineAdapter

class Executor:
    def __init__(self, ...):
        # Replace old evaluator with new engine
        self.policy_evaluator = PolicyEngineAdapter(
            policies_directory="/etc/ai-control-plane/policies"
        )
        
        # Alias for compatibility
        self.policy_engine = self.policy_evaluator
```

### Option 3: Feature Flag

Use a feature flag to switch between engines.

```python
# gateway/executor.py

import os
from control_plane.policy.engine.adapter import PolicyEngineAdapter

class Executor:
    def __init__(self, ...):
        # Both evaluators
        self.old_evaluator = policy_evaluator
        self.new_engine = PolicyEngineAdapter()
        
        # Feature flag
        self.use_new_engine = os.getenv("USE_NEW_POLICY_ENGINE", "false").lower() == "true"
    
    async def execute(self, agent_id, prompt, context, user):
        # ... validation ...
        
        # Choose evaluator based on flag
        if self.use_new_engine:
            decision = self.new_engine.evaluate(agent, prompt, context, user)
        else:
            decision = self.old_evaluator.evaluate(agent, prompt, context, user)
        
        # ... handle decision ...
```

## Step-by-Step Integration

### Step 1: Create Policies Directory

```bash
mkdir -p /etc/ai-control-plane/policies
```

### Step 2: Add Policy Files

Copy example policies or create custom ones:

```bash
cp control_plane/policy/policies/examples/*.yaml /etc/ai-control-plane/policies/
```

### Step 3: Update Executor

Add the adapter to your executor:

```python
# gateway/executor.py

from control_plane.policy.engine.adapter import PolicyEngineAdapter

class Executor:
    def __init__(self, ...):
        # ... existing initialization ...
        
        # Add new engine adapter
        try:
            self.policy_engine = PolicyEngineAdapter(
                policies_directory="/etc/ai-control-plane/policies"
            )
            logger.info("Deterministic policy engine initialized")
        except Exception as e:
            logger.warning(f"Could not initialize policy engine: {e}")
            self.policy_engine = None
```

### Step 4: Update Evaluation Logic

Modify the policy evaluation in the execute flow:

```python
# gateway/executor.py

async def execute(self, agent_id, prompt, context, user):
    # ... kill switch and validation ...
    
    # Policy evaluation
    if self.policy_engine and self.policy_engine.policies:
        # Use new deterministic engine
        decision = self.policy_engine.evaluate(agent, prompt, context, user)
    else:
        # Fall back to existing evaluator
        decision = self.policy_evaluator.evaluate(agent, prompt, context, user)
    
    # Log decision
    logger.info(f"Policy decision: {decision['action']}, reason: {decision['reason']}")
    
    # Branch on decision
    if decision["action"] == "block":
        raise PolicyViolationError(decision["reason"])
    
    elif decision["action"] == "escalate":
        # Create approval request
        approval_id = await self._create_approval_request(
            agent_id=agent_id,
            prompt=prompt,
            context=context,
            user=user,
            reason=decision["reason"]
        )
        return {
            "status": "pending_approval",
            "approval_id": approval_id,
            "reason": decision["reason"]
        }
    
    else:  # allow
        # Execute the request
        result = await self._execute_request(agent, prompt, context)
        return {
            "status": "success",
            "response": result,
            "execution_id": execution_id
        }
```

### Step 5: Environment Configuration

Set environment variables:

```bash
# Enable new engine
export USE_NEW_POLICY_ENGINE=true

# Set policies directory
export POLICY_ENGINE_DIR=/etc/ai-control-plane/policies

# Set environment for scope matching
export ENVIRONMENT=production
```

### Step 6: Test Integration

```python
# Test script

import asyncio
from gateway.executor import Executor

async def test_integration():
    executor = Executor()
    
    # Test case 1: Production + PII → REVIEW
    result = await executor.execute(
        agent_id="test_agent",
        prompt="Process this SSN: 123-45-6789",
        context={
            "environment": "production",
            "tags": ["pii"]
        },
        user="test_user"
    )
    
    assert result["status"] == "pending_approval"
    print("✅ Test 1 passed: prod + pii → REVIEW")
    
    # Test case 2: Development + PII → ALLOW
    result = await executor.execute(
        agent_id="test_agent",
        prompt="Process this SSN: 123-45-6789",
        context={
            "environment": "development",
            "tags": ["pii"]
        },
        user="test_user"
    )
    
    assert result["status"] == "success"
    print("✅ Test 2 passed: dev + pii → ALLOW")
    
    # Test case 3: Production + banned → DENY
    try:
        result = await executor.execute(
            agent_id="test_agent",
            prompt="Banned content",
            context={
                "environment": "production",
                "tags": ["banned"]
            },
            user="test_user"
        )
        assert False, "Should have raised PolicyViolationError"
    except PolicyViolationError:
        print("✅ Test 3 passed: prod + banned → DENY")

if __name__ == "__main__":
    asyncio.run(test_integration())
```

## Request Context Mapping

The adapter automatically maps gateway request data to `RequestContext`:

| Gateway Field | RequestContext Field | Notes |
|---------------|---------------------|-------|
| `user` | `actor_id` | User identifier |
| `context.role` | `actor_role` | User role (default: "user") |
| `agent.id` | `resource_id` | Agent being accessed |
| (fixed) | `resource_type` | Always "agent" |
| `context.environment` | `environment` | Deployment environment |
| `context.intent` | `intent` | Action being performed |
| `agent.tags` + `context.tags` | `tags` | Combined tags |
| `context.metadata` + agent data | `metadata` | Combined metadata |

## Decision Mapping

The adapter converts engine decisions to gateway format:

| Engine Decision | Gateway Action | Behavior |
|----------------|---------------|----------|
| `ALLOW` | `allow` | Execute request |
| `DENY` | `block` | Raise PolicyViolationError |
| `REVIEW` | `escalate` | Queue for approval |

## Runtime Policy Updates

Reload policies without restart:

```python
# In a management endpoint
@router.post("/admin/reload-policies")
async def reload_policies():
    """Reload policies from disk."""
    executor.policy_engine.reload_policies()
    return {
        "status": "success",
        "policies_loaded": len(executor.policy_engine.policies)
    }
```

## Monitoring and Observability

Log policy decisions for audit:

```python
# After evaluation
decision = self.policy_engine.evaluate(agent, prompt, context, user)

# Log to audit trail
self.audit_trail.append(
    event_type="policy_decision",
    action=decision["action"],
    status="completed",
    details={
        "matched_policies": decision["matched_policies"],
        "reason": decision["reason"],
        "agent_id": agent_id,
        "environment": context.get("environment"),
        "tags": context.get("tags", [])
    },
    user=user
)
```

## Migration Strategy

### Phase 1: Parallel Evaluation (Week 1-2)
- Run both engines
- Compare results
- Log differences
- Fix discrepancies

### Phase 2: Shadow Mode (Week 3-4)
- Use new engine for decisions
- Log old engine results for comparison
- Validate behavior matches expectations

### Phase 3: Full Cutover (Week 5)
- Remove old evaluator
- Use only new engine
- Monitor for issues

### Phase 4: Optimization (Week 6+)
- Add more policies
- Tune performance
- Enhance capabilities

## Troubleshooting

### Policies Not Loading

Check the policies directory exists and contains valid YAML:

```python
import os
from control_plane.policy.engine.loader import load_policies_from_directory

policies_dir = "/etc/ai-control-plane/policies"
if not os.path.exists(policies_dir):
    print(f"Directory not found: {policies_dir}")
else:
    try:
        policies = load_policies_from_directory(policies_dir)
        print(f"Loaded {len(policies)} policies")
    except Exception as e:
        print(f"Error loading policies: {e}")
```

### Wrong Environment

Ensure environment is set correctly:

```python
import os
print(f"Environment: {os.getenv('ENVIRONMENT', 'not set')}")
```

### Tags Not Matching

Check that tags are being passed correctly:

```python
# In gateway request
context = {
    "environment": "production",
    "tags": ["pii", "sensitive"],  # Make sure tags are here
    "metadata": {}
}
```

## Next Steps

1. ✅ **Test**: Run integration tests
2. ✅ **Deploy**: Roll out to staging first
3. ✅ **Monitor**: Watch audit logs and metrics
4. ✅ **Iterate**: Add more policies as needed
5. ✅ **Document**: Update runbooks and SOPs

## Benefits of Integration

Once integrated, you get:

- ✅ **Deterministic decisions** - Same input always produces same output
- ✅ **Auditable policies** - Every decision logged with reasoning
- ✅ **Easy policy updates** - Change YAML files without code changes
- ✅ **Compliance-ready** - Human-readable policies for auditors
- ✅ **Test coverage** - Comprehensive tests prove enforcement works

This is governance that's **real, not aspirational**.
