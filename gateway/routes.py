"""
API routes for the gateway.

Defines all endpoints for AI execution, policy management, and control operations.
"""

import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field

from gateway.executor import Executor
from kill_switch.service import KillSwitchService
from registry.service import RegistryService
from policy.evaluator import PolicyEvaluator
from observability.logger import ObservabilityLogger

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services (in production, use dependency injection)
executor = Executor()
kill_switch = KillSwitchService()
registry = RegistryService()
policy_evaluator = PolicyEvaluator()
obs_logger = ObservabilityLogger()


# Request/Response models
class ExecuteRequest(BaseModel):
    """Request to execute an AI agent."""
    agent_id: str = Field(..., description="Registered agent ID")
    prompt: str = Field(..., description="User prompt/input")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    user: Optional[str] = Field(None, description="User identifier")


class ExecuteResponse(BaseModel):
    """Response from AI execution."""
    status: str = Field(..., description="Execution status: success, blocked, pending_approval")
    response: Optional[str] = Field(None, description="AI response content")
    execution_id: str = Field(..., description="Unique execution ID")
    reason: Optional[str] = Field(None, description="Reason for block/escalation")
    latency_ms: Optional[int] = Field(None, description="Execution latency in milliseconds")


class RegisterAgentRequest(BaseModel):
    """Request to register an AI agent."""
    name: str = Field(..., description="Agent name")
    model: str = Field(..., description="AI model (e.g., gpt-3.5-turbo)")
    risk_level: str = Field(default="medium", description="Risk level: low, medium, high, critical")
    policies: list[str] = Field(default_factory=list, description="Policy IDs to apply")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class KillSwitchRequest(BaseModel):
    """Request to activate/deactivate kill switch."""
    scope: str = Field(..., description="Scope: global or agent")
    agent_id: Optional[str] = Field(None, description="Agent ID for agent-scoped kill switch")
    reason: str = Field(..., description="Reason for activation")


# Execution endpoint (THE CORE)
@router.post("/execute", response_model=ExecuteResponse)
async def execute_agent(request: ExecuteRequest):
    """
    Execute an AI agent through the control plane.
    
    This is THE endpoint. The choke point. All AI execution flows through here.
    
    Flow:
    1. Check kill switch
    2. Validate agent registration
    3. Evaluate policies
    4. Execute if allowed
    5. Log everything
    """
    logger.info(f"Execution request for agent={request.agent_id} user={request.user}")
    
    try:
        # Execute through the executor (handles full flow)
        result = await executor.execute(
            agent_id=request.agent_id,
            prompt=request.prompt,
            context=request.context,
            user=request.user,
        )
        
        return ExecuteResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal execution error")


# Agent registration
@router.post("/agents")
async def register_agent(request: RegisterAgentRequest):
    """Register a new AI agent."""
    logger.info(f"Registering agent: {request.name}")
    
    try:
        agent = registry.register_agent(
            name=request.name,
            model=request.model,
            risk_level=request.risk_level,
            policies=request.policies,
            metadata=request.metadata,
        )
        
        return {
            "agent_id": agent["id"],
            "status": "registered",
            "risk_level": agent["risk_level"],
            "policies": agent["policies"],
        }
    
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed")


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details."""
    agent = registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("/agents")
async def list_agents():
    """List all registered agents."""
    return {"agents": registry.list_agents()}


# Kill switch endpoints
@router.post("/kill-switch/activate")
async def activate_kill_switch(request: KillSwitchRequest):
    """
    Activate the kill switch.
    
    This is the "oh shit" button. Must be instant and reliable.
    """
    logger.warning(f"Kill switch activation requested: scope={request.scope} reason={request.reason}")
    
    result = kill_switch.activate(
        scope=request.scope,
        agent_id=request.agent_id,
        reason=request.reason,
    )
    
    # Log to observability
    obs_logger.log_kill_switch_event(
        action="activate",
        scope=request.scope,
        agent_id=request.agent_id,
        reason=request.reason,
    )
    
    return result


@router.post("/kill-switch/deactivate")
async def deactivate_kill_switch(scope: str = "global", agent_id: Optional[str] = None):
    """Deactivate the kill switch."""
    logger.info(f"Kill switch deactivation requested: scope={scope}")
    
    result = kill_switch.deactivate(scope=scope, agent_id=agent_id)
    
    obs_logger.log_kill_switch_event(
        action="deactivate",
        scope=scope,
        agent_id=agent_id,
        reason="Manual deactivation",
    )
    
    return result


@router.get("/kill-switch/status")
async def kill_switch_status():
    """Get kill switch status."""
    return kill_switch.get_status()


# Observability endpoints
@router.get("/logs")
async def get_logs(
    user: Optional[str] = None,
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
):
    """Query audit logs."""
    return obs_logger.query_logs(
        user=user,
        agent_id=agent_id,
        status=status,
        limit=limit,
    )


@router.get("/logs/{execution_id}")
async def get_execution_log(execution_id: str):
    """Get detailed log for a specific execution."""
    log = obs_logger.get_execution_log(execution_id)
    if not log:
        raise HTTPException(status_code=404, detail="Execution log not found")
    return log


@router.get("/logs/{execution_id}/replay")
async def replay_execution(execution_id: str):
    """Replay a specific execution (for audit/debugging)."""
    replay = obs_logger.replay_execution(execution_id)
    if not replay:
        raise HTTPException(status_code=404, detail="Execution not found")
    return replay


# Policy endpoints
@router.get("/policies")
async def list_policies():
    """List all available policies."""
    return {"policies": policy_evaluator.list_policies()}


@router.get("/policies/{policy_id}")
async def get_policy(policy_id: str):
    """Get policy details."""
    policy = policy_evaluator.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


# Health and status
@router.get("/status")
async def gateway_status():
    """Get comprehensive gateway status."""
    return {
        "gateway": "operational",
        "kill_switch": kill_switch.get_status(),
        "registry": {"agents": len(registry.list_agents())},
        "policies": {"count": len(policy_evaluator.list_policies())},
    }
