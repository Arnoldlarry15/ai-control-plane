# Phase 2 & 3: Identity, Authority, and Human-Centric Observability

## Overview

This document describes the Phase 2 and Phase 3 enhancements to the AI Control Plane:

- **Phase 2**: Proper identity and authority tracking
- **Phase 3**: Human-centric observability

These features transform the control plane into a truth oracle for AI behavior where every action is traceable and every decision is explainable.

## Phase 2: Identity and Authority

### Goal

> "This model response exists because Alice approved it under policy X at time Y."

Every request carries identity metadata. Every action leaves a trace. Complete accountability.

### Identity Metadata

Every request now carries comprehensive identity information:

```python
from auth.identity import IdentityMetadata
from auth.models import User

# Create identity metadata from a user
identity = IdentityMetadata.from_user(
    user=user,
    request_id="req-12345",
    source_ip="192.168.1.100",
    user_agent="Mozilla/5.0...",
    metadata={
        "department": "Engineering",
        "location": "US-West",
    }
)

# Identity metadata includes:
# - user_id: Who initiated the action
# - user_email: User's email address
# - user_role: User's role at time of action
# - user_name: User's full name
# - timestamp: When the action was initiated
# - request_id: Request correlation ID
# - source_ip: Source IP address
# - user_agent: User agent string
# - metadata: Additional context
```

### Action Records

Complete audit records with identity and decision context:

```python
from auth.identity import ActionRecord

record = ActionRecord(
    identity=identity,
    action_type="approve",
    action_id="action-123",
    agent_id="agent-456",
    decision="allow",
    policy_id="pol-789",
    policy_name="High Risk Approval",
    reason="Request approved by approver",
    timestamp=timestamp,
    context={"cost": 50},
)

# Generate the gold standard audit sentence
sentence = record.to_audit_sentence()
# "This response was approved by Alice Developer (developer) 
#  under policy 'High Risk Approval' at 2024-01-01T12:00:00Z."
```

### Middleware Integration

Identity is automatically extracted and propagated through the request lifecycle:

```python
# In middleware
class IdentityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract identity from headers
        request.state.user_id = request.headers.get("X-User-ID")
        request.state.user_email = request.headers.get("X-User-Email")
        request.state.user_role = request.headers.get("X-User-Role")
        request.state.source_ip = request.client.host
        request.state.user_agent = request.headers.get("User-Agent")
        
        # Identity is now available throughout the request
        response = await call_next(request)
        return response
```

### Audit Trail Enhancement

Every audit entry now includes identity metadata:

```python
audit_trail.append(
    event_type="execution_started",
    action="start_execution",
    status="initiated",
    details={...},
    execution_id=execution_id,
    agent_id=agent_id,
    user=user_id,
    identity_metadata={
        "user_id": "alice",
        "user_role": "developer",
        "user_name": "Alice Developer",
        "timestamp": "2024-01-01T12:00:00Z",
        ...
    }
)
```

## Phase 3: Human-Centric Observability

### Goal

Answer human questions, not machine questions:

- **Why was this blocked?**
- **Who approved this?**
- **Which policy fired?**
- **What would have happened under a different policy?**

### Decision Records

Transform logs into decision records:

```python
from observability.events import DecisionRecord

record = DecisionRecord(
    execution_id="exec-123",
    correlation_id="corr-123",
    request_timestamp="2024-01-01T12:00:00Z",
    decision_timestamp="2024-01-01T12:00:01Z",
    completion_timestamp="2024-01-01T12:05:00Z",
    
    # WHO
    requester_id="alice",
    requester_name="Alice Developer",
    requester_role="developer",
    approver_id="bob",
    approver_name="Bob Approver",
    approver_role="approver",
    
    # WHAT and WHY
    decision="allow",
    reason="High cost operation approved",
    
    # WHICH
    policy_id="pol-approval",
    policy_name="Approval Required Policy",
    
    # Context
    agent_id="agent-456",
    status="success",
)

# The gold standard audit sentence
sentence = record.to_audit_sentence()
# "This model response exists because Bob Approver approved it 
#  under policy 'Approval Required Policy' at 2024-01-01T12:05:00Z."
```

### Human-Centric Queries

#### Why was this blocked?

```bash
curl http://localhost:8000/api/decisions/exec-123/why-blocked
```

Response:
```json
{
  "found": true,
  "blocked": true,
  "reason": "Prompt contains PII",
  "policy_id": "pol-pii",
  "policy_name": "PII Detection Policy",
  "blocked_at": "2024-01-01T12:00:01Z",
  "blocked_for": "Alice Developer",
  "summary": "Blocked by policy 'PII Detection Policy': Prompt contains PII",
  "audit_sentence": "This request was blocked for Alice Developer by policy 'PII Detection Policy' at 2024-01-01T12:00:01Z. Reason: Prompt contains PII"
}
```

#### Who approved this?

```bash
curl http://localhost:8000/api/decisions/exec-456/who-approved
```

Response:
```json
{
  "found": true,
  "approved": true,
  "approver_id": "bob",
  "approver_name": "Bob Approver",
  "approver_role": "approver",
  "approved_at": "2024-01-01T12:05:00Z",
  "policy": "Approval Required Policy",
  "summary": "Approved by Bob Approver (approver) under policy 'Approval Required Policy' at 2024-01-01T12:05:00Z",
  "audit_sentence": "This model response exists because Bob Approver approved it under policy 'Approval Required Policy' at 2024-01-01T12:05:00Z."
}
```

#### Which policy fired?

```bash
curl http://localhost:8000/api/decisions/exec-789/which-policy
```

