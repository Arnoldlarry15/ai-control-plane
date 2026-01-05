# Compliance Policy Modules Guide

## Overview

AI Control Plane includes pre-built policy modules for major compliance standards:
- **GDPR** (EU General Data Protection Regulation)
- **HIPAA** (US Health Insurance Portability and Accountability Act)
- **SOC 2** (Trust Services Criteria)
- **PCI-DSS** (Payment Card Industry Data Security Standard)

---

## Quick Start

### Loading Compliance Policies

```python
from policy.compliance import ComplianceLoader

loader = ComplianceLoader()

# List available standards
standards = loader.list_standards()
print(standards)
# {
#   'gdpr': 'GDPR (EU General Data Protection Regulation)',
#   'hipaa': 'HIPAA (US Health Insurance Portability...',
#   ...
# }

# Load a specific policy
gdpr_policy = loader.load_policy('gdpr')

# Load all compliance policies
all_policies = loader.load_all()
```

### Applying to Agents

```python
from sdk.python.client import ControlPlaneClient

client = ControlPlaneClient(base_url="http://localhost:8000")

# Register agent with HIPAA compliance
agent = client.register_agent(
    name="healthcare-bot",
    model="gpt-4",
    policies=["hipaa-compliance"],
)

# Multiple compliance standards
agent = client.register_agent(
    name="financial-advisor",
    model="gpt-4",
    policies=["gdpr-compliance", "soc2-compliance"],
)
```

---

## GDPR Compliance

### What It Covers

**GDPR** (General Data Protection Regulation) is EU regulation protecting personal data.

Key requirements enforced:
- ✅ Right to erasure (Art. 17)
- ✅ Automated decision-making transparency (Art. 22)
- ✅ Special category data protection (Art. 9)
- ✅ Data minimization (Art. 5)
- ✅ Cross-border transfer controls (Ch. V)

### Rules Implemented

```yaml
# Article 17: Right to erasure
- Detects deletion requests → Escalates for review
- Keywords: "delete my data", "forget me", "erase my data"

# Article 22: Automated decisions
- Detects high-impact decisions → Escalates for human review
- Examples: credit, employment, legal, health decisions

# Article 9: Special category data
- Blocks racial/ethnic origin references
- Escalates religious, political, health data → Requires consent

# Article 5: Data minimization
- Escalates excessive data input (>5000 chars)

# Chapter V: Cross-border transfer
- Escalates international data transfer requests
```

### Usage Example

```python
# Will be blocked by GDPR policy
response = client.execute(
    agent_id=agent_id,
    prompt="Store this person's racial background...",
)
# Result: PolicyViolationError - GDPR Art. 9

# Will be escalated for review
response = client.execute(
    agent_id=agent_id,
    prompt="Approve this person's loan application",
)
# Result: Pending approval - GDPR Art. 22
```

### Compliance Reference

Full policy: `policy/compliance/gdpr.yaml`

Official regulation: https://gdpr-info.eu/

---

## HIPAA Compliance

### What It Covers

**HIPAA** (Health Insurance Portability and Accountability Act) protects health information in the US.

Key requirements enforced:
- ✅ Protected Health Information (PHI) detection
- ✅ Minimum necessary standard
- ✅ Patient identifier protection (45 CFR 164.514)
- ✅ Sensitive authentication data

### Rules Implemented

```yaml
# PHI Detection
- SSN patterns → Blocked
- Medical Record Numbers → Blocked
- Patient identifiers → Escalated
- Health-related dates → Escalated

# Minimum Necessary
- "Entire medical history" requests → Blocked

# Geographic Identifiers
- ZIP codes → Escalated (potential identifier)

# Contact Information
- Phone/Fax numbers → Escalated
- Email addresses → Escalated
- IP addresses → Escalated

# Account Numbers
- Certificate, license numbers → Escalated
```

### Usage Example

```python
# Will be blocked by HIPAA policy
response = client.execute(
    agent_id=healthcare_agent,
    prompt="Process patient SSN: 123-45-6789",
)
# Result: PolicyViolationError - HIPAA PHI detected

# Will be escalated
response = client.execute(
    agent_id=healthcare_agent,
    prompt="Show patient's email address",
)
# Result: Pending approval - HIPAA PHI identifier
```

### De-identification

HIPAA requires 18 identifiers to be removed for de-identification:

1. Names
2. Geographic subdivisions smaller than state
3. Dates (except year)
4. Telephone/fax numbers
5. Email addresses
6. SSN
7. Medical record numbers
8. Health plan beneficiary numbers
9. Account numbers
10. Certificate/license numbers
11. Vehicle identifiers
12. Device identifiers/serial numbers
13. URLs
14. IP addresses
15. Biometric identifiers
16. Full-face photos
17. Any other unique identifying number

