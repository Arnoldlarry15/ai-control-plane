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
Tests for registry service.
"""

import pytest
from registry.service import RegistryService


def test_register_agent():
    """Test agent registration."""
    registry = RegistryService()
    
    agent = registry.register_agent(
        name="Test Agent",
        model="gpt-3.5-turbo",
        risk_level="low",
        policies=["no-pii"],
    )
    
    assert agent["id"] == "test-agent"
    assert agent["name"] == "Test Agent"
    assert agent["model"] == "gpt-3.5-turbo"
    assert agent["risk_level"] == "low"
    assert "no-pii" in agent["policies"]
    assert agent["active"] is True


def test_get_agent():
    """Test getting agent by ID."""
    registry = RegistryService()
    
    # Register agent
    registry.register_agent(name="Test Agent", model="gpt-3.5-turbo")
    
    # Get agent
    agent = registry.get_agent("test-agent")
    assert agent is not None
    assert agent["id"] == "test-agent"


def test_list_agents():
    """Test listing agents."""
    registry = RegistryService()
    
    # Register multiple agents
    registry.register_agent(name="Agent 1", model="gpt-3.5-turbo")
    registry.register_agent(name="Agent 2", model="gpt-4")
    
    # List all
    agents = registry.list_agents()
    assert len(agents) == 2


def test_duplicate_registration():
    """Test that duplicate registration fails."""
    registry = RegistryService()
    
    registry.register_agent(name="Test Agent", model="gpt-3.5-turbo")
    
    with pytest.raises(ValueError, match="already registered"):
        registry.register_agent(name="Test Agent", model="gpt-3.5-turbo")


def test_invalid_risk_level():
    """Test that invalid risk level fails."""
    registry = RegistryService()
    
    with pytest.raises(ValueError, match="Invalid risk_level"):
        registry.register_agent(
            name="Test Agent",
            model="gpt-3.5-turbo",
            risk_level="invalid",
        )


def test_deactivate_agent():
    """Test agent deactivation."""
    registry = RegistryService()
    
    registry.register_agent(name="Test Agent", model="gpt-3.5-turbo")
    
    agent = registry.deactivate_agent("test-agent")
    assert agent["active"] is False
    
    # Should not appear in active list
    active_agents = registry.list_agents(active_only=True)
    assert len(active_agents) == 0
