"""
Executor: Where AI calls live, wrapped, controlled, logged.

This is THE core. This is where governance happens.

Every AI execution flows through this file. Every. Single. One.
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional

from gateway.errors import (
    KillSwitchActiveError,
    PolicyViolationError,
    AgentNotFoundError,
    ExecutionError,
)

logger = logging.getLogger(__name__)


class Executor:
    """
    The Executor. Where AI calls live, wrapped, controlled, logged.
    
    This class orchestrates the complete execution flow:
    1. Check kill switch
    2. Validate agent
    3. Evaluate policies
    4. Execute (if allowed)
    5. Log everything
    
    Fail closed. Always.
    """
    
    def __init__(self, kill_switch=None, registry=None, policy_evaluator=None, obs_logger=None):
        # Use injected services or import and get singletons
        if kill_switch is None or registry is None or policy_evaluator is None or obs_logger is None:
            from gateway.services import (
                get_kill_switch,
                get_registry,
                get_policy_evaluator,
                get_observability_logger,
            )
            self.kill_switch = kill_switch or get_kill_switch()
            self.registry = registry or get_registry()
            self.policy_evaluator = policy_evaluator or get_policy_evaluator()
            self.obs_logger = obs_logger or get_observability_logger()
        else:
            self.kill_switch = kill_switch
            self.registry = registry
            self.policy_evaluator = policy_evaluator
            self.obs_logger = obs_logger
        
        logger.info("Executor initialized. The choke point is ready.")
    
    async def execute(
        self,
        agent_id: str,
        prompt: str,
        context: Dict[str, Any],
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute an AI agent through the control plane.
        
        This is THE method. The throne. All execution flows through here.
        
        Args:
            agent_id: Registered agent identifier
            prompt: User input/prompt
            context: Execution context (metadata, user info, etc.)
            user: User identifier
        
        Returns:
            Execution result with status, response, and metadata
        
        Raises:
            KillSwitchActiveError: If kill switch blocks execution
            AgentNotFoundError: If agent is not registered
            PolicyViolationError: If policy blocks execution
            ExecutionError: If execution fails
        """
        # Generate unique execution ID
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"[{execution_id}] Starting execution: agent={agent_id} user={user}")
        
        try:
            # STEP 1: Check kill switch (must be instant)
            self._check_kill_switch(execution_id, agent_id)
            
            # STEP 2: Validate agent registration
            agent = self._validate_agent(execution_id, agent_id)
            
            # STEP 3: Evaluate policies (allow / block / escalate)
            policy_decision = self._evaluate_policies(
                execution_id, agent, prompt, context, user
            )
            
            # STEP 4: Handle policy decision
            if policy_decision["action"] == "block":
                return self._handle_block(
                    execution_id, agent_id, prompt, policy_decision, start_time, user
                )
            elif policy_decision["action"] == "escalate":
                return self._handle_escalate(
                    execution_id, agent_id, prompt, policy_decision, start_time, user
                )
            
            # STEP 5: Execute the AI call (if allowed)
            response = await self._execute_ai(
                execution_id, agent, prompt, context
            )
            
            # STEP 6: Log successful execution
            latency_ms = int((time.time() - start_time) * 1000)
            self._log_execution(
                execution_id=execution_id,
                agent_id=agent_id,
                prompt=prompt,
                response=response,
                status="success",
                latency_ms=latency_ms,
                user=user,
                context=context,
            )
            
            logger.info(f"[{execution_id}] Execution successful: latency={latency_ms}ms")
            
            return {
                "status": "success",
                "response": response,
                "execution_id": execution_id,
                "latency_ms": latency_ms,
            }
        
        except (KillSwitchActiveError, PolicyViolationError, AgentNotFoundError) as e:
            # Expected control plane errors - already logged in handlers
            raise
        
        except Exception as e:
            # Unexpected errors - log and fail closed
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[{execution_id}] Execution error: {e}", exc_info=True)
            
            self._log_execution(
                execution_id=execution_id,
                agent_id=agent_id,
                prompt=prompt,
                response=None,
                status="error",
                error=str(e),
                latency_ms=latency_ms,
                user=user,
                context=context,
            )
            
            raise ExecutionError(str(e))
    
    def _check_kill_switch(self, execution_id: str, agent_id: str):
        """
        Check if kill switch blocks execution.
        
        This must be INSTANT. No database calls. In-memory only.
        """
        logger.debug(f"[{execution_id}] Checking kill switch")
        
        # Check global kill switch
        if self.kill_switch.is_active("global"):
            reason = self.kill_switch.get_reason("global")
            logger.warning(f"[{execution_id}] BLOCKED by global kill switch: {reason}")
            raise KillSwitchActiveError(reason)
        
        # Check agent-specific kill switch
        if self.kill_switch.is_active("agent", agent_id):
            reason = self.kill_switch.get_reason("agent", agent_id)
            logger.warning(f"[{execution_id}] BLOCKED by agent kill switch: {reason}")
            raise KillSwitchActiveError(reason)
        
        logger.debug(f"[{execution_id}] Kill switch check passed")
    
    def _validate_agent(self, execution_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Validate that agent is registered.
        
        If it's not in the registry, it cannot execute. Period.
        This is how you prevent shadow AI.
        """
        logger.debug(f"[{execution_id}] Validating agent: {agent_id}")
        
        agent = self.registry.get_agent(agent_id)
        if not agent:
            logger.warning(f"[{execution_id}] BLOCKED: agent not found: {agent_id}")
            raise AgentNotFoundError(agent_id)
        
        logger.debug(f"[{execution_id}] Agent validated: {agent['name']}")
        return agent
    
    def _evaluate_policies(
        self,
        execution_id: str,
        agent: Dict[str, Any],
        prompt: str,
        context: Dict[str, Any],
        user: Optional[str],
    ) -> Dict[str, Any]:
        """
        Evaluate all applicable policies.
        
        Returns: allow, block, or escalate
        
        This must stay dumb and deterministic. No ML. No guessing.
        """
        logger.debug(f"[{execution_id}] Evaluating policies")
        
        decision = self.policy_evaluator.evaluate(
            agent=agent,
            prompt=prompt,
            context=context,
            user=user,
        )
        
        logger.info(
            f"[{execution_id}] Policy decision: {decision['action']} "
            f"(reason: {decision.get('reason', 'N/A')})"
        )
        
        return decision
    
    def _handle_block(
        self,
        execution_id: str,
        agent_id: str,
        prompt: str,
        policy_decision: Dict[str, Any],
        start_time: float,
        user: Optional[str],
    ) -> Dict[str, Any]:
        """Handle blocked execution."""
        latency_ms = int((time.time() - start_time) * 1000)
        reason = policy_decision.get("reason", "Policy violation")
        policy_id = policy_decision.get("policy_id", "unknown")
        
        logger.warning(f"[{execution_id}] BLOCKED: {reason}")
        
        # Log the block
        self._log_execution(
            execution_id=execution_id,
            agent_id=agent_id,
            prompt=prompt,
            response=None,
            status="blocked",
            reason=reason,
            policy_id=policy_id,
            latency_ms=latency_ms,
            user=user,
        )
        
        raise PolicyViolationError(policy_id=policy_id, reason=reason)
    
    def _handle_escalate(
        self,
        execution_id: str,
        agent_id: str,
        prompt: str,
        policy_decision: Dict[str, Any],
        start_time: float,
        user: Optional[str],
    ) -> Dict[str, Any]:
        """Handle escalated execution (requires approval)."""
        latency_ms = int((time.time() - start_time) * 1000)
        reason = policy_decision.get("reason", "Requires approval")
        
        logger.info(f"[{execution_id}] ESCALATED: {reason}")
        
        # Log the escalation
        self._log_execution(
            execution_id=execution_id,
            agent_id=agent_id,
            prompt=prompt,
            response=None,
            status="pending_approval",
            reason=reason,
            latency_ms=latency_ms,
            user=user,
        )
        
        # TODO: Queue for approval (V1: just return pending status)
        approval_id = f"approval-{execution_id}"
        
        return {
            "status": "pending_approval",
            "execution_id": execution_id,
            "approval_id": approval_id,
            "reason": reason,
        }
    
    async def _execute_ai(
        self,
        execution_id: str,
        agent: Dict[str, Any],
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Execute the actual AI call.
        
        V1: Stubbed response. In production, this calls OpenAI/Anthropic/etc.
        """
        logger.info(f"[{execution_id}] Executing AI model: {agent['model']}")
        
        # V1: Stubbed response
        # TODO: Integrate with actual AI providers (OpenAI, Anthropic, etc.)
        
        # Simulate AI call
        await self._simulate_ai_latency()
        
        response = f"[STUBBED AI RESPONSE] Processed prompt: '{prompt[:50]}...'"
        
        logger.debug(f"[{execution_id}] AI execution completed")
        return response
    
    async def _simulate_ai_latency(self):
        """Simulate AI API latency for demo purposes."""
        import asyncio
        await asyncio.sleep(0.1)  # 100ms simulated latency
    
    def _log_execution(
        self,
        execution_id: str,
        agent_id: str,
        prompt: str,
        response: Optional[str],
        status: str,
        latency_ms: int,
        user: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        policy_id: Optional[str] = None,
        error: Optional[str] = None,
    ):
        """
        Log execution to observability.
        
        Everything logged. No exceptions.
        """
        self.obs_logger.log_execution(
            execution_id=execution_id,
            agent_id=agent_id,
            prompt=prompt,
            response=response,
            status=status,
            latency_ms=latency_ms,
            user=user,
            context=context,
            reason=reason,
            policy_id=policy_id,
            error=error,
        )
