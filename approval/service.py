"""
Approval Service: Human-in-the-loop workflow management.
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional

from approval.models import ApprovalRequest
from approval.queue import ApprovalQueue

logger = logging.getLogger(__name__)


class ApprovalService:
    """
    Service for managing human approval workflows.
    
    Handles approval requests, queuing, and decision tracking.
    """
    
    def __init__(self):
        self.queue = ApprovalQueue()
        logger.info("Approval service initialized")
    
    def request_approval(
        self,
        execution_id: str,
        agent_id: str,
        prompt: str,
        reason: str,
        user: Optional[str] = None,
        policy_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
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
        
        Returns:
            Approval request data
        """
        approval_id = f"approval-{str(uuid.uuid4())[:8]}"
        
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
            context=context or {},
        )
        
        self.queue.enqueue(approval)
        
        logger.info(
            f"Approval requested: {approval_id} "
            f"for execution {execution_id} (reason: {reason})"
        )
        
        return {
            "approval_id": approval_id,
            "execution_id": execution_id,
            "status": "pending",
            "reason": reason,
            "requested_at": approval.requested_at,
        }
    
    def approve(
        self,
        approval_id: str,
        reviewer: str,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Approve a request.
        
        Args:
            approval_id: Approval identifier
            reviewer: Reviewer identifier
            comment: Optional reviewer comment
        
        Returns:
            Approval result
        """
        self.queue.update_status(
            approval_id=approval_id,
            status="approved",
            reviewer=reviewer,
            comment=comment,
            reviewed_at=time.time(),
        )
        
        logger.info(f"Approval granted: {approval_id} by {reviewer}")
        
        return {
            "approval_id": approval_id,
            "status": "approved",
            "reviewer": reviewer,
            "reviewed_at": time.time(),
        }
    
    def reject(
        self,
        approval_id: str,
        reviewer: str,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reject a request.
        
        Args:
            approval_id: Approval identifier
            reviewer: Reviewer identifier
            comment: Optional reviewer comment
        
        Returns:
            Rejection result
        """
        self.queue.update_status(
            approval_id=approval_id,
            status="rejected",
            reviewer=reviewer,
            comment=comment,
            reviewed_at=time.time(),
        )
        
        logger.info(f"Approval rejected: {approval_id} by {reviewer}")
        
        return {
            "approval_id": approval_id,
            "status": "rejected",
            "reviewer": reviewer,
            "reviewed_at": time.time(),
        }
    
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
        Get approval status.
        
        Args:
            approval_id: Approval identifier
        
        Returns:
            Approval data or None
        """
        approval = self.queue.get_by_id(approval_id)
        if approval:
            return approval.model_dump()
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get approval queue statistics."""
        return self.queue.get_stats()
