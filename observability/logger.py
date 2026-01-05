"""
Observability Logger: Everything logged.

This is what lawyers, auditors, and postmortems live on.
If you build nothing else well, build this well.
"""

import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from observability.events import (
    ExecutionEvent,
    PolicyEvent,
    KillSwitchEvent,
    ApprovalEvent,
)
from observability.storage import ObservabilityStorage

logger = logging.getLogger(__name__)


class ObservabilityLogger:
    """
    Observability logger for complete audit trail.
    
    Logs:
    - Every execution request and response
    - Every policy decision
    - Every kill switch activation
    - Every approval decision
    
    Immutable, structured, searchable.
    """
    
    def __init__(self):
        self.storage = ObservabilityStorage()
        logger.info("Observability logger initialized")
    
    def log_execution(
        self,
        execution_id: str,
        agent_id: str,
        prompt: str,
        response: Optional[str],
        status: str,
        latency_ms: int,
        user: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        policy_id: Optional[str] = None,
        error: Optional[str] = None,
    ):
        """
        Log an AI execution event.
        
        Args:
            execution_id: Unique execution ID
            agent_id: Agent identifier
            prompt: User prompt/input
            response: AI response (if executed)
            status: Execution status
            latency_ms: Execution latency
            user: User identifier
            context: Execution context
            reason: Reason for block/escalate
            policy_id: Policy that triggered block/escalate
            error: Error message if status is error
        """
        now = time.time()
        
        event = ExecutionEvent(
            event_id=str(uuid.uuid4()),
            execution_id=execution_id,
            agent_id=agent_id,
            user=user,
            prompt=prompt,
            response=response,
            status=status,
            latency_ms=latency_ms,
            policy_decision={
                "reason": reason,
                "policy_id": policy_id,
            } if reason else None,
            context=context,
            error=error,
            timestamp=now,
            iso_timestamp=datetime.utcnow().isoformat(),
        )
        
        self.storage.store_event(event.model_dump())
        
        logger.info(
            f"Execution logged: {execution_id} "
            f"status={status} latency={latency_ms}ms"
        )
    
    def log_policy_event(
        self,
        execution_id: str,
        policy_id: str,
        action: str,
        agent_id: str,
        reason: Optional[str] = None,
        user: Optional[str] = None,
    ):
        """Log a policy evaluation event."""
        now = time.time()
        
        event = PolicyEvent(
            event_id=str(uuid.uuid4()),
            execution_id=execution_id,
            policy_id=policy_id,
            action=action,
            reason=reason,
            agent_id=agent_id,
            user=user,
            timestamp=now,
            iso_timestamp=datetime.utcnow().isoformat(),
        )
        
        self.storage.store_event(event.model_dump())
        
        logger.debug(f"Policy event logged: {policy_id} action={action}")
    
    def log_kill_switch_event(
        self,
        action: str,
        scope: str,
        reason: str,
        agent_id: Optional[str] = None,
        activated_by: Optional[str] = None,
    ):
        """Log a kill switch event."""
        now = time.time()
        
        event = KillSwitchEvent(
            event_id=str(uuid.uuid4()),
            action=action,
            scope=scope,
            agent_id=agent_id,
            reason=reason,
            activated_by=activated_by,
            timestamp=now,
            iso_timestamp=datetime.utcnow().isoformat(),
        )
        
        self.storage.store_event(event.model_dump())
        
        logger.warning(
            f"Kill switch event logged: {action} scope={scope} reason='{reason}'"
        )
    
    def log_approval_event(
        self,
        approval_id: str,
        execution_id: str,
        action: str,
        reviewer: Optional[str] = None,
        comment: Optional[str] = None,
    ):
        """Log an approval workflow event."""
        now = time.time()
        
        event = ApprovalEvent(
            event_id=str(uuid.uuid4()),
            approval_id=approval_id,
            execution_id=execution_id,
            action=action,
            reviewer=reviewer,
            comment=comment,
            timestamp=now,
            iso_timestamp=datetime.utcnow().isoformat(),
        )
        
        self.storage.store_event(event.model_dump())
        
        logger.info(f"Approval event logged: {approval_id} action={action}")
    
    def query_logs(
        self,
        user: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs.
        
        Args:
            user: Filter by user
            agent_id: Filter by agent
            status: Filter by status
            event_type: Filter by event type
            limit: Maximum results
        
        Returns:
            List of matching events
        """
        return self.storage.query(
            user=user,
            agent_id=agent_id,
            status=status,
            event_type=event_type,
            limit=limit,
        )
    
    def get_execution_log(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed log for a specific execution."""
        events = self.storage.query(execution_id=execution_id, limit=10)
        if events:
            # Return the execution event (first one should be execution event)
            for event in events:
                if event.get("event_type") == "execution":
                    return event
        return None
    
    def replay_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Replay a specific execution for audit/debugging.
        
        Returns complete execution flow: request, policy evaluation, response.
        """
        events = self.storage.query(execution_id=execution_id, limit=100)
        
        if not events:
            return None
        
        return {
            "execution_id": execution_id,
            "events": events,
            "count": len(events),
        }
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent logs for dashboard display.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of recent log events
        """
        return self.storage.query(limit=limit)
