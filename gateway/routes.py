"""
API routes for the gateway.

Defines all endpoints for AI execution, policy management, and control operations.
"""

import logging
from typing import Dict, Any, Optional, List

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


# ============================================================================
# Phase 2: Trust & Compliance Endpoints
# ============================================================================

# Approval Workflow endpoints

class ApprovalActionRequest(BaseModel):
    """Request to approve or reject an approval"""
    reviewer: str = Field(..., description="Reviewer identifier")
    reviewer_role: str = Field(default="approver", description="Reviewer role")
    rationale: str = Field(..., description="Decision rationale")
    comment: Optional[str] = Field(None, description="Additional comment")


@router.get("/approvals/pending")
async def get_pending_approvals(limit: int = 100):
    """
    Get all pending approval requests.
    
    Returns list of approvals awaiting human review.
    """
    try:
        from approval.service import ApprovalService
        approval_service = ApprovalService()
        return approval_service.get_pending(limit=limit)
    except Exception as e:
        logger.error(f"Failed to get pending approvals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approvals/workflows")
async def list_approval_workflows():
    """
    List available approval workflows.
    
    Returns configured workflows with timeout and escalation settings.
    """
    try:
        from approval.service import ApprovalService
        approval_service = ApprovalService()
        
        workflows = {}
        for workflow_id, workflow in approval_service.workflows.items():
            workflows[workflow_id] = {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "required_approver_roles": workflow.required_approver_roles,
                "required_approvals": workflow.required_approvals,
                "timeout_seconds": workflow.timeout_seconds,
                "timeout_action": workflow.timeout_action,
                "escalation_rules_count": len(workflow.escalation_rules),
            }
        
        return {
            "workflows": workflows,
            "count": len(workflows),
        }
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approvals/stats")
async def get_approval_stats():
    """
    Get approval queue statistics.
    
    Returns metrics on pending, approved, rejected, and timed-out approvals.
    """
    try:
        from approval.service import ApprovalService
        approval_service = ApprovalService()
        return approval_service.get_stats()
    except Exception as e:
        logger.error(f"Failed to get approval stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approvals/{approval_id}")
