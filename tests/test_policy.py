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
Tests for policy evaluator.
"""

import pytest
from policy.evaluator import PolicyEvaluator
from policy.parser import PolicyParser


def test_no_pii_policy():
    """Test built-in no-pii policy."""
    evaluator = PolicyEvaluator()
    
    # Test with SSN
    result = evaluator.evaluate(
        agent={"id": "test", "policies": ["no-pii"]},
        prompt="My SSN is 123-45-6789",
        context={},
        user="test",
    )
    
    assert result["action"] == "block"
    assert "SSN" in result["reason"]


def test_no_pii_policy_clean():
    """Test no-pii policy with clean input."""
    evaluator = PolicyEvaluator()
    
    result = evaluator.evaluate(
        agent={"id": "test", "policies": ["no-pii"]},
        prompt="What are your business hours?",
        context={},
        user="test",
    )
    
    assert result["action"] == "allow"


def test_allow_all_policy():
    """Test allow-all policy."""
    evaluator = PolicyEvaluator()
    
    result = evaluator.evaluate(
        agent={"id": "test", "policies": ["allow-all"]},
        prompt="Any prompt",
        context={},
        user="test",
    )
    
    assert result["action"] == "allow"


def test_no_policies():
    """Test execution with no policies."""
    evaluator = PolicyEvaluator()
    
    result = evaluator.evaluate(
        agent={"id": "test", "policies": []},
        prompt="Any prompt",
        context={},
        user="test",
    )
    
    assert result["action"] == "allow"


def test_policy_evaluation_order():
    """Test that first block wins."""
    evaluator = PolicyEvaluator()
    
    # Register a custom policy that blocks everything
    yaml_content = """
policy:
  id: "block-test"
  version: "1.0"
  name: "Block Test"
  rules:
    - condition:
        always: true
      action: block
      reason: "Test block"
"""
    
    parser = PolicyParser()
    policy = parser.parse_yaml(yaml_content)
    evaluator.register_policy(policy)
    
    # Evaluate with both policies (block-test should win)
    result = evaluator.evaluate(
        agent={"id": "test", "policies": ["block-test", "allow-all"]},
        prompt="Any prompt",
        context={},
        user="test",
    )
    
    assert result["action"] == "block"
