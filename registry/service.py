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
Registry Service: System of record for AI agents.

Core rule: If it's not in the registry, it cannot execute.
This is how you prevent shadow AI.
"""

import logging
import time
import uuid
from typing import Dict, Any, List, Optional

from registry.models import Agent
from registry.storage import RegistryStorage

logger = logging.getLogger(__name__)


class RegistryService:
    """
    Registry service for AI agent management.
    
    Provides centralized catalog of all AI agents/models in the system.
    """
    
    def __init__(self):
        self.storage = RegistryStorage()
        logger.info("Registry service initialized")
    
    def register_agent(
        self,
        name: str,
        model: str,
        risk_level: str = "medium",
        policies: Optional[List[str]] = None,
        environment: str = "dev",
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new AI agent.
        
        Args:
            name: Human-readable agent name
            model: AI model identifier
            risk_level: Risk classification (low, medium, high, critical)
            policies: List of policy IDs to apply
            environment: Deployment environment
            metadata: Additional agent metadata
            created_by: User/system registering the agent
        
        Returns:
            Registered agent data
        """
        # Validate risk level
        if risk_level not in ["low", "medium", "high", "critical"]:
            raise ValueError(f"Invalid risk_level: {risk_level}")
        
        # Generate agent ID (slug from name)
        agent_id = self._generate_agent_id(name)
        
        # Check for duplicates
        if self.storage.get(agent_id):
            logger.warning(f"Agent already exists: {agent_id}")
            raise ValueError(f"Agent already registered: {agent_id}")
        
        # Create agent
        agent = Agent(
            id=agent_id,
            name=name,
            model=model,
            risk_level=risk_level,
            policies=policies or [],
            environment=environment,
            metadata=metadata or {},
            created_at=time.time(),
            updated_at=time.time(),
            created_by=created_by,
            version="1.0.0",
            active=True,
        )
        
        # Store agent
        self.storage.save(agent_id, agent.model_dump())
        
        logger.info(
            f"Agent registered: {agent_id} "
            f"(model={model}, risk={risk_level}, policies={len(policies or [])})"
        )
        
        return agent.model_dump()
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Agent data or None if not found
        """
        return self.storage.get(agent_id)
    
    def list_agents(
        self,
        environment: Optional[str] = None,
        risk_level: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Args:
            environment: Filter by environment
            risk_level: Filter by risk level
            active_only: Only return active agents
        
        Returns:
            List of agents
        """
        agents = self.storage.list_all()
        
        # Apply filters
        if environment:
            agents = [a for a in agents if a.get("environment") == environment]
        
        if risk_level:
            agents = [a for a in agents if a.get("risk_level") == risk_level]
        
        if active_only:
            agents = [a for a in agents if a.get("active", True)]
        
        return agents
    
    def update_agent(
        self,
        agent_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update agent configuration.
        
        Args:
            agent_id: Agent identifier
            updates: Fields to update
        
        Returns:
            Updated agent data
        """
        agent = self.storage.get(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Update fields
        for key, value in updates.items():
            if key in ["id", "created_at", "created_by"]:
                # Immutable fields
                continue
            agent[key] = value
        
        agent["updated_at"] = time.time()
        
        # Save
        self.storage.save(agent_id, agent)
        
        logger.info(f"Agent updated: {agent_id}")
        return agent
    
    def deactivate_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Deactivate an agent (soft delete).
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Updated agent data
        """
        return self.update_agent(agent_id, {"active": False})
    
    def activate_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Activate a deactivated agent.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Updated agent data
        """
        return self.update_agent(agent_id, {"active": True})
    
    def delete_agent(self, agent_id: str):
        """
        Hard delete an agent.
        
        Use with caution. Prefer deactivate_agent for soft deletion.
        
        Args:
            agent_id: Agent identifier
        """
        self.storage.delete(agent_id)
        logger.warning(f"Agent deleted: {agent_id}")
    
    def _generate_agent_id(self, name: str) -> str:
        """Generate agent ID from name (slugified)."""
        # Simple slugification
        agent_id = name.lower().replace(" ", "-").replace("_", "-")
        # Remove special characters
        agent_id = "".join(c for c in agent_id if c.isalnum() or c == "-")
        return agent_id
