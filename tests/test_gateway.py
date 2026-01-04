"""
Basic tests for gateway executor.

Note: These are integration tests that test the full execution flow.
"""

import pytest
import asyncio
from gateway.executor import Executor
from gateway.errors import KillSwitchActiveError, AgentNotFoundError
from registry.service import RegistryService
from kill_switch.service import KillSwitchService


@pytest.mark.asyncio
async def test_successful_execution():
    """Test successful execution flow."""
    executor = Executor()
    
    # Register agent first
    executor.registry.register_agent(
        name="Test Agent",
        model="gpt-3.5-turbo",
        policies=[],
    )
    
    # Execute
    result = await executor.execute(
        agent_id="test-agent",
        prompt="Hello, world!",
        context={},
        user="test@example.com",
    )
    
    assert result["status"] == "success"
    assert result["execution_id"] is not None
    assert result["response"] is not None


@pytest.mark.asyncio
async def test_kill_switch_blocks_execution():
    """Test that kill switch blocks execution."""
    executor = Executor()
    
    # Register agent
    executor.registry.register_agent(name="Test Agent", model="gpt-3.5-turbo")
    
    # Activate kill switch
    executor.kill_switch.activate(scope="global", reason="Test")
    
    # Try to execute
    with pytest.raises(KillSwitchActiveError):
        await executor.execute(
            agent_id="test-agent",
            prompt="Hello",
            context={},
        )


@pytest.mark.asyncio
async def test_unregistered_agent_fails():
    """Test that unregistered agent fails."""
    executor = Executor()
    
    with pytest.raises(AgentNotFoundError):
        await executor.execute(
            agent_id="nonexistent-agent",
            prompt="Hello",
            context={},
        )


@pytest.mark.asyncio
async def test_policy_blocks_execution():
    """Test that policy can block execution."""
    executor = Executor()
    
    # Register agent with no-pii policy
    executor.registry.register_agent(
        name="Test Agent",
        model="gpt-3.5-turbo",
        policies=["no-pii"],
    )
    
    # Try to execute with PII
    from gateway.errors import PolicyViolationError
    with pytest.raises(PolicyViolationError):
        await executor.execute(
            agent_id="test-agent",
            prompt="My SSN is 123-45-6789",
            context={},
        )
