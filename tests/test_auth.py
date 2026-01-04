"""
Tests for authentication and authorization.
"""

import pytest
from datetime import datetime, timedelta

from auth.service import AuthService
from auth.models import User, Role, Permission


def test_create_user():
    """Test user creation."""
    auth = AuthService()
    
    user = auth.create_user(
        user_id="alice",
        email="alice@example.com",
        full_name="Alice Developer",
        role=Role.DEVELOPER,
    )
    
    assert user.id == "alice"
    assert user.email == "alice@example.com"
    assert user.role == Role.DEVELOPER
    assert user.active is True


def test_duplicate_user():
    """Test that duplicate user creation fails."""
    auth = AuthService()
    
    auth.create_user("alice", "alice@example.com", "Alice", Role.USER)
    
    with pytest.raises(ValueError, match="already exists"):
        auth.create_user("alice", "alice2@example.com", "Alice 2", Role.USER)


def test_api_key_creation():
    """Test API key creation."""
    auth = AuthService()
    
    user = auth.create_user("bob", "bob@example.com", "Bob", Role.USER)
    api_key = auth.create_api_key("bob", "Test Key")
    
    assert api_key is not None
    assert len(api_key) > 20  # Secure random key


def test_api_key_authentication():
    """Test API key authentication."""
    auth = AuthService()
    
    user = auth.create_user("charlie", "charlie@example.com", "Charlie", Role.USER)
    api_key = auth.create_api_key("charlie", "Test Key")
    
    # Authenticate with key
    authed_user = auth.authenticate_api_key(api_key)
    
    assert authed_user is not None
    assert authed_user.id == "charlie"


def test_invalid_api_key():
    """Test authentication with invalid API key."""
    auth = AuthService()
    
    authed_user = auth.authenticate_api_key("invalid-key")
    
    assert authed_user is None


def test_revoke_api_key():
    """Test API key revocation."""
    auth = AuthService()
    
    user = auth.create_user("dave", "dave@example.com", "Dave", Role.USER)
    api_key = auth.create_api_key("dave", "Test Key")
    
    # Key should work
    assert auth.authenticate_api_key(api_key) is not None
    
    # Revoke key
    auth.revoke_api_key(api_key)
    
    # Key should not work
    assert auth.authenticate_api_key(api_key) is None


def test_api_key_expiration():
    """Test API key expiration."""
    auth = AuthService()
    
    user = auth.create_user("eve", "eve@example.com", "Eve", Role.USER)
    
    # Create expired key
    expired_time = datetime.utcnow() - timedelta(days=1)
    api_key = auth.create_api_key("eve", "Expired Key", expires_at=expired_time)
    
    # Expired key should not work
    assert auth.authenticate_api_key(api_key) is None


def test_role_permissions():
    """Test role permission mappings."""
    auth = AuthService()
    
    # Admin has all permissions (use the default admin user)
    admin = auth.get_user("admin")
    assert admin.has_permission(Permission.ADMIN)
    assert admin.has_permission(Permission.AGENT_WRITE)
    assert admin.has_permission(Permission.KILL_SWITCH_ACTIVATE)
    
    # Developer has limited permissions
    dev = auth.create_user("dev", "dev@example.com", "Dev", Role.DEVELOPER)
    assert dev.has_permission(Permission.AGENT_WRITE)
    assert dev.has_permission(Permission.EXECUTE)
    assert not dev.has_permission(Permission.KILL_SWITCH_ACTIVATE)
    
    # User has minimal permissions
    user = auth.create_user("user", "user@example.com", "User", Role.USER)
    assert user.has_permission(Permission.EXECUTE)
    assert not user.has_permission(Permission.AGENT_WRITE)
    assert not user.has_permission(Permission.ADMIN)


def test_authorize():
    """Test authorization checking."""
    auth = AuthService()
    
    admin = auth.create_user("admin2", "admin2@example.com", "Admin", Role.ADMIN)
    user = auth.create_user("user2", "user2@example.com", "User", Role.USER)
    
    # Admin can do everything
    assert auth.authorize(admin, Permission.ADMIN) is True
    assert auth.authorize(admin, Permission.AGENT_WRITE) is True
    
    # User has limited access
    assert auth.authorize(user, Permission.EXECUTE) is True
    assert auth.authorize(user, Permission.AGENT_WRITE) is False
    assert auth.authorize(user, Permission.ADMIN) is False


def test_list_users():
    """Test listing all users."""
    auth = AuthService()
    
    initial_count = len(auth.list_users())
    
    auth.create_user("user1", "user1@example.com", "User 1", Role.USER)
    auth.create_user("user2", "user2@example.com", "User 2", Role.DEVELOPER)
    
    users = auth.list_users()
    assert len(users) == initial_count + 2


def test_list_api_keys():
    """Test listing user's API keys."""
    auth = AuthService()
    
    user = auth.create_user("frank", "frank@example.com", "Frank", Role.USER)
    
    key1 = auth.create_api_key("frank", "Key 1")
    key2 = auth.create_api_key("frank", "Key 2")
    
    keys = auth.list_api_keys("frank")
    assert len(keys) == 2
    assert all(k.user_id == "frank" for k in keys)
