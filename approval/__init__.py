"""
Human-in-the-Loop Approval Module

Provides approval workflows with:
- Multi-level approval chains
- Timeout handling
- Escalation paths
- Decision rationale preservation
"""

from approval.models import ApprovalRequest
from approval.queue import ApprovalQueue
from approval.service import ApprovalService
from approval.workflows import (
    ApprovalWorkflow,
    EscalationRule,
    EscalationLevel,
    ApprovalOutcome,
    ApprovalDecisionRecord,
    DEFAULT_WORKFLOWS,
)

__version__ = "0.1.0"

__all__ = [
    "ApprovalRequest",
    "ApprovalQueue",
    "ApprovalService",
    "ApprovalWorkflow",
    "EscalationRule",
    "EscalationLevel",
    "ApprovalOutcome",
    "ApprovalDecisionRecord",
    "DEFAULT_WORKFLOWS",
]
