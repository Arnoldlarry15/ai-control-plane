# Threat Model

## Scope

This threat model covers **ai-control-plane**, a governance layer for AI systems. The goal is to identify threats, mitigations, and residual risks.

**In Scope**:
- Control plane infrastructure
- Policy enforcement mechanisms
- Audit logging integrity
- Kill switch reliability
- API authentication/authorization

**Out of Scope**:
- AI model vulnerabilities (prompt injection, jailbreaking)
- Underlying infrastructure security (OS, network)
- Third-party AI provider security

---

## Assets

What we're protecting:

1. **Policy Integrity** - Policies must not be bypassed or tampered with
2. **Audit Logs** - Complete, immutable record of all activity
3. **Kill Switch** - Emergency control must be reliable
4. **Agent Registry** - Authoritative source of truth
5. **Execution Gateway** - Must enforce all controls
6. **Credentials** - API keys, tokens, secrets

---

## Trust Boundaries

```
┌──────────────────────────────────────────┐
│        Untrusted: External Users          │
│         (via SDK / API)                   │
└────────────────┬─────────────────────────┘
                 │
      ════════════════════════
      TRUST BOUNDARY: Authentication
      ════════════════════════
                 │
┌────────────────▼─────────────────────────┐
│       Trusted: Control Plane              │
│   (Gateway, Policy, Registry, etc.)       │
└────────────────┬─────────────────────────┘
                 │
      ════════════════════════
      TRUST BOUNDARY: Authorization
      ════════════════════════
                 │
┌────────────────▼─────────────────────────┐
│      Privileged: Admin Functions          │
│    (Kill Switch, Policy Management)       │
└──────────────────────────────────────────┘
```

---

## Threat Categories

### 1. Bypass Threats

**Goal**: Execute AI without going through control plane.

#### T1.1: Direct API Calls to AI Providers

**Description**: Attacker calls OpenAI/Anthropic directly, bypassing governance.

**Impact**: High - No audit, no policy enforcement, shadow AI usage.

