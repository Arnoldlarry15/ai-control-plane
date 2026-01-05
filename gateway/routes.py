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

# Import singleton services
from gateway.services import (
    get_registry,
    get_kill_switch,
    get_policy_evaluator,
    get_observability_logger,
)

# Initialize services (singletons)
registry = get_registry()
kill_switch = get_kill_switch()
policy_evaluator = get_policy_evaluator()
obs_logger = get_observability_logger()

# Initialize executor with shared services
executor = Executor(
    kill_switch=kill_switch,
    registry=registry,
    policy_evaluator=policy_evaluator,
    obs_logger=obs_logger,
)


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
    
    # Execute through the executor (handles full flow)
    # Let ControlPlaneErrors bubble up to be handled by error handlers
    result = await executor.execute(
        agent_id=request.agent_id,
        prompt=request.prompt,
        context=request.context,
        user=request.user,
    )
    
    return ExecuteResponse(**result)


# Agent registration
@router.post("/agents")
async def register_agent(request: RegisterAgentRequest):
    """Register a new AI agent."""
    logger.info(f"Registering agent: {request.name}")
    
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


# Enhanced platform endpoints

@router.get("/audit/integrity")
async def verify_audit_integrity():
    """
    Verify cryptographic integrity of audit trail.
    
    Returns integrity status with tamper detection.
    """
    try:
        from observability.audit_trail import AuditTrail
        audit_trail = AuditTrail()  # In production, use shared instance
        
        integrity = audit_trail.verify_integrity()
        return integrity
    except Exception as e:
        logger.error(f"Audit integrity check failed: {e}")
        return {
            "valid": False,
            "error": str(e),
            "message": "Audit integrity check unavailable"
        }


@router.get("/audit/export")
async def export_audit_trail(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json"
):
    """
    Export audit trail for compliance.
    
    Supports JSON and CSV formats.
    Subpoena-ready exports with cryptographic verification.
    """
    try:
        from observability.audit_trail import AuditTrail
        audit_trail = AuditTrail()  # In production, use shared instance
        
        export_data = audit_trail.export_for_compliance(
            start_date=start_date,
            end_date=end_date,
            format=format
        )
        
        if format == "csv":
            from fastapi.responses import Response
            return Response(
                content=export_data,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=audit_trail.csv"}
            )
        
        return {"export": export_data}
    except Exception as e:
        logger.error(f"Audit export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/chain-of-custody/{execution_id}")
async def get_chain_of_custody(execution_id: str):
    """
    Get chain of custody for specific execution.
    
    This is what you present in court or to regulators.
    Includes full timeline with cryptographic verification.
    """
    try:
        from observability.audit_trail import AuditTrail
        audit_trail = AuditTrail()  # In production, use shared instance
        
        chain = audit_trail.get_chain_of_custody(execution_id)
        return chain
    except Exception as e:
        logger.error(f"Chain of custody retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plugins")
async def list_plugins():
    """
    List all registered plugins.
    
    Shows available extensions: risk scorers, compliance modules, hooks, etc.
    """
    try:
        from policy.plugins import PluginRegistry
        plugin_registry = PluginRegistry()  # In production, use shared instance
        
        return {"plugins": plugin_registry.list_plugins()}
    except Exception as e:
        logger.error(f"Plugin listing failed: {e}")
        return {"plugins": [], "error": str(e)}


