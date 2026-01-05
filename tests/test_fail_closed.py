"""
Tests for fail-closed enforcement system.

Tests health checks, circuit breaker, and fail-closed behavior.
"""

import pytest
import time
from gateway.fail_closed import (
    HealthCheck,
    HealthStatus,
    CircuitBreaker,
    CircuitState,
    CircuitOpenError,
    FailClosedError,
    FailClosedEnforcer,
)


class TestHealthCheck:
    """Test health check system."""
    
    def test_register_and_run_check(self):
        """Test registering and running health checks."""
        health = HealthCheck()
        
        def mock_check():
            return {
                "status": HealthStatus.HEALTHY,
                "message": "All good",
            }
        
        health.register_check("test_component", mock_check)
        result = health.check_health()
        
        assert result["status"] == HealthStatus.HEALTHY
        assert "test_component" in result["components"]
        assert result["all_healthy"] is True
    
    def test_unhealthy_component(self):
        """Test detection of unhealthy component."""
        health = HealthCheck()
        
        def unhealthy_check():
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": "Component down",
            }
        
        health.register_check("bad_component", unhealthy_check)
        result = health.check_health()
        
        assert result["status"] == HealthStatus.DEGRADED
        assert result["all_healthy"] is False
    
    def test_critical_component_down(self):
        """Test critical component failure triggers fail-closed."""
        health = HealthCheck()
        
        def critical_down():
            return {
                "status": HealthStatus.DOWN,
                "critical": True,
                "message": "Critical failure",
            }
        
        health.register_check("critical_component", critical_down)
        result = health.check_health()
        
        assert result["status"] == HealthStatus.DOWN
        assert result["fail_closed"] is True
    
    def test_exception_in_check(self):
        """Test that exceptions in checks are handled."""
        health = HealthCheck()
        
        def failing_check():
            raise Exception("Check failed")
        
        health.register_check("failing_component", failing_check)
        result = health.check_health()
        
        assert result["status"] == HealthStatus.DOWN
        assert result["fail_closed"] is True
        assert "error" in result["components"]["failing_component"]
    
    def test_multiple_components(self):
        """Test multiple components with mixed health."""
        health = HealthCheck()
        
        def healthy():
            return {"status": HealthStatus.HEALTHY}
        
        def degraded():
            return {"status": HealthStatus.DEGRADED}
        
        def down():
            return {"status": HealthStatus.DOWN, "critical": False}
        
        health.register_check("comp1", healthy)
        health.register_check("comp2", degraded)
        health.register_check("comp3", down)
        
        result = health.check_health()
        
        assert result["status"] == HealthStatus.DEGRADED
        assert result["all_healthy"] is False
        assert result["fail_closed"] is False  # No critical failures


