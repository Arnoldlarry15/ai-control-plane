# Phase 2 Trust & Compliance Implementation Guide

## Overview

Phase 2 transforms the AI Control Plane into an enterprise-grade governance platform that compliance officers can sign off on without reading source code. All governance is configuration-driven, auditable, and explainable.

---

## 1. Enhanced RBAC with Approver Role

### New Role: Approver

The **Approver** role is specifically designed for personnel responsible for reviewing and approving AI operations that require human oversight.

**Permissions:**
- `agent:read` - View agent configurations
- `policy:read` - View policies
- `approval:approve` - Approve or reject requests
- `approval:read` - View approval requests and history
- `audit:read` - View audit logs

**Use Cases:**
- Risk managers reviewing high-risk AI operations
- Legal counsel approving sensitive AI use cases
- Compliance officers ensuring regulatory adherence
- Domain experts approving specialized AI applications

### Role Comparison

| Role | Purpose | Key Permissions |
|------|---------|----------------|
| **Admin** | Full system control | All permissions |
| **Operator** | Day-to-day operations | Execute, view, kill switch |
| **Developer** | Build & deploy agents | Agent management, execute |
| **Auditor** | Compliance & review | Read-only access, audit export |
| **Approver** | Human-in-the-loop decisions | Approve/reject, audit read |
| **User** | End users | Execute only |

### Creating an Approver User

```python
from auth.service import AuthService
from auth.models import Role

auth_service = AuthService()

# Create approver user
approver = auth_service.create_user(
    user_id="risk-manager-001",
    email="risk.manager@company.com",
    full_name="Risk Manager",
    role=Role.APPROVER,
)

# Create API key for approver
api_key = auth_service.create_api_key(
    user_id=approver.id,
    name="Risk Manager API Key",
)

print(f"Approver created: {approver.id}")
print(f"API Key: {api_key}")
```

---

## 2. OIDC/Auth0 Integration

### Enterprise SSO Support

The platform now supports OpenID Connect (OIDC) for enterprise single sign-on (SSO) integration with:

- **Auth0**
- **Okta**
- **Azure Active Directory**
- **Google Workspace**
- **Any OIDC-compliant provider**

### Configuration

#### Configure an OIDC Provider

```python
from auth.oidc import OIDCConfig, OIDCService

# Initialize OIDC service
oidc_service = OIDCService()

# Configure Auth0
auth0_config = OIDCConfig(
    issuer="https://your-tenant.auth0.com/",
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="https://your-app.com/callback",
    audience="https://api.your-app.com",  # Auth0 specific
    scopes=["openid", "profile", "email"],
)

provider = oidc_service.add_provider("auth0", auth0_config)
```

#### Via API

```bash
# Configure OIDC provider
curl -X POST http://localhost:8000/api/auth/oidc/configure \
  -H "Content-Type: application/json" \
  -d '{
    "provider_name": "auth0",
    "issuer": "https://your-tenant.auth0.com/",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "redirect_uri": "https://your-app.com/callback",
    "audience": "https://api.your-app.com"
  }'
```

### Authentication Flow

#### 1. Get Authorization URL

```bash
curl http://localhost:8000/api/auth/oidc/auth0/authorize-url?state=random-state
```

Returns:
```json
{
  "authorization_url": "https://your-tenant.auth0.com/authorize?client_id=...",
  "provider_name": "auth0"
}
```

#### 2. User Authenticates

Redirect user to the authorization URL. After authentication, they're redirected back with an authorization code.

#### 3. Validate Token

```bash
curl -X POST http://localhost:8000/api/auth/oidc/validate \
  -H "Content-Type: application/json" \
  -d '{
    "provider_name": "auth0",
    "token": "eyJhbGciOiJSUzI1NiIs..."
  }'
```

Returns:
```json
{
  "authenticated": true,
  "user_info": {
    "sub": "auth0|123456",
    "email": "user@company.com",
    "email_verified": true,
    "name": "John Doe",
    "roles": ["approver"],
    "permissions": ["approval:approve"]
  }
}
```

### Role Mapping

Map OIDC claims to AI Control Plane roles:

