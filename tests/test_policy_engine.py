"""
Policy Engine Tests - Proof that governance is real.

These tests prove:
1. prod + pii → REVIEW
2. dev + pii → ALLOW
3. prod + banned_tag → DENY
4. Priority-based conflict resolution
5. Deterministic evaluation

Once these tests exist, governance claims become defensible.
"""

import pytest
from control_plane.policy.schemas.context import RequestContext
from control_plane.policy.schemas.decision import DecisionType, PolicyDecision
from control_plane.policy.schemas.policy_schema import PolicySchema
from control_plane.policy.engine.evaluator import evaluate_policies


class TestPolicyEngineBasics:
    """Test basic policy engine functionality."""
    
    def test_prod_pii_requires_review(self):
        """Test: prod + pii → REVIEW"""
        # Define policy
        policy = PolicySchema({
            "id": "prod_pii_requires_review",
            "version": "1.0.0",
            "description": "PII in production requires review",
            "scope": {
                "environment": ["production"],
                "resource_type": ["model", "agent"]
            },
            "conditions": {
                "tags": ["pii"]
            },
            "effect": "REVIEW",
            "priority": 100
        })
        
        # Create context: production + model + pii
        context = RequestContext(
            actor_id="user_123",
            actor_role="developer",
            resource_id="model_gpt4",
            resource_type="model",
            environment="production",
            intent="data_access",
            tags=["pii"],
            metadata={}
        )
        
        # Evaluate
        decision = evaluate_policies([policy], context)
        
        # Assert
        assert decision.decision == DecisionType.REVIEW
        assert "prod_pii_requires_review" in decision.matched_policies
        assert "review" in decision.reason.lower()
    
    def test_dev_pii_allows(self):
        """Test: dev + pii → ALLOW"""
        # Define policy
        policy = PolicySchema({
            "id": "dev_pii_allow",
            "version": "1.0.0",
            "description": "PII allowed in dev",
            "scope": {
                "environment": ["development", "dev"]
            },
            "conditions": {
                "tags": ["pii"]
            },
            "effect": "ALLOW",
            "priority": 50
        })
        
        # Create context: development + pii
        context = RequestContext(
            actor_id="dev_user",
            actor_role="developer",
            resource_id="test_model",
            resource_type="model",
            environment="development",
            intent="testing",
            tags=["pii"],
            metadata={}
        )
        
        # Evaluate
        decision = evaluate_policies([policy], context)
        
        # Assert
        assert decision.decision == DecisionType.ALLOW
        assert "dev_pii_allow" in decision.matched_policies
    
    def test_prod_banned_denies(self):
        """Test: prod + banned_tag → DENY"""
        # Define policy
        policy = PolicySchema({
            "id": "prod_banned_deny",
            "version": "1.0.0",
            "description": "Banned content denied in prod",
            "scope": {
                "environment": ["production"]
            },
            "conditions": {
                "tags": ["banned"]
            },
            "effect": "DENY",
            "priority": 200
        })
        
        # Create context: production + banned
        context = RequestContext(
            actor_id="user_456",
            actor_role="operator",
            resource_id="agent_xyz",
            resource_type="agent",
            environment="production",
            intent="generation",
            tags=["banned"],
            metadata={}
        )
        
        # Evaluate
        decision = evaluate_policies([policy], context)
        
        # Assert
        assert decision.decision == DecisionType.DENY
        assert "prod_banned_deny" in decision.matched_policies
        assert "denied" in decision.reason.lower()


