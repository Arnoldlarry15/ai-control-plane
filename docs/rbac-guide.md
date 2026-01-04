# Role-Based Access Control (RBAC) Guide

## Overview

AI Control Plane implements fine-grained role-based access control to ensure proper authorization and auditability of all actions.

---

## Role Hierarchy

### Admin
**Full system access**

Permissions:
- All agent operations (read, write, delete)
- All policy operations (read, write, delete)
- Execute AI operations
- Activate/deactivate kill switch
- Approve requests
- Read and export audit logs
- System administration

Use cases:
- Platform administrators
- Security team leads
- System operators

### Operator
**Operational control**

Permissions:
- Read agents
- Read policies
- Execute AI operations
- Activate/deactivate kill switch
- Read audit logs

Use cases:
- On-call engineers
- DevOps team
- Production support

### Developer
**Development access**

Permissions:
- Read agents
- Create/update agents
- Read policies
- Execute AI operations
- Read audit logs

Use cases:
- Application developers
- AI engineers
- Integration developers

### Auditor
**Read-only compliance access**

Permissions:
- Read agents
- Read policies
- Read audit logs
- Export audit logs
- Read approval requests

Use cases:
- Compliance officers
- Security auditors
- Legal team

### User
**Basic execution**

Permissions:
- Execute AI operations (with agent assigned)

Use cases:
- End users
- Service accounts
- Basic integrations

---

## User Management

### Creating Users

Using Python SDK:

```python
from auth.service import AuthService
from auth.models import Role

auth = AuthService()

# Create a developer user
user = auth.create_user(
    user_id="alice",
    email="alice@example.com",
    full_name="Alice Developer",
    role=Role.DEVELOPER,
)

# Generate API key
api_key = auth.create_api_key(
    user_id="alice",
    name="Alice's Development Key",
)

print(f"API Key: {api_key}")
```

### API Key Management

```python
# List user's API keys
keys = auth.list_api_keys("alice")

# Revoke an API key
auth.revoke_api_key("old-api-key")
```

---

## Authentication

### API Key Authentication

Include API key in request headers:

```bash
curl -H "X-API-Key: your-api-key-here" \
  http://localhost:8000/api/agents
```

Using Python SDK:

```python
from sdk.python.client import ControlPlaneClient

client = ControlPlaneClient(
    base_url="http://localhost:8000",
    api_key="your-api-key-here"
)
```

---

## Authorization

### Permission Checking

The system automatically checks permissions for all operations:

```python
# In gateway routes
@router.post("/agents")
async def create_agent(request: Request):
    # Get authenticated user
    user = request.state.user
    
    # Check permission
    if not auth.authorize(user, Permission.AGENT_WRITE):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Proceed with operation
    ...
```

### Custom Permission Rules

Define custom authorization logic:

```python
from auth.models import Permission

def can_access_agent(user, agent_id):
    """Check if user can access specific agent"""
    # Admin can access all
    if user.has_permission(Permission.ADMIN):
        return True
    
    # Check agent ownership
    agent = registry.get_agent(agent_id)
    if agent.owner == user.id:
        return True
    
    return False
```

---

## Audit Trails

All operations are logged with user identity:

```python
{
    "timestamp": "2026-01-04T19:00:00Z",
    "event_type": "agent_created",
    "user_id": "alice",
    "user_email": "alice@example.com",
    "user_role": "developer",
    "agent_id": "agent-123",
    "result": "success"
}
```

### Querying Audit Logs

```python
from observability.logger import AuditLogger

logger = AuditLogger()

# Get all actions by a user
events = logger.query_events(user_id="alice")

# Get all policy violations
violations = logger.query_events(event_type="policy_violation")

# Get all kill switch activations
activations = logger.query_events(event_type="kill_switch_activated")
```

---

## Best Practices

### 1. Principle of Least Privilege

Assign the minimum role required:

```python
# ✅ Good: Assign specific role
user = auth.create_user(
    user_id="service-account",
    role=Role.USER,  # Only execution
)

# ❌ Bad: Over-privileged
user = auth.create_user(
    user_id="service-account",
    role=Role.ADMIN,  # Too much access
)
```

### 2. API Key Rotation

Rotate keys regularly:

```python
# Revoke old key
auth.revoke_api_key(old_key)

# Generate new key
new_key = auth.create_api_key(
    user_id="alice",
    name="Rotated Key - 2026-01",
)
```

### 3. Key Expiration

Set expiration for temporary access:

```python
from datetime import datetime, timedelta

# Key expires in 30 days
expiry = datetime.utcnow() + timedelta(days=30)

api_key = auth.create_api_key(
    user_id="contractor",
    name="Temporary Access",
    expires_at=expiry,
)
```

