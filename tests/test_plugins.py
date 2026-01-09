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
Tests for Plugin System

Tests plugin loader, registry, and various plugin types.
"""

import pytest
from typing import Dict, Any

from policy.plugins import (
    PolicyPlugin,
    PluginType,
    RiskScorerPlugin,
    RiskEnginePlugin,
    LifecycleHookPlugin,
    PolicyEvaluatorPlugin,
    PluginRegistry,
)
from policy.plugin_loader import PluginLoader


# Test plugin implementations

class TestRiskScorer(RiskScorerPlugin):
    @property
    def plugin_id(self) -> str:
        return "test-risk-scorer"
    
    @property
    def plugin_name(self) -> str:
        return "Test Risk Scorer"
    
    def calculate_risk_score(self, agent_id, prompt, context):
        return {
            "score": 50.0,
            "level": "medium",
            "factors": ["test"],
            "recommendations": []
        }


class TestRiskEngine(RiskEnginePlugin):
    @property
    def plugin_id(self) -> str:
        return "test-risk-engine"
    
    @property
    def plugin_name(self) -> str:
        return "Test Risk Engine"
    
    def assess_risk(self, agent_id, prompt, context):
        return {
            "risk_score": 75.0,
            "risk_level": "high",
            "risk_factors": ["external_api"],
            "threat_indicators": ["TEST"],
            "recommendations": ["Review"],
            "external_ref": "test-ref"
        }


class TestPolicyEvaluator(PolicyEvaluatorPlugin):
    @property
    def plugin_id(self) -> str:
        return "test-evaluator"
    
    @property
    def plugin_name(self) -> str:
        return "Test Evaluator"
    
    def evaluate_policy(self, agent, prompt, context):
        if "block" in prompt.lower():
            return {"action": "block", "reason": "Test block"}
        return {"action": "allow", "reason": "Test allow"}


class TestPreRequestHook(LifecycleHookPlugin):
    @property
    def plugin_id(self) -> str:
        return "test-pre-request"
    
    @property
    def plugin_name(self) -> str:
        return "Test Pre-Request Hook"
    
    @property
    def hook_stage(self) -> str:
        return "pre_request"
    
    def on_pre_request(self, context):
        context["enriched"] = True
        return {"status": "continue", "context": context}


class TestPostDecisionHook(LifecycleHookPlugin):
    @property
    def plugin_id(self) -> str:
        return "test-post-decision"
    
    @property
    def plugin_name(self) -> str:
        return "Test Post-Decision Hook"
    
    @property
    def hook_stage(self) -> str:
        return "post_decision"
    
    def on_post_decision(self, context):
        return {"status": "continue", "logged": True}


class TestIncidentHook(LifecycleHookPlugin):
    @property
    def plugin_id(self) -> str:
        return "test-incident"
    
    @property
    def plugin_name(self) -> str:
        return "Test Incident Hook"
    
    @property
    def hook_stage(self) -> str:
        return "on_incident"
    
    def on_incident(self, context):
        return {
            "status": "continue",
            "incident_id": "INC-TEST-001",
            "alerted": True
        }


# Tests

class TestPluginRegistry:
    """Test plugin registry functionality."""
    
    def test_register_plugin(self):
        """Test registering a plugin."""
        registry = PluginRegistry()
        plugin = TestRiskScorer()
        
        registry.register(plugin)
        
        retrieved = registry.get_plugin("test-risk-scorer")
        assert retrieved is not None
        assert retrieved.plugin_id == "test-risk-scorer"
    
    def test_get_plugins_by_type(self):
        """Test getting plugins by type."""
        registry = PluginRegistry()
        
        risk_scorer = TestRiskScorer()
        risk_engine = TestRiskEngine()
        
        registry.register(risk_scorer)
        registry.register(risk_engine)
        
        scorers = registry.get_plugins_by_type(PluginType.RISK_SCORER)
        engines = registry.get_plugins_by_type(PluginType.RISK_ENGINE)
        
        assert len(scorers) == 1
        assert len(engines) == 1
        assert scorers[0].plugin_id == "test-risk-scorer"
        assert engines[0].plugin_id == "test-risk-engine"
    
    def test_unregister_plugin(self):
        """Test unregistering a plugin."""
        registry = PluginRegistry()
        plugin = TestRiskScorer()
        
        registry.register(plugin)
        registry.unregister("test-risk-scorer")
        
        retrieved = registry.get_plugin("test-risk-scorer")
        assert retrieved is None
    
    def test_list_plugins(self):
        """Test listing all plugins."""
        registry = PluginRegistry()
        
        registry.register(TestRiskScorer())
        registry.register(TestRiskEngine())
        
        plugins = registry.list_plugins()
        assert len(plugins) == 2
        assert all("id" in p and "name" in p for p in plugins)
    
    def test_execute_hooks(self):
        """Test executing lifecycle hooks."""
        registry = PluginRegistry()
        
        hook = TestPreRequestHook()
        registry.register(hook)
        
        context = {"agent_id": "test"}
        results = registry.execute_hooks("pre_request", context)
        
        assert len(results) == 1
        assert results[0]["status"] == "success"
        assert "result" in results[0]


class TestPluginLoader:
    """Test plugin loader functionality."""
    
    def test_register_plugin(self):
        """Test registering a plugin directly."""
        loader = PluginLoader()
        plugin = TestRiskScorer()
        
        loader.register_plugin(plugin)
        
        retrieved = loader.registry.get_plugin("test-risk-scorer")
        assert retrieved is not None
    
    def test_get_loaded_plugins(self):
        """Test getting loaded plugins list."""
        loader = PluginLoader()
        
        loader.register_plugin(TestRiskScorer())
        loader.register_plugin(TestRiskEngine())
        
        plugins = loader.get_loaded_plugins()
        assert len(plugins) == 2
    
    def test_unload_plugin(self):
        """Test unloading a plugin."""
        loader = PluginLoader()
        plugin = TestRiskScorer()
        
        loader.register_plugin(plugin)
        loader.unload_plugin("test-risk-scorer")
        
        plugins = loader.get_loaded_plugins()
        assert len(plugins) == 0


class TestRiskScorerPlugin:
    """Test risk scorer plugin."""
    
    def test_calculate_risk_score(self):
        """Test risk score calculation."""
        plugin = TestRiskScorer()
        
        result = plugin.calculate_risk_score(
            agent_id="test-agent",
            prompt="test prompt",
            context={}
        )
        
        assert "score" in result
        assert "level" in result
        assert "factors" in result
        assert result["score"] == 50.0
        assert result["level"] == "medium"
    
    def test_execute(self):
        """Test execute method."""
        plugin = TestRiskScorer()
        
        context = {
            "agent_id": "test-agent",
            "prompt": "test prompt"
        }
        
        result = plugin.execute(context)
        assert "score" in result


class TestRiskEnginePlugin:
    """Test risk engine plugin."""
    
    def test_assess_risk(self):
        """Test risk assessment."""
        plugin = TestRiskEngine()
        
        result = plugin.assess_risk(
            agent_id="test-agent",
            prompt="test prompt",
            context={}
        )
        
        assert "risk_score" in result
        assert "risk_level" in result
        assert "risk_factors" in result
        assert "external_ref" in result
        assert result["risk_score"] == 75.0
        assert result["risk_level"] == "high"


class TestPolicyEvaluatorPlugin:
    """Test policy evaluator plugin."""
    
    def test_evaluate_allow(self):
        """Test evaluation allowing request."""
        plugin = TestPolicyEvaluator()
        
        result = plugin.evaluate_policy(
            agent={},
            prompt="test prompt",
            context={}
        )
        
        assert result["action"] == "allow"
        assert "reason" in result
    
    def test_evaluate_block(self):
        """Test evaluation blocking request."""
        plugin = TestPolicyEvaluator()
        
        result = plugin.evaluate_policy(
            agent={},
            prompt="please block this",
            context={}
        )
        
        assert result["action"] == "block"
        assert "reason" in result


class TestLifecycleHooks:
    """Test lifecycle hook plugins."""
    
    def test_pre_request_hook(self):
        """Test pre-request hook."""
        hook = TestPreRequestHook()
        
        context = {"agent_id": "test"}
        result = hook.execute(context)
        
        assert result["status"] == "continue"
        assert "context" in result
        assert result["context"]["enriched"] is True
    
    def test_post_decision_hook(self):
        """Test post-decision hook."""
        hook = TestPostDecisionHook()
        
        context = {
            "decision": {"action": "allow"},
            "agent_id": "test"
        }
        result = hook.execute(context)
        
        assert result["status"] == "continue"
        assert result["logged"] is True
    
    def test_incident_hook(self):
        """Test incident hook."""
        hook = TestIncidentHook()
        
        context = {
            "incident_type": "security",
            "severity": "high",
            "agent_id": "test"
        }
        result = hook.execute(context)
        
        assert result["status"] == "continue"
        assert "incident_id" in result
        assert result["alerted"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