```python
# In Auth0, configure custom claims
# Rules or Actions can add roles to the ID token
{
  "https://ai-control-plane.com/roles": ["approver"],
  "https://ai-control-plane.com/permissions": ["approval:approve"]
}
```

The OIDC integration automatically extracts roles from:
- Standard claims: `roles`, `groups`, `permissions`
- Custom namespace claims: `https://*` or `http://*`

---

## 3. Compliance Packs

### Available Standards

The platform includes 6 compliance packs (all configuration-based, no code):

1. **GDPR** - EU General Data Protection Regulation
2. **HIPAA** - US Health Insurance Portability and Accountability Act
3. **SOC 2** - Trust Services Criteria
4. **PCI-DSS** - Payment Card Industry Data Security Standard
5. **NIST AI RMF** - NIST AI Risk Management Framework ✨ NEW
6. **EU AI Act** - European Union Artificial Intelligence Act ✨ NEW

### NIST AI RMF Compliance Pack

**Coverage:**
- **GOVERN**: Accountability, transparency, risk-based governance
- **MAP**: Context documentation, risk categorization
- **MEASURE**: Bias testing, performance metrics, data quality
- **MANAGE**: Incident response, continuous monitoring, third-party evaluation

**Example Rules:**

```yaml
# Human oversight for high-risk AI
- id: "nist-ai-rmf-govern-1"
  when:
    and:
      - field: "risk_level"
        in: ["high", "critical"]
      - field: "context.impact_level"
        in: ["high", "critical"]
  then: "escalate"
  reason: "High-risk AI decision requires human review per NIST AI RMF GOVERN-1.1"

# Bias testing requirement
- id: "nist-ai-rmf-measure-1"
  when:
    and:
      - field: "context.affects_protected_groups"
        equals: true
      - field: "context.bias_tested"
        equals: false
  then: "block"
  reason: "Bias testing required for AI affecting protected groups per NIST AI RMF MEASURE-2.3"
```

### EU AI Act Compliance Pack

**Risk Tiers:**
- **Unacceptable Risk**: Prohibited practices (social scoring, subliminal manipulation)
- **High Risk**: Stringent requirements (biometrics, employment, education, credit scoring)
- **Limited Risk**: Transparency obligations (chatbots, emotion recognition)
- **Minimal Risk**: No specific requirements

**Example Rules:**

```yaml
# Prohibited: Social scoring
- id: "eu-ai-act-prohibited-1"
  when:
    field: "context.use_case"
    contains: "social scoring"
  then: "block"
  reason: "Social scoring is prohibited under EU AI Act Article 5(1)(c)"

# High-risk: Human oversight required
- id: "eu-ai-act-high-risk-5"
  when:
    and:
      - field: "context.risk_tier"
        equals: "high"
      - field: "context.human_oversight_enabled"
        equals: false
  then: "block"
  reason: "High-risk AI requires human oversight per Article 14"

# Limited risk: Chatbot disclosure
- id: "eu-ai-act-limited-risk-1"
  when:
    and:
      - field: "context.ai_type"
        in: ["chatbot", "conversational_ai"]
      - field: "context.user_informed_of_ai"
        equals: false
  then: "escalate"
  reason: "Users must be informed of AI interaction per Article 52(1)"
```

### Loading Compliance Policies

```python
from policy.compliance import ComplianceLoader

loader = ComplianceLoader()

# List all standards
standards = loader.list_standards()
print(standards)
# {
#   'gdpr': 'GDPR (EU General Data Protection Regulation)',
#   'hipaa': 'HIPAA (US Health Insurance...)',
#   'soc2': 'SOC 2 (Trust Services Criteria)',
#   'pci-dss': 'PCI-DSS (Payment Card Industry...)',
#   'nist-ai-rmf': 'NIST AI RMF (AI Risk Management Framework)',
#   'eu-ai-act': 'EU AI Act (European Union...)'
# }

# Load specific standard
nist_policy = loader.load_policy('nist-ai-rmf')
eu_policy = loader.load_policy('eu-ai-act')

# Load all compliance policies
all_policies = loader.load_all()
```