@router.post("/policies/dry-run")
async def dry_run_policy(
    agent_id: str,
    prompt: str,
    context: Dict[str, Any] = {}
):
    """
    Test policy evaluation without executing.
    
    Shows what would happen without actually executing AI.
    Useful for policy testing and debugging.
    """
    try:
        from policy.explainer import PolicyExplainer
        
        # Get agent
        agent = registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Evaluate policies
        enhanced_context = {
            **context,
            "agent": agent,
            "agent_id": agent_id,
            "prompt": prompt,
        }
        
        decision = policy_evaluator.evaluate(
            agent=agent,
            prompt=prompt,
            context=context,
            user=context.get("user"),
        )
        
        # Generate explanation
        explainer = PolicyExplainer()
        all_policies = policy_evaluator.list_policies()
        
        report = explainer.generate_dry_run_report(
            context=enhanced_context,
            all_policies=all_policies
        )
        
        return {
            "dry_run": True,
            "decision": decision,
            "report": report,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dry-run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies/templates")
async def list_policy_templates():
    """
    List available policy templates.
    
    Pre-built templates for common use cases.
    """
    try:
        from policy.dsl import POLICY_TEMPLATES
        
        return {
            "templates": [
                {
                    "id": template_id,
                    "name": template["name"],
                    "description": template["description"],
                }
                for template_id, template in POLICY_TEMPLATES.items()
            ]
        }
    except Exception as e:
        logger.error(f"Template listing failed: {e}")
        return {"templates": [], "error": str(e)}


@router.get("/policies/templates/{template_id}")
async def get_policy_template(template_id: str):
    """
    Get a specific policy template.
    
    Returns template definition with variable placeholders.
    """
    try:
        from policy.dsl import POLICY_TEMPLATES
        
        if template_id not in POLICY_TEMPLATES:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {"template": POLICY_TEMPLATES[template_id]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Compliance API Routes
# ============================================================================

class ComplianceValidateRequest(BaseModel):
    """Request to validate input against compliance standards."""
    input_text: str = Field(..., description="Text to validate")
    standards: Optional[List[str]] = Field(None, description="Compliance standards to check (gdpr, hipaa, soc2, pci-dss)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


@router.get("/compliance/standards")
async def list_compliance_standards():
    """
    List available compliance standards.
    
    Returns all supported compliance standards with descriptions.
    """
    try:
        from policy.compliance.validator import get_compliance_validator
        
        validator = get_compliance_validator()
        standards = validator.get_compliance_standards()
        
        return {
            "standards": [
                {"id": std_id, "name": std_id.upper(), "description": desc}
                for std_id, desc in standards.items()
            ],
            "total": len(standards),
        }
    except Exception as e:
        logger.error(f"Failed to list compliance standards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/standards/{standard}")
async def get_compliance_standard(standard: str):
    """
    Get detailed information about a compliance standard.
    
    Returns policy rules, references, and implementation details.
    """
    try:
        from policy.compliance.validator import get_compliance_validator
        
        validator = get_compliance_validator()
        details = validator.get_standard_details(standard)
        
        return {"standard": standard.upper(), "details": details}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get compliance standard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance/validate")
async def validate_compliance(request: ComplianceValidateRequest):
    """
    Validate input text against compliance policies.
    
    Checks input against specified compliance standards and returns
    compliance status, violations, and warnings.
    """
    try:
        from policy.compliance.validator import get_compliance_validator
        
        validator = get_compliance_validator()
        result = validator.validate_input(
            input_text=request.input_text,
            standards=request.standards or [],
            context=request.context,
        )
        
        return result
    except Exception as e:
        logger.error(f"Compliance validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/report/{agent_id}")
async def generate_compliance_report(
    agent_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    standards: Optional[str] = None,
):
    """
    Generate compliance report for an agent.
    
    Creates a compliance report for the specified agent over a time range.
    
    Query parameters:
    - start_date: ISO 8601 date (default: 30 days ago)
    - end_date: ISO 8601 date (default: now)
    - standards: Comma-separated list of standards (default: all)
    """
    try:
        from datetime import datetime, timedelta
        from policy.compliance.validator import get_compliance_validator
        
        # Parse dates
        if end_date:
            time_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            time_end = datetime.utcnow()
        
        if start_date:
            time_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            time_start = time_end - timedelta(days=30)
        
        # Parse standards
        standards_list = None
        if standards:
            standards_list = [s.strip() for s in standards.split(',')]
        
        validator = get_compliance_validator()
        report = validator.generate_compliance_report(
            agent_id=agent_id,
            time_range_start=time_start,
            time_range_end=time_end,
            standards=standards_list,
        )
        
        return report
    except Exception as e:
        logger.error(f"Compliance report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