class TestCircuitBreaker:
    """Test circuit breaker."""
    
    def test_initial_state(self):
        """Test initial circuit state."""
        breaker = CircuitBreaker()
        state = breaker.get_state()
        
        assert state["state"] == CircuitState.CLOSED
        assert state["failure_count"] == 0
    
    def test_successful_execution(self):
        """Test successful function execution."""
        breaker = CircuitBreaker()
        
        def success_func():
            return "success"
        
        result = breaker.call(success_func)
        
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
    
    def test_failed_execution(self):
        """Test failed function execution."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        def failing_func():
            raise ValueError("Test error")
        
        # First failure
        with pytest.raises(FailClosedError):
            breaker.call(failing_func)
        
        assert breaker.failure_count == 1
        assert breaker.state == CircuitState.CLOSED
    
    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        def failing_func():
            raise ValueError("Test error")
        
        # Trigger failures
        for _ in range(3):
            with pytest.raises(FailClosedError):
                breaker.call(failing_func)
        
        # Circuit should be open now
        assert breaker.state == CircuitState.OPEN
        
        # Next call should fail immediately without calling function
        with pytest.raises(CircuitOpenError):
            breaker.call(failing_func)
    
    def test_circuit_half_open_after_timeout(self):
        """Test circuit goes half-open after timeout."""
        breaker = CircuitBreaker(
            failure_threshold=2,
            timeout=0.1  # Short timeout for testing
        )
        
        def failing_func():
            raise ValueError("Test error")
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(FailClosedError):
                breaker.call(failing_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        time.sleep(0.2)
        
        # Next call should attempt execution (goes to half-open)
        # But since it fails, circuit goes back to OPEN
        with pytest.raises(FailClosedError):
            breaker.call(failing_func)
        
        # After failure in half-open, circuit reopens
        assert breaker.state == CircuitState.OPEN
    
    def test_circuit_closes_after_success_threshold(self):
        """Test circuit closes after success threshold in half-open."""
        breaker = CircuitBreaker(
            failure_threshold=2,
            success_threshold=2,
            timeout=0.1
        )
        
        counter = [0]
        
        def sometimes_failing():
            counter[0] += 1
            if counter[0] <= 2:
                raise ValueError("Fail first two times")
            return "success"
        
        # Open circuit
        for _ in range(2):
            with pytest.raises(FailClosedError):
                breaker.call(sometimes_failing)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait and go half-open
        time.sleep(0.2)
        
        # First success in half-open
        result = breaker.call(sometimes_failing)
        assert result == "success"
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Second success should close circuit
        result = breaker.call(sometimes_failing)
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED


class TestFailClosedEnforcer:
    """Test fail-closed enforcer."""
    
    def test_healthy_execution(self):
        """Test execution when system is healthy."""
        enforcer = FailClosedEnforcer()
        
        def healthy_check():
            return {"status": HealthStatus.HEALTHY, "critical": True}
        
        enforcer.register_component_check("test", healthy_check)
        
        def test_func(x):
            return x * 2
        
        result = enforcer.execute_with_protection(test_func, 5)
        
        assert result["success"] is True
        assert result["action"] == "allow"
        assert result["result"] == 10
    
    def test_unhealthy_component_blocks(self):
        """Test that unhealthy critical component blocks execution."""
        enforcer = FailClosedEnforcer()
        
        def unhealthy_check():
            return {"status": HealthStatus.DOWN, "critical": True}
        
        enforcer.register_component_check("critical", unhealthy_check)
        
        def test_func():
            return "should not execute"
        
        result = enforcer.execute_with_protection(test_func)
        
        assert result["success"] is False
        assert result["action"] == "block"
        assert result["fail_closed"] is True
        assert "unhealthy" in result["reason"].lower()
    
    def test_circuit_breaker_integration(self):
        """Test circuit breaker integration."""
        enforcer = FailClosedEnforcer()
        enforcer.circuit_breaker.failure_threshold = 2
        
        def healthy_check():
            return {"status": HealthStatus.HEALTHY, "critical": False}
        
        enforcer.register_component_check("test", healthy_check)
        
        def failing_func():
            raise ValueError("Always fails")
        
        # First two failures
        for _ in range(2):
            result = enforcer.execute_with_protection(failing_func)
            assert result["success"] is False
            assert result["fail_closed"] is True
        
        # Circuit should be open now
        result = enforcer.execute_with_protection(failing_func)
        assert result["success"] is False
        assert "circuit" in result["reason"].lower()
    
    def test_enforce_mode_toggle(self):
        """Test toggling enforcement mode."""
        enforcer = FailClosedEnforcer()
        
        def unhealthy_check():
            return {"status": HealthStatus.DOWN, "critical": True}
        
        enforcer.register_component_check("critical", unhealthy_check)
        
        def test_func():
            return "success"
        
        # With enforcement (default)
        result = enforcer.execute_with_protection(test_func)
        assert result["success"] is False
        
        # Disable enforcement
        enforcer.set_enforce_mode(False)
        result = enforcer.execute_with_protection(test_func)
        assert result["success"] is True
    
    def test_get_status(self):
        """Test getting enforcer status."""
        enforcer = FailClosedEnforcer()
        
        def mock_check():
            return {"status": HealthStatus.HEALTHY}
        
        enforcer.register_component_check("test", mock_check)
        
        status = enforcer.get_status()
        
        assert "enforce_mode" in status
        assert "health" in status
        assert "circuit" in status
        assert status["health"]["status"] == HealthStatus.HEALTHY


class TestFailClosedPrinciples:
    """Test fail-closed principles."""
    
    def test_deny_by_default_on_error(self):
        """Test that errors result in denial, not silent allow."""
        enforcer = FailClosedEnforcer()
        
        def error_prone_func():
            raise RuntimeError("Unexpected error")
        
        result = enforcer.execute_with_protection(error_prone_func)
        
        # Should fail closed, not allow
        assert result["success"] is False
        assert result["action"] == "block"
        assert result["fail_closed"] is True
    
    def test_critical_component_failure_blocks_all(self):
        """Test that critical component failure blocks everything."""
        enforcer = FailClosedEnforcer()
        
        def policy_engine_down():
            return {
                "status": HealthStatus.DOWN,
                "critical": True,
                "message": "Policy engine unreachable",
            }
        
        enforcer.register_component_check("policy_engine", policy_engine_down)
        
        def simple_operation():
            return "This should not execute"
        
        result = enforcer.execute_with_protection(simple_operation)
        
        assert result["success"] is False
        assert result["action"] == "block"
        assert "unhealthy" in result["reason"].lower()
    
    def test_cascading_failure_protection(self):
        """Test protection against cascading failures."""
        enforcer = FailClosedEnforcer()
        enforcer.circuit_breaker.failure_threshold = 3
        
        call_count = [0]
        
        def flaky_service():
            call_count[0] += 1
            raise TimeoutError("Service timeout")
        
        # Trigger failures to open circuit
        for _ in range(3):
            result = enforcer.execute_with_protection(flaky_service)
            assert result["success"] is False
        
        # Circuit should be open - prevents cascading failures
        initial_count = call_count[0]
        
        # These should fail immediately without calling function
        for _ in range(5):
            result = enforcer.execute_with_protection(flaky_service)
            assert result["success"] is False
        
        # Function should not have been called additional times
        assert call_count[0] == initial_count


class TestRealWorldScenarios:
    """Test real-world fail-closed scenarios."""
    
    def test_policy_engine_failure_scenario(self):
        """Test scenario where policy engine fails."""
        enforcer = FailClosedEnforcer()
        
        def policy_engine_check():
            # Simulate policy engine failure
            return {
                "status": HealthStatus.DOWN,
                "critical": True,
                "error": "Cannot load policies",
            }
        
        enforcer.register_component_check("policy_engine", policy_engine_check)
        
        def ai_request():
            return {"response": "AI generated content"}
        
        # Should fail closed
        result = enforcer.execute_with_protection(ai_request)
        
        assert result["success"] is False
        assert result["action"] == "block"
        assert result["fail_closed"] is True
        
        # User gets clear explanation
        assert "unhealthy" in result["reason"].lower()
    
    def test_audit_log_failure_scenario(self):
        """Test scenario where audit log fails."""
        enforcer = FailClosedEnforcer()
        
        def audit_log_check():
            return {
                "status": HealthStatus.DOWN,
                "critical": True,
                "error": "Audit log integrity compromised",
            }
        
        enforcer.register_component_check("audit_log", audit_log_check)
        
        def ai_request():
            return "AI response"
        
        # Should fail closed - can't log without audit trail
        result = enforcer.execute_with_protection(ai_request)
        
        assert result["success"] is False
        assert result["fail_closed"] is True
    
    def test_partial_system_degradation(self):
        """Test system can operate with non-critical degradation."""
        enforcer = FailClosedEnforcer()
        
        def critical_healthy():
            return {"status": HealthStatus.HEALTHY, "critical": True}
        
        def non_critical_degraded():
            return {"status": HealthStatus.DEGRADED, "critical": False}
        
        enforcer.register_component_check("policy_engine", critical_healthy)
        enforcer.register_component_check("analytics", non_critical_degraded)
        
        def ai_request():
            return "success"
        
        # Should still allow - only non-critical component degraded
        result = enforcer.execute_with_protection(ai_request)
        
        assert result["success"] is True
        assert result["action"] == "allow"
