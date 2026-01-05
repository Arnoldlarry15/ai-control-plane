"""
Approval Service: Human-in-the-loop workflow management.
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from approval.models import ApprovalRequest
from approval.queue import ApprovalQueue
from approval.workflows import (
    ApprovalWorkflow,
    ApprovalDecisionRecord,
    ApprovalOutcome,
    DEFAULT_WORKFLOWS,
)

logger = logging.getLogger(__name__)


class ApprovalService:
    """
    Service for managing human approval workflows.
    
    Handles approval requests, queuing, timeout handling, escalation paths,
    and decision rationale preservation.
    """
    
    def __init__(self):
        self.queue = ApprovalQueue()
        self.workflows: Dict[str, ApprovalWorkflow] = DEFAULT_WORKFLOWS.copy()
        self.decision_records: Dict[str, List[ApprovalDecisionRecord]] = {}
        logger.info("Approval service initialized with workflows")
    
    def add_workflow(self, workflow: ApprovalWorkflow):
        """Add a custom approval workflow"""
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"Workflow added: {workflow.workflow_id}")
    
    def get_workflow(self, workflow_id: str) -> Optional[ApprovalWorkflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def request_approval(
        self,
        execution_id: str,
        agent_id: str,
        prompt: str,
        reason: str,
        user: Optional[str] = None,
        policy_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        workflow_id: str = "standard",
    ) -> Dict[str, Any]:
        """
        Request human approval for an execution.
        
        Args:
            execution_id: Execution identifier
            agent_id: Agent identifier
            prompt: User prompt
            reason: Reason approval is required
            user: User identifier
            policy_id: Policy that triggered escalation
            context: Additional context
            workflow_id: Workflow to use (default: "standard")
        
        Returns:
            Approval request data
        """
        approval_id = f"approval-{str(uuid.uuid4())[:8]}"
        
        # Get workflow
        workflow = self.workflows.get(workflow_id, self.workflows["standard"])
        
        # Enrich context with workflow info
        enriched_context = context or {}
        enriched_context["workflow_id"] = workflow_id
        enriched_context["timeout_seconds"] = workflow.timeout_seconds
        
        approval = ApprovalRequest(
            approval_id=approval_id,
            execution_id=execution_id,
            agent_id=agent_id,
            user=user,
            prompt=prompt,
            reason=reason,
            policy_id=policy_id,
            status="pending",
            requested_at=time.time(),
            context=enriched_context,
        )
        
        self.queue.enqueue(approval)
        
        logger.info(
            f"Approval requested: {approval_id} "
            f"for execution {execution_id} (reason: {reason}, workflow: {workflow_id})"
        )
        
        return {
            "approval_id": approval_id,
            "execution_id": execution_id,
            "status": "pending",
            "reason": reason,
            "requested_at": approval.requested_at,
            "workflow_id": workflow_id,
            "timeout_seconds": workflow.timeout_seconds,
        }
    
    def approve(
        self,
        approval_id: str,
        reviewer: str,
        reviewer_role: str = "approver",
        rationale: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Approve a request with full decision rationale.
        
        Args:
            approval_id: Approval identifier
            reviewer: Reviewer identifier
            reviewer_role: Reviewer's role
            rationale: Required rationale for the decision
            comment: Optional additional comment
        
        Returns:
            Approval result
        """
        approval = self.queue.get_by_id(approval_id)
        if not approval:
            raise ValueError(f"Approval not found: {approval_id}")
        
        # Get workflow
        workflow_id = approval.context.get("workflow_id", "standard")
        workflow = self.workflows.get(workflow_id, self.workflows["standard"])
        
        # Check if user is authorized
        if not workflow.is_user_authorized(reviewer_role):
            raise PermissionError(
                f"Role {reviewer_role} not authorized to approve "
                f"(required: {workflow.required_approver_roles})"
            )
        
        # Require rationale if configured
        if workflow.require_rationale and not rationale:
            raise ValueError("Rationale is required for this approval")
        
        # Update approval status
        self.queue.update_status(
            approval_id=approval_id,
            status="approved",
            reviewer=reviewer,
            comment=comment,
            reviewed_at=time.time(),
        )
        
        # Create decision record
        decision_record = ApprovalDecisionRecord(
            record_id=f"decision-{uuid.uuid4().hex[:8]}",
            approval_id=approval_id,
            decision=ApprovalOutcome.APPROVED,
            decided_at=datetime.utcnow(),
            decided_by=reviewer,
            decided_by_role=reviewer_role,
            rationale=rationale or comment or "Approved",
            risk_level=approval.context.get("risk_level"),
            reviewed_context=approval.context,
            workflow_id=workflow_id,
        )
        
        # Store decision record
        if approval_id not in self.decision_records:
            self.decision_records[approval_id] = []
        self.decision_records[approval_id].append(decision_record)
        
        logger.info(
            f"Approval granted: {approval_id} by {reviewer} ({reviewer_role})"
        )
        
        return {
            "approval_id": approval_id,
            "status": "approved",
            "reviewer": reviewer,
            "reviewer_role": reviewer_role,
            "rationale": rationale,
            "reviewed_at": time.time(),
            "decision_record_id": decision_record.record_id,
        }
    
    def reject(
        self,
        approval_id: str,
        reviewer: str,
        reviewer_role: str = "approver",
        rationale: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reject a request with full decision rationale.
        
        Args:
            approval_id: Approval identifier
            reviewer: Reviewer identifier
            reviewer_role: Reviewer's role
            rationale: Required rationale for the decision
            comment: Optional additional comment
        
        Returns:
            Rejection result
        """
        approval = self.queue.get_by_id(approval_id)
        if not approval:
            raise ValueError(f"Approval not found: {approval_id}")
        
        # Get workflow
        workflow_id = approval.context.get("workflow_id", "standard")
        workflow = self.workflows.get(workflow_id, self.workflows["standard"])
        
        # Require rationale if configured
        if workflow.require_rationale and not rationale:
            raise ValueError("Rationale is required for this rejection")
        
        # Update approval status
        self.queue.update_status(
            approval_id=approval_id,
            status="rejected",
            reviewer=reviewer,
            comment=comment,
            reviewed_at=time.time(),
        )
        
        # Create decision record
        decision_record = ApprovalDecisionRecord(
            record_id=f"decision-{uuid.uuid4().hex[:8]}",
            approval_id=approval_id,
            decision=ApprovalOutcome.REJECTED,
            decided_at=datetime.utcnow(),
            decided_by=reviewer,
            decided_by_role=reviewer_role,
            rationale=rationale or comment or "Rejected",
            risk_level=approval.context.get("risk_level"),
            reviewed_context=approval.context,
            workflow_id=workflow_id,
        )
        
        # Store decision record
        if approval_id not in self.decision_records:
            self.decision_records[approval_id] = []
        self.decision_records[approval_id].append(decision_record)
        
        logger.info(
            f"Approval rejected: {approval_id} by {reviewer} ({reviewer_role})"
        )
        
        return {
            "approval_id": approval_id,
            "status": "rejected",
            "reviewer": reviewer,
            "reviewer_role": reviewer_role,
            "rationale": rationale,
            "reviewed_at": time.time(),
            "decision_record_id": decision_record.record_id,
        }
    
    def check_timeouts(self) -> List[Dict[str, Any]]:
        """
        Check for timed-out approvals and handle them.
        
        Returns:
            List of timed-out approvals that were handled
        """
        handled = []
        pending = self.queue.get_pending()
        
        for approval in pending:
            workflow_id = approval.context.get("workflow_id", "standard")
            workflow = self.workflows.get(workflow_id, self.workflows["standard"])
            
            requested_datetime = datetime.fromtimestamp(approval.requested_at)
            
            if workflow.is_expired(requested_datetime):
                # Handle timeout based on workflow configuration
                if workflow.timeout_action == "reject":
                    self._handle_timeout_reject(approval, workflow)
                elif workflow.timeout_action == "approve":
                    self._handle_timeout_approve(approval, workflow)
                else:  # escalate
                    self._handle_timeout_escalate(approval, workflow)
                
                handled.append({
                    "approval_id": approval.approval_id,
                    "action": workflow.timeout_action,
                    "workflow_id": workflow_id,
                })
        
        return handled
    
    def _handle_timeout_reject(self, approval: ApprovalRequest, workflow: ApprovalWorkflow):
        """Handle timeout by rejecting"""
        self.queue.update_status(
            approval_id=approval.approval_id,
            status="timeout",
            reviewer="system",
            comment="Approval request timed out and was rejected",
            reviewed_at=time.time(),
        )
        logger.warning(f"Approval timed out and rejected: {approval.approval_id}")
    
    def _handle_timeout_approve(self, approval: ApprovalRequest, workflow: ApprovalWorkflow):
        """Handle timeout by auto-approving"""
        self.queue.update_status(
            approval_id=approval.approval_id,
            status="approved",
            reviewer="system",
            comment="Approval request timed out and was auto-approved",
            reviewed_at=time.time(),
        )
        logger.warning(f"Approval timed out and auto-approved: {approval.approval_id}")
    
    def _handle_timeout_escalate(self, approval: ApprovalRequest, workflow: ApprovalWorkflow):
        """Handle timeout by escalating"""
        # Find escalation rule for timeout
        requested_datetime = datetime.fromtimestamp(approval.requested_at)
        escalation_rule = workflow.should_escalate(
            requested_at=requested_datetime,
            rejection_count=0,
            risk_level=approval.context.get("risk_level")
        )
        
        if escalation_rule:
            logger.warning(
                f"Approval timed out and escalated: {approval.approval_id} "
                f"to {escalation_rule.escalate_to_level}"
            )
            # In V2+, would trigger notifications and re-queue with new approvers
        else:
            # No escalation rule found, default to rejection
            self._handle_timeout_reject(approval, workflow)
    
    def get_decision_history(self, approval_id: str) -> List[Dict[str, Any]]:
        """
        Get complete decision history for an approval.
        
        Args:
            approval_id: Approval identifier
        
        Returns:
            List of decision records
        """
        records = self.decision_records.get(approval_id, [])
        return [record.to_audit_log_entry() for record in records]
    
    def get_pending(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get all pending approval requests.
        
        Args:
            limit: Maximum requests to return
        
        Returns:
            List of pending requests
        """
        pending = self.queue.get_pending(limit=limit)
        
        return {
            "pending": [req.model_dump() for req in pending],
            "count": len(pending),
        }
    
    def get_status(self, approval_id: str) -> Optional[Dict[str, Any]]:
        """
        Get approval status with decision history.
        
        Args:
            approval_id: Approval identifier
        
        Returns:
            Approval data with decision history or None
        """
        approval = self.queue.get_by_id(approval_id)
        if not approval:
            return None
        
        result = approval.model_dump()
        result["decision_history"] = self.get_decision_history(approval_id)
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get approval queue statistics."""
        stats = self.queue.get_stats()
        stats["workflows"] = list(self.workflows.keys())
        stats["decision_records"] = sum(
            len(records) for records in self.decision_records.values()
        )
        return stats