### 4. Service Accounts

Create dedicated service accounts:

```python
# Create service account
service = auth.create_user(
    user_id="production-app",
    email="no-reply@example.com",
    full_name="Production Application",
    role=Role.USER,
)

# Generate non-expiring key (for services)
key = auth.create_api_key(
    user_id="production-app",
    name="Production Service Key",
    expires_at=None,
)
```

---

## Integration with Identity Providers

### LDAP/Active Directory

```python
def authenticate_ldap(username, password):
    """Authenticate against LDAP"""
    # Connect to LDAP
    ldap_conn = ldap.initialize("ldap://ldap.example.com")
    
    try:
        # Bind with credentials
        ldap_conn.simple_bind_s(
            f"uid={username},ou=users,dc=example,dc=com",
            password
        )
        
        # Get or create user
        user = auth.get_user(username)
        if not user:
            user = auth.create_user(
                user_id=username,
                email=f"{username}@example.com",
                full_name=get_ldap_name(username),
                role=get_ldap_role(username),
            )
        
        # Generate session key
        return auth.create_api_key(user.id, "Session Key")
        
    except ldap.INVALID_CREDENTIALS:
        return None
```

### OAuth2/OIDC

```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='google',
    client_id='...',
    client_secret='...',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/auth/callback')
async def auth_callback(request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)
    
    # Get or create user
    user = auth.get_user(user_info['email'])
    if not user:
        user = auth.create_user(
            user_id=user_info['email'],
            email=user_info['email'],
            full_name=user_info['name'],
            role=Role.USER,
        )
    
    # Create session
    api_key = auth.create_api_key(user.id, "OAuth Session")
    return {"api_key": api_key}
```

---

## Security Considerations

### 1. API Key Storage

- Never commit API keys to version control
- Store in environment variables or secret management systems
- Use different keys for different environments

### 2. Key Security

```python
# ✅ Good: Secure key handling
import os
api_key = os.environ.get("AI_CONTROL_PLANE_API_KEY")

# ❌ Bad: Hardcoded keys
api_key = "abc123-hardcoded-key"
```

### 3. Rate Limiting

Implement per-user rate limits:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/agents")
@limiter.limit("100/minute")
async def list_agents(request: Request):
    ...
```

### 4. Audit Everything

Log all authentication attempts:

```python
# Successful authentication
logger.audit_event(
    event_type="auth_success",
    user_id=user.id,
    ip_address=request.client.host,
)

# Failed authentication
logger.audit_event(
    event_type="auth_failed",
    user_id=attempted_user_id,
    ip_address=request.client.host,
    reason="invalid_api_key",
)
```

---

## Troubleshooting

### Permission Denied Errors

```bash
# Check user role
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/users/me

# Check required permission
# Admin can view all permissions
curl -H "X-API-Key: $ADMIN_KEY" \
  http://localhost:8000/api/permissions
```

### API Key Not Working

```python
# Verify key is active
key = auth._api_keys.get("your-key")
if not key:
    print("Key not found")
elif not key.active:
    print("Key has been revoked")
elif key.expires_at and key.expires_at < datetime.utcnow():
    print("Key has expired")
```

---

## Migration Guide

### Upgrading from No-Auth to RBAC

1. **Create admin user**:
```python
admin = auth.create_user(
    user_id="admin",
    email="admin@example.com",
    full_name="System Administrator",
    role=Role.ADMIN,
)
admin_key = auth.create_api_key(admin.id, "Admin Key")
```

2. **Create users for existing clients**:
```python
for client in existing_clients:
    user = auth.create_user(
        user_id=client.id,
        email=client.email,
        full_name=client.name,
        role=determine_role(client),
    )
    key = auth.create_api_key(user.id, f"{client.name} Key")
    # Distribute key to client
```

3. **Enable authentication middleware**:
```python
app.add_middleware(AuthenticationMiddleware)
```

---

## Reference

### Complete Permission List

```python
class Permission(str, Enum):
    # Agent management
    AGENT_READ = "agent:read"
    AGENT_WRITE = "agent:write"
    AGENT_DELETE = "agent:delete"
    
    # Policy management
    POLICY_READ = "policy:read"
    POLICY_WRITE = "policy:write"
    POLICY_DELETE = "policy:delete"
    
    # Execution
    EXECUTE = "execute"
    
    # Kill switch
    KILL_SWITCH_ACTIVATE = "killswitch:activate"
    KILL_SWITCH_DEACTIVATE = "killswitch:deactivate"
    
    # Approval
    APPROVE = "approval:approve"
    APPROVE_READ = "approval:read"
    
    # Audit
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    
    # System admin
    ADMIN = "admin"
```
