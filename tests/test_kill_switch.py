"""
Tests for kill switch service.
"""

import pytest
from kill_switch.service import KillSwitchService


def test_activate_global_kill_switch():
    """Test global kill switch activation."""
    service = KillSwitchService()
    
    result = service.activate(
        scope="global",
        reason="Test activation",
        activated_by="admin",
    )
    
    assert result["status"] == "activated"
    assert result["scope"] == "global"
    assert service.is_active("global") is True


def test_deactivate_global_kill_switch():
    """Test global kill switch deactivation."""
    service = KillSwitchService()
    
    # Activate first
    service.activate(scope="global", reason="Test")
    assert service.is_active("global") is True
    
    # Deactivate
    service.deactivate(scope="global")
    assert service.is_active("global") is False


def test_agent_specific_kill_switch():
    """Test agent-specific kill switch."""
    service = KillSwitchService()
    
    # Activate for specific agent
    service.activate(
        scope="agent",
        agent_id="test-agent",
        reason="Agent misbehaving",
    )
    
    assert service.is_active("agent", "test-agent") is True
    assert service.is_active("agent", "other-agent") is False
    assert service.is_active("global") is False


def test_kill_switch_reason():
    """Test getting kill switch reason."""
    service = KillSwitchService()
    
    service.activate(
        scope="global",
        reason="Emergency maintenance",
    )
    
    reason = service.get_reason("global")
    assert reason == "Emergency maintenance"


def test_get_status():
    """Test getting complete kill switch status."""
    service = KillSwitchService()
    
    service.activate(scope="global", reason="Test global")
    service.activate(scope="agent", agent_id="test-agent", reason="Test agent")
    
    status = service.get_status()
    
    assert status["global"]["active"] is True
    assert "test-agent" in status["agents"]
    assert status["agents"]["test-agent"]["active"] is True


def test_invalid_scope():
    """Test that invalid scope raises error."""
    service = KillSwitchService()
    
    with pytest.raises(ValueError, match="Invalid scope"):
        service.activate(scope="invalid", reason="Test")


def test_agent_scope_without_agent_id():
    """Test that agent scope requires agent_id."""
    service = KillSwitchService()
    
    with pytest.raises(ValueError, match="agent_id required"):
        service.activate(scope="agent", reason="Test")
