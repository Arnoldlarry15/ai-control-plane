"""
Observability Storage: Immutable event storage.

V1: In-memory (good for demo)
V2+: Time-series database (InfluxDB, TimescaleDB, etc.)
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ObservabilityStorage:
    """
    In-memory storage for observability events.
    
    Append-only. Immutable. Simple.
    """
    
    def __init__(self):
        # Append-only event log
        self._events: List[Dict[str, Any]] = []
        logger.info("Observability storage initialized (in-memory)")
    
    def store_event(self, event: Dict[str, Any]):
        """
        Store an event. Append-only.
        
        Args:
            event: Event data
        """
        self._events.append(event)
        logger.debug(f"Event stored: {event.get('event_type')} id={event.get('event_id')}")
    
    def query(
        self,
        user: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        event_type: Optional[str] = None,
        execution_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query events with filters.
        
        Args:
            user: Filter by user
            agent_id: Filter by agent
            status: Filter by status
            event_type: Filter by event type
            execution_id: Filter by execution ID
            limit: Maximum results
        
        Returns:
            List of matching events
        """
        results = self._events
        
        # Apply filters
        if user:
            results = [e for e in results if e.get("user") == user]
        
        if agent_id:
            results = [e for e in results if e.get("agent_id") == agent_id]
        
        if status:
            results = [e for e in results if e.get("status") == status]
        
        if event_type:
            results = [e for e in results if e.get("event_type") == event_type]
        
        if execution_id:
            results = [e for e in results if e.get("execution_id") == execution_id]
        
        # Return most recent events up to limit
        return results[-limit:]
    
    def count(self) -> int:
        """Get total event count."""
        return len(self._events)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        event_types: Dict[str, int] = {}
        for event in self._events:
            event_type = event.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            "total_events": len(self._events),
            "by_type": event_types,
        }
