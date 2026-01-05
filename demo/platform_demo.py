#!/usr/bin/env python3
"""
Demo: "Salesforce of AI" Platform Capabilities

This demonstrates the key features that make ai-control-plane
the operating system for AI usage in organizations.

Features showcased:
1. Declarative Policy DSL (business-readable rules)
2. Plugin System (extensibility without core changes)
3. Cryptographic Audit Trail (subpoena-ready logs)
4. Policy Explainability (transparent decisions)
5. Lifecycle Hooks (intercept and augment execution)
"""

import json
from datetime import datetime

print("=" * 80)
print("AI Control Plane - The Operating System for AI Usage")
print("=" * 80)
print()

# ============================================================================
# 1. DECLARATIVE POLICY DSL
# ============================================================================
print("1️⃣  DECLARATIVE POLICY DSL")
print("-" * 80)
print("Write policies like business rules, not Python code.\n")

from policy.dsl import BusinessPolicy, get_policy_template, POLICY_TEMPLATES

# Create a business policy using the DSL
high_risk_policy = BusinessPolicy(
    name="High Risk Model Control",
    description="Require approval for high-risk AI models",
    when={
        "and": [
            {"field": "model", "equals": "gpt-4"},
            {"field": "agent.risk_level", "in": ["high", "critical"]}
        ]
    },
    then="escalate",
    reason="High-risk model requires human approval",
    metadata={
        "compliance": ["SOC2", "GDPR"],
        "owner": "security-team",
    }
)

print("Policy created:")
print(f"  Name: {high_risk_policy.name}")
print(f"  Action: {high_risk_policy.then.value}")
print(f"  Reason: {high_risk_policy.reason}")
print()

# Evaluate against different contexts
test_contexts = [
    {
        "model": "gpt-4",
        "agent": {"risk_level": "high"},
        "scenario": "Match: gpt-4 + high risk"
    },
    {
        "model": "gpt-3.5",
        "agent": {"risk_level": "high"},
        "scenario": "No match: different model"
    },
    {
        "model": "gpt-4",
        "agent": {"risk_level": "low"},
        "scenario": "No match: low risk"
    },
]

print("Policy evaluation:")
for ctx in test_contexts:
    result = high_risk_policy.evaluate(ctx)
    status = "✓ MATCHED" if result["matched"] else "✗ No match"
    print(f"  {status}: {ctx['scenario']}")

print()

# Show policy templates
print("Available policy templates:")
for template_id, template in list(POLICY_TEMPLATES.items())[:3]:
    print(f"  • {template_id}: {template['name']}")
print(f"  ... and {len(POLICY_TEMPLATES) - 3} more")
print()

# ============================================================================
# 2. PLUGIN SYSTEM
# ============================================================================
print("2️⃣  PLUGIN SYSTEM")
print("-" * 80)
print("Extend without modifying core. This is what makes it a platform.\n")

from policy.plugins import (
    PluginRegistry,
    ContentFilterPlugin,
    AuditLogHookPlugin,
)

# Create plugin registry
plugin_registry = PluginRegistry()

# Register plugins
content_filter = ContentFilterPlugin()
audit_hook = AuditLogHookPlugin()

plugin_registry.register(content_filter)
plugin_registry.register(audit_hook)

print("Registered plugins:")
for plugin in plugin_registry.list_plugins():
    print(f"  • {plugin['name']} ({plugin['type']}) v{plugin['version']}")
print()

# Demonstrate risk scorer plugin
test_prompt = "Please delete all customer payment records"
risk_result = content_filter.calculate_risk_score(
    agent_id="test-agent",
    prompt=test_prompt,
    context={}
)

print("Risk scoring example:")
print(f"  Prompt: '{test_prompt}'")
print(f"  Risk Score: {risk_result['score']}/100")
print(f"  Risk Level: {risk_result['level']}")
print(f"  Factors:")
for factor in risk_result['factors']:
    print(f"    - {factor}")
print()

# ============================================================================
# 3. CRYPTOGRAPHIC AUDIT TRAIL
# ============================================================================
print("3️⃣  CRYPTOGRAPHIC AUDIT TRAIL")
print("-" * 80)
print("Tamper-proof, legally defensible logs. This is your system of record.\n")

from observability.audit_trail import AuditTrail

# Create audit trail
audit_trail = AuditTrail()

# Simulate an execution flow
execution_id = "exec-demo-001"

# Entry 1: Execution started
entry1 = audit_trail.append(
    event_type="execution_started",
    action="start_execution",
    status="initiated",
    details={
        "agent_id": "customer-support-bot",
        "user": "alice@company.com",
        "timestamp": datetime.utcnow().isoformat(),
    },
    execution_id=execution_id,
    agent_id="customer-support-bot",
    user="alice@company.com",
)

# Entry 2: Policy evaluated
entry2 = audit_trail.append(
    event_type="policy_evaluated",
    action="evaluate_policies",
    status="completed",
    details={
        "decision": "escalate",
        "policy": "GDPR Compliance",
        "reason": "Special category data detected",
    },
    execution_id=execution_id,
    agent_id="customer-support-bot",
    user="alice@company.com",
)