**Mitigation**:
- Network policies to block direct egress to AI providers
- Credential management (don't distribute raw API keys)
- Monitor for anomalous traffic patterns
- SDK adoption metrics

**Residual Risk**: Medium - Can't control user-owned API keys.

#### T1.2: Credential Theft

**Description**: Steal control plane API keys or AI provider keys from config.

**Impact**: High - Attacker can execute as legitimate user or bypass entirely.

**Mitigation**:
- Rotate credentials regularly
- Use environment variables, not hardcoded keys
- Implement API key scoping (limited permissions)
- Monitor for unusual usage patterns
- Require multi-factor authentication for sensitive operations

**Residual Risk**: Low - Standard security practices apply.

#### T1.3: SDK Forking

**Description**: User modifies SDK to skip control plane checks.

**Impact**: High - Bypass all governance controls.

**Mitigation**:
- Network enforcement (block direct AI provider access)
- Audit all AI usage via network logs
- Certificate pinning in SDK
- Integrity checks on SDK distribution

**Residual Risk**: High - Can't control user's local environment.

---

### 2. Policy Evasion Threats

**Goal**: Execute prohibited actions without detection.

#### T2.1: Input Obfuscation

**Description**: Encode/obfuscate prohibited content to evade detection.

**Impact**: Medium - Bypass input filtering policies.

**Example**: Base64 encode PII, use homoglyphs, etc.

**Mitigation**:
- Normalize input before policy evaluation
- Decode common encodings
- Use semantic analysis, not just pattern matching
- Regularly update detection patterns

**Residual Risk**: Medium - Arms race with attackers.

#### T2.2: Prompt Injection

**Description**: Trick AI model into ignoring system instructions.

**Impact**: Medium - Model behavior diverges from policy intent.

**Note**: This is a MODEL threat, not a control plane threat, but we can help.

**Mitigation**:
- Output scanning policies
- Behavioral anomaly detection
- Model-level defenses (outside our scope)

**Residual Risk**: High - Fundamentally a model problem.

#### T2.3: Policy Timing Attacks

**Description**: Execute during policy update windows or race conditions.

**Impact**: Low - Brief window of incorrect policy enforcement.

**Mitigation**:
- Atomic policy updates
- Version locking during evaluation
- Graceful policy transitions

**Residual Risk**: Low - Narrow attack window.

---

### 3. Privilege Escalation Threats

**Goal**: Gain unauthorized access to admin functions.

#### T3.1: Kill Switch Unauthorized Activation

**Description**: Non-admin user activates kill switch, causing DoS.

**Impact**: High - Business disruption.

**Mitigation**:
- Strong RBAC on kill switch endpoints
- Multi-factor authentication for activation
- Audit all kill switch operations
- Rate limiting on kill switch API

**Residual Risk**: Low - Standard access control.

#### T3.2: Policy Modification

**Description**: Attacker modifies or disables policies.

**Impact**: Critical - Complete bypass of governance.

**Mitigation**:
- Policy changes require admin role
- Policy files in version control with code review
- Immutable policy history
- Separate policy deployment pipeline

**Residual Risk**: Low - Policies are code, follow software dev practices.

#### T3.3: Registry Tampering

**Description**: Register malicious agent or modify existing agent metadata.

**Impact**: High - Execute unvetted AI agents.

**Mitigation**:
- Registry writes require elevated permissions
- Agent registration requires approval workflow
- Integrity checks on agent definitions
- Version control for registry changes

**Residual Risk**: Low - Standard data integrity controls.

---

### 4. Audit Log Threats

**Goal**: Hide malicious activity or corrupt audit trail.

#### T4.1: Log Tampering

**Description**: Modify or delete audit logs to cover tracks.

**Impact**: Critical - Loss of accountability and forensics.

**Mitigation**:
- Immutable log storage (append-only)
- Cryptographic log signing
- Write logs to separate, hardened system
- Regular log integrity checks
- Off-system log backups

**Residual Risk**: Low - Strong technical controls.

#### T4.2: Log Flooding

**Description**: Generate massive volume of logs to hide malicious activity or cause DoS.

**Impact**: Medium - Obscure real threats, storage exhaustion.

**Mitigation**:
- Rate limiting on API calls
- Log sampling for high-volume users
- Anomaly detection on log patterns
- Auto-scaling log storage

**Residual Risk**: Medium - Trade-off between completeness and DoS resistance.

#### T4.3: Log Replay Attacks

**Description**: Replay logged requests to re-execute AI operations.

**Impact**: Low - Duplicate execution, potential resource abuse.

**Mitigation**:
- Request nonces/timestamps
- Idempotency tokens
- Detect duplicate request signatures

**Residual Risk**: Low - Standard replay prevention.

---

### 5. Denial of Service Threats

**Goal**: Make control plane unavailable.

#### T5.1: Gateway Overload

**Description**: Flood gateway with requests to exhaust resources.

**Impact**: High - No AI execution possible (fail closed).

**Mitigation**:
- Rate limiting per user/IP
- Load balancing across gateway instances
- Circuit breakers for failing dependencies
- Request queuing with backpressure

**Residual Risk**: Medium - Always vulnerable to DDoS at some scale.

#### T5.2: Policy Evaluation DoS

**Description**: Craft inputs that cause expensive policy evaluation (e.g., catastrophic regex backtracking).

**Impact**: Medium - Slow down or crash policy engine.

**Mitigation**:
- Timeout policy evaluation
- Limit regex complexity
- Pre-compile and cache policies
- Resource limits on evaluator

**Residual Risk**: Low - Bounded execution time.

#### T5.3: Kill Switch as Weapon

**Description**: Attacker triggers kill switch to cause business disruption.

**Impact**: High - All AI execution halted.

**Mitigation**:
- Strong authentication for kill switch
- Multi-person approval for global kill switch
- Audit trail of all activations
- Granular kill switch (per-agent, not just global)

**Residual Risk**: Low - Access controls prevent casual misuse.

---

### 6. Information Disclosure Threats

**Goal**: Leak sensitive information.

#### T6.1: Audit Log Exposure

**Description**: Unauthorized access to audit logs containing sensitive data.

**Impact**: High - Logs may contain PII, business logic, API patterns.

**Mitigation**:
- Encrypt logs at rest
- Strict access controls on log storage
- PII redaction in logs
- Separate log access from operational access

**Residual Risk**: Medium - Logs inherently contain sensitive data.

#### T6.2: Policy Enumeration

**Description**: Attacker learns policy rules to craft evasions.

**Impact**: Medium - Knowledge of policies aids bypass attempts.

**Mitigation**:
- Don't expose detailed policy logic in error messages
- Generic "blocked" responses
- Monitor for policy probing patterns

**Residual Risk**: Medium - Security through obscurity is weak.

#### T6.3: Timing Side Channels

**Description**: Infer information from response times (e.g., policy evaluation time).

**Impact**: Low - Limited information leakage.

**Mitigation**:
- Constant-time responses where feasible
- Add jitter to response times

**Residual Risk**: Low - Limited exploitability.

---

### 7. Supply Chain Threats

**Goal**: Compromise control plane through dependencies.

#### T7.1: Compromised Dependencies

**Description**: Malicious code in Python packages (FastAPI, SQLAlchemy, etc.).

**Impact**: Critical - Full system compromise.

**Mitigation**:
- Pin dependency versions
- Use dependency scanning tools
- Regular security audits
- Vendor dependencies in repo (optional)

**Residual Risk**: Medium - Inherent to software supply chain.

#### T7.2: Compromised AI Provider

**Description**: OpenAI/Anthropic infrastructure compromised.

**Impact**: High - But out of scope for control plane.

**Mitigation**:
- Monitor provider status
- Multi-provider fallback
- Output validation policies

**Residual Risk**: High - We can't control provider security.

---

## Risk Matrix

| Threat ID | Impact | Likelihood | Risk | Mitigation Priority |
|-----------|--------|------------|------|---------------------|
| T1.1 | High | High | **Critical** | High |
| T1.2 | High | Medium | High | High |
| T1.3 | High | Low | Medium | Medium |
| T2.1 | Medium | Medium | Medium | Medium |
| T2.2 | Medium | High | Medium | Low (model problem) |
| T2.3 | Low | Low | Low | Low |
| T3.1 | High | Low | Medium | High |
| T3.2 | Critical | Low | High | High |
| T3.3 | High | Low | Medium | Medium |
| T4.1 | Critical | Low | High | High |
| T4.2 | Medium | Medium | Medium | Medium |
| T4.3 | Low | Low | Low | Low |
| T5.1 | High | Medium | High | High |
| T5.2 | Medium | Low | Low | Medium |
| T5.3 | High | Low | Medium | High |
| T6.1 | High | Medium | High | High |
| T6.2 | Medium | Medium | Medium | Low |
| T6.3 | Low | Low | Low | Low |
| T7.1 | Critical | Low | High | High |
| T7.2 | High | Low | Medium | Low (out of scope) |

---

## Security Design Principles

These principles guide all security decisions:

1. **Fail Closed**: When in doubt, block execution
2. **Defense in Depth**: Multiple layers of security
3. **Least Privilege**: Minimal permissions by default
4. **Audit Everything**: Complete activity logs
5. **Assume Breach**: Design for containment and detection
6. **Transparent Security**: No hidden security mechanisms

---

## Compliance Considerations

The control plane helps satisfy:

- **SOC 2**: Audit logging, access controls, monitoring
- **GDPR**: PII detection and redaction policies
- **HIPAA**: PHI protection policies
- **SOX**: Separation of duties, audit trails
- **ISO 27001**: Information security controls

---

## Incident Response

If the control plane is compromised:

1. **Activate kill switch** - Halt all AI execution
2. **Preserve logs** - Export audit logs to offline storage
3. **Revoke credentials** - Rotate all API keys
4. **Assess scope** - Review logs for unauthorized activity
5. **Remediate** - Fix vulnerability, update policies
6. **Post-mortem** - Document incident, update threat model

---

## Security Testing

Regular security validation:

- **Policy bypass testing** - Attempt to evade each policy
- **Access control testing** - Verify RBAC enforcement
- **Log integrity testing** - Validate immutability
- **Kill switch testing** - Exercise emergency controls
- **Dependency scanning** - Check for known vulnerabilities
- **Penetration testing** - Annual third-party audit

---

## Future Threats

As the system evolves, watch for:

- **AI-generated attacks** - Models crafting evasions
- **Federated deployment** - Multiple control plane instances
- **Advanced persistent threats** - Long-term compromise
- **Insider threats** - Malicious administrators
- **Zero-day vulnerabilities** - Unknown software flaws

---

## Conclusion

The control plane is a security-critical system. Its purpose is to provide governance, but it must not become the weakest link.

**Key takeaway**: The control plane protects against misuse of AI, not against all AI risks. Model-level threats (jailbreaking, hallucinations) are separate concerns.

**Philosophy**: We can't make AI 100% safe, but we can make it 100% accountable.