class TestPolicyPriorityAndConflicts:
    """Test policy priority and conflict resolution."""
    
    def test_deny_takes_precedence_over_allow(self):
        """DENY should take precedence over ALLOW."""
        # Define two conflicting policies
        allow_policy = PolicySchema({
            "id": "allow_all",
            "version": "1.0.0",
            "description": "Allow everything",
            "scope": {},
            "conditions": {},
            "effect": "ALLOW",
            "priority": 50
        })
        
        deny_policy = PolicySchema({
            "id": "deny_banned",
            "version": "1.0.0",
            "description": "Deny banned tags",
            "scope": {},
            "conditions": {
                "tags": ["banned"]
            },
            "effect": "DENY",
            "priority": 100
        })
        
        # Context with banned tag
        context = RequestContext(
            actor_id="user_789",
            actor_role="user",
            resource_id="resource_1",
            resource_type="model",
            environment="production",
            intent="access",
            tags=["banned"],
            metadata={}
        )
        
        # Evaluate (deny_policy has higher priority)
        decision = evaluate_policies([allow_policy, deny_policy], context)
        
        # DENY should win
        assert decision.decision == DecisionType.DENY
        assert "deny_banned" in decision.matched_policies
    
    def test_review_takes_precedence_over_allow(self):
        """REVIEW should take precedence over ALLOW."""
        # Define policies
        allow_policy = PolicySchema({
            "id": "allow_dev",
            "version": "1.0.0",
            "description": "Allow dev environment",
            "scope": {
                "environment": ["development"]
            },
            "conditions": {},
            "effect": "ALLOW",
            "priority": 30
        })
        
        review_policy = PolicySchema({
            "id": "review_pii",
            "version": "1.0.0",
            "description": "Review PII access",
            "scope": {},
            "conditions": {
                "tags": ["pii"]
            },
            "effect": "REVIEW",
            "priority": 80
        })
        
        # Context: dev + pii
        context = RequestContext(
            actor_id="dev_user",
            actor_role="developer",
            resource_id="model_x",
            resource_type="model",
            environment="development",
            intent="testing",
            tags=["pii"],
            metadata={}
        )
        
        # Evaluate
        decision = evaluate_policies([allow_policy, review_policy], context)
        
        # REVIEW should win
        assert decision.decision == DecisionType.REVIEW
        assert "review_pii" in decision.matched_policies
    
    def test_higher_priority_evaluated_first(self):
        """Higher priority policies should be evaluated first."""
        # Two policies, both would match, different priorities
        low_priority = PolicySchema({
            "id": "low_review",
            "version": "1.0.0",
            "description": "Low priority review",
            "scope": {},
            "conditions": {},
            "effect": "REVIEW",
            "priority": 10
        })
        
        high_priority = PolicySchema({
            "id": "high_deny",
            "version": "1.0.0",
            "description": "High priority deny",
            "scope": {},
            "conditions": {},
            "effect": "DENY",
            "priority": 100
        })
        
        # Context that matches both
        context = RequestContext(
            actor_id="user_x",
            actor_role="user",
            resource_id="res_y",
            resource_type="model",
            environment="production",
            intent="access",
            tags=[],
            metadata={}
        )
        
        # Evaluate
        decision = evaluate_policies([low_priority, high_priority], context)
        
        # High priority DENY should win
        assert decision.decision == DecisionType.DENY
        assert "high_deny" in decision.matched_policies


class TestScopeMatching:
    """Test policy scope matching."""
    
    def test_empty_scope_matches_everything(self):
        """Empty scope should match all contexts."""
        policy = PolicySchema({
            "id": "global_policy",
            "version": "1.0.0",
            "description": "Applies to everything",
            "scope": {},
            "conditions": {},
            "effect": "ALLOW",
            "priority": 1
        })
        
        # Various contexts
        contexts = [
            RequestContext("user1", "admin", "res1", "model", "production", "access", [], {}),
            RequestContext("user2", "dev", "res2", "agent", "development", "test", [], {}),
            RequestContext("user3", "operator", "res3", "data", "staging", "read", [], {}),
        ]
        
        for ctx in contexts:
            decision = evaluate_policies([policy], ctx)
            assert decision.decision == DecisionType.ALLOW
            assert "global_policy" in decision.matched_policies
    
    def test_environment_scope_filtering(self):
        """Environment scope should filter correctly."""
        policy = PolicySchema({
            "id": "prod_only",
            "version": "1.0.0",
            "description": "Production only",
            "scope": {
                "environment": ["production"]
            },
            "conditions": {},
            "effect": "REVIEW",
            "priority": 1
        })
        
        # Production context - should match
        prod_ctx = RequestContext(
            "user", "dev", "res", "model", "production", "access", [], {}
        )
        decision = evaluate_policies([policy], prod_ctx)
        assert decision.decision == DecisionType.REVIEW
        
        # Development context - should not match
        dev_ctx = RequestContext(
            "user", "dev", "res", "model", "development", "access", [], {}
        )
        decision = evaluate_policies([policy], dev_ctx)
        assert decision.decision == DecisionType.ALLOW  # No policy matched
        assert len(decision.matched_policies) == 0
    
    def test_resource_type_scope_filtering(self):
        """Resource type scope should filter correctly."""
        policy = PolicySchema({
            "id": "model_only",
            "version": "1.0.0",
            "description": "Models only",
            "scope": {
                "resource_type": ["model"]
            },
            "conditions": {},
            "effect": "REVIEW",
            "priority": 1
        })
        
        # Model resource - should match
        model_ctx = RequestContext(
            "user", "dev", "model_123", "model", "production", "access", [], {}
        )
        decision = evaluate_policies([policy], model_ctx)
        assert decision.decision == DecisionType.REVIEW
        
        # Agent resource - should not match
        agent_ctx = RequestContext(
            "user", "dev", "agent_456", "agent", "production", "access", [], {}
        )
        decision = evaluate_policies([policy], agent_ctx)
        assert decision.decision == DecisionType.ALLOW
        assert len(decision.matched_policies) == 0


