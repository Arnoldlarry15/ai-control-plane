"""
Authentication and Authorization Models
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class Permission(str, Enum):
    """System permissions"""
    # Agent management
    AGENT_READ = "agent:read"
    AGENT_WRITE = "agent:write"
    AGENT_DELETE = "agent:delete"
    
    # Policy management
    POLICY_READ = "policy:read"
    POLICY_WRITE = "policy:write"
    POLICY_DELETE = "policy:delete"
    
    # Execution
    EXECUTE = "execute"
    
    # Kill switch
    KILL_SWITCH_ACTIVATE = "killswitch:activate"
    KILL_SWITCH_DEACTIVATE = "killswitch:deactivate"
    
    # Approval
    APPROVE = "approval:approve"
    APPROVE_READ = "approval:read"
    
    # Audit
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    
    # System admin
    ADMIN = "admin"


class Role(str, Enum):
    """Predefined roles"""
    ADMIN = "admin"
    OPERATOR = "operator"
    DEVELOPER = "developer"
    AUDITOR = "auditor"
    USER = "user"


# Role-Permission mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.ADMIN,
        Permission.AGENT_READ,
        Permission.AGENT_WRITE,
        Permission.AGENT_DELETE,
        Permission.POLICY_READ,
        Permission.POLICY_WRITE,
        Permission.POLICY_DELETE,
        Permission.EXECUTE,
        Permission.KILL_SWITCH_ACTIVATE,
        Permission.KILL_SWITCH_DEACTIVATE,
        Permission.APPROVE,
        Permission.APPROVE_READ,
        Permission.AUDIT_READ,
        Permission.AUDIT_EXPORT,
    ],
    Role.OPERATOR: [
        Permission.AGENT_READ,
        Permission.POLICY_READ,
        Permission.EXECUTE,
        Permission.KILL_SWITCH_ACTIVATE,
        Permission.KILL_SWITCH_DEACTIVATE,
        Permission.AUDIT_READ,
    ],
    Role.DEVELOPER: [
        Permission.AGENT_READ,
        Permission.AGENT_WRITE,
        Permission.POLICY_READ,
        Permission.EXECUTE,
        Permission.AUDIT_READ,
    ],
    Role.AUDITOR: [
        Permission.AGENT_READ,
        Permission.POLICY_READ,
        Permission.AUDIT_READ,
        Permission.AUDIT_EXPORT,
        Permission.APPROVE_READ,
    ],
    Role.USER: [
        Permission.EXECUTE,
    ],
}


class User(BaseModel):
    """User model"""
    id: str
    email: EmailStr
    full_name: str
    role: Role
    api_key: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        return permission in ROLE_PERMISSIONS.get(self.role, [])
    
    def get_permissions(self) -> List[Permission]:
        """Get all permissions for this user"""
        return ROLE_PERMISSIONS.get(self.role, [])


class APIKey(BaseModel):
    """API Key model"""
    key: str
    user_id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    active: bool = True