Our policy detects and blocks/escalates most of these.

### Compliance Reference

Full policy: `policy/compliance/hipaa.yaml`

Official regulation: https://www.hhs.gov/hipaa/

---

## SOC 2 Compliance

### What It Covers

**SOC 2** (Service Organization Control 2) validates trust through five Trust Services Criteria.

Key requirements enforced:
- ✅ Security (Common Criteria)
- ✅ Availability
- ✅ Processing Integrity
- ✅ Confidentiality
- ✅ Privacy

### Rules Implemented

```yaml
# Security - Access Control (CC6.1)
- Credentials in input → Blocked
- Keywords: passwords, API secrets, private keys

# Confidentiality (C1.1)
- Confidential data markers → Escalated
- Keywords: "confidential", "proprietary", "trade secret"

# Processing Integrity (PI1.1)
- High-risk operations → Escalated
- Examples: database deletion, command execution

# Change Management (CC8.1)
- System changes → Escalated
- Examples: production deploys, config updates

# Privacy (P4.2)
- Data deletion requests → Escalated

# Monitoring (CC7.2)
- Disable monitoring attempts → Blocked

# Availability (A1.1)
- Service shutdown attempts → Escalated
```

### Usage Example

```python
# Will be blocked by SOC 2 policy
response = client.execute(
    agent_id=agent_id,
    prompt="Store the admin password: abc123",
)
# Result: PolicyViolationError - SOC 2 CC6.1

# Will be escalated
response = client.execute(
    agent_id=agent_id,
    prompt="Deploy this change to production",
)
# Result: Pending approval - SOC 2 CC8.1
```

### Compliance Reference

Full policy: `policy/compliance/soc2.yaml`

Official framework: https://www.aicpa.org/soc

---

## PCI-DSS Compliance

### What It Covers

**PCI-DSS** (Payment Card Industry Data Security Standard) protects cardholder data.

Key requirements enforced:
- ✅ Cardholder data protection (Req 3)
- ✅ Sensitive authentication data (Req 3.2)
- ✅ PAN masking (Req 3.3)
- ✅ Access control (Req 7)
- ✅ Audit trails (Req 10)

### Rules Implemented

```yaml
# Requirement 3.2: No sensitive authentication data after authorization
- CVV/CVC codes → Blocked
- PIN blocks → Blocked
- Magnetic stripe data → Blocked

# Requirement 3.3: Mask PAN when displayed
- Card number patterns → Blocked
  - Visa: 4xxx-xxxx-xxxx-xxxx
  - Mastercard: 5xxx-xxxx-xxxx-xxxx
  - Amex: 37xx-xxxxxx-xxxxx

# Requirement 3.4: Render PAN unreadable
- "Full card number" requests → Blocked

# Requirement 7: Restrict access
- Bulk cardholder data access → Escalated

# Requirement 10: Track access
- Cardholder data access → Escalated & logged
```

### Card Number Detection

Detects major card brands:

```python
# Visa
Pattern: ^4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$

# Mastercard
Pattern: ^5[1-5]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$

# American Express
Pattern: ^3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5}$

# Discover
Pattern: ^6(?:011|5\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$
```

### Usage Example

```python
# Will be blocked by PCI-DSS policy
response = client.execute(
    agent_id=payment_agent,
    prompt="Process card: 4532-1234-5678-9010 CVV: 123",
)
# Result: PolicyViolationError - PCI-DSS Req 3.2/3.3

# Proper usage (tokenized)
response = client.execute(
    agent_id=payment_agent,
    prompt="Process token: tok_1234567890abcdef",
)
# Result: Success
```

### Compliance Reference

Full policy: `policy/compliance/pci-dss.yaml`

Official standard: https://www.pcisecuritystandards.org/

---

## Customizing Compliance Policies

### Extending Existing Policies

```python
from policy.compliance import ComplianceLoader
from policy.parser import PolicyParser

# Load base policy
loader = ComplianceLoader()
gdpr = loader.load_policy('gdpr')

# Add custom rules
custom_yaml = """
policy:
  id: "gdpr-extended"
  version: "1.1"
  name: "GDPR Extended"
  description: "GDPR with company-specific rules"
  
  rules:
    # Include all GDPR rules...
    
    # Add custom rule
    - condition:
        input_contains: "company-specific-term"
      action: block
      reason: "Company policy - GDPR extension"
"""

parser = PolicyParser()
extended_policy = parser.parse_yaml(custom_yaml)
```

### Creating Custom Compliance Policies

