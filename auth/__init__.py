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
