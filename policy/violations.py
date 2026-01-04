"""
Policy Violations: Tracking and reporting policy violations.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ViolationTracker:
    """
    Track policy violations for monitoring and alerting.
    """
    
    def __init__(self):
        self._violations: List[Dict[str, Any]] = []
        logger.info("Violation tracker initialized")
    
    def record_violation(
        self,
        policy_id: str,
        reason: str,
        agent_id: str,
        user: str,
        prompt: str,
        execution_id: str,
    ):
        """
        Record a policy violation.
        
        Args:
            policy_id: ID of violated policy
            reason: Violation reason
            agent_id: Agent that attempted execution
            user: User who made the request
            prompt: Input prompt (may be redacted)
            execution_id: Execution ID
        """
        violation = {
            "policy_id": policy_id,
            "reason": reason,
            "agent_id": agent_id,
            "user": user,
            "prompt": prompt[:100],  # Truncate for storage
            "execution_id": execution_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self._violations.append(violation)
        
        logger.warning(
            f"Policy violation recorded: {policy_id} - {reason} "
            f"(agent={agent_id}, user={user}, exec={execution_id})"
        )
    
    def get_violations(
        self,
        policy_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query violations.
        
        Args:
            policy_id: Filter by policy
            agent_id: Filter by agent
            user: Filter by user
            limit: Maximum number of results
        
        Returns:
            List of violations
        """
        violations = self._violations
        
        if policy_id:
            violations = [v for v in violations if v["policy_id"] == policy_id]
        
        if agent_id:
            violations = [v for v in violations if v["agent_id"] == agent_id]
        
        if user:
            violations = [v for v in violations if v["user"] == user]
        
        return violations[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get violation statistics.
        
        Returns:
            Statistics about policy violations
        """
        if not self._violations:
            return {"total": 0, "by_policy": {}, "by_agent": {}, "by_user": {}}
        
        # Count by policy
        by_policy: Dict[str, int] = {}
        by_agent: Dict[str, int] = {}
        by_user: Dict[str, int] = {}
        
        for v in self._violations:
            by_policy[v["policy_id"]] = by_policy.get(v["policy_id"], 0) + 1
            by_agent[v["agent_id"]] = by_agent.get(v["agent_id"], 0) + 1
            if v["user"]:
                by_user[v["user"]] = by_user.get(v["user"], 0) + 1
        
        return {
            "total": len(self._violations),
            "by_policy": by_policy,
            "by_agent": by_agent,
            "by_user": by_user,
        }


# Global tracker instance
from typing import Optional as Opt
_tracker: Opt[ViolationTracker] = None


def get_tracker() -> ViolationTracker:
    """Get global violation tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = ViolationTracker()
    return _tracker
