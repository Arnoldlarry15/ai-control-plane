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
Replay: Re-execute or analyze past executions.

For audit, debugging, and understanding what happened.
"""

import logging
from typing import Dict, Any, Optional, List

from observability.storage import ObservabilityStorage

logger = logging.getLogger(__name__)


class ReplayService:
    """
    Service for replaying and analyzing past executions.
    """
    
    def __init__(self):
        self.storage = ObservabilityStorage()
        logger.info("Replay service initialized")
    
    def replay_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Replay a specific execution.
        
        Returns the complete execution flow: request, policies, response.
        """
        events = self.storage.query(execution_id=execution_id, limit=100)
        
        if not events:
            logger.warning(f"No events found for execution: {execution_id}")
            return None
        
        # Extract key events
        execution_event = None
        policy_events = []
        
        for event in events:
            if event.get("event_type") == "execution":
                execution_event = event
            elif event.get("event_type") == "policy":
                policy_events.append(event)
        
        if not execution_event:
            return None
        
        return {
            "execution_id": execution_id,
            "execution": execution_event,
            "policies": policy_events,
            "timeline": events,
        }
    
    def analyze_user_activity(self, user: str, limit: int = 100) -> Dict[str, Any]:
        """
        Analyze activity for a specific user.
        
        Returns statistics and patterns.
        """
        events = self.storage.query(user=user, event_type="execution", limit=limit)
        
        if not events:
            return {"user": user, "total_executions": 0}
        
        # Analyze
        total = len(events)
        by_status = {}
        by_agent = {}
        
        for event in events:
            status = event.get("status", "unknown")
            agent_id = event.get("agent_id", "unknown")
            
            by_status[status] = by_status.get(status, 0) + 1
            by_agent[agent_id] = by_agent.get(agent_id, 0) + 1
        
        return {
            "user": user,
            "total_executions": total,
            "by_status": by_status,
            "by_agent": by_agent,
            "recent_events": events[-10:],
        }
    
    def get_timeline(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get timeline of all events in time range.
        """
        # V1: Get recent events (no time filtering yet)
        return self.storage.query(limit=limit)
