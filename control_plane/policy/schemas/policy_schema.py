"""
Policy Schema - Declarative policy definitions.

Policies are JSON/YAML friendly configurations, not executable code.
This makes them auditable, versionable, and understandable by non-developers.
"""

from typing import Dict, List, Any, Optional


class PolicySchema:
    """
    Policy schema definition.
    
    A policy is a rule with intent. It specifies:
    - scope: What it applies to (environment, resource type, etc.)
    - conditions: When it triggers (tags, metadata, etc.)
    - effect: What happens (ALLOW, DENY, REVIEW)
    - priority: Conflict resolution order (higher = evaluated first)
    
    Example policy in plain English:
    "If a model tries to access PII in production, require review."
    
    Example policy in JSON/YAML:
    {
      "id": "prod_pii_requires_review",
      "version": "1.0.0",
      "description": "Access to PII in production requires human approval",
      "scope": {
        "environment": ["production"],
        "resource_type": ["model", "agent"]
      },
      "conditions": {
        "tags": ["pii"]
      },
      "effect": "REVIEW",
      "priority": 100
    }
    """
    
    def __init__(self, policy_dict: Dict[str, Any]):
        """
        Initialize policy from dictionary.
        
        Args:
            policy_dict: Policy definition as dictionary
        """
        self.id: str = policy_dict["id"]
        self.version: str = policy_dict.get("version", "1.0.0")
        self.description: str = policy_dict.get("description", "")
        self.scope: Dict[str, List[str]] = policy_dict.get("scope", {})
        self.conditions: Dict[str, Any] = policy_dict.get("conditions", {})
        self.effect: str = policy_dict["effect"]
        self.priority: int = policy_dict.get("priority", 0)
        
        # Validate effect
        if self.effect not in ["ALLOW", "DENY", "REVIEW"]:
            raise ValueError(f"Invalid effect: {self.effect}. Must be ALLOW, DENY, or REVIEW")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary."""
        return {
            "id": self.id,
            "version": self.version,
            "description": self.description,
            "scope": self.scope,
            "conditions": self.conditions,
            "effect": self.effect,
            "priority": self.priority,
        }
    
    @staticmethod
    def from_dict(policy_dict: Dict[str, Any]) -> "PolicySchema":
        """Create policy from dictionary."""
        return PolicySchema(policy_dict)


def load_policy_from_yaml_dict(yaml_dict: Dict[str, Any]) -> PolicySchema:
    """
    Load policy from YAML dictionary.
    
    Args:
        yaml_dict: Dictionary loaded from YAML
        
    Returns:
        PolicySchema instance
    """
    return PolicySchema(yaml_dict)


def load_policy_from_json_dict(json_dict: Dict[str, Any]) -> PolicySchema:
    """
    Load policy from JSON dictionary.
    
    Args:
        json_dict: Dictionary loaded from JSON
        
    Returns:
        PolicySchema instance
    """
    return PolicySchema(json_dict)