### API Endpoints

```bash
# List all standards
curl http://localhost:8000/api/compliance/standards

# Get standard details
curl http://localhost:8000/api/compliance/standards/nist-ai-rmf
curl http://localhost:8000/api/compliance/standards/eu-ai-act

# Validate input against standards
curl -X POST http://localhost:8000/api/compliance/validate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Deploy AI for employee performance monitoring",
    "standards": ["nist-ai-rmf", "eu-ai-act"]
  }'
```

---

## 4. Human-in-the-Loop Workflows

### Approval Workflows

Three pre-configured workflows with timeout handling and escalation:

#### Standard Workflow
- **Use case**: Normal AI operations
- **Approvers**: approver, admin roles
- **Required approvals**: 1
- **Timeout**: 1 hour
- **On timeout**: Escalate to L2

#### High-Risk Workflow
- **Use case**: High-risk AI operations
- **Approvers**: approver, admin roles
- **Required approvals**: 2
- **Timeout**: 30 minutes
- **On timeout**: Escalate to L3
- **Escalation**: Immediate for high-risk level

#### Critical Workflow
- **Use case**: Critical system changes
- **Approvers**: admin only
- **Required approvals**: 2
- **Timeout**: 15 minutes
- **Escalation**: Immediate to L4 for critical risk

### Escalation Levels

- **L1**: First-level approver (standard approver role)
- **L2**: Manager/supervisor level
- **L3**: Director/executive level
- **L4**: C-level/board level

### Decision Rationale Preservation

Every approval/rejection requires a rationale, which is:
- Preserved in the approval record
- Included in audit logs
- Available for compliance reporting
- Cryptographically signed

### Using Approval Workflows

#### Request Approval

```python
from approval.service import ApprovalService

approval_service = ApprovalService()

# Request approval with specific workflow
result = approval_service.request_approval(
    execution_id="exec-123",
    agent_id="high-risk-agent",
    prompt="Analyze sensitive customer data",
    reason="High-risk AI requires approval per NIST AI RMF",
    user="analyst@company.com",
    policy_id="nist-ai-rmf-govern-1",
    context={
        "risk_level": "high",
        "impact_level": "high",
    },
    workflow_id="high-risk",  # Use high-risk workflow
)

print(f"Approval ID: {result['approval_id']}")
print(f"Timeout: {result['timeout_seconds']} seconds")
```

#### Approve with Rationale

```python
# Approver reviews and approves
approval_service.approve(
    approval_id="approval-abc123",
    reviewer="risk-manager-001",
    reviewer_role="approver",
    rationale=(
        "Reviewed the request context. The AI model has been "
        "validated for bias, performance metrics are documented, "
        "and continuous monitoring is enabled. Risk is acceptable "
        "with current controls in place."
    ),
    comment="Approved for 30-day period. Re-review required after."
)
```

#### Reject with Rationale

```python
# Approver rejects
approval_service.reject(
    approval_id="approval-abc123",
    reviewer="risk-manager-001",
    reviewer_role="approver",
    rationale=(
        "Request does not meet NIST AI RMF requirements. "
        "Bias testing results are incomplete, and data quality "
        "assessment has not been performed. Request additional "
        "documentation before re-submission."
    ),
    comment="See attached checklist for missing requirements."
)
```

### API Endpoints

```bash
# Get pending approvals
curl http://localhost:8000/api/approvals/pending

# Get approval status with history
curl http://localhost:8000/api/approvals/{approval_id}

# Approve with rationale
curl -X POST http://localhost:8000/api/approvals/{approval_id}/approve \
  -H "Content-Type: application/json" \
  -d '{
    "reviewer": "risk-manager-001",
    "reviewer_role": "approver",
    "rationale": "Risk assessment complete. Approved per NIST AI RMF.",
    "comment": "Valid for 30 days."
  }'

# Reject with rationale
curl -X POST http://localhost:8000/api/approvals/{approval_id}/reject \
  -H "Content-Type: application/json" \
  -d '{
    "reviewer": "risk-manager-001",
    "reviewer_role": "approver",
    "rationale": "Incomplete bias testing. Re-submit after testing.",
    "comment": "See compliance checklist."
  }'

# Get decision history
curl http://localhost:8000/api/approvals/{approval_id}/history

# List available workflows
curl http://localhost:8000/api/approvals/workflows

# Get approval statistics
curl http://localhost:8000/api/approvals/stats
```