```yaml
# policy/compliance/custom.yaml
policy:
  id: "company-compliance"
  version: "1.0"
  name: "Company Internal Compliance"
  description: "Company-specific compliance requirements"
  compliance_standard: "INTERNAL"
  
  rules:
    - condition:
        input_contains_any:
          - "project-codename"
          - "confidential-term"
      action: block
      reason: "Internal compliance - confidential project"
    
    - condition:
        input_contains: "competitor-name"
      action: escalate
      reason: "Internal compliance - competitive intelligence requires approval"
```

---

## Multi-Standard Compliance

### Combining Standards

```python
# Register agent with multiple compliance standards
agent = client.register_agent(
    name="healthcare-financial-bot",
    model="gpt-4",
    policies=[
        "hipaa-compliance",  # Healthcare data
        "pci-dss-compliance",  # Payment data
        "soc2-compliance",  # General security
    ],
)
```

### Compliance Hierarchy

When multiple policies apply:
1. **First block wins**: If any policy blocks, request is blocked
2. **Escalation propagates**: If any policy escalates, request is escalated
3. **All logs recorded**: All policy decisions are logged

Example:

```python
# Input: "Process patient credit card: 4532-1234-5678-9010"
#
# HIPAA: Escalate (patient data)
# PCI-DSS: Block (card number)
# 
# Result: BLOCKED (PCI-DSS takes precedence)
```

---

## Audit and Reporting

### Compliance Reports

```python
from observability.logger import AuditLogger

logger = AuditLogger()

# Get all GDPR violations
gdpr_violations = logger.query_events(
    event_type="policy_violation",
    policy_id="gdpr-compliance",
)

# Generate compliance report
report = {
    "standard": "GDPR",
    "period": "2026-01",
    "total_requests": 1000,
    "violations": len(gdpr_violations),
    "escalations": len([v for v in gdpr_violations if v.action == "escalate"]),
    "blocks": len([v for v in gdpr_violations if v.action == "block"]),
}
```

### Export for Auditors

```python
# Export audit trail
import json

events = logger.get_all_events()

with open("compliance-audit-2026-01.json", "w") as f:
    json.dump(events, f, indent=2)
```

---

## Testing Compliance

### Unit Testing

```python
import pytest
from policy.compliance import ComplianceLoader
from policy.evaluator import PolicyEvaluator

def test_gdpr_pii_detection():
    loader = ComplianceLoader()
    policy = loader.load_policy('gdpr')
    
    evaluator = PolicyEvaluator()
    evaluator.register_policy(policy)
    
    result = evaluator._evaluate_policy(
        policy,
        prompt="Delete my racial background data",
        context={},
        user="test@company.test",
    )
    
    assert result["action"] == "block"
    assert "GDPR Art. 9" in result["reason"]
```

### Integration Testing

```bash
# Test HIPAA compliance
python -m pytest tests/test_compliance_hipaa.py -v

# Test all compliance policies
python -m pytest tests/test_compliance*.py -v
```

---

## Best Practices

### 1. Document Compliance Mappings

```python
# Document which policies cover which requirements
COMPLIANCE_MAPPING = {
    "GDPR": {
        "Article 17": ["gdpr-compliance"],
        "Article 22": ["gdpr-compliance"],
        "Article 9": ["gdpr-compliance"],
    },
    "HIPAA": {
        "45 CFR 164.514": ["hipaa-compliance"],
        "45 CFR 164.502": ["hipaa-compliance"],
    },
}
```

### 2. Regular Policy Updates

```bash
# Subscribe to compliance updates
# Update policies when regulations change
# Test thoroughly before deploying
```

### 3. Compliance Training

- Train team on compliance requirements
- Document policy decisions
- Regular compliance reviews

### 4. Incident Response

```python
# When compliance violation occurs:
1. Log incident immediately
2. Escalate to compliance team
3. Document response
4. Update policies if needed
5. Report to authorities if required
```

---

## Regulatory Resources

### GDPR
- Official text: https://gdpr-info.eu/
- ICO guidance: https://ico.org.uk/for-organisations/guide-to-data-protection/

### HIPAA
- HHS HIPAA page: https://www.hhs.gov/hipaa/
- Privacy Rule: https://www.hhs.gov/hipaa/for-professionals/privacy/

### SOC 2
- AICPA: https://www.aicpa.org/soc
- Trust Services Criteria: https://www.aicpa.org/soc4so

### PCI-DSS
- PCI Security Standards: https://www.pcisecuritystandards.org/
- Current standard: https://www.pcisecuritystandards.org/document_library/

---

## Support

For compliance questions:
- Review policy files: `policy/compliance/*.yaml`
- Check audit logs for violations
- Consult with legal/compliance team
- Open issue: https://github.com/Arnoldlarry15/ai-control-plane/issues
