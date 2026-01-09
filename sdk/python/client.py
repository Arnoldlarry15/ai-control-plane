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
AI Control Plane Python Client.

Adoption weapon. Drop-in replacement for direct LLM calls.
"""

import logging
from typing import Dict, Any, Optional, List

import requests

from sdk.python.exceptions import (
    ControlPlaneException,
    ExecutionBlockedError,
    AgentNotFoundError,
    ApprovalPendingError,
)

logger = logging.getLogger(__name__)


class ControlPlaneClient:
    """
    Client for AI Control Plane.
    
    Drop-in replacement for direct LLM API calls with governance built-in.
    
    Example:
        ```python
        client = ControlPlaneClient()
        
        # Register agent
        agent = client.register_agent(
            name="my-agent",
            model="gpt-3.5-turbo",
            policies=["no-pii"]
        )
        
        # Execute through control plane
        response = client.execute(
            agent_id=agent["agent_id"],
            prompt="Hello, world!"
        )
        ```
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize control plane client.
        
        Args:
            base_url: Control plane gateway URL
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        
        self.session = requests.Session()
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
        
        logger.info(f"Control plane client initialized: {base_url}")
    
    def register_agent(
        self,
        name: str,
        model: str,
        risk_level: str = "medium",
        policies: Optional[List[str]] = None,
        environment: str = "dev",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register an AI agent.
        
        Args:
            name: Human-readable agent name
            model: AI model (e.g., gpt-3.5-turbo)
            risk_level: Risk level (low, medium, high, critical)
            policies: List of policy IDs to apply
            environment: Deployment environment (dev, staging, prod)
            metadata: Additional metadata
        
        Returns:
            Registered agent data
        
        Raises:
            ControlPlaneException: On registration error
        """
        data = {
            "name": name,
            "model": model,
            "risk_level": risk_level,
            "policies": policies or [],
            "environment": environment,
            "metadata": metadata or {},
        }
        
        response = self._post("/api/agents", data)
        logger.info(f"Agent registered: {response['agent_id']}")
        return response
    
    def execute(
        self,
        agent_id: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute an AI agent through the control plane.
        
        Args:
            agent_id: Registered agent ID
            prompt: User prompt/input
            context: Execution context
            user: User identifier
        
        Returns:
            Execution result with response and metadata
        
        Raises:
            ExecutionBlockedError: If execution is blocked
            AgentNotFoundError: If agent is not registered
            ApprovalPendingError: If execution requires approval
            ControlPlaneException: On other errors
        """
        data = {
            "agent_id": agent_id,
            "prompt": prompt,
            "context": context or {},
            "user": user,
        }
        
        try:
            response = self._post("/api/execute", data)
            
            # Handle different statuses
            status = response.get("status")
            
            if status == "success":
                return response
            elif status == "blocked":
                raise ExecutionBlockedError(
                    reason=response.get("reason", "Unknown"),
                    details=response,
                )
            elif status == "pending_approval":
                raise ApprovalPendingError(
                    approval_id=response.get("approval_id"),
                    reason=response.get("reason", "Unknown"),
                )
            else:
                raise ControlPlaneException(f"Unknown status: {status}")
        
        except ExecutionBlockedError:
            raise
        except ApprovalPendingError:
            raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise AgentNotFoundError(agent_id)
            elif e.response.status_code == 403:
                # Parse error response for policy violation
                try:
                    error_data = e.response.json()
                    raise ExecutionBlockedError(
                        reason=error_data.get("error", "Forbidden"),
                        details=error_data.get("details", {}),
                    )
                except:
                    raise ExecutionBlockedError(reason="Execution blocked", details={})
            raise ControlPlaneException(str(e), status_code=e.response.status_code)
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent details.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Agent data
        """
        return self._get(f"/api/agents/{agent_id}")
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agents
        """
        response = self._get("/api/agents")
        return response.get("agents", [])
    
    def activate_kill_switch(
        self,
        scope: str = "global",
        reason: str = "Manual activation",
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Activate kill switch.
        
        Args:
            scope: "global" or "agent"
            reason: Reason for activation
            agent_id: Required if scope is "agent"
        
        Returns:
            Activation result
        """
        data = {
            "scope": scope,
            "reason": reason,
        }
        if agent_id:
            data["agent_id"] = agent_id
        
        response = self._post("/api/kill-switch/activate", data)
        logger.warning(f"Kill switch activated: {scope}")
        return response
    
    def deactivate_kill_switch(
        self,
        scope: str = "global",
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Deactivate kill switch.
        
        Args:
            scope: "global" or "agent"
            agent_id: Required if scope is "agent"
        
        Returns:
            Deactivation result
        """
        params = {"scope": scope}
        if agent_id:
            params["agent_id"] = agent_id
        
        response = self._post("/api/kill-switch/deactivate", params=params)
        logger.info(f"Kill switch deactivated: {scope}")
        return response
    
    def get_kill_switch_status(self) -> Dict[str, Any]:
        """Get kill switch status."""
        return self._get("/api/kill-switch/status")
    
    def get_logs(
        self,
        user: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs.
        
        Args:
            user: Filter by user
            agent_id: Filter by agent
            status: Filter by status
            limit: Maximum results
        
        Returns:
            List of log entries
        """
        params = {"limit": limit}
        if user:
            params["user"] = user
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status
        
        return self._get("/api/logs", params=params)
    
    def get_execution_log(self, execution_id: str) -> Dict[str, Any]:
        """
        Get detailed log for a specific execution.
        
        Args:
            execution_id: Execution identifier
        
        Returns:
            Execution log
        """
        return self._get(f"/api/logs/{execution_id}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check gateway health."""
        return self._get("/health")
    
    # Helper methods
    
    def _get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request."""
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def _post(
        self,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make POST request."""
        url = f"{self.base_url}{path}"
        response = self.session.post(
            url, json=data, params=params, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