Response:
```json
{
  "found": true,
  "policy_id": "pol-hours",
  "policy_name": "Business Hours Policy",
  "decision": "block",
  "reason": "Requests only allowed during business hours",
  "policies_evaluated": ["pol-default", "pol-hours", "pol-cost"],
  "decided_at": "2024-01-01T12:00:01Z",
  "summary": "Policy 'Business Hours Policy' decided to block: Requests only allowed during business hours"
}
```

#### Get decision timeline

```bash
curl http://localhost:8000/api/decisions/exec-101/timeline
```

Response:
```json
{
  "found": true,
  "execution_id": "exec-101",
  "timeline": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "event": "Request initiated",
      "actor": "Alice Developer",
      "role": "developer"
    },
    {
      "timestamp": "2024-01-01T12:00:01Z",
      "event": "Policy decision: allow",
      "policy": "Approval Required Policy",
      "reason": "High cost operation"
    },
    {
      "timestamp": "2024-01-01T12:05:00Z",
      "event": "Approved",
      "actor": "Bob Approver",
      "role": "approver"
    }
  ],
  "audit_sentence": "This model response exists because Bob Approver approved it under policy 'Approval Required Policy' at 2024-01-01T12:05:00Z."
}
```

### Query and Statistics

#### Query decisions

```bash
# All blocked requests
curl "http://localhost:8000/api/decisions/query?decision=block"

# All requests by Alice
curl "http://localhost:8000/api/decisions/query?requester_id=alice"

# All approvals by Bob
curl "http://localhost:8000/api/decisions/query?approver_id=bob"

# Requests in time range
curl "http://localhost:8000/api/decisions/query?start_time=2024-01-01T00:00:00Z&end_time=2024-01-02T00:00:00Z"
```

#### Get statistics

```bash
curl http://localhost:8000/api/decisions/statistics
```

Response:
```json
{
  "total_decisions": 150,
  "by_decision": {
    "allow": 120,
    "block": 25,
    "escalate": 5
  },
  "by_policy": {
    "pol-default": 100,
    "pol-pii": 20,
    "pol-approval": 30
  },
  "unique_requesters": 25,
  "unique_approvers": 5
}
```

## Integration Example

### Complete execution flow with identity and decision records

```python
from gateway.executor import Executor
from auth.identity import IdentityMetadata

# Create executor (has decision_store automatically)
executor = Executor()

# Execute with identity metadata
result = await executor.execute(
    agent_id="my-agent",
    prompt="Analyze customer data...",
    context={
        "identity_metadata": {
            "user_id": "alice",
            "user_email": "alice@company.com",
            "user_role": "developer",
            "user_name": "Alice Developer",
            "timestamp": "2024-01-01T12:00:00Z",
            "request_id": "req-123",
            "source_ip": "192.168.1.100",
        },
        "cost": 50,
    },
    user="alice"
)

# Query the decision record
execution_id = result["execution_id"]

# Why was this blocked? (if it was)
why = executor.decision_store.why_blocked(execution_id)

# Who approved this? (if it was escalated)
who = executor.decision_store.who_approved(execution_id)

# Which policy fired?
which = executor.decision_store.which_policy_fired(execution_id)

# Get timeline
timeline = executor.decision_store.get_timeline(execution_id)
```

## Benefits

### For Auditors

- **Complete accountability**: Every decision is traceable to a person and policy
- **Gold standard audit sentences**: Human-readable explanations
- **Immutable audit trail**: Cryptographically verified chain
- **Timeline replay**: Reconstruct any execution from start to finish

### For Lawyers

- **Defensible records**: "This model response exists because X approved it under policy Y at time Z"
- **Chain of custody**: Legal-grade audit trail exports
- **Compliance evidence**: SOC 2, HIPAA, GDPR compliance built-in
- **Subpoena-ready**: Export audit trails in compliance formats

### For Engineers

- **Debugging**: "Why was this blocked?" answered instantly
- **Trust**: Every decision is explainable
- **Observability**: Human-centric queries, not log diving
- **Transparency**: Complete visibility into AI behavior

## Technical Details

### Architecture

```
Request → Middleware (extract identity) → Executor
                                             ↓
                                    Check kill switch
                                             ↓
                                    Validate agent
                                             ↓
                                    Evaluate policies
                                             ↓
                                    Create decision record
                                             ↓
                                    Execute (if allowed)
                                             ↓
                                    Log to audit trail (with identity)
                                             ↓
                                    Store decision record
```

### Components

1. **auth/identity.py**: Identity metadata and action records
2. **observability/decision_records.py**: Decision record store and queries
3. **observability/events.py**: Enhanced event models with decision context
4. **observability/audit_trail.py**: Audit trail with identity metadata
5. **gateway/middleware.py**: Identity extraction middleware
6. **gateway/executor.py**: Executor with identity and decision tracking
7. **gateway/routes.py**: Human-centric API endpoints

## Next Steps

### Persistent Storage

Currently in-memory. Next:
- PostgreSQL for decision records
- Redis for fast queries
- Time-series database for analytics

### Real-Time Notifications

- WebSocket for approval notifications
- Slack/email integration
- Dashboard real-time updates

### Advanced Analytics

- Trend analysis
- Anomaly detection
- Policy effectiveness metrics
- Risk scoring improvements

### Multi-Tenancy

- Organization isolation
- Per-org decision records
- Cross-org compliance reporting

## Conclusion

Phases 2 and 3 transform the AI Control Plane from a governance tool into a **truth oracle for AI behavior**.

Every request carries identity. Every action leaves a trace. Every decision is explainable.

This is what makes the system enterprise-grade. This is what auditors love. This is what lawyers need. This is what engineers trust.

**The system can now say:**

> "This model response exists because Alice approved it under policy X at time Y."

That sentence is gold.
