"""
Kill Switch State: In-memory state management.

This is where the actual state lives. In-memory for instant access.

V1: In-memory only (lost on restart - acceptable for V1)
V2+: Back by Redis/etcd for persistence and distributed systems
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class KillSwitchState:
    """
    In-memory state for kill switch.
    
    Fast, simple, reliable. No database round trips.
    """
    
    def __init__(self):
        # Global kill switch state
        self.global_active = False
        self.global_reason = ""
        self.global_activated_by = None
        self.global_activated_at = None
        
        # Agent-specific kill switches
        # Format: {agent_id: {active, reason, activated_by, activated_at}}
        self.agent_switches: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Kill switch state initialized (in-memory)")
    
    def activate(
        self,
        scope: str,
        reason: str,
        agent_id: Optional[str] = None,
        activated_by: Optional[str] = None,
        activated_at: Optional[float] = None,
    ):
        """Activate kill switch in state."""
        if scope == "global":
            self.global_active = True
            self.global_reason = reason
            self.global_activated_by = activated_by
            self.global_activated_at = activated_at
            logger.warning(f"Global kill switch activated: {reason}")
        
        elif scope == "agent" and agent_id:
            self.agent_switches[agent_id] = {
                "active": True,
                "reason": reason,
                "activated_by": activated_by,
                "activated_at": activated_at,
            }
            logger.warning(f"Agent kill switch activated: {agent_id} - {reason}")
    
    def deactivate(self, scope: str, agent_id: Optional[str] = None):
        """Deactivate kill switch in state."""
        if scope == "global":
            self.global_active = False
            self.global_reason = ""
            logger.info("Global kill switch deactivated")
        
        elif scope == "agent" and agent_id:
            if agent_id in self.agent_switches:
                del self.agent_switches[agent_id]
                logger.info(f"Agent kill switch deactivated: {agent_id}")
    
    def is_active(self, scope: str, agent_id: Optional[str] = None) -> bool:
        """
        Check if kill switch is active.
        
        MUST be instant. This is called on EVERY execution.
        """
        if scope == "global":
            return self.global_active
        
        elif scope == "agent" and agent_id:
            return agent_id in self.agent_switches and self.agent_switches[agent_id]["active"]
        
        return False
    
    def get_reason(self, scope: str, agent_id: Optional[str] = None) -> str:
        """Get reason for kill switch activation."""
        if scope == "global":
            return self.global_reason if self.global_active else ""
        
        elif scope == "agent" and agent_id:
            if agent_id in self.agent_switches:
                return self.agent_switches[agent_id]["reason"]
        
        return ""
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get complete status of all kill switches."""
        return {
            "global": {
                "active": self.global_active,
                "reason": self.global_reason,
                "activated_by": self.global_activated_by,
                "activated_at": self.global_activated_at,
            },
            "agents": {
                agent_id: {
                    "active": state["active"],
                    "reason": state["reason"],
                    "activated_by": state["activated_by"],
                    "activated_at": state["activated_at"],
                }
                for agent_id, state in self.agent_switches.items()
            },
        }
