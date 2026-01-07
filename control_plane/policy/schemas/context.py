"""
Request Context Schema - Immutable truth payload for policy evaluation.

This is the complete context that gets judged by policies.
Immutability prevents tampering during evaluation.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class RequestContext:
    """
    Request context for policy evaluation.
    
    This is the immutable truth payload being judged by policies.
    Frozen to prevent any modifications during evaluation.
    
    Attributes:
        actor_id: Who initiated the request (user ID, service account, etc.)
        actor_role: Role of the actor (admin, operator, developer, auditor, etc.)
        resource_id: The resource being accessed (model ID, agent ID, data ID, etc.)
        resource_type: Type of resource (model, agent, data, etc.)
        environment: Deployment environment (dev, staging, production)
        intent: What action is being performed (generation, tool_call, data_access, etc.)
        tags: Classification tags (pii, hipaa, financial, sensitive, etc.)
        metadata: Additional context information
    """
    
    actor_id: str
    actor_role: str
    resource_id: str
    resource_type: str
    environment: str
    intent: str
    tags: List[str]
    metadata: Dict[str, str]
    
    def __post_init__(self):
        """
        Validate context on initialization.
        
        Note: Uses object.__setattr__ to modify frozen dataclass attributes
        to ensure proper types (list/dict) before freezing. This is a standard
        pattern for frozen dataclasses that need validation or type coercion.
        """
        if not self.actor_id:
            raise ValueError("actor_id is required")
        if not self.resource_id:
            raise ValueError("resource_id is required")
        if not self.environment:
            raise ValueError("environment is required")
        
        # Ensure tags is a list (coerce if needed before freezing)
        if not isinstance(self.tags, list):
            object.__setattr__(self, 'tags', list(self.tags))
        
        # Ensure metadata is a dict (coerce if needed before freezing)
        if not isinstance(self.metadata, dict):
            object.__setattr__(self, 'metadata', dict(self.metadata))
