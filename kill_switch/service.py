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
Kill Switch Service: The "oh shit" button.

This must be:
- Instant (sub-millisecond checks)
- Central (single source of truth)
- Logged (every activation tracked)

This alone justifies the platform to risk teams.
"""

import logging
import time
from typing import Dict, Any, Optional

from kill_switch.state import KillSwitchState

logger = logging.getLogger(__name__)


class KillSwitchService:
    """
    Kill switch service for emergency AI shutdown.
    
    Provides instant, reliable controls to halt AI execution.
    
    Scopes:
    - global: Shut down ALL AI execution
    - agent: Shut down specific agent
    """
    
    def __init__(self):
        self.state = KillSwitchState()
        logger.info("Kill switch service initialized")
    
    def activate(
        self,
        scope: str,
        reason: str,
        agent_id: Optional[str] = None,
        activated_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Activate kill switch.
        
        Args:
            scope: "global" or "agent"
            reason: Reason for activation
            agent_id: Required if scope is "agent"
            activated_by: User/system that activated it
        
        Returns:
            Activation result with timestamp and details
        """
        if scope not in ["global", "agent"]:
            raise ValueError(f"Invalid scope: {scope}. Must be 'global' or 'agent'")
        
        if scope == "agent" and not agent_id:
            raise ValueError("agent_id required for agent-scoped kill switch")
        
        logger.warning(
            f"KILL SWITCH ACTIVATED: scope={scope} "
            f"agent={agent_id} reason='{reason}' by={activated_by}"
        )
        
        # Activate in state
        activated_at = time.time()
        self.state.activate(
            scope=scope,
            agent_id=agent_id,
            reason=reason,
            activated_by=activated_by,
            activated_at=activated_at,
        )
        
        return {
            "status": "activated",
            "scope": scope,
            "agent_id": agent_id,
            "reason": reason,
            "activated_by": activated_by,
            "activated_at": activated_at,
        }
    
    def deactivate(
        self,
        scope: str = "global",
        agent_id: Optional[str] = None,
        deactivated_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Deactivate kill switch.
        
        Args:
            scope: "global" or "agent"
            agent_id: Required if scope is "agent"
            deactivated_by: User/system that deactivated it
        
        Returns:
            Deactivation result
        """
        logger.info(
            f"Kill switch deactivated: scope={scope} agent={agent_id} by={deactivated_by}"
        )
        
        # Deactivate in state
        self.state.deactivate(scope=scope, agent_id=agent_id)
        
        return {
            "status": "deactivated",
            "scope": scope,
            "agent_id": agent_id,
            "deactivated_by": deactivated_by,
            "deactivated_at": time.time(),
        }
    
    def is_active(self, scope: str, agent_id: Optional[str] = None) -> bool:
        """
        Check if kill switch is active.
        
        This must be INSTANT. Sub-millisecond. No database calls.
        
        Args:
            scope: "global" or "agent"
            agent_id: Required if scope is "agent"
        
        Returns:
            True if kill switch blocks execution
        """
        return self.state.is_active(scope=scope, agent_id=agent_id)
    
    def get_reason(self, scope: str, agent_id: Optional[str] = None) -> str:
        """Get the reason why kill switch is active."""
        return self.state.get_reason(scope=scope, agent_id=agent_id)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get complete kill switch status.
        
        Returns:
            Status for global and all agent-specific kill switches
        """
        return self.state.get_all_status()