### Timeout Handling

The approval service automatically checks for timeouts:

```python
# Check and handle timeouts (call periodically)
timed_out = approval_service.check_timeouts()

for timeout_info in timed_out:
    print(f"Approval {timeout_info['approval_id']} timed out")
    print(f"Action taken: {timeout_info['action']}")
```

In production, this should run as a background task (e.g., every 5 minutes).

---

## 5. Exit Criteria Achievement

### ✅ Compliance Officer Sign-Off

A compliance officer can now sign off on AI usage because:

1. **No Code Reading Required**
   - All policies are declarative YAML
   - Rules are in plain English with regulatory references
   - Configuration-driven, not code-driven

2. **Complete Audit Trail**
   - Every approval has a rationale
   - Full decision history preserved
   - Cryptographically verified logs
   - Subpoena-ready exports

3. **Clear Compliance Structure**
   - 6 compliance packs with regulatory mappings
   - NIST AI RMF and EU AI Act coverage
   - Risk-based classification
   - Automatic compliance reporting

4. **Human Oversight Workflows**
   - Multi-level approval chains
   - Timeout handling
   - Escalation paths
   - Decision rationale required

### Example Compliance Report

```bash
# Generate compliance report for an agent
curl http://localhost:8000/api/compliance/report/my-agent?standards=nist-ai-rmf,eu-ai-act
```

Returns:
```json
{
  "agent_id": "my-agent",
  "time_range": "2024-01-01 to 2024-12-31",
  "standards": ["nist-ai-rmf", "eu-ai-act"],
  "total_executions": 1250,
  "compliant_executions": 1248,
  "violations": 2,
  "approval_requests": 45,
  "approvals_granted": 43,
  "approvals_rejected": 2,
  "compliance_rate": 99.84,
  "violations_detail": [
    {
      "rule": "nist-ai-rmf-measure-1",
      "count": 2,
      "description": "Bias testing required"
    }
  ]
}
```

---

## 6. Production Deployment

### Environment Variables

```bash
# OIDC Configuration
OIDC_PROVIDER=auth0
OIDC_ISSUER=https://your-tenant.auth0.com/
OIDC_CLIENT_ID=your-client-id
OIDC_CLIENT_SECRET=your-client-secret
OIDC_REDIRECT_URI=https://your-app.com/callback
OIDC_AUDIENCE=https://api.your-app.com

# Approval Configuration
APPROVAL_DEFAULT_TIMEOUT=3600
APPROVAL_CHECK_INTERVAL=300
```

### Kubernetes Deployment

Update your Kubernetes deployment to include approval timeout checking:

```yaml
# Background job for approval timeout checking
apiVersion: batch/v1
kind: CronJob
metadata:
  name: approval-timeout-checker
spec:
  schedule: "*/5 * * * *"  # Every 5 minutes
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: checker
            image: ai-control-plane:latest
            command: ["python", "-m", "approval.timeout_checker"]
```

---

## 7. Next Steps

### Recommended Actions

1. **Configure OIDC provider** for your organization
2. **Create approver users** for risk management team
3. **Load compliance packs** relevant to your industry
4. **Test approval workflows** with sample high-risk requests
5. **Generate compliance reports** for review
6. **Set up timeout monitoring** as a background job

### V3 Enhancements (Future)

- Real-time approval notifications (WebSockets, email, Slack)
- Visual approval workflow builder
- Advanced escalation rules (time-of-day, on-call rotation)
- Integration with ticketing systems (Jira, ServiceNow)
- Compliance certification workflows
- ML-powered risk scoring for auto-routing

---

## Support

For questions or issues:
- Documentation: `/docs`
- API Docs: `http://localhost:8000/api/docs`
- GitHub Issues: `https://github.com/Arnoldlarry15/ai-control-plane/issues`
