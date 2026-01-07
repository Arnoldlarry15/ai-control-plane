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
Registry Storage: In-memory storage for agent registry.

V1: In-memory (simple, fast, good for demo)
V2+: PostgreSQL/SQLite for persistence
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class RegistryStorage:
    """
    In-memory storage for agent registry.
    
    Simple key-value store for V1.
    """
    
    def __init__(self):
        # In-memory storage: {agent_id: agent_data}
        self._agents: Dict[str, Dict[str, Any]] = {}
        logger.info("Registry storage initialized (in-memory)")
    
    def save(self, agent_id: str, agent_data: Dict[str, Any]):
        """Save agent to storage."""
        self._agents[agent_id] = agent_data
        logger.debug(f"Agent saved: {agent_id}")
    
    def get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent from storage."""
        return self._agents.get(agent_id)
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all agents."""
        return list(self._agents.values())
    
    def delete(self, agent_id: str):
        """Delete agent from storage."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            logger.debug(f"Agent deleted: {agent_id}")
    
    def exists(self, agent_id: str) -> bool:
        """Check if agent exists."""
        return agent_id in self._agents
