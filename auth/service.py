"""
Authentication and Authorization Service
"""

import secrets
import hashlib
import logging
from typing import Dict, Optional, List
from datetime import datetime

from auth.models import User, Role, Permission, APIKey

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication and authorization service.
    
    Manages users, roles, permissions, and API keys.
    """
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._api_keys: Dict[str, APIKey] = {}
        self._load_default_users()
        
        logger.info("Auth service initialized")
    
    def _load_default_users(self):
        """Load default system users"""
        # Create default admin user
        admin_user = User(
            id="admin",
            email="admin@example.com",
            full_name="System Administrator",
            role=Role.ADMIN,
        )
        self._users[admin_user.id] = admin_user
        
        # Create default API key for admin
        admin_key = self.create_api_key(admin_user.id, "Default Admin Key")
        logger.info(f"Default admin API key created: {admin_key}")
    
    def create_user(
        self,
        user_id: str,
        email: str,
        full_name: str,
        role: Role,
    ) -> User:
        """
        Create a new user.
        
        Args:
            user_id: Unique user identifier
            email: User email
            full_name: User full name
            role: User role
            
        Returns:
            Created user
        """
        if user_id in self._users:
            raise ValueError(f"User {user_id} already exists")
        
        user = User(
            id=user_id,
            email=email,
            full_name=full_name,
            role=role,
        )
        
        self._users[user_id] = user
        logger.info(f"User created: {user_id} ({role})")
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)
    
    def list_users(self) -> List[User]:
        """List all users"""
        return list(self._users.values())
    
    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """
        Authenticate a request using an API key.
        
        Args:
            api_key: API key to authenticate
            
        Returns:
            Authenticated user or None
        """
        key_obj = self._api_keys.get(api_key)
        
        if not key_obj or not key_obj.active:
            return None
        
        # Check expiration
        if key_obj.expires_at and key_obj.expires_at < datetime.utcnow():
            logger.warning(f"API key expired: {api_key[:8]}...")
            return None
        
        # Update last used
        key_obj.last_used = datetime.utcnow()
        
        # Get user
        user = self._users.get(key_obj.user_id)
        
        if not user or not user.active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        logger.debug(f"API key authenticated: {api_key[:8]}... (user: {user.id})")
        
        return user
    
    def authorize(self, user: User, permission: Permission) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user: User to check
            permission: Permission to check
            
        Returns:
            True if authorized
        """
        has_perm = user.has_permission(permission)
        
        if not has_perm:
            logger.warning(
                f"Permission denied: user={user.id} permission={permission}"
            )
        
        return has_perm
    
    def create_api_key(
        self,
        user_id: str,
        name: str,
        expires_at: Optional[datetime] = None,
    ) -> str:
        """
        Create a new API key for a user.
        
        Args:
            user_id: User ID
            name: Key name/description
            expires_at: Optional expiration date
            
        Returns:
            Generated API key
        """
        user = self._users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Generate secure random key
        raw_key = secrets.token_urlsafe(32)
        
        # Hash for storage (in real implementation, hash the key)
        # For simplicity in V1, we store the key directly
        api_key = APIKey(
            key=raw_key,
            user_id=user_id,
            name=name,
            expires_at=expires_at,
        )
        
        self._api_keys[raw_key] = api_key
        
        logger.info(f"API key created: {name} (user: {user_id})")
        
        return raw_key
    
    def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            api_key: API key to revoke
            
        Returns:
            True if revoked
        """
        key_obj = self._api_keys.get(api_key)
        
        if not key_obj:
            return False
        
        key_obj.active = False
        logger.info(f"API key revoked: {api_key[:8]}...")
        
        return True
    
    def list_api_keys(self, user_id: str) -> List[APIKey]:
        """List all API keys for a user"""
        return [
            key for key in self._api_keys.values()
            if key.user_id == user_id
        ]
