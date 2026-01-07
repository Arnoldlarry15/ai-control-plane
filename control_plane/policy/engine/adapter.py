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
Integration Adapter - Bridge between new policy engine and existing gateway.

This adapter allows the new deterministic policy engine to work alongside
the existing policy evaluator, providing a migration path.
"""

import os
import logging
from typing import Dict, Any, Optional

from control_plane.policy.engine.evaluator import evaluate_policies
from control_plane.policy.engine.loader import load_policies_from_directory
from control_plane.policy.schemas.context import RequestContext
from control_plane.policy.schemas.decision import DecisionType

logger = logging.getLogger(__name__)


class PolicyEngineAdapter:
    """
    Adapter to integrate the new deterministic policy engine with the existing gateway.
    
    This class:
    1. Loads policies from configuration
    2. Converts gateway requests to RequestContext
    3. Evaluates using the deterministic engine
    4. Converts decisions back to gateway format
    """
    
    def __init__(self, policies_directory: Optional[str] = None):
        """
        Initialize the adapter.
        
        Args:
            policies_directory: Directory containing policy YAML/JSON files.
                              If None, uses environment variable or default.
        """
        if policies_directory is None:
            policies_directory = os.getenv(
                "POLICY_ENGINE_DIR",
                "/etc/ai-control-plane/policies"
            )
        
        self.policies_directory = policies_directory
        self.policies = []
        self._load_policies()
    
    def _load_policies(self):
        """Load policies from directory."""
        try:
            if os.path.exists(self.policies_directory):
                self.policies = load_policies_from_directory(self.policies_directory)
                logger.info(f"Loaded {len(self.policies)} policies from {self.policies_directory}")
            else:
                logger.warning(f"Policies directory not found: {self.policies_directory}")
        except Exception as e:
            logger.error(f"Failed to load policies: {e}")
    
    def reload_policies(self):
        """Reload policies from directory (useful for runtime updates)."""
        self.policies = []
        self._load_policies()
    
    def evaluate(
        self,
        agent: Dict[str, Any],
        prompt: str,
        context: Dict[str, Any],
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a request using the deterministic policy engine.
        
        This method maintains compatibility with the existing PolicyEvaluator interface
        while using the new engine internally.
        
        Args:
            agent: Agent configuration dict with id, model, risk_level, etc.
            prompt: User prompt/input
            context: Execution context dict
            user: User identifier
            
        Returns:
            Policy decision dict with keys: action, reason, policy_id
            Compatible with existing gateway expectations.
        """
        # Convert to RequestContext
        request_context = self._build_request_context(agent, prompt, context, user)
        
        # Evaluate using deterministic engine
        decision = evaluate_policies(self.policies, request_context)
        
        # Convert to gateway format
        return self._convert_decision_to_gateway_format(decision)
    
    def _build_request_context(
        self,
        agent: Dict[str, Any],
        prompt: str,
        context: Dict[str, Any],
        user: Optional[str],
    ) -> RequestContext:
        """
        Build a RequestContext from gateway request data.
        
        Args:
            agent: Agent configuration
            prompt: User prompt
            context: Execution context
            user: User identifier
            
        Returns:
            RequestContext for policy evaluation
        """
        # Extract environment from context or use default
        environment = context.get("environment", os.getenv("ENVIRONMENT", "production"))
        
        # Extract tags from agent and context
        tags = []
        if "tags" in agent:
            tags.extend(agent["tags"])
        if "tags" in context:
            tags.extend(context["tags"])
        
        # Remove duplicates
        tags = list(set(tags))
        
        # Build metadata
        metadata = {}
        metadata.update(context.get("metadata", {}))
        metadata["model"] = agent.get("model", "unknown")
        metadata["risk_level"] = agent.get("risk_level", "medium")
        
        # Create context
        return RequestContext(
            actor_id=user or "anonymous",
            actor_role=context.get("role", "user"),
            resource_id=agent.get("id", "unknown"),
            resource_type="agent",
            environment=environment,
            intent=context.get("intent", "execution"),
            tags=tags,
            metadata=metadata
        )
    
    def _convert_decision_to_gateway_format(self, decision) -> Dict[str, Any]:
        """
        Convert PolicyDecision to gateway-compatible format.
        
        Maps:
        - ALLOW → allow
        - DENY → block
        - REVIEW → escalate
        
        Args:
            decision: PolicyDecision from engine
            
        Returns:
            Dict compatible with gateway expectations
        """
        action_mapping = {
            DecisionType.ALLOW: "allow",
            DecisionType.DENY: "block",
            DecisionType.REVIEW: "escalate",
        }
        
        return {
            "action": action_mapping[decision.decision],
            "reason": decision.reason,
            "policy_id": decision.matched_policies[0] if decision.matched_policies else None,
            "matched_policies": decision.matched_policies,
        }


# Convenience function for easy integration
def create_policy_engine_adapter(policies_directory: Optional[str] = None) -> PolicyEngineAdapter:
    """
    Create and return a policy engine adapter.
    
    Args:
        policies_directory: Directory containing policy files
        
    Returns:
        PolicyEngineAdapter instance
    """
    return PolicyEngineAdapter(policies_directory)
