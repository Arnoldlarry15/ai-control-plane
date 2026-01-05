"""
Example Lifecycle Hook Plugins

Demonstrates pre-request, post-decision, and incident trigger hooks.
"""

import logging
from typing import Dict, Any
from policy.plugins import LifecycleHookPlugin

logger = logging.getLogger(__name__)


class RequestEnrichmentHook(LifecycleHookPlugin):
    """
    Pre-request hook for enriching request context.
    
    Adds additional metadata before policy evaluation.
    """
    
    @property
    def plugin_id(self) -> str:
        return "request-enrichment-hook"
    
    @property
    def plugin_name(self) -> str:
        return "Request Enrichment Hook"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_description(self) -> str:
        return "Enriches requests with additional context"
    
    @property
    def hook_stage(self) -> str:
        return "pre_request"
    
    def on_pre_request(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich request with additional metadata.
        
        Example: Add user department, cost center, geolocation.
        """
        user = context.get('user')
        
        # In production, fetch from user directory
        enriched_context = context.copy()
        enriched_context['user_department'] = 'Engineering'
        enriched_context['cost_center'] = 'ENG-001'
        enriched_context['user_location'] = 'US-West'
        
        logger.info(f"[ENRICHMENT] Added metadata for user: {user}")
        
        return {
            "status": "continue",
            "context": enriched_context
        }


class DecisionNotificationHook(LifecycleHookPlugin):
    """
    Post-decision hook for notifications.
    
    Sends alerts when important decisions are made.
    """
    
    @property
    def plugin_id(self) -> str:
        return "decision-notification-hook"
    
    @property
    def plugin_name(self) -> str:
        return "Decision Notification Hook"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_description(self) -> str:
        return "Sends notifications for policy decisions"
    
    @property
    def hook_stage(self) -> str:
        return "post_decision"
    
    def on_post_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send notifications based on decision.
        
        Example: Alert security team on blocks, notify managers on escalations.
        """
        decision = context.get('decision', {})
        action = decision.get('action')
        
        if action == 'block':
            # In production: Send to Slack, email, PagerDuty
            logger.warning(
                f"[NOTIFICATION] Blocked request - "
                f"User: {context.get('user')}, "
                f"Reason: {decision.get('reason')}"
            )
            # self._send_slack_alert(context)
        
        elif action == 'escalate':
            logger.info(
                f"[NOTIFICATION] Escalation required - "
                f"Approval needed for {context.get('agent_id')}"
            )
            # self._notify_approvers(context)
        
        return {"status": "continue"}


class IncidentResponseHook(LifecycleHookPlugin):
    """
    Incident trigger hook for security/compliance incidents.
    
    Triggers incident response workflows.
    """
    
    @property
    def plugin_id(self) -> str:
        return "incident-response-hook"
    
    @property
    def plugin_name(self) -> str:
        return "Incident Response Hook"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_description(self) -> str:
        return "Triggers incident response for security/compliance events"
    
    @property
    def hook_stage(self) -> str:
        return "on_incident"
    
    def on_incident(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle security/compliance incidents.
        
        Example actions:
        - Alert security team
        - Create incident ticket
        - Lock affected agent
        - Trigger forensics collection
        """
        incident_type = context.get('incident_type')
        severity = context.get('severity')
        details = context.get('details', {})
        
        logger.critical(
            f"[INCIDENT] {incident_type} incident detected - "
            f"Severity: {severity}, "
            f"Agent: {context.get('agent_id')}, "
            f"User: {context.get('user')}"
        )
        
        # In production: Integrate with incident management system
        if severity in ['high', 'critical']:
            self._create_incident_ticket(context)
            self._alert_security_team(context)
            
            if incident_type == 'security':
                self._lock_agent(context.get('agent_id'))
                self._collect_forensics(context)
        
        return {
            "status": "continue",
            "incident_id": f"INC-{context.get('agent_id')}-001"
        }
    
    def _create_incident_ticket(self, context: Dict[str, Any]):
        """Create incident ticket in ticketing system."""
        logger.info(f"[INCIDENT] Creating ticket for {context.get('incident_type')}")
        # Integration with Jira, ServiceNow, etc.
    
    def _alert_security_team(self, context: Dict[str, Any]):
        """Alert security team via multiple channels."""
        logger.info("[INCIDENT] Alerting security team")
        # Integration with Slack, PagerDuty, email
    
    def _lock_agent(self, agent_id: str):
        """Lock agent to prevent further use."""
        logger.warning(f"[INCIDENT] Locking agent: {agent_id}")
        # Activate kill switch for specific agent
    
    def _collect_forensics(self, context: Dict[str, Any]):
        """Collect forensic data for investigation."""
        logger.info("[INCIDENT] Collecting forensic data")
        # Capture full context, logs, system state


class AuditComplianceHook(LifecycleHookPlugin):
    """
    Post-decision hook for compliance audit trail.
    
    Ensures all decisions are properly audited.
    """
    
    @property
    def plugin_id(self) -> str:
        return "audit-compliance-hook"
    
    @property
    def plugin_name(self) -> str:
        return "Audit Compliance Hook"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_description(self) -> str:
        return "Ensures compliance-grade audit logging"
    
    @property
    def hook_stage(self) -> str:
        return "post_decision"
    
    def on_post_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create compliance-grade audit record.
        
        Includes all required fields for regulatory compliance.
        """
        audit_record = {
            'timestamp': context.get('timestamp'),
            'user': context.get('user'),
            'agent_id': context.get('agent_id'),
            'decision': context.get('decision'),
            'policies_evaluated': context.get('policies_evaluated', []),
            'reason': context.get('decision', {}).get('reason'),
            'ip_address': context.get('ip_address'),
            'user_agent': context.get('user_agent'),
            'compliance_standard': 'SOX',  # Example: Sarbanes-Oxley
            'retention_period': '7_years',
        }
        
        logger.info(f"[AUDIT] Compliance record created: {audit_record}")
        
        # In production: Store in immutable audit storage
        # self._store_compliance_record(audit_record)
        
        return {"status": "continue", "audit_id": "AUD-001"}
