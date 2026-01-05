"""
Authentication and Authorization Module

Provides RBAC (Role-Based Access Control) with:
- Users and roles
- Permissions
- API key management
- OIDC/Auth0 integration for enterprise SSO
"""

from auth.models import User, Role, Permission, APIKey, ROLE_PERMISSIONS
from auth.service import AuthService
from auth.oidc import OIDCConfig, OIDCProvider, OIDCService, OIDCToken, OIDCUserInfo

__all__ = [
    "User",
    "Role",
    "Permission",
    "APIKey",
    "ROLE_PERMISSIONS",
    "AuthService",
    "OIDCConfig",
    "OIDCProvider",
    "OIDCService",
    "OIDCToken",
    "OIDCUserInfo",
]