async def get_approval_status(approval_id: str):
    """
    Get approval status with decision history.
    
    Returns complete approval information including decision rationale.
    """
    try:
        from approval.service import ApprovalService
        approval_service = ApprovalService()
        status = approval_service.get_status(approval_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Approval not found")
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get approval status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approvals/{approval_id}/approve")
async def approve_request(approval_id: str, request: ApprovalActionRequest):
    """
    Approve an approval request with rationale.
    
    Requires:
    - Reviewer identifier
    - Reviewer role (must have APPROVE permission)
    - Decision rationale (mandatory for compliance)
    """
    try:
        from approval.service import ApprovalService
        approval_service = ApprovalService()
        
        result = approval_service.approve(
            approval_id=approval_id,
            reviewer=request.reviewer,
            reviewer_role=request.reviewer_role,
            rationale=request.rationale,
            comment=request.comment,
        )
        
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to approve request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approvals/{approval_id}/reject")
async def reject_request(approval_id: str, request: ApprovalActionRequest):
    """
    Reject an approval request with rationale.
    
    Requires:
    - Reviewer identifier
    - Reviewer role (must have APPROVE permission)
    - Decision rationale (mandatory for compliance)
    """
    try:
        from approval.service import ApprovalService
        approval_service = ApprovalService()
        
        result = approval_service.reject(
            approval_id=approval_id,
            reviewer=request.reviewer,
            reviewer_role=request.reviewer_role,
            rationale=request.rationale,
            comment=request.comment,
        )
        
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to reject request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approvals/{approval_id}/history")
async def get_approval_history(approval_id: str):
    """
    Get complete decision history for an approval.
    
    Returns all decision records with rationale for compliance auditing.
    """
    try:
        from approval.service import ApprovalService
        approval_service = ApprovalService()
        
        history = approval_service.get_decision_history(approval_id)
        
        return {
            "approval_id": approval_id,
            "decision_history": history,
            "count": len(history),
        }
    except Exception as e:
        logger.error(f"Failed to get approval history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# OIDC Authentication endpoints

class OIDCConfigRequest(BaseModel):
    """Request to configure OIDC provider"""
    provider_name: str = Field(..., description="Provider name (e.g., auth0, okta)")
    issuer: str = Field(..., description="OIDC issuer URL")
    client_id: str = Field(..., description="Application client ID")
    client_secret: Optional[str] = Field(None, description="Client secret")
    redirect_uri: str = Field(..., description="Redirect URI")
    audience: Optional[str] = Field(None, description="API audience (Auth0)")


@router.post("/auth/oidc/configure")
async def configure_oidc_provider(request: OIDCConfigRequest):
    """
    Configure an OIDC identity provider.
    
    Supports Auth0, Okta, Azure AD, Google, and other OIDC-compliant providers.
    """
    try:
        from auth.oidc import OIDCConfig, OIDCService
        
        config = OIDCConfig(
            issuer=request.issuer,
            client_id=request.client_id,
            client_secret=request.client_secret,
            redirect_uri=request.redirect_uri,
            audience=request.audience,
        )
        
        oidc_service = OIDCService()
        provider = oidc_service.add_provider(request.provider_name, config)
        
        return {
            "status": "configured",
            "provider_name": request.provider_name,
            "issuer": config.issuer,
            "client_id": config.client_id,
        }
    except Exception as e:
        logger.error(f"Failed to configure OIDC provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/oidc/{provider_name}/authorize-url")
async def get_oidc_authorization_url(
    provider_name: str,
    state: Optional[str] = None
):
    """
    Get OIDC authorization URL for OAuth flow.
    
    Returns the URL to redirect users to for authentication.
    """
    try:
        from auth.oidc import OIDCService
        
        oidc_service = OIDCService()
        provider = oidc_service.get_provider(provider_name)
        
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"OIDC provider not found: {provider_name}"
            )
        
        auth_url = provider.get_authorization_url(state=state)
        
        return {
            "authorization_url": auth_url,
            "provider_name": provider_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get authorization URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class OIDCTokenRequest(BaseModel):
    """Request to validate OIDC token"""
    provider_name: str = Field(..., description="Provider name")
    token: str = Field(..., description="Access token or ID token")


@router.post("/auth/oidc/validate")
async def validate_oidc_token(request: OIDCTokenRequest):
    """
    Validate an OIDC token and extract user information.
    
    Returns user info including roles and permissions from the token.
    """
    try:
        from auth.oidc import OIDCService
        
        oidc_service = OIDCService()
        user_info = oidc_service.authenticate(
            provider_name=request.provider_name,
            token=request.token
        )
        
        if not user_info:
            raise HTTPException(
                status_code=401,
                detail="Token validation failed"
            )
        
        return {
            "authenticated": True,
            "user_info": user_info.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced Compliance endpoints

@router.get("/compliance/standards")
async def list_compliance_standards():
    """
    List all available compliance standards.
    
    Returns all compliance packs including GDPR, HIPAA, SOC 2, PCI-DSS,
    NIST AI RMF, and EU AI Act.
    """
    try:
        from policy.compliance import ComplianceLoader
        
        loader = ComplianceLoader()
        standards = loader.list_standards()
        
        return {
            "standards": standards,
            "count": len(standards),
        }
    except Exception as e:
        logger.error(f"Failed to list compliance standards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/standards/{standard}")
async def get_compliance_standard_details(standard: str):
    """
    Get details about a specific compliance standard.
    
    Returns policy information without loading the full policy.
    """
    try:
        from policy.compliance import ComplianceLoader
        
        loader = ComplianceLoader()
        info = loader.get_policy_info(standard)
        
        return info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get compliance standard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ComplianceValidationRequest(BaseModel):
    """Request to validate compliance"""
    input_text: str = Field(..., description="Text to validate")
    standards: List[str] = Field(..., description="Standards to check against")


@router.post("/compliance/validate")
async def validate_compliance(request: ComplianceValidationRequest):
    """
    Validate input against compliance standards.
    
    Checks input text for compliance violations across specified standards.
    Returns violations found and compliance status.
    
    Note:
        V1 Implementation: Basic structure and policy loading.
        
        Current behavior: Loads policies but does not perform actual validation
        against input text. This is a placeholder implementation.
        
        V2 Enhancement: Implement actual policy evaluation:
        1. Parse input text for sensitive patterns
        2. Evaluate against policy rules
        3. Detect violations and classify severity
        4. Generate actionable recommendations
        
        For now, this endpoint confirms policy availability and structure.
    """
    try:
        from policy.compliance import ComplianceLoader
        from policy.evaluator import PolicyEvaluator
        
        loader = ComplianceLoader()
        evaluator = PolicyEvaluator()
        
        results = {}
        violations = []
        
        for standard in request.standards:
            try:
                policy = loader.load_policy(standard)
                
                # V1: Simplified check - confirms policy loads successfully
                # TODO V2: Implement actual policy evaluation against input_text
                results[standard] = {
                    "compliant": True,  # V1: Placeholder - always returns true
                    "violations": [],
                    "rules_checked": len(policy.rules),
                    "note": "V1: Policy structure validated. Full evaluation coming in V2."
                }
            except Exception as e:
                logger.warning(f"Failed to check {standard}: {e}")
                results[standard] = {
                    "compliant": False,
                    "error": str(e),
                }
        
        return {
            "input_text": request.input_text[:100] + "..." if len(request.input_text) > 100 else request.input_text,
            "standards_checked": request.standards,
            "results": results,
            "overall_compliant": all(
                r.get("compliant", False) for r in results.values()
            ),
            "note": "V1 implementation: Policy loading validated. Full text analysis coming in V2."
        }
    except Exception as e:
        logger.error(f"Compliance validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Phase 3: Human-Centric Observability Endpoints
# ============================================================================

@router.get("/api/decisions/{execution_id}/why-blocked")
async def why_was_blocked(execution_id: str):
    """
    Answer: Why was this request blocked?
    
    Human-centric query that explains why a specific request was blocked.
    """
    try:
        # Get decision store from executor
        if not hasattr(executor, 'decision_store') or not executor.decision_store:
            raise HTTPException(
                status_code=503,
                detail="Decision record store not available"
            )
        
        result = executor.decision_store.why_blocked(execution_id)
        
        if not result.get("found"):
            raise HTTPException(
                status_code=404,
                detail=f"No decision record found for execution {execution_id}"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query why blocked: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/decisions/{execution_id}/who-approved")
async def who_approved_this(execution_id: str):
    """
    Answer: Who approved this request?
    
    Human-centric query that shows who approved a request and when.
    """
    try:
        if not hasattr(executor, 'decision_store') or not executor.decision_store:
            raise HTTPException(
                status_code=503,
                detail="Decision record store not available"
            )
        
        result = executor.decision_store.who_approved(execution_id)
        
        if not result.get("found"):
            raise HTTPException(
                status_code=404,
                detail=f"No decision record found for execution {execution_id}"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query who approved: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/decisions/{execution_id}/which-policy")
async def which_policy_fired(execution_id: str):
    """
    Answer: Which policy fired for this request?
    
    Human-centric query that shows which policy made the decision and why.
    """
    try:
        if not hasattr(executor, 'decision_store') or not executor.decision_store:
            raise HTTPException(
                status_code=503,
                detail="Decision record store not available"
            )
        
        result = executor.decision_store.which_policy_fired(execution_id)
        
        if not result.get("found"):
            raise HTTPException(
                status_code=404,
                detail=f"No decision record found for execution {execution_id}"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query which policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/decisions/{execution_id}/timeline")
async def get_decision_timeline(execution_id: str):
    """
    Get complete decision timeline for a request.
    
    Shows every decision point from request initiation to completion.
    """
    try:
        if not hasattr(executor, 'decision_store') or not executor.decision_store:
            raise HTTPException(
                status_code=503,
                detail="Decision record store not available"
            )
        
        result = executor.decision_store.get_timeline(execution_id)
        
        if not result.get("found"):
            raise HTTPException(
                status_code=404,
                detail=f"No decision record found for execution {execution_id}"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/decisions/query")
async def query_decisions(
    decision: Optional[str] = None,
    policy_id: Optional[str] = None,
    requester_id: Optional[str] = None,
    approver_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100
):
    """
    Query decision records with filters.
    
    Supports filtering by decision type, policy, requester, approver, and time range.
    """
    try:
        if not hasattr(executor, 'decision_store') or not executor.decision_store:
            raise HTTPException(
                status_code=503,
                detail="Decision record store not available"
            )
        
        records = executor.decision_store.query_decisions(
            decision=decision,
            policy_id=policy_id,
            requester_id=requester_id,
            approver_id=approver_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        return {
            "total": len(records),
            "records": [r.dict() for r in records]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query decisions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/decisions/statistics")
async def get_decision_statistics():
    """
    Get statistics about decision records.
    
    Provides aggregate statistics for observability and reporting.
    """
    try:
        if not hasattr(executor, 'decision_store') or not executor.decision_store:
            raise HTTPException(
                status_code=503,
                detail="Decision record store not available"
            )
        
        stats = executor.decision_store.get_statistics()
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
