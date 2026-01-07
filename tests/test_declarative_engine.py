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
Tests for declarative policy engine.

Tests the if/then policy syntax without requiring Python code.
"""

import pytest
from policy.declarative_engine import (
    DeclarativePolicyEngine,
    create_policy_from_yaml_style,
    EXAMPLE_POLICIES,
)


class TestDeclarativePolicyEngine:
    """Test declarative policy engine."""
    
    def test_simple_field_match(self):
        """Test simple field matching."""
        engine = DeclarativePolicyEngine()
        engine.load_policy({
            'name': 'GPT-4 Policy',
            'if': {'model': 'gpt-4'},
            'then': 'escalate',
            'reason': 'GPT-4 requires approval'
        })
        
        result = engine.evaluate({'model': 'gpt-4'})
        
        assert result['action'] == 'escalate'
        assert 'GPT-4 Policy' in result['policy_name']
    
    def test_comparison_operators(self):
        """Test comparison operators."""
        engine = DeclarativePolicyEngine()
        
        # Greater than
        engine.load_policy({
            'name': 'High Risk',
            'if': {'risk_score': '>0.7'},
            'then': 'block',
            'reason': 'Risk too high'
        })
        
        result = engine.evaluate({'risk_score': 0.8})
        assert result['action'] == 'block'
        
        result = engine.evaluate({'risk_score': 0.5})
        assert result['action'] == 'allow'
    
    def test_greater_than_equal(self):
        """Test >= operator."""
        engine = DeclarativePolicyEngine()
        engine.load_policy({
            'name': 'Cost Threshold',
            'if': {'cost': '>=100'},
            'then': 'require_approval',
            'reason': 'High cost'
        })
        
        result = engine.evaluate({'cost': 100})
        assert result['action'] == 'require_approval'
        
        result = engine.evaluate({'cost': 150})
        assert result['action'] == 'require_approval'
        
        result = engine.evaluate({'cost': 50})
        assert result['action'] == 'allow'
    
    def test_and_operator(self):
        """Test AND logical operator."""
        engine = DeclarativePolicyEngine()
        engine.load_policy({
            'name': 'Combined Policy',
            'if': {
                'and': [
                    {'model': 'gpt-4'},
                    {'risk_score': '>0.7'}
                ]
            },
            'then': 'escalate',
            'reason': 'Both conditions met'
        })
        
        # Both true
        result = engine.evaluate({'model': 'gpt-4', 'risk_score': 0.8})
        assert result['action'] == 'escalate'
        
        # Only one true
        result = engine.evaluate({'model': 'gpt-4', 'risk_score': 0.5})
        assert result['action'] == 'allow'
    
    def test_or_operator(self):
        """Test OR logical operator."""
        engine = DeclarativePolicyEngine()
        engine.load_policy({
            'name': 'Either Condition',
            'if': {
                'or': [
                    {'environment': 'prod'},
                    {'risk_level': 'critical'}
                ]
            },
            'then': 'escalate',
            'reason': 'Production or critical'
        })
        
        # First true
        result = engine.evaluate({'environment': 'prod', 'risk_level': 'low'})
        assert result['action'] == 'escalate'
        
        # Second true
        result = engine.evaluate({'environment': 'dev', 'risk_level': 'critical'})
        assert result['action'] == 'escalate'
        
        # Both false
        result = engine.evaluate({'environment': 'dev', 'risk_level': 'low'})
        assert result['action'] == 'allow'
    
    def test_not_operator(self):
        """Test NOT logical operator."""
        engine = DeclarativePolicyEngine()
        engine.load_policy({
            'name': 'Not Production',
            'if': {
                'not': {'environment': 'prod'}
            },
            'then': 'allow',
            'reason': 'Non-production allowed'
        })
        
        result = engine.evaluate({'environment': 'dev'})
        assert result['action'] == 'allow'
    
    def test_list_matching(self):
        """Test matching against a list of values."""
        engine = DeclarativePolicyEngine()
        engine.load_policy({
            'name': 'Risk Levels',
            'if': {'risk_level': ['high', 'critical']},
            'then': 'escalate',
            'reason': 'High or critical risk'
        })
        
        result = engine.evaluate({'risk_level': 'high'})
        assert result['action'] == 'escalate'
        
        result = engine.evaluate({'risk_level': 'critical'})
        assert result['action'] == 'escalate'
        
        result = engine.evaluate({'risk_level': 'low'})
        assert result['action'] == 'allow'
    
    def test_contains_operator(self):
        """Test contains pattern matching."""
        engine = DeclarativePolicyEngine()
        engine.load_policy({
            'name': 'PII Detection',
            'if': {'prompt': 'contains:SSN'},
            'then': 'block',
            'reason': 'SSN detected'
        })
        
        result = engine.evaluate({'prompt': 'My SSN is 123-45-6789'})
        assert result['action'] == 'block'
        
        result = engine.evaluate({'prompt': 'What is your business?'})
        assert result['action'] == 'allow'
    
    def test_nested_fields(self):
        """Test nested field access with dot notation."""
        engine = DeclarativePolicyEngine()
        engine.load_policy({
            'name': 'User Role',
            'if': {'user.role': 'admin'},
            'then': 'allow',
            'reason': 'Admin access'
        })
        
        result = engine.evaluate({'user': {'role': 'admin'}})
        assert result['action'] == 'allow'
    
    def test_multiple_policies_resolution(self):
        """Test resolving multiple matching policies."""
        engine = DeclarativePolicyEngine()
        
        # Add multiple policies
        engine.load_policy({
            'name': 'Allow Policy',
            'if': {'model': 'gpt-4'},
            'then': 'allow',
            'reason': 'Model allowed'
        })
        
        engine.load_policy({
            'name': 'Block Policy',
            'if': {'model': 'gpt-4'},
            'then': 'block',
            'reason': 'Model blocked'
        })
        
        result = engine.evaluate({'model': 'gpt-4'})
        
        # Block should win (most restrictive)
        assert result['action'] == 'block'
        assert len(result['matched_policies']) == 2
    
    def test_require_approval_flag(self):
        """Test require_approval flag in then clause."""
        engine = DeclarativePolicyEngine()
        engine.load_policy({
            'name': 'Approval Required',
            'if': {'cost': '>100'},
            'then': {'require_approval': True},
            'reason': 'High cost'
        })
        
        result = engine.evaluate({'cost': 150})
        assert result['action'] == 'require_approval'
    
    def test_disabled_policy(self):
        """Test that disabled policies are not evaluated."""
        engine = DeclarativePolicyEngine()
        engine.load_policy({
            'name': 'Disabled Policy',
            'if': {'model': 'gpt-4'},
            'then': 'block',
            'reason': 'Blocked',
            'enabled': False
        })
        
        result = engine.evaluate({'model': 'gpt-4'})
        assert result['action'] == 'allow'


class TestPolicyCreation:
    """Test policy creation helpers."""
    
    def test_create_from_yaml_style(self):
        """Test creating policy from YAML-style spec."""
        spec = {
            'name': 'Test Policy',
            'if': {'model': 'gpt-4'},
            'then': 'escalate',
            'reason': 'Test reason'
        }
        
        policy = create_policy_from_yaml_style(spec)
        
        assert policy['name'] == 'Test Policy'
        assert policy['if'] == {'model': 'gpt-4'}
        assert policy['then'] == 'escalate'
        assert policy['reason'] == 'Test reason'
    
    def test_example_policies(self):
        """Test that example policies are valid."""
        engine = DeclarativePolicyEngine()
        
        # Load high risk approval example
        policy = create_policy_from_yaml_style(EXAMPLE_POLICIES['high_risk_approval'])
        engine.load_policy(policy)
        
        # Should trigger
        result = engine.evaluate({'model': 'gpt-4', 'risk_score': 0.8})
        assert result['action'] == 'require_approval'
        
        # Should not trigger
        result = engine.evaluate({'model': 'gpt-3.5', 'risk_score': 0.5})
        assert result['action'] == 'allow'


class TestRealWorldScenarios:
    """Test real-world policy scenarios."""
    
    def test_production_high_risk_scenario(self):
        """Test production + high risk scenario."""
        engine = DeclarativePolicyEngine()
        
        engine.load_policy(
            create_policy_from_yaml_style(EXAMPLE_POLICIES['production_safety'])
        )
        
        # Production + high risk = escalate
        result = engine.evaluate({
            'environment': 'prod',
            'risk_level': 'high'
        })
        assert result['action'] == 'escalate'
        
        # Dev + high risk = allow (policy doesn't match)
        result = engine.evaluate({
            'environment': 'dev',
            'risk_level': 'high'
        })
        assert result['action'] == 'allow'
    
    def test_cost_control_scenario(self):
        """Test cost control with OR conditions."""
        engine = DeclarativePolicyEngine()
        
        engine.load_policy(
            create_policy_from_yaml_style(EXAMPLE_POLICIES['cost_control'])
        )
        
        # High tokens
        result = engine.evaluate({'estimated_tokens': 15000})
        assert result['action'] == 'require_approval'
        
        # High cost
        result = engine.evaluate({'estimated_cost': 150})
        assert result['action'] == 'require_approval'
        
        # Both low
        result = engine.evaluate({
            'estimated_tokens': 1000,
            'estimated_cost': 10
        })
        assert result['action'] == 'allow'
    
    def test_pii_blocking_scenario(self):
        """Test PII blocking."""
        engine = DeclarativePolicyEngine()
        
        engine.load_policy(
            create_policy_from_yaml_style(EXAMPLE_POLICIES['pii_blocking'])
        )
        
        # Contains SSN
        result = engine.evaluate({'prompt': 'Process SSN 123-45-6789'})
        assert result['action'] == 'block'
        
        # No PII
        result = engine.evaluate({'prompt': 'What are your hours?'})
        assert result['action'] == 'allow'
    
    def test_multi_policy_scenario(self):
        """Test multiple policies interacting."""
        engine = DeclarativePolicyEngine()
        
        # Load all example policies
        for policy_spec in EXAMPLE_POLICIES.values():
            engine.load_policy(create_policy_from_yaml_style(policy_spec))
        
        # Scenario: Production, GPT-4, high risk, contains PII
        result = engine.evaluate({
            'environment': 'prod',
            'model': 'gpt-4',
            'risk_score': 0.8,
            'risk_level': 'high',
            'prompt': 'Process this SSN: 123-45-6789'
        })
        
        # Block should win (most restrictive)
        assert result['action'] == 'block'
        assert result['reason'] == 'PII detected in prompt'
        
        # Multiple policies should have matched
        assert len(result['matched_policies']) > 1
