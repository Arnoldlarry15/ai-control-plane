# Architecture Overview

## Design Philosophy

**ai-control-plane** is built on six non-negotiable principles:

1. **Fail Closed** - If the control plane fails, AI execution stops. No bypass.
2. **Everything Logged** - Every request, decision, and action is recorded immutably.
3. **Policies are Code** - Policy definitions are version-controlled, reviewable, auditable.
4. **Gateway is Mandatory** - All AI executions flow through the gateway. No exceptions.
5. **Kill Switch is Instant** - Emergency shutdown must be immediate and reliable.
6. **No Hidden Magic** - Transparent, deterministic behavior. No ML in the control plane itself.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                               │
│                    (SDK / REST API)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                        GATEWAY                               │
│                    (The Choke Point)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Check Registry (is agent registered?)             │ │
│  │  2. Check Kill Switch (is execution allowed?)         │ │
│  │  3. Evaluate Policy (allow / block / escalate?)       │ │
│  │  4. Check Approval (if needed)                        │ │
│  │  5. Execute (if approved)                             │ │
│  │  6. Log Everything (observability)                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┬──────────┐
        ▼             ▼             ▼             ▼          ▼
   ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌──────┐
   │ REGISTRY│  │  POLICY  │  │  AUDIT  │  │ APPROVAL │  │ KILL │
   │         │  │  ENGINE  │  │   LOG   │  │  QUEUE   │  │SWITCH│
   └─────────┘  └──────────┘  └─────────┘  └──────────┘  └──────┘
                      │
                      ▼
              ┌────────────────┐
              │  AI MODEL API  │
              │ (OpenAI, etc.) │
              └────────────────┘
```

---

## Core Services

### Gateway (`gateway/`)

**Purpose**: The throne. The single control point for all AI execution.

**The gateway is THE platform**. If this breaks, the system fails closed by design.

**Key file**: `executor.py` - Where AI calls live, wrapped, controlled, logged.

**Flow**:
1. Receive request
2. Validate authentication
3. Check kill switch status
4. Verify agent is registered
5. Evaluate policies
6. Queue for approval if needed
7. Execute if allowed
8. Log everything
9. Return response

**Critical**: Must be fast, reliable, and fail closed.

---

### Registry (`registry/`)

**Purpose**: System of record for AI entities.

**Core rule**: If it's not in the registry, it cannot execute. This is how you prevent shadow AI.

**Tracks**:
- Agent/model definitions
- Version history
- Risk classifications (low/medium/high/critical)
- Environment separation (dev/staging/prod)
- Ownership and metadata

**Why it matters**: Visibility into what AI systems exist and are being used.

---

### Policy Engine (`policy/`)

**Purpose**: Executable authority. No opinions allowed.

**Key file**: `evaluator.py` - Returns `allow`, `block`, or `escalate`.

**This must stay dumb and deterministic**. No ML. No guessing. Pure rule evaluation.

**Policy types**:
- Input validation (PII detection, content filtering)
- Rate limiting
- Time-based restrictions
- Approval requirements
- Output filtering

**Design**: Policies are YAML or JSON, version-controlled, and loaded at runtime.

---

### Observability (`observability/`)

**Purpose**: The black box recorder.

**If you build nothing else well, build this well.**

This is what lawyers, auditors, and postmortems live on.

**Logs**:
- Every execution request and response
- Policy decisions (allow/block/escalate)
- Approval decisions
- Kill switch activations
- Performance metrics

**Requirements**:
- Immutable storage
- Structured events
- Replay capability
- Fast queries

---

### Approval Service (`approval/`)

**Purpose**: Human-in-the-loop without chaos.

**Structure**:
- Approval queues by priority
- Decision logging
- Timeout handling
- Notification hooks

Even if V1 approvals are manual or mocked, the structure must exist. This is future leverage.

---

### Kill Switch (`kill_switch/`)

**Purpose**: The "oh shit" button.

**This alone justifies the platform to risk teams.**

**Capabilities**:
- Global disable (shut down ALL AI execution)
- Per-agent disable (kill specific agents)
- Fast state lookup (sub-millisecond)

**Requirements**:
- Instant activation
- Centralized state
- Fully logged
- Cannot be overridden

**Implementation**: In-memory state with persistent backing. No database round trips.

---

## Data Flow Example

```
User Request
    ↓
[Gateway receives: agent_id, prompt, context]
    ↓
[Check Kill Switch] → BLOCKED? → Return 403
    ↓
[Check Registry] → NOT FOUND? → Return 404
    ↓
[Evaluate Policies]
    ↓
    ├─→ ALLOW → [Execute] → [Log] → Return 200
    ├─→ BLOCK → [Log] → Return 403
    └─→ ESCALATE → [Queue for Approval] → [Wait] → [Execute or Block] → [Log]
```

---

## Failure Modes

**The system fails closed**. This is a feature, not a bug.

| Component Failure | Behavior |
|------------------|----------|
| Gateway down | All requests fail (503) |
| Policy engine error | Block execution (fail closed) |
| Kill switch unreachable | Block execution (fail closed) |
| Registry unavailable | Block execution (fail closed) |
| Observability down | Block execution (everything must be logged) |
| Approval service timeout | Block execution or use default policy |

---

## Security Model

1. **Authentication**: All API requests require valid credentials
2. **Authorization**: Role-based access control (RBAC)
3. **Isolation**: Registry enforces environment separation
4. **Audit**: Complete chain of custody for all decisions
5. **Emergency Control**: Kill switch requires elevated privileges

---

## Scalability Considerations

**V1 constraints**:
- Single-node deployment
- In-memory kill switch state
- Simple SQLite or PostgreSQL for registry/logs

**Future scaling**:
- Horizontal gateway scaling
- Distributed kill switch (Redis/etcd)
- Time-series database for observability
- Separate approval service instances

---

## Integration Points

### Inbound
- REST API (FastAPI)
- Python SDK (drop-in replacement for OpenAI client)
- (Future) Language-specific SDKs

### Outbound
- OpenAI API
- Anthropic API
- Azure OpenAI
- Custom model endpoints
- (Future) Other LLM providers

---

## What This Is NOT

- **Not an AI model**: We don't train or host models
- **Not a vector database**: Use external tools for that
- **Not a prompt management system**: Focus is governance, not prompt engineering
- **Not an observability platform**: We log for compliance, not APM

---

## Success Metrics

1. **Governance**: % of AI calls going through control plane
2. **Safety**: Policy violations detected and blocked
3. **Visibility**: Complete audit trail coverage
4. **Response Time**: Kill switch activation time
5. **Adoption**: SDK integration rate
