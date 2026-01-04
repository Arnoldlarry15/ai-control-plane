"""
SDK Exceptions.
"""


class ControlPlaneException(Exception):
    """Base exception for control plane errors."""
    
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ExecutionBlockedError(ControlPlaneException):
    """Raised when execution is blocked by policy or kill switch."""
    
    def __init__(self, reason: str, details: dict = None):
        super().__init__(
            message=f"Execution blocked: {reason}",
            status_code=403,
            details=details,
        )


class AgentNotFoundError(ControlPlaneException):
    """Raised when agent is not registered."""
    
    def __init__(self, agent_id: str):
        super().__init__(
            message=f"Agent not found: {agent_id}",
            status_code=404,
            details={"agent_id": agent_id},
        )


class ApprovalPendingError(ControlPlaneException):
    """Raised when execution requires approval."""
    
    def __init__(self, approval_id: str, reason: str):
        super().__init__(
            message=f"Approval required: {reason}",
            status_code=202,
            details={"approval_id": approval_id, "reason": reason},
        )