class TestConditionMatching:
    """Test policy condition matching."""
    
    def test_tag_condition_matching(self):
        """Tag conditions should match correctly."""
        policy = PolicySchema({
            "id": "pii_policy",
            "version": "1.0.0",
            "description": "PII handling",
            "scope": {},
            "conditions": {
                "tags": ["pii", "sensitive"]
            },
            "effect": "REVIEW",
            "priority": 1
        })
        
        # Context with pii tag - should match
        ctx_with_pii = RequestContext(
            "user", "dev", "res", "model", "prod", "access",
            tags=["pii", "data"],
            metadata={}
        )
        decision = evaluate_policies([policy], ctx_with_pii)
        assert decision.decision == DecisionType.REVIEW
        
        # Context with sensitive tag - should match
        ctx_with_sensitive = RequestContext(
            "user", "dev", "res", "model", "prod", "access",
            tags=["sensitive"],
            metadata={}
        )
        decision = evaluate_policies([policy], ctx_with_sensitive)
        assert decision.decision == DecisionType.REVIEW
        
        # Context without matching tags - should not match
        ctx_no_match = RequestContext(
            "user", "dev", "res", "model", "prod", "access",
            tags=["public"],
            metadata={}
        )
        decision = evaluate_policies([policy], ctx_no_match)
        assert decision.decision == DecisionType.ALLOW
    
    def test_metadata_condition_matching(self):
        """Metadata conditions should match correctly."""
        policy = PolicySchema({
            "id": "metadata_policy",
            "version": "1.0.0",
            "description": "Metadata-based policy",
            "scope": {},
            "conditions": {
                "metadata": {
                    "classification": "secret",
                    "department": "finance"
                }
            },
            "effect": "DENY",
            "priority": 1
        })
        
        # Matching metadata - should match
        ctx_match = RequestContext(
            "user", "dev", "res", "model", "prod", "access",
            tags=[],
            metadata={"classification": "secret", "department": "finance", "extra": "value"}
        )
        decision = evaluate_policies([policy], ctx_match)
        assert decision.decision == DecisionType.DENY
        
        # Non-matching metadata - should not match
        ctx_no_match = RequestContext(
            "user", "dev", "res", "model", "prod", "access",
            tags=[],
            metadata={"classification": "public", "department": "finance"}
        )
        decision = evaluate_policies([policy], ctx_no_match)
        assert decision.decision == DecisionType.ALLOW


class TestDeterminism:
    """Test that policy evaluation is deterministic."""
    
    def test_same_input_produces_same_output(self):
        """Same input should always produce same output."""
        policy = PolicySchema({
            "id": "test_policy",
            "version": "1.0.0",
            "description": "Test determinism",
            "scope": {},
            "conditions": {
                "tags": ["test"]
            },
            "effect": "REVIEW",
            "priority": 1
        })
        
        context = RequestContext(
            "user", "dev", "res", "model", "prod", "access",
            tags=["test"],
            metadata={}
        )
        
        # Evaluate multiple times
        results = [
            evaluate_policies([policy], context)
            for _ in range(10)
        ]
        
        # All results should be identical
        for result in results:
            assert result.decision == DecisionType.REVIEW
            assert result.matched_policies == ["test_policy"]
            assert "test_policy" in result.reason.lower()
    
    def test_no_side_effects(self):
        """Evaluation should not modify inputs."""
        policy = PolicySchema({
            "id": "test",
            "version": "1.0.0",
            "description": "Test",
            "scope": {},
            "conditions": {},
            "effect": "ALLOW",
            "priority": 1
        })
        
        context = RequestContext(
            "user", "role", "res", "type", "env", "intent",
            tags=["tag1"],
            metadata={"key": "value"}
        )
        
        # Store original values
        original_tags = context.tags.copy()
        original_metadata = context.metadata.copy()
        
        # Evaluate
        evaluate_policies([policy], context)
        
        # Context should be unchanged (it's frozen)
        assert context.tags == original_tags
        assert context.metadata == original_metadata


class TestNoMatchingPolicies:
    """Test behavior when no policies match."""
    
    def test_no_policies_allows(self):
        """No policies should result in ALLOW."""
        context = RequestContext(
            "user", "role", "res", "type", "env", "intent", [], {}
        )
        
        decision = evaluate_policies([], context)
        
        assert decision.decision == DecisionType.ALLOW
        assert len(decision.matched_policies) == 0
        assert "no blocking" in decision.reason.lower()
    
    def test_policies_dont_match_allows(self):
        """Policies that don't match should result in ALLOW."""
        # Policy that won't match
        policy = PolicySchema({
            "id": "wont_match",
            "version": "1.0.0",
            "description": "Won't match",
            "scope": {
                "environment": ["staging"]
            },
            "conditions": {},
            "effect": "DENY",
            "priority": 1
        })
        
        # Context with different environment
        context = RequestContext(
            "user", "role", "res", "type", "production", "intent", [], {}
        )
        
        decision = evaluate_policies([policy], context)
        
        assert decision.decision == DecisionType.ALLOW
        assert len(decision.matched_policies) == 0
