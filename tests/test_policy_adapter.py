"""
Tests for the Policy Engine Adapter.

These tests verify the adapter correctly bridges the new policy engine
with the existing gateway interface.
"""

import pytest
import tempfile
import os
import yaml

from control_plane.policy.engine.adapter import PolicyEngineAdapter


class TestPolicyEngineAdapter:
    """Test policy engine adapter functionality."""
    
    def test_adapter_initialization(self):
        """Test adapter initializes correctly."""
        adapter = PolicyEngineAdapter(policies_directory="/tmp/nonexistent")
        
        # Should initialize without error even if directory doesn't exist
        assert adapter is not None
        assert adapter.policies == []
    
    def test_adapter_loads_policies(self):
        """Test adapter loads policies from directory."""
        # Create temporary directory with policy files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test policy
            policy = {
                "id": "test_policy",
                "version": "1.0.0",
                "description": "Test policy",
                "scope": {},
                "conditions": {},
                "effect": "ALLOW",
                "priority": 1
            }
            
            policy_file = os.path.join(tmpdir, "test_policy.yaml")
            with open(policy_file, 'w') as f:
                yaml.dump(policy, f)
            
            # Initialize adapter
            adapter = PolicyEngineAdapter(policies_directory=tmpdir)
            
            # Should load the policy
            assert len(adapter.policies) == 1
            assert adapter.policies[0].id == "test_policy"
    
    def test_evaluate_gateway_format(self):
        """Test evaluate returns gateway-compatible format."""
        adapter = PolicyEngineAdapter(policies_directory="/tmp/nonexistent")
        
        # Create test data
        agent = {
            "id": "test_agent",
            "model": "gpt-4",
            "risk_level": "medium",
            "tags": []
        }
        
        # Evaluate (no policies, should ALLOW)
        decision = adapter.evaluate(
            agent=agent,
            prompt="Test prompt",
            context={},
            user="test_user"
        )
        
        # Check format
        assert "action" in decision
        assert "reason" in decision
        assert "policy_id" in decision
        assert decision["action"] == "allow"
    
    def test_evaluate_with_policy(self):
        """Test evaluation with actual policy."""
        # Create temporary directory with policy
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a PII blocking policy
            policy = {
                "id": "block_pii",
                "version": "1.0.0",
                "description": "Block PII in production",
                "scope": {
                    "environment": ["production"]
                },
                "conditions": {
                    "tags": ["pii"]
                },
                "effect": "DENY",
                "priority": 100
            }
            
            policy_file = os.path.join(tmpdir, "block_pii.yaml")
            with open(policy_file, 'w') as f:
                yaml.dump(policy, f)
            
            # Initialize adapter
            adapter = PolicyEngineAdapter(policies_directory=tmpdir)
            
            # Test with PII in production
            agent = {"id": "agent1", "tags": []}
            decision = adapter.evaluate(
                agent=agent,
                prompt="Process SSN",
                context={
                    "environment": "production",
                    "tags": ["pii"]
                },
                user="user1"
            )
            
            # Should block
            assert decision["action"] == "block"
            assert "block_pii" in decision["matched_policies"]
    
    def test_context_building(self):
        """Test RequestContext is built correctly from gateway data."""
        adapter = PolicyEngineAdapter(policies_directory="/tmp/nonexistent")
        
        # Create test data
        agent = {
            "id": "agent_123",
            "model": "gpt-4",
            "risk_level": "high",
            "tags": ["production"]
        }
        
        context = {
            "environment": "production",
            "role": "developer",
            "intent": "data_access",
            "tags": ["pii", "sensitive"],
            "metadata": {"department": "finance"}
        }
        
        # Build context
        request_context = adapter._build_request_context(
            agent=agent,
            prompt="Test",
            context=context,
            user="user_456"
        )
        
        # Verify mapping
        assert request_context.actor_id == "user_456"
        assert request_context.actor_role == "developer"
        assert request_context.resource_id == "agent_123"
        assert request_context.resource_type == "agent"
        assert request_context.environment == "production"
        assert request_context.intent == "data_access"
        
        # Check tags are combined
        assert "production" in request_context.tags
        assert "pii" in request_context.tags
        assert "sensitive" in request_context.tags
        
        # Check metadata
        assert request_context.metadata["department"] == "finance"
        assert request_context.metadata["model"] == "gpt-4"
        assert request_context.metadata["risk_level"] == "high"
    
    def test_decision_conversion(self):
        """Test decision conversion to gateway format."""
        from control_plane.policy.schemas.decision import PolicyDecision, DecisionType
        
        adapter = PolicyEngineAdapter(policies_directory="/tmp/nonexistent")
        
        # Test ALLOW conversion
        allow_decision = PolicyDecision(
            decision=DecisionType.ALLOW,
            matched_policies=["policy1"],
            reason="Test allow"
        )
        result = adapter._convert_decision_to_gateway_format(allow_decision)
        assert result["action"] == "allow"
        assert result["reason"] == "Test allow"
        
        # Test DENY conversion
        deny_decision = PolicyDecision(
            decision=DecisionType.DENY,
            matched_policies=["policy2"],
            reason="Test deny"
        )
        result = adapter._convert_decision_to_gateway_format(deny_decision)
        assert result["action"] == "block"
        assert result["policy_id"] == "policy2"
        
        # Test REVIEW conversion
        review_decision = PolicyDecision(
            decision=DecisionType.REVIEW,
            matched_policies=["policy3", "policy4"],
            reason="Test review"
        )
        result = adapter._convert_decision_to_gateway_format(review_decision)
        assert result["action"] == "escalate"
        assert result["matched_policies"] == ["policy3", "policy4"]
    
    def test_reload_policies(self):
        """Test policy reloading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Start with one policy
            policy1 = {
                "id": "policy1",
                "version": "1.0.0",
                "description": "First policy",
                "scope": {},
                "conditions": {},
                "effect": "ALLOW",
                "priority": 1
            }
            
            policy_file1 = os.path.join(tmpdir, "policy1.yaml")
            with open(policy_file1, 'w') as f:
                yaml.dump(policy1, f)
            
            # Initialize adapter
            adapter = PolicyEngineAdapter(policies_directory=tmpdir)
            assert len(adapter.policies) == 1
            
            # Add another policy
            policy2 = {
                "id": "policy2",
                "version": "1.0.0",
                "description": "Second policy",
                "scope": {},
                "conditions": {},
                "effect": "DENY",
                "priority": 2
            }
            
            policy_file2 = os.path.join(tmpdir, "policy2.yaml")
            with open(policy_file2, 'w') as f:
                yaml.dump(policy2, f)
            
            # Reload
            adapter.reload_policies()
            
            # Should have both policies now
            assert len(adapter.policies) == 2
            policy_ids = [p.id for p in adapter.policies]
            assert "policy1" in policy_ids
            assert "policy2" in policy_ids
    
    def test_evaluate_anonymous_user(self):
        """Test evaluation with no user specified."""
        adapter = PolicyEngineAdapter(policies_directory="/tmp/nonexistent")
        
        agent = {"id": "agent1", "tags": []}
        
        # Evaluate without user
        decision = adapter.evaluate(
            agent=agent,
            prompt="Test",
            context={},
            user=None
        )
        
        # Should use "anonymous"
        assert decision["action"] == "allow"
    
    def test_evaluate_default_environment(self):
        """Test default environment handling."""
        adapter = PolicyEngineAdapter(policies_directory="/tmp/nonexistent")
        
        agent = {"id": "agent1", "tags": []}
        
        # Context without environment
        decision = adapter.evaluate(
            agent=agent,
            prompt="Test",
            context={},  # No environment specified
            user="user1"
        )
        
        # Should work (defaults to production from env or "production")
        assert decision["action"] == "allow"


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def test_prod_pii_review_scenario(self):
        """Test: Production + PII → REVIEW"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create PII review policy
            policy = {
                "id": "prod_pii_review",
                "version": "1.0.0",
                "description": "PII in production requires review",
                "scope": {
                    "environment": ["production"]
                },
                "conditions": {
                    "tags": ["pii"]
                },
                "effect": "REVIEW",
                "priority": 100
            }
            
            with open(os.path.join(tmpdir, "policy.yaml"), 'w') as f:
                yaml.dump(policy, f)
            
            adapter = PolicyEngineAdapter(policies_directory=tmpdir)
            
            # Evaluate production + PII
            decision = adapter.evaluate(
                agent={"id": "agent1", "tags": []},
                prompt="Process customer data",
                context={
                    "environment": "production",
                    "tags": ["pii"]
                },
                user="user1"
            )
            
            assert decision["action"] == "escalate"
            assert "prod_pii_review" in decision["matched_policies"]
    
    def test_dev_pii_allow_scenario(self):
        """Test: Development + PII → ALLOW"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dev allow policy
            policy = {
                "id": "dev_allow",
                "version": "1.0.0",
                "description": "Dev environment allows PII",
                "scope": {
                    "environment": ["development", "dev"]
                },
                "conditions": {
                    "tags": ["pii"]
                },
                "effect": "ALLOW",
                "priority": 50
            }
            
            with open(os.path.join(tmpdir, "policy.yaml"), 'w') as f:
                yaml.dump(policy, f)
            
            adapter = PolicyEngineAdapter(policies_directory=tmpdir)
            
            # Evaluate dev + PII
            decision = adapter.evaluate(
                agent={"id": "agent1", "tags": []},
                prompt="Test with customer data",
                context={
                    "environment": "development",
                    "tags": ["pii"]
                },
                user="dev_user"
            )
            
            assert decision["action"] == "allow"
    
    def test_prod_banned_deny_scenario(self):
        """Test: Production + Banned → DENY"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create banned deny policy
            policy = {
                "id": "prod_banned",
                "version": "1.0.0",
                "description": "Banned content in production",
                "scope": {
                    "environment": ["production"]
                },
                "conditions": {
                    "tags": ["banned"]
                },
                "effect": "DENY",
                "priority": 200
            }
            
            with open(os.path.join(tmpdir, "policy.yaml"), 'w') as f:
                yaml.dump(policy, f)
            
            adapter = PolicyEngineAdapter(policies_directory=tmpdir)
            
            # Evaluate production + banned
            decision = adapter.evaluate(
                agent={"id": "agent1", "tags": []},
                prompt="Banned content",
                context={
                    "environment": "production",
                    "tags": ["banned"]
                },
                user="user1"
            )
            
            assert decision["action"] == "block"
            assert "prod_banned" in decision["matched_policies"]
