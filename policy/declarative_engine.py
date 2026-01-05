"""
Enhanced Declarative Policy Engine v1

Supports YAML/JSON policy specs with if/then logic.
No Python code required - pure configuration.

Example:
    if:
      model: gpt-4
      risk_score: >0.7
    then:
      require_approval: true
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
import re


class PolicyAction(str, Enum):
    """Policy action types."""
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"
    REDACT = "redact"
    WARN = "warn"
    REQUIRE_APPROVAL = "require_approval"


class DeclarativePolicyEngine:
    """
    Declarative policy engine - evaluate policies without code.
    
    Supports:
    - Field-based conditions (field: value)
    - Comparison operators (>, <, >=, <=, ==, !=)
    - Logical operators (and, or, not)
    - Pattern matching (contains, matches)
    - List operations (in, not_in)
    """
    
    def __init__(self):
        self.policies: List[Dict[str, Any]] = []
    
    def load_policy(self, policy_spec: Dict[str, Any]) -> None:
        """
        Load a policy from declarative spec.
        
        Args:
            policy_spec: Policy specification dict
        """
        self.policies.append(policy_spec)
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate all policies against context.
        
        Args:
            context: Execution context with fields to evaluate
            
        Returns:
            Decision dict with action and reason
        """
        results = []
        
        for policy in self.policies:
            if not policy.get('enabled', True):
                continue
            
            # Evaluate condition
            condition_met = self._evaluate_condition(
                policy.get('if', policy.get('when', {})),
                context
            )
            
            if condition_met:
                action = self._extract_action(policy.get('then', {}))
                results.append({
                    'policy_id': policy.get('id', policy.get('name', 'unknown')),
                    'policy_name': policy.get('name', 'Unknown Policy'),
                    'action': action,
                    'reason': policy.get('reason', 'Policy matched'),
                    'matched': True,
                })
        
        # Determine final action (most restrictive wins)
        return self._resolve_actions(results)
    
    def _evaluate_condition(self, condition: Union[Dict, List, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition against context.
        
        Supports:
        - Simple field matching: {field: value}
        - Comparison: {field: ">0.7", field: ">=100"}
        - Logical operators: {and: [...], or: [...], not: {...}}
        - Pattern matching: {field: "contains:text"}
        """
        if not condition:
            return True
        
        # Handle logical operators
        if isinstance(condition, dict):
            # AND operator (default for multiple fields)
            if 'and' in condition:
                return all(
                    self._evaluate_condition(c, context)
                    for c in condition['and']
                )
            
            # OR operator
            if 'or' in condition:
                return any(
                    self._evaluate_condition(c, context)
                    for c in condition['or']
                )
            
            # NOT operator
            if 'not' in condition:
                return not self._evaluate_condition(condition['not'], context)
            
            # Field-based conditions
            for field, expected in condition.items():
                if not self._evaluate_field(field, expected, context):
                    return False
            
            return True
        
        return False
    
    def _evaluate_field(self, field: str, expected: Any, context: Dict[str, Any]) -> bool:
        """Evaluate a single field condition."""
        # Get field value from context (supports nested fields with dot notation)
        value = self._get_nested_value(context, field)
        
        if value is None:
            return False
        
        # Handle string-based operators
        if isinstance(expected, str):
            # Comparison operators (check compound operators first)
            if expected.startswith('>='):
                threshold = float(expected[2:].strip())
                return float(value) >= threshold
            
            if expected.startswith('<='):
                threshold = float(expected[2:].strip())
                return float(value) <= threshold
            
            if expected.startswith('>'):
                threshold = float(expected[1:].strip())
                return float(value) > threshold
            
            if expected.startswith('<'):
                threshold = float(expected[1:].strip())
                return float(value) < threshold
            
            # Pattern matching
            if expected.startswith('contains:'):
                pattern = expected[9:]
                return pattern.lower() in str(value).lower()
            
            if expected.startswith('matches:'):
                pattern = expected[8:]
                return bool(re.search(pattern, str(value)))
            
            # Exact match
            return str(value).lower() == expected.lower()
        
        # List operations
        if isinstance(expected, list):
            return value in expected
        
        # Direct equality
        return value == expected
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """Get nested value from dict using dot notation."""
        parts = path.split('.')
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _extract_action(self, then_clause: Union[str, Dict[str, Any]]) -> str:
        """Extract action from then clause."""
        if isinstance(then_clause, str):
            return then_clause
        
        if isinstance(then_clause, dict):
            # Check for explicit actions
            if 'action' in then_clause:
                return then_clause['action']
            
            # Check for boolean flags
            if then_clause.get('require_approval') is True:
                return PolicyAction.REQUIRE_APPROVAL.value
            
            if then_clause.get('block') is True:
                return PolicyAction.BLOCK.value
            
            if then_clause.get('allow') is True:
                return PolicyAction.ALLOW.value
        
        return PolicyAction.ALLOW.value
    
    def _resolve_actions(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve multiple policy results into final decision.
        
        Priority (most restrictive first):
        1. block
        2. require_approval / escalate
        3. redact
        4. warn
        5. allow
        """
        if not results:
            return {
                'action': 'allow',
                'reason': 'No policies matched',
                'matched_policies': []
            }
        
        # Priority order
        action_priority = {
            'block': 1,
            'require_approval': 2,
            'escalate': 2,
            'redact': 3,
            'warn': 4,
            'allow': 5,
        }
        
        # Sort by priority (lower number = higher priority)
        sorted_results = sorted(
            results,
            key=lambda r: action_priority.get(r['action'], 999)
        )
        
        # Return highest priority action
        top_result = sorted_results[0]
        
        return {
            'action': top_result['action'],
            'reason': top_result['reason'],
            'policy_id': top_result['policy_id'],
            'policy_name': top_result['policy_name'],
            'matched_policies': [r['policy_id'] for r in results],
            'all_results': results,
        }


def create_policy_from_yaml_style(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a policy from YAML-style specification.
    
    Example:
        policy = create_policy_from_yaml_style({
            "name": "High Risk Approval",
            "if": {
                "model": "gpt-4",
                "risk_score": ">0.7"
            },
            "then": {
                "require_approval": True
            },
            "reason": "High-risk model with elevated risk score"
        })
    """
    return {
        'id': spec.get('id', spec.get('name', 'policy')),
        'name': spec.get('name', 'Unnamed Policy'),
        'if': spec.get('if', spec.get('when', {})),
        'then': spec.get('then', 'allow'),
        'reason': spec.get('reason', 'Policy matched'),
        'enabled': spec.get('enabled', True),
        'description': spec.get('description', ''),
        'priority': spec.get('priority', 100),
    }


# Example policies
EXAMPLE_POLICIES = {
    'high_risk_approval': {
        'name': 'High Risk Approval Required',
        'if': {
            'model': 'gpt-4',
            'risk_score': '>0.7'
        },
        'then': {
            'require_approval': True
        },
        'reason': 'High-risk model with elevated risk score requires approval'
    },
    
    'cost_control': {
        'name': 'Cost Control',
        'if': {
            'or': [
                {'estimated_tokens': '>10000'},
                {'estimated_cost': '>100'}
            ]
        },
        'then': {
            'require_approval': True
        },
        'reason': 'High cost operation requires approval'
    },
    
    'pii_blocking': {
        'name': 'Block PII',
        'if': {
            'prompt': 'contains:SSN'
        },
        'then': 'block',
        'reason': 'PII detected in prompt'
    },
    
    'production_safety': {
        'name': 'Production Safety',
        'if': {
            'and': [
                {'environment': 'prod'},
                {'risk_level': ['high', 'critical']}
            ]
        },
        'then': 'escalate',
        'reason': 'High-risk operation in production requires escalation'
    }
}
