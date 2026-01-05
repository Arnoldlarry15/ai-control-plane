"""
Basic tests for gateway executor.

Note: These are integration tests that test the full execution flow.
"""

import pytest
import asyncio
from gateway.executor import Executor
from gateway.errors import KillSwitchActiveError, AgentNotFoundError
from registry.service import RegistryService
from registry.storage import RegistryStorage
from kill_switch.service import KillSwitchService
from kill_switch.state import KillSwitchState
from policy.evaluator import PolicyEvaluator
from observability.logger import ObservabilityLogger


@pytest.fixture
def fresh_executor():
    """Create a fresh executor with isolated services for each test."""
    # Create fresh instances
    registry = RegistryService()
    registry.storage = RegistryStorage()  # Fresh storage
    
    kill_switch = KillSwitchService()
    kill_switch.state = KillSwitchState()  # Fresh state
    
    policy_evaluator = PolicyEvaluator()
    obs_logger = ObservabilityLogger()
    
    return Executor(
        kill_switch=kill_switch,
        registry=registry,
        policy_evaluator=policy_evaluator,
        obs_logger=obs_logger,
    )


@pytest.mark.asyncio
async def test_successful_execution(fresh_executor):
    """Test successful execution flow."""
    executor = fresh_executor
    
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
        user="test@company.test",
    )
    
    assert result["status"] == "success"
    assert result["execution_id"] is not None
    assert result["response"] is not None


@pytest.mark.asyncio
async def test_kill_switch_blocks_execution(fresh_executor):
    """Test that kill switch blocks execution."""
    executor = fresh_executor
    
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
async def test_unregistered_agent_fails(fresh_executor):
    """Test that unregistered agent fails."""
    executor = fresh_executor
    
    with pytest.raises(AgentNotFoundError):
        await executor.execute(
            agent_id="nonexistent-agent",
            prompt="Hello",
            context={},
        )


@pytest.mark.asyncio
async def test_policy_blocks_execution(fresh_executor):
    """Test that policy can block execution."""
    executor = fresh_executor
    
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