# Entry 3: Human approval granted
entry3 = audit_trail.append(
    event_type="approval_granted",
    action="approve_execution",
    status="approved",
    details={
        "approver": "manager@company.com",
        "decision": "granted",
        "notes": "Reviewed and approved",
    },
    execution_id=execution_id,
    agent_id="customer-support-bot",
    user="alice@company.com",
)

# Entry 4: Execution completed
entry4 = audit_trail.append(
    event_type="execution_completed",
    action="complete_execution",
    status="success",
    details={
        "latency_ms": 1234,
        "response_length": 567,
    },
    execution_id=execution_id,
    agent_id="customer-support-bot",
    user="alice@company.com",
)

print("Audit trail created (4 entries):")
print(f"  Entry 1: {entry1.event_type} (hash: {entry1.entry_hash[:16]}...)")
print(f"  Entry 2: {entry2.event_type} (hash: {entry2.entry_hash[:16]}...)")
print(f"  Entry 3: {entry3.event_type} (hash: {entry3.entry_hash[:16]}...)")
print(f"  Entry 4: {entry4.event_type} (hash: {entry4.entry_hash[:16]}...)")
print()

# Verify integrity
integrity = audit_trail.verify_integrity()
print("Integrity verification:")
print(f"  Status: {'✓ VALID' if integrity['valid'] else '✗ COMPROMISED'}")
print(f"  Total entries: {integrity['total_entries']}")
print(f"  Invalid entries: {len(integrity['invalid_entries'])}")
print(f"  Broken chains: {len(integrity['broken_chains'])}")
print()

# Get chain of custody
chain = audit_trail.get_chain_of_custody(execution_id)
print("Chain of custody:")
print(f"  Execution ID: {chain['execution_id']}")
print(f"  Status: {chain['status'].upper()}")
print(f"  Total events: {chain['total_events']}")
print(f"  Timeline:")
for i, event in enumerate(chain['timeline'], 1):
    hash_status = "✓" if event['hash_verified'] else "✗"
    print(f"    {i}. {event['event_type']}: {event['status']} {hash_status}")
print()

# ============================================================================
# 4. POLICY EXPLAINABILITY
# ============================================================================
print("4️⃣  POLICY EXPLAINABILITY")
print("-" * 80)
print("Every decision explained. Trust through transparency.\n")

from policy.explainer import PolicyExplainer

explainer = PolicyExplainer()

# Simulate a policy decision
context = {
    "agent_id": "customer-support-bot",
    "agent": {
        "name": "Customer Support Bot",
        "model": "gpt-4",
        "risk_level": "high",
    },
    "prompt": "Process this customer data containing SSN: 123-45-6789",
    "user": "alice@company.com",
}

policies_evaluated = [
    {
        "id": "gdpr-compliance",
        "name": "GDPR Compliance Policy",
        "action": "escalate",
        "reason": "Special category data detected",
        "matched": True,
    },
    {
        "id": "pii-protection",
        "name": "PII Protection Policy",
        "action": "block",
        "reason": "SSN pattern detected in prompt",
        "matched": True,
    },
]

explanation = explainer.explain_decision(
    decision="block",
    context=context,
    policies_evaluated=policies_evaluated,
    final_policy=policies_evaluated[1],
)

print("Policy explanation (machine format):")
print(f"  Decision: {explanation.decision}")
print(f"  Confidence: {explanation.confidence}")
print(f"  Primary reason: {explanation.primary_reason}")
print()

print("Policy explanation (human format):")
print("-" * 40)
print(explanation.to_plain_english())
print("-" * 40)
print()

# ============================================================================
# 5. COMPLIANCE EXPORT
# ============================================================================
print("5️⃣  COMPLIANCE EXPORT")
print("-" * 80)
print("Subpoena-ready exports. Legal compliance built-in.\n")

# Export as JSON (for systems integration)
json_export = audit_trail.export_for_compliance(format="json")
print("JSON export (first 200 chars):")
print(f"  {json_export[:200]}...")
print()

# Get statistics
stats = audit_trail.get_statistics()
print("Audit trail statistics:")
print(f"  Total entries: {stats['total_entries']}")
print(f"  Unique users: {stats['unique_users']}")
print(f"  Unique agents: {stats['unique_agents']}")
print(f"  Event types:")
for event_type, count in stats['by_event_type'].items():
    print(f"    • {event_type}: {count}")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("✅ DEMONSTRATION COMPLETE")
print("=" * 80)
print()
print("Key Takeaways:")
print()
print("1. DECLARATIVE - Policies read like business rules, not code")
print("   → Non-technical stakeholders can review policies")
print()
print("2. EXTENSIBLE - Plugin system without core changes")
print("   → Custom risk models, compliance modules, hooks")
print()
print("3. TRUSTWORTHY - Cryptographic integrity, immutable logs")
print("   → Legal-grade audit trail, tamper detection")
print()
print("4. TRANSPARENT - Every decision explained in plain English")
print("   → Regulators, auditors, executives can understand")
print()
print("5. COMPLIANT - Export formats ready for legal proceedings")
print("   → Subpoena-ready, chain of custody verified")
print()
print("This is not a tool. This is platform infrastructure.")
print("This is the operating system for AI usage in organizations.")
print()
print("🎯 The Salesforce of AI")
print("=" * 80)
