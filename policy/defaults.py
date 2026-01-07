# Copyright 2024 AI Control Plane Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Opinionated Default Policy Bundles

This is how platforms win categories: Ship opinions.

Pre-configured policy bundles for common scenarios:
- safe_mode: Maximum safety for production
- development: Balanced for dev environments
- production: Enterprise-grade governance
- permissive: Minimal restrictions for testing

These defaults quietly shape behavior across the industry.
"""

from typing import Dict, List, Any
from enum import Enum


class PolicyBundle(str, Enum):
    """Pre-configured policy bundles"""
    SAFE_MODE = "safe_mode"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    PERMISSIVE = "permissive"


class EnforcementLevel(str, Enum):
    """Recommended enforcement levels"""
    STRICT = "strict"      # Block on any violation
    BALANCED = "balanced"  # Block on high/critical, warn on low/medium
    PERMISSIVE = "permissive"  # Warn only, never block
    CUSTOM = "custom"      # User-defined


# ============================================================================
# Safe Mode - Maximum Safety for Production
# ============================================================================

SAFE_MODE_POLICIES = {
    "name": "Safe Mode",
    "description": "Maximum safety preset for production environments. Blocks all high-risk operations.",
    "enforcement_level": EnforcementLevel.STRICT,
    "policies": [
        {
            "policy_id": "safe_mode_pii_block",
            "name": "Block All PII",
            "when": {
                "or": [
                    {"field": "prompt", "contains_pattern": "SSN|social.security"},
                    {"field": "prompt", "contains_pattern": "credit.card|\\d{16}"},
                    {"field": "prompt", "contains_pattern": "email|password"},
                ]
            },
            "then": "block",
            "reason": "PII detected - Safe Mode does not allow PII processing"
        },
        {
            "policy_id": "safe_mode_high_risk_escalate",
            "name": "Escalate High-Risk Models",
            "when": {
                "and": [
                    {"field": "risk_level", "in": ["high", "critical"]},
                    {"field": "model", "in": ["gpt-4", "claude-3-opus"]}
                ]
            },
            "then": "escalate",
            "reason": "High-risk model requires approval in Safe Mode",
            "workflow": "high-risk"
        },
        {
            "policy_id": "safe_mode_production_only",
            "name": "Production Environment Only",
            "when": {
                "field": "context.environment",
                "not_equals": "production"
            },
            "then": "warn",
            "reason": "Safe Mode is designed for production use"
        },
        {
            "policy_id": "safe_mode_audit_required",
            "name": "Audit All Requests",
            "when": {"field": "*", "equals": "*"},
            "then": "audit",
            "reason": "All requests must be audited in Safe Mode"
        }
    ],
    "compliance": ["GDPR", "HIPAA", "SOC2", "PCI-DSS"],
    "features": {
        "pii_detection": True,
        "content_filtering": True,
        "rate_limiting": True,
        "approval_workflows": True,
        "full_audit": True,
    }
}


# ============================================================================
# Production - Enterprise-Grade Governance
# ============================================================================

PRODUCTION_POLICIES = {
    "name": "Production",
    "description": "Enterprise-grade governance for production AI systems. Balanced security with usability.",
    "enforcement_level": EnforcementLevel.BALANCED,
    "policies": [
        {
            "policy_id": "prod_sensitive_data_escalate",
            "name": "Escalate Sensitive Data",
            "when": {
                "or": [
                    {"field": "prompt", "contains_pattern": "SSN|credit.card"},
                    {"field": "context.data_classification", "equals": "sensitive"}
                ]
            },
            "then": "escalate",
            "reason": "Sensitive data requires approval",
            "workflow": "standard"
        },
        {
            "policy_id": "prod_high_cost_limit",
            "name": "High Cost Threshold",
            "when": {
                "field": "context.estimated_cost",
                "greater_than": 100
            },
            "then": "escalate",
            "reason": "Estimated cost exceeds $100 threshold"
        },
        {
            "policy_id": "prod_business_hours",
            "name": "Business Hours Only",
            "when": {
                "field": "context.timestamp",
                "outside_business_hours": True
            },
            "then": "warn",
            "reason": "Production executions outside business hours"
        },
        {
            "policy_id": "prod_rate_limit",
            "name": "Rate Limiting",
            "when": {
                "field": "context.requests_per_minute",
                "greater_than": 60
            },
            "then": "block",
            "reason": "Rate limit exceeded (60 req/min)"
        }
    ],
    "compliance": ["GDPR", "SOC2"],
    "features": {
        "pii_detection": True,
        "content_filtering": True,
        "rate_limiting": True,
        "approval_workflows": True,
        "full_audit": True,
    }
}


# ============================================================================
# Development - Balanced for Dev Environments
# ============================================================================

DEVELOPMENT_POLICIES = {
    "name": "Development",
    "description": "Balanced governance for development environments. Focus on learning and visibility.",
    "enforcement_level": EnforcementLevel.BALANCED,
    "policies": [
        {
            "policy_id": "dev_pii_warn",
            "name": "Warn on PII",
            "when": {
                "field": "prompt",
                "contains_pattern": "SSN|credit.card|email"
            },
            "then": "warn",
            "reason": "PII detected - consider using test data"
        },
        {
            "policy_id": "dev_high_risk_warn",
            "name": "Warn on High-Risk Models",
            "when": {
                "field": "risk_level",
                "in": ["high", "critical"]
            },
            "then": "warn",
            "reason": "High-risk model - extra caution advised"
        },
        {
            "policy_id": "dev_cost_threshold",
            "name": "Cost Threshold Warning",
            "when": {
                "field": "context.estimated_cost",
                "greater_than": 10
            },
            "then": "warn",
            "reason": "Development cost exceeds $10"
        }
    ],
    "compliance": [],
    "features": {
        "pii_detection": True,
        "content_filtering": False,
        "rate_limiting": False,
        "approval_workflows": False,
        "full_audit": True,
    }
}


# ============================================================================
# Permissive - Minimal Restrictions for Testing
# ============================================================================

PERMISSIVE_POLICIES = {
    "name": "Permissive",
    "description": "Minimal restrictions for testing and experimentation. Not for production use.",
    "enforcement_level": EnforcementLevel.PERMISSIVE,
    "policies": [
        {
            "policy_id": "permissive_audit_only",
            "name": "Audit Only",
            "when": {"field": "*", "equals": "*"},
            "then": "audit",
            "reason": "All requests audited in permissive mode"
        },
        {
            "policy_id": "permissive_warning",
            "name": "Permissive Mode Warning",
            "when": {
                "field": "context.environment",
                "equals": "production"
            },
            "then": "warn",
            "reason": "WARNING: Permissive mode should not be used in production"
        }
    ],
    "compliance": [],
    "features": {
        "pii_detection": False,
        "content_filtering": False,
        "rate_limiting": False,
        "approval_workflows": False,
        "full_audit": True,
    }
}


# ============================================================================
# Policy Bundle Registry
# ============================================================================

DEFAULT_BUNDLES: Dict[str, Dict[str, Any]] = {
    PolicyBundle.SAFE_MODE: SAFE_MODE_POLICIES,
    PolicyBundle.PRODUCTION: PRODUCTION_POLICIES,
    PolicyBundle.DEVELOPMENT: DEVELOPMENT_POLICIES,
    PolicyBundle.PERMISSIVE: PERMISSIVE_POLICIES,
}


def get_policy_bundle(bundle: PolicyBundle) -> Dict[str, Any]:
    """
    Get a pre-configured policy bundle.
    
    Args:
        bundle: Policy bundle identifier
    
    Returns:
        Policy bundle configuration
    
    Example:
        >>> bundle = get_policy_bundle(PolicyBundle.SAFE_MODE)
        >>> print(bundle['name'])
        Safe Mode
    """
    return DEFAULT_BUNDLES.get(bundle, PRODUCTION_POLICIES)


def list_policy_bundles() -> List[Dict[str, Any]]:
    """
    List all available policy bundles.
    
    Returns:
        List of bundle summaries
    """
    return [
        {
            "bundle_id": bundle_id,
            "name": bundle['name'],
            "description": bundle['description'],
            "enforcement_level": bundle['enforcement_level'],
            "policy_count": len(bundle['policies']),
            "compliance": bundle['compliance'],
            "features": bundle['features'],
        }
        for bundle_id, bundle in DEFAULT_BUNDLES.items()
    ]


def get_recommended_bundle(environment: str, risk_level: str) -> PolicyBundle:
    """
    Get recommended policy bundle based on environment and risk level.
    
    This is opinionated guidance. Shapes user behavior.
    
    Args:
        environment: Deployment environment (dev, staging, prod)
        risk_level: Risk level (low, medium, high, critical)
    
    Returns:
        Recommended policy bundle
    
    Example:
        >>> bundle = get_recommended_bundle("production", "high")
        >>> print(bundle)
        PolicyBundle.SAFE_MODE
    """
    # Critical systems always use safe mode
    if risk_level == "critical":
        return PolicyBundle.SAFE_MODE
    
    # Production environments
    if environment in ["production", "prod"]:
        if risk_level in ["high", "critical"]:
            return PolicyBundle.SAFE_MODE
        return PolicyBundle.PRODUCTION
    
    # Development/staging environments
    if environment in ["development", "dev", "staging"]:
        return PolicyBundle.DEVELOPMENT
    
    # Testing environments
    if environment in ["test", "testing", "sandbox"]:
        return PolicyBundle.PERMISSIVE
    
    # Default to production for safety
    return PolicyBundle.PRODUCTION


def apply_bundle_to_agent(
    agent_config: Dict[str, Any],
    bundle: PolicyBundle
) -> Dict[str, Any]:
    """
    Apply a policy bundle to an agent configuration.
    
    Merges bundle policies with agent-specific overrides.
    
    Args:
        agent_config: Agent configuration
        bundle: Policy bundle to apply
    
    Returns:
        Updated agent configuration
    """
    bundle_config = get_policy_bundle(bundle)
    
    # Start with bundle policies
    policies = [p['policy_id'] for p in bundle_config['policies']]
    
    # Add agent-specific policies
    if 'policies' in agent_config:
        policies.extend(agent_config['policies'])
    
    # Update agent config
    agent_config['policies'] = list(set(policies))  # Remove duplicates
    agent_config['policy_bundle'] = bundle.value
    agent_config['enforcement_level'] = bundle_config['enforcement_level']
    
    return agent_config


# ============================================================================
# Configuration Wizard
# ============================================================================

def configure_agent_interactive() -> Dict[str, Any]:
    """
    Interactive configuration wizard for agents.
    
    Guides users through best practices.
    
    Returns:
        Agent configuration
    """
    print("🧙 AI Control Plane Configuration Wizard")
    print("=" * 50)
    print()
    
    # Basic info
    name = input("Agent name: ").strip()
    model = input("AI model (e.g., gpt-4, claude-3): ").strip()
    
    # Environment
    print("\nDeployment environment:")
    print("  1. Development")
    print("  2. Staging")
    print("  3. Production")
    env_choice = input("Choose (1-3): ").strip()
    
    environment = {
        "1": "development",
        "2": "staging",
        "3": "production",
    }.get(env_choice, "development")
    
    # Risk level
    print("\nRisk level:")
    print("  1. Low - Simple queries, no sensitive data")
    print("  2. Medium - Standard operations")
    print("  3. High - Sensitive data or critical decisions")
    print("  4. Critical - Financial, healthcare, or life-safety")
    risk_choice = input("Choose (1-4): ").strip()
    
    risk_level = {
        "1": "low",
        "2": "medium",
        "3": "high",
        "4": "critical",
    }.get(risk_choice, "medium")
    
    # Get recommended bundle
    recommended = get_recommended_bundle(environment, risk_level)
    bundle_config = get_policy_bundle(recommended)
    
    print(f"\n✅ Recommended: {bundle_config['name']}")
    print(f"   {bundle_config['description']}")
    print(f"\n   Enforcement: {bundle_config['enforcement_level']}")
    print(f"   Policies: {len(bundle_config['policies'])}")
    print(f"   Compliance: {', '.join(bundle_config['compliance']) if bundle_config['compliance'] else 'None'}")
    
    accept = input("\nAccept recommendation? (Y/n): ").strip().lower()
    
    if accept in ['n', 'no']:
        print("\nAvailable bundles:")
        for i, (bundle_id, bundle) in enumerate(DEFAULT_BUNDLES.items(), 1):
            print(f"  {i}. {bundle['name']} - {bundle['description']}")
        
        bundle_choice = input("Choose bundle (1-4): ").strip()
        bundle_map = {str(i+1): bundle_id for i, bundle_id in enumerate(DEFAULT_BUNDLES.keys())}
        recommended = bundle_map.get(bundle_choice, recommended)
    
    # Build configuration
    config = {
        "name": name,
        "model": model,
        "environment": environment,
        "risk_level": risk_level,
        "policy_bundle": recommended.value,
    }
    
    config = apply_bundle_to_agent(config, recommended)
    
    print("\n" + "=" * 50)
    print("✅ Configuration complete!")
    print("\nAgent configuration:")
    for key, value in config.items():
        if key != 'policies':
            print(f"  {key}: {value}")
    print(f"  policies: {len(config['policies'])} policies applied")
    print("=" * 50)
    
    return config
