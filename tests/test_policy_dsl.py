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
Tests for Policy DSL and Business Policies

Tests the declarative policy language that makes governance readable.
"""

import pytest
from policy.dsl import (
    BusinessPolicy,
    PolicyDSLCompiler,
    PolicyAction,
    get_policy_template,
    POLICY_TEMPLATES,
)


def test_business_policy_creation():
    """Test creating a business policy."""
    policy = BusinessPolicy(
        name="Test Policy",
        description="A test policy",
        when={"field": "model", "equals": "gpt-4"},
        then="escalate",
        reason="Testing",
    )
    
    assert policy.name == "Test Policy"
    assert policy.then == PolicyAction.ESCALATE


def test_policy_evaluation_simple_equals():
    """Test simple equals condition."""
    policy = BusinessPolicy(
        name="Model Check",
        description="Check specific model",
        when={"field": "model", "equals": "gpt-4"},
        then="escalate",
        reason="High-risk model",
    )
    
    context = {"model": "gpt-4"}
    result = policy.evaluate(context)
    
    assert result["matched"] is True
    assert result["action"] == "escalate"


def test_policy_evaluation_and_condition():
    """Test AND condition."""
    policy = BusinessPolicy(
        name="Combined Check",
        description="Multiple conditions",
        when={
            "and": [
                {"field": "model", "equals": "gpt-4"},
                {"field": "risk_level", "equals": "high"}
            ]
        },
        then="block",
        reason="High-risk combination",
    )
    
    # Both conditions match
    context = {"model": "gpt-4", "risk_level": "high"}
    result = policy.evaluate(context)
    assert result["matched"] is True
    
    # Only one condition matches
    context = {"model": "gpt-4", "risk_level": "low"}
    result = policy.evaluate(context)
    assert result["matched"] is False


def test_policy_evaluation_or_condition():
    """Test OR condition."""
    policy = BusinessPolicy(
        name="Either Check",
        description="Match any condition",
        when={
            "or": [
                {"field": "model", "equals": "gpt-4"},
                {"field": "risk_level", "equals": "critical"}
            ]
        },
        then="escalate",
        reason="Risky operation",
    )
    
    # First condition matches
    context = {"model": "gpt-4", "risk_level": "low"}
    result = policy.evaluate(context)
    assert result["matched"] is True
    
    # Second condition matches
    context = {"model": "gpt-3", "risk_level": "critical"}
    result = policy.evaluate(context)
    assert result["matched"] is True
    
    # Neither matches
    context = {"model": "gpt-3", "risk_level": "low"}
    result = policy.evaluate(context)
    assert result["matched"] is False


def test_policy_evaluation_in_list():
    """Test 'in' condition."""
    policy = BusinessPolicy(
        name="List Check",
        description="Check if value in list",
        when={"field": "risk_level", "in": ["high", "critical"]},
        then="escalate",
        reason="High-risk level",
    )
    
    context = {"risk_level": "high"}
    result = policy.evaluate(context)
    assert result["matched"] is True
    
    context = {"risk_level": "low"}
    result = policy.evaluate(context)
    assert result["matched"] is False


def test_policy_evaluation_contains():
    """Test 'contains' condition."""
    policy = BusinessPolicy(
        name="Content Check",
        description="Check if text contains keyword",
        when={"field": "prompt", "contains": "delete"},
        then="block",
        reason="Destructive operation",
    )
    
    context = {"prompt": "Please delete this record"}
    result = policy.evaluate(context)
    assert result["matched"] is True
    
    context = {"prompt": "Please create this record"}
    result = policy.evaluate(context)
    assert result["matched"] is False


def test_policy_evaluation_nested_fields():
    """Test nested field access."""
    policy = BusinessPolicy(
        name="Nested Check",
        description="Check nested field",
        when={"field": "agent.risk_level", "equals": "high"},
        then="escalate",
        reason="High-risk agent",
    )
    
    context = {"agent": {"risk_level": "high"}}
    result = policy.evaluate(context)
    assert result["matched"] is True


def test_policy_dsl_compiler():
    """Test policy compilation from dictionary."""
    compiler = PolicyDSLCompiler()
    
    policy_dict = {
        "name": "Test Policy",
        "description": "A test policy",
        "when": {"field": "model", "equals": "gpt-4"},
        "then": "escalate",
        "reason": "Testing",
    }
    
    policy = compiler.compile_from_dict(policy_dict)
    
    assert policy.name == "Test Policy"
    assert policy.then == PolicyAction.ESCALATE


def test_policy_dsl_compiler_validation():
    """Test policy validation."""
    compiler = PolicyDSLCompiler()
    
    # Valid policy
    valid_policy = BusinessPolicy(
        name="Valid",
        description="Valid policy",
        when={"field": "test", "equals": "value"},
        then="allow",
        reason="Test",
    )
    
    assert compiler.validate_policy(valid_policy) is True
    
    # Invalid action
    with pytest.raises(ValueError):
        invalid_policy = BusinessPolicy(
            name="Invalid",
            description="Invalid policy",
            when={"field": "test", "equals": "value"},
            then="invalid_action",
            reason="Test",
        )
        compiler.validate_policy(invalid_policy)


def test_policy_templates():
    """Test policy templates."""
    assert len(POLICY_TEMPLATES) > 0
    
    # Check known templates exist
    assert "require_approval_for_model" in POLICY_TEMPLATES
    assert "block_pii" in POLICY_TEMPLATES
    assert "high_risk_escalation" in POLICY_TEMPLATES


def test_get_policy_template():
    """Test getting policy template with substitution."""
    template = get_policy_template(
        "require_approval_for_model",
        MODEL_NAME="gpt-4"
    )
    
    assert template["name"] == "Require Approval for Specific Model"
    assert "gpt-4" in str(template)


def test_policy_to_dict():
    """Test policy serialization."""
    policy = BusinessPolicy(
        name="Test",
        description="Test policy",
        when={"field": "test", "equals": "value"},
        then="allow",
        reason="Testing",
    )
    
    policy_dict = policy.to_dict()
    
    assert policy_dict["name"] == "Test"
    assert policy_dict["then"] == "allow"
    assert "when" in policy_dict
