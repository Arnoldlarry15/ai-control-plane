"""
Policy Evaluator: Returns allow, block, or escalate.

This must stay dumb and deterministic. No ML. No guessing.

Just rule evaluation. Fast and predictable.
"""

import logging
import re
from typing import Dict, Any, List, Optional

from policy.schemas import Policy, PolicyRule
from policy.parser import PolicyParser

logger = logging.getLogger(__name__)


class PolicyEvaluator:
    """
    Policy evaluator for AI execution requests.
    
    Evaluates policies deterministically. No ML. No guessing.
    
    First match wins. Evaluation stops at first block or escalate.
    """
    
    def __init__(self):
        self.parser = PolicyParser()
        self._policies: Dict[str, Policy] = {}
        
        # Load built-in policies
        self._load_builtin_policies()
        
        logger.info(f"Policy evaluator initialized with {len(self._policies)} policies")
    
    def evaluate(
        self,
        agent: Dict[str, Any],
        prompt: str,
        context: Dict[str, Any],
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate policies for an execution request.
        
        Args:
            agent: Agent configuration
            prompt: User prompt/input
            context: Execution context
            user: User identifier
        
        Returns:
            Policy decision: {action: allow/block/escalate, reason: str, policy_id: str}
        """
        # Get applicable policies
        policy_ids = agent.get("policies", [])
        
        if not policy_ids:
            # No policies: allow by default
            return {"action": "allow", "reason": "No policies configured"}
        
        # Evaluate each policy
        for policy_id in policy_ids:
            policy = self._policies.get(policy_id)
            if not policy or not policy.enabled:
                continue
            
            # Evaluate policy
            result = self._evaluate_policy(policy, prompt, context, user)
            
            if result["action"] != "allow":
                # First block or escalate wins
                result["policy_id"] = policy_id
                return result
        
        # All policies passed
        return {"action": "allow", "reason": "All policies passed"}
    
    def _evaluate_policy(
        self,
        policy: Policy,
        prompt: str,
        context: Dict[str, Any],
        user: Optional[str],
    ) -> Dict[str, Any]:
        """
        Evaluate a single policy.
        
        Args:
            policy: Policy to evaluate
            prompt: User prompt
            context: Execution context
            user: User identifier
        
        Returns:
            Policy decision
        """
        for rule in policy.rules:
            if self._evaluate_rule(rule, prompt, context, user):
                # Rule matched
                return {
                    "action": rule.action,
                    "reason": rule.reason or f"Policy {policy.id} triggered",
                }
        
        # No rules matched
        return {"action": "allow", "reason": f"Policy {policy.id} passed"}
    
    def _evaluate_rule(
        self,
        rule: PolicyRule,
        prompt: str,
        context: Dict[str, Any],
        user: Optional[str],
    ) -> bool:
        """
        Evaluate a single policy rule.
        
        Args:
            rule: Policy rule
            prompt: User prompt
            context: Execution context
            user: User identifier
        
        Returns:
            True if rule matches
        """
        condition = rule.condition
        
        # Always condition
        if condition.always:
            return True
        
        # Text contains (exact substring match)
        if condition.input_contains:
            if condition.input_contains.lower() in prompt.lower():
                return True
        
        # Text contains any (OR match)
        if condition.input_contains_any:
            for phrase in condition.input_contains_any:
                if phrase.lower() in prompt.lower():
                    return True
        
        # Regex pattern match
        if condition.input_matches_pattern:
            pattern = re.compile(condition.input_matches_pattern, re.IGNORECASE)
            if pattern.search(prompt):
                return True
        
        return False
    
    def register_policy(self, policy: Policy):
        """
        Register a policy with the evaluator.
        
        Args:
            policy: Policy to register
        """
        self._policies[policy.id] = policy
        logger.info(f"Policy registered: {policy.id}")
    
    def list_policies(self) -> List[Dict[str, Any]]:
        """List all registered policies."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "enabled": p.enabled,
                "rules": len(p.rules),
            }
            for p in self._policies.values()
        ]
    
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy by ID."""
        policy = self._policies.get(policy_id)
        if policy:
            return policy.model_dump()
        return None
    
    def _load_builtin_policies(self):
        """Load built-in policies."""
        # Built-in: no-pii (basic PII detection)
        no_pii_yaml = """
policy:
  id: "no-pii"
  version: "1.0"
  name: "Block PII in Input"
  description: "Detects and blocks common PII patterns"
  rules:
    - condition:
        input_matches_pattern: "\\\\d{3}-\\\\d{2}-\\\\d{4}"
      action: block
      reason: "SSN pattern detected"
    
    - condition:
        input_contains_any:
          - "social security"
          - "ssn"
          - "credit card"
          - "passport number"
      action: block
      reason: "PII keyword detected"
"""
        
        # Built-in: allow-all
        allow_all_yaml = """
policy:
  id: "allow-all"
  version: "1.0"
  name: "Allow All"
  description: "Permissive policy for testing"
  rules:
    - condition:
        always: true
      action: allow
"""
        
        # Built-in: block-all (emergency)
        block_all_yaml = """
policy:
  id: "block-all"
  version: "1.0"
  name: "Block All"
  description: "Emergency lockdown policy"
  rules:
    - condition:
        always: true
      action: block
      reason: "Emergency lockdown active"
"""
        
        # Load policies
        try:
            self.register_policy(self.parser.parse_yaml(no_pii_yaml))
            self.register_policy(self.parser.parse_yaml(allow_all_yaml))
            self.register_policy(self.parser.parse_yaml(block_all_yaml))
            
            # Disable block-all by default
            self._policies["block-all"].enabled = False
            
            logger.info("Built-in policies loaded")
        except Exception as e:
            logger.error(f"Error loading built-in policies: {e}")
