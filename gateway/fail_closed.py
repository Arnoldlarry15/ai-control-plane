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
Fail-Closed Enforcement System

Core principle: If the control plane is unreachable or unhealthy, DENY by default.
This is how trust is earned in enterprise environments.

Never fail open. Block on error. Explain clearly.
"""

import time
from typing import Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime


class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DOWN = "down"


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures exceeded threshold, blocking requests
    HALF_OPEN = "half_open"  # Testing if system recovered


class HealthCheck:
    """
    Health check system for control plane components.
    
    Monitors component health and fails closed on errors.
    """
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], Dict[str, Any]]] = {}
        self.last_results: Dict[str, Dict[str, Any]] = {}
    
    def register_check(self, name: str, check_func: Callable[[], Dict[str, Any]]):
        """
        Register a health check.
        
        Args:
            name: Component name
            check_func: Function that returns health status
        """
        self.checks[name] = check_func
    
    def check_health(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Overall health status
        """
        results = {}
        all_healthy = True
        any_critical = False
        
        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results[name] = result
                
                if result.get("status") != HealthStatus.HEALTHY:
                    all_healthy = False
                
                if result.get("critical", False) and result.get("status") == HealthStatus.DOWN:
                    any_critical = True
                    
            except Exception as e:
                results[name] = {
                    "status": HealthStatus.DOWN,
                    "error": str(e),
                    "critical": True,
                }
                all_healthy = False
                any_critical = True
        
        self.last_results = results
        
        # Determine overall status
        if any_critical:
            overall_status = HealthStatus.DOWN
        elif not all_healthy:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "components": results,
            "all_healthy": all_healthy,
            "fail_closed": any_critical,  # Should fail closed
        }


class CircuitBreaker:
    """
    Circuit breaker pattern for fail-closed enforcement.
    
    Prevents cascading failures by failing fast when errors exceed threshold.
    Follows Martin Fowler's circuit breaker pattern.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0,
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures before opening circuit
            success_threshold: Successes needed to close circuit (from half-open)
            timeout: Seconds before attempting recovery (half-open)
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitOpenError: When circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = time.time()
            else:
                raise CircuitOpenError(
                    "Circuit breaker is OPEN. Control plane is unavailable. "
                    "Failing closed to protect system integrity."
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise FailClosedError(
                f"Control plane execution failed. Failing closed: {str(e)}"
            ) from e
    
    def _on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                self.last_state_change = time.time()
    
    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.success_count = 0
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False
        return (time.time() - self.last_failure_time) >= self.timeout
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": datetime.fromtimestamp(self.last_failure_time).isoformat()
                if self.last_failure_time else None,
            "state_duration_seconds": time.time() - self.last_state_change,
        }


class FailClosedEnforcer:
    """
    Fail-closed enforcement coordinator.
    
    Combines health checks and circuit breaker to enforce fail-closed behavior.
    """
    
    def __init__(self):
        self.health_check = HealthCheck()
        self.circuit_breaker = CircuitBreaker()
        self._enforce_mode = True
    
    def register_component_check(
        self,
        name: str,
        check_func: Callable[[], Dict[str, Any]],
    ):
        """Register a component health check."""
        self.health_check.register_check(name, check_func)
    
    def execute_with_protection(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute function with fail-closed protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Execution result with status
        """
        # Check health first
        health = self.health_check.check_health()
        
        if self._enforce_mode and health.get("fail_closed"):
            return {
                "success": False,
                "action": "block",
                "reason": "Control plane is unhealthy. Failing closed for safety.",
                "health_status": health,
                "fail_closed": True,
            }
        
        # Execute through circuit breaker
        try:
            result = self.circuit_breaker.call(func, *args, **kwargs)
            return {
                "success": True,
                "action": "allow",
                "result": result,
                "health_status": health,
                "circuit_state": self.circuit_breaker.get_state(),
            }
        except CircuitOpenError as e:
            return {
                "success": False,
                "action": "block",
                "reason": str(e),
                "fail_closed": True,
                "circuit_state": self.circuit_breaker.get_state(),
            }
        except FailClosedError as e:
            return {
                "success": False,
                "action": "block",
                "reason": f"Execution failed: {str(e)}",
                "fail_closed": True,
                "circuit_state": self.circuit_breaker.get_state(),
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get enforcer status."""
        return {
            "enforce_mode": self._enforce_mode,
            "health": self.health_check.check_health(),
            "circuit": self.circuit_breaker.get_state(),
        }
    
    def set_enforce_mode(self, enforce: bool):
        """Enable or disable enforcement (use carefully!)."""
        self._enforce_mode = enforce


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class FailClosedError(Exception):
    """Raised when failing closed due to error."""
    pass


# Pre-built health check functions
def check_policy_engine_health() -> Dict[str, Any]:
    """Check policy engine health."""
    try:
        from policy.evaluator import PolicyEvaluator
        evaluator = PolicyEvaluator()
        # Simple smoke test
        result = evaluator.evaluate(
            agent={"id": "test", "policies": []},
            prompt="test",
            context={},
            user="health-check",
        )
        return {
            "status": HealthStatus.HEALTHY,
            "critical": True,
            "message": "Policy engine operational",
        }
    except Exception as e:
        return {
            "status": HealthStatus.DOWN,
            "critical": True,
            "error": str(e),
            "message": "Policy engine failed",
        }


def check_audit_log_health() -> Dict[str, Any]:
    """Check audit log health."""
    try:
        from observability.immutable_audit import ImmutableAuditLog
        log = ImmutableAuditLog()
        log.log_event("health.check", {"test": True})
        integrity = log.verify_integrity()
        
        if integrity["valid"]:
            return {
                "status": HealthStatus.HEALTHY,
                "critical": True,
                "message": "Audit log operational",
            }
        else:
            return {
                "status": HealthStatus.DOWN,
                "critical": True,
                "message": "Audit log integrity failed",
            }
    except Exception as e:
        return {
            "status": HealthStatus.DOWN,
            "critical": True,
            "error": str(e),
            "message": "Audit log failed",
        }


def check_kill_switch_health() -> Dict[str, Any]:
    """Check kill switch health."""
    try:
        from kill_switch.state import KillSwitchState
        state = KillSwitchState()
        # If kill switch is active, system should fail closed
        if state.is_active():
            return {
                "status": HealthStatus.DOWN,
                "critical": True,
                "message": "Kill switch is ACTIVE - system locked down",
            }
        return {
            "status": HealthStatus.HEALTHY,
            "critical": False,
            "message": "Kill switch operational",
        }
    except Exception as e:
        return {
            "status": HealthStatus.DEGRADED,
            "critical": False,
            "error": str(e),
            "message": "Kill switch check failed",
        }
