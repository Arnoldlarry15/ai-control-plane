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
Approval Queue: Priority queue for human review.

Even if V1 approvals are manual or mocked, the structure must exist.
This is future leverage.
"""

import logging
from typing import Dict, Any, List, Optional
from collections import deque

from approval.models import ApprovalRequest

logger = logging.getLogger(__name__)


class ApprovalQueue:
    """
    Priority queue for approval requests.
    
    V1: Simple FIFO queue in memory
    V2+: Persistent queue with priority, SLA tracking, notifications
    """
    
    def __init__(self):
        # Simple FIFO queue for V1
        self._queue: deque = deque()
        
        # Index by approval_id for fast lookup
        self._index: Dict[str, ApprovalRequest] = {}
        
        logger.info("Approval queue initialized (in-memory)")
    
    def enqueue(self, approval: ApprovalRequest):
        """
        Add approval request to queue.
        
        Args:
            approval: Approval request
        """
        self._queue.append(approval)
        self._index[approval.approval_id] = approval
        
        logger.info(
            f"Approval queued: {approval.approval_id} "
            f"(agent={approval.agent_id}, user={approval.user})"
        )
    
    def get_pending(self, limit: int = 100) -> List[ApprovalRequest]:
        """
        Get pending approval requests.
        
        Args:
            limit: Maximum requests to return
        
        Returns:
            List of pending requests
        """
        pending = [req for req in self._queue if req.status == "pending"]
        return pending[:limit]
    
    def get_by_id(self, approval_id: str) -> Optional[ApprovalRequest]:
        """
        Get approval request by ID.
        
        Args:
            approval_id: Approval identifier
        
        Returns:
            Approval request or None
        """
        return self._index.get(approval_id)
    
    def update_status(
        self,
        approval_id: str,
        status: str,
        reviewer: Optional[str] = None,
        comment: Optional[str] = None,
        reviewed_at: Optional[float] = None,
    ):
        """
        Update approval status.
        
        Args:
            approval_id: Approval identifier
            status: New status (approved, rejected, timeout)
            reviewer: Reviewer identifier
            comment: Review comment
            reviewed_at: Review timestamp
        """
        approval = self._index.get(approval_id)
        if not approval:
            logger.warning(f"Approval not found: {approval_id}")
            return
        
        approval.status = status
        approval.reviewer = reviewer
        approval.comment = comment
        approval.reviewed_at = reviewed_at
        
        logger.info(
            f"Approval updated: {approval_id} status={status} reviewer={reviewer}"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        pending = sum(1 for req in self._queue if req.status == "pending")
        approved = sum(1 for req in self._queue if req.status == "approved")
        rejected = sum(1 for req in self._queue if req.status == "rejected")
        timeout = sum(1 for req in self._queue if req.status == "timeout")
        
        return {
            "total": len(self._queue),
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "timeout": timeout,
        }
