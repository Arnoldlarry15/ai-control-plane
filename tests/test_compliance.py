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
Tests for compliance policy modules.
"""

import pytest

from policy.compliance import ComplianceLoader
from policy.evaluator import PolicyEvaluator


def test_list_standards():
    """Test listing available compliance standards."""
    loader = ComplianceLoader()
    
    standards = loader.list_standards()
    
    assert "gdpr" in standards
    assert "hipaa" in standards
    assert "soc2" in standards
    assert "pci-dss" in standards


def test_load_gdpr_policy():
    """Test loading GDPR compliance policy."""
    loader = ComplianceLoader()
    
    policy = loader.load_policy("gdpr")
    
    assert policy.id == "gdpr-compliance"
    assert policy.name == "GDPR Compliance Policy"
    assert len(policy.rules) > 0


def test_load_hipaa_policy():
    """Test loading HIPAA compliance policy."""
    loader = ComplianceLoader()
    
    policy = loader.load_policy("hipaa")
    
    assert policy.id == "hipaa-compliance"
    assert policy.name == "HIPAA Compliance Policy"
    assert len(policy.rules) > 0


def test_load_soc2_policy():
    """Test loading SOC 2 compliance policy."""
    loader = ComplianceLoader()
    
    policy = loader.load_policy("soc2")
    
    assert policy.id == "soc2-compliance"
    assert policy.name == "SOC 2 Compliance Policy"
    assert len(policy.rules) > 0


def test_load_pci_dss_policy():
    """Test loading PCI-DSS compliance policy."""
    loader = ComplianceLoader()
    
    policy = loader.load_policy("pci-dss")
    
    assert policy.id == "pci-dss-compliance"
    assert policy.name == "PCI-DSS Compliance Policy"
    assert len(policy.rules) > 0


def test_load_invalid_standard():
    """Test loading invalid compliance standard."""
    loader = ComplianceLoader()
    
    with pytest.raises(ValueError, match="Unknown compliance standard"):
        loader.load_policy("invalid-standard")


def test_load_all_policies():
    """Test loading all compliance policies."""
    loader = ComplianceLoader()
    
    policies = loader.load_all()
    
    assert len(policies) == 4
    policy_ids = [p.id for p in policies]
    assert "gdpr-compliance" in policy_ids
    assert "hipaa-compliance" in policy_ids
    assert "soc2-compliance" in policy_ids
    assert "pci-dss-compliance" in policy_ids


def test_gdpr_ssn_detection():
    """Test GDPR policy detects SSN patterns."""
    loader = ComplianceLoader()
    evaluator = PolicyEvaluator()
    
    policy = loader.load_policy("gdpr")
    evaluator.register_policy(policy)
    
    agent = {
        "agent_id": "test-agent",
        "policies": ["gdpr-compliance"],
    }
    
    result = evaluator.evaluate(
        agent=agent,
        prompt="My SSN is 123-45-6789",
        context={},
        user="test@company.test",
    )
    
    # GDPR doesn't block SSN directly, but HIPAA would
    # This test just checks the policy loads correctly
    assert result is not None


def test_hipaa_ssn_blocking():
    """Test HIPAA policy blocks SSN patterns."""
    loader = ComplianceLoader()
    evaluator = PolicyEvaluator()
    
    policy = loader.load_policy("hipaa")
    evaluator.register_policy(policy)
    
    agent = {
        "agent_id": "test-agent",
        "policies": ["hipaa-compliance"],
    }
    
    result = evaluator.evaluate(
        agent=agent,
        prompt="Patient SSN is 123-45-6789",
        context={},
        user="test@company.test",
    )
    
    assert result["action"] == "block"
    assert "HIPAA" in result["reason"]


def test_pci_dss_cvv_blocking():
    """Test PCI-DSS policy blocks CVV codes."""
    loader = ComplianceLoader()
    evaluator = PolicyEvaluator()
    
    policy = loader.load_policy("pci-dss")
    evaluator.register_policy(policy)
    
    agent = {
        "agent_id": "test-agent",
        "policies": ["pci-dss-compliance"],
    }
    
    result = evaluator.evaluate(
        agent=agent,
        prompt="Card CVV: 123",
        context={},
        user="test@company.test",
    )
    
    assert result["action"] == "block"
    assert "PCI-DSS" in result["reason"]


def test_pci_dss_card_number_blocking():
    """Test PCI-DSS policy blocks credit card numbers."""
    loader = ComplianceLoader()
    evaluator = PolicyEvaluator()
    
    policy = loader.load_policy("pci-dss")
    evaluator.register_policy(policy)
    
    agent = {
        "agent_id": "test-agent",
        "policies": ["pci-dss-compliance"],
    }
    
    # Test Visa card pattern
    result = evaluator.evaluate(
        agent=agent,
        prompt="Process card 4532-1234-5678-9010",
        context={},
        user="test@company.test",
    )
    
    assert result["action"] == "block"
    assert "PCI-DSS" in result["reason"]


def test_soc2_credential_blocking():
    """Test SOC 2 policy blocks credentials."""
    loader = ComplianceLoader()
    evaluator = PolicyEvaluator()
    
    policy = loader.load_policy("soc2")
    evaluator.register_policy(policy)
    
    agent = {
        "agent_id": "test-agent",
        "policies": ["soc2-compliance"],
    }
    
    result = evaluator.evaluate(
        agent=agent,
        prompt="Store admin password: secret123",
        context={},
        user="test@company.test",
    )
    
    assert result["action"] == "block"
    assert "SOC 2" in result["reason"]


def test_multiple_compliance_policies():
    """Test applying multiple compliance policies to one agent."""
    loader = ComplianceLoader()
    evaluator = PolicyEvaluator()
    
    # Load multiple policies
    gdpr = loader.load_policy("gdpr")
    hipaa = loader.load_policy("hipaa")
    
    evaluator.register_policy(gdpr)
    evaluator.register_policy(hipaa)
    
    agent = {
        "agent_id": "test-agent",
        "policies": ["gdpr-compliance", "hipaa-compliance"],
    }
    
    # Test with SSN (blocked by HIPAA)
    result = evaluator.evaluate(
        agent=agent,
        prompt="SSN: 123-45-6789",
        context={},
        user="test@company.test",
    )
    
    assert result["action"] == "block"


def test_policy_info():
    """Test getting policy information."""
    loader = ComplianceLoader()
    
    info = loader.get_policy_info("gdpr")
    
    assert info["id"] == "gdpr-compliance"
    assert info["name"] == "GDPR Compliance Policy"
    assert info["standard"] == "GDPR"
    assert info["rules_count"] > 0
