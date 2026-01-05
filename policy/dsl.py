"""
Policy DSL (Domain-Specific Language)

Provides a business-readable, declarative policy language that reads like natural rules.

Example:
    When model = "gpt-4" and risk > "high" then require approval
    When input contains PII then block with reason "Data protection violation"
    When user not in ["admin", "operator"] and cost > 100 then escalate
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)


class PolicyAction(Enum):
    """Policy actions that can be taken."""
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"
    REDACT = "redact"
    LOG_ONLY = "log_only"


class PolicyConditionType(Enum):
    """Types of conditions that can be evaluated."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    MATCHES_PATTERN = "matches_pattern"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    AND = "and"
    OR = "or"


class BusinessPolicy:
    """
    Business-readable policy representation.
    
    This is what users write. It gets compiled to machine-executable form.
    
    Example:
        policy = BusinessPolicy(
            name="High Risk Model Control",
            description="Require approval for high-risk models",
            when={
                "and": [
                    {"field": "model", "equals": "gpt-4"},
                    {"field": "risk_level", "in": ["high", "critical"]}
                ]
            },
            then="escalate",
            reason="High-risk model requires human approval"
        )
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        when: Dict[str, Any],
        then: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.description = description
        self.when = when
        self.then = PolicyAction(then)
        self.reason = reason
        self.metadata = metadata or {}
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate policy against execution context.
        
        Args:
            context: Execution context with fields to check
            
        Returns:
            Dictionary with 'matched' boolean and 'action' if matched
        """
        matched = self._evaluate_condition(self.when, context)
        
        result = {
            "matched": matched,
            "policy_name": self.name,
        }
        
        if matched:
            result.update({
                "action": self.then.value,
                "reason": self.reason,
            })
        
        return result
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Recursively evaluate condition tree.
        
        Args:
            condition: Condition specification
            context: Execution context
            
        Returns:
            True if condition matches
        """
        # Handle logical operators (AND, OR)
        if "and" in condition:
            return all(self._evaluate_condition(c, context) for c in condition["and"])
        
        if "or" in condition:
            return any(self._evaluate_condition(c, context) for c in condition["or"])
        
        # Handle field comparisons
        field = condition.get("field")
        if not field:
            logger.warning(f"Condition missing 'field': {condition}")
            return False
        
        value = self._get_nested_value(context, field)
        
        # Evaluate different condition types
        if "equals" in condition:
            return value == condition["equals"]
        
        if "not_equals" in condition:
            return value != condition["not_equals"]
        
        if "contains" in condition:
            return condition["contains"] in str(value).lower()
        
        if "not_contains" in condition:
            return condition["not_contains"] not in str(value).lower()
        
        if "matches_pattern" in condition:
            pattern = condition["matches_pattern"]
            return bool(re.search(pattern, str(value), re.IGNORECASE))
        
        if "in" in condition:
            return value in condition["in"]
        
        if "not_in" in condition:
            return value not in condition["not_in"]
        
        if "greater_than" in condition:
            try:
                return float(value) > float(condition["greater_than"])
            except (ValueError, TypeError):
                return False
        
        if "less_than" in condition:
            try:
                return float(value) < float(condition["less_than"])
            except (ValueError, TypeError):
                return False
        
        logger.warning(f"Unknown condition type: {condition}")
        return False
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """
        Get value from nested dictionary using dot notation.
        
        Example: "agent.risk_level" -> obj["agent"]["risk_level"]
        
        Args:
            obj: Dictionary to traverse
            path: Dot-separated path
            
        Returns:
            Value at path or None
        """
        parts = path.split(".")
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "when": self.when,
            "then": self.then.value,
            "reason": self.reason,
            "metadata": self.metadata,
        }


class PolicyDSLCompiler:
    """
    Compiles business-readable policies into executable form.
    
    This is the bridge between what users write and what the engine executes.
    """
    
    def __init__(self):
        logger.info("Policy DSL compiler initialized")
    
    def compile_from_dict(self, policy_dict: Dict[str, Any]) -> BusinessPolicy:
        """
        Compile policy from dictionary specification.
        
        Args:
            policy_dict: Policy specification
            
        Returns:
            Compiled BusinessPolicy
        """
        required_fields = ["name", "description", "when", "then", "reason"]
        
        for field in required_fields:
            if field not in policy_dict:
                raise ValueError(f"Policy missing required field: {field}")
        
        return BusinessPolicy(
            name=policy_dict["name"],
            description=policy_dict["description"],
            when=policy_dict["when"],
            then=policy_dict["then"],
            reason=policy_dict["reason"],
            metadata=policy_dict.get("metadata", {}),
        )
    
    def validate_policy(self, policy: Union[BusinessPolicy, Dict[str, Any]]) -> bool:
        """
        Validate policy structure and logic.
        
        Args:
            policy: Policy to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If policy is invalid
        """
        if isinstance(policy, dict):
            policy = self.compile_from_dict(policy)
        
        # Validate action
        if policy.then not in PolicyAction:
            raise ValueError(f"Invalid action: {policy.then}")
        
        # Validate condition structure
        self._validate_condition(policy.when)
        
        return True
    
    def _validate_condition(self, condition: Dict[str, Any]):
        """
        Validate condition structure recursively.
        
        Args:
            condition: Condition to validate
            
        Raises:
            ValueError: If condition is invalid
        """
        # Handle logical operators
        if "and" in condition:
            if not isinstance(condition["and"], list):
                raise ValueError("'and' must be a list of conditions")
            for c in condition["and"]:
                self._validate_condition(c)
            return
        
        if "or" in condition:
            if not isinstance(condition["or"], list):
                raise ValueError("'or' must be a list of conditions")
            for c in condition["or"]:
                self._validate_condition(c)
            return
        
        # Must have field for leaf conditions
        if "field" not in condition:
            raise ValueError(f"Condition missing 'field': {condition}")
        
        # Must have at least one comparison operator
        operators = [
            "equals", "not_equals", "contains", "not_contains",
            "matches_pattern", "in", "not_in", "greater_than", "less_than"
        ]
        
        if not any(op in condition for op in operators):
            raise ValueError(f"Condition missing comparison operator: {condition}")


# Pre-built policy templates for common use cases
POLICY_TEMPLATES = {
    "require_approval_for_model": {
        "name": "Require Approval for Specific Model",
        "description": "Escalate requests to specific AI models for human approval",
        "when": {
            "field": "model",
            "equals": "{{MODEL_NAME}}"
        },
        "then": "escalate",
        "reason": "Model {{MODEL_NAME}} requires approval",
    },
    "block_pii": {
        "name": "Block Personally Identifiable Information",
        "description": "Block requests containing PII patterns",
        "when": {
            "or": [
                {"field": "prompt", "matches_pattern": "\\d{3}-\\d{2}-\\d{4}"},  # SSN
                {"field": "prompt", "contains": "credit card"},
                {"field": "prompt", "contains": "social security"},
            ]
        },
        "then": "block",
        "reason": "PII detected in request",
    },
    "high_risk_escalation": {
        "name": "High Risk Escalation",
        "description": "Escalate high and critical risk agents",
        "when": {
            "field": "agent.risk_level",
            "in": ["high", "critical"]
        },
        "then": "escalate",
        "reason": "High-risk agent requires approval",
    },
    "business_hours_only": {
        "name": "Business Hours Only",
        "description": "Block execution outside business hours",
        "when": {
            "or": [
                {"field": "context.hour", "less_than": 9},
                {"field": "context.hour", "greater_than": 17}
            ]
        },
        "then": "block",
        "reason": "Execution only allowed during business hours (9-17)",
    },
    "cost_threshold": {
        "name": "Cost Threshold Control",
        "description": "Escalate requests exceeding cost threshold",
        "when": {
            "field": "context.estimated_cost",
            "greater_than": 100
        },
        "then": "escalate",
        "reason": "Estimated cost exceeds approval threshold ($100)",
    },
}


def get_policy_template(template_name: str, **kwargs) -> Dict[str, Any]:
    """
    Get a policy template with variable substitution.
    
    Args:
        template_name: Name of template
        **kwargs: Variables to substitute (e.g., MODEL_NAME="gpt-4")
        
    Returns:
        Policy specification with substituted values
        
    Example:
        policy = get_policy_template("require_approval_for_model", MODEL_NAME="gpt-4")
    """
    if template_name not in POLICY_TEMPLATES:
        available = ", ".join(POLICY_TEMPLATES.keys())
        raise ValueError(f"Unknown template: {template_name}. Available: {available}")
    
    import copy
    import json
    
    template = copy.deepcopy(POLICY_TEMPLATES[template_name])
    
    # Convert to JSON string, substitute, and parse back
    template_str = json.dumps(template)
    for key, value in kwargs.items():
        template_str = template_str.replace(f"{{{{{key}}}}}", str(value))
    
    return json.loads(template_str)
