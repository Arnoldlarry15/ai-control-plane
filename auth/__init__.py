"""
Authentication and Authorization Module

Provides role-based access control (RBAC) and identity management
for the AI Control Plane.
"""

from auth.models import User, Role, Permission
from auth.service import AuthService

__all__ = ["User", "Role", "Permission", "AuthService"]
