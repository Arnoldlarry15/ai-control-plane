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
OIDC (OpenID Connect) Integration Module

Supports Auth0 and other OIDC-compliant identity providers for enterprise SSO.
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import json
import base64

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class OIDCConfig(BaseModel):
    """OIDC provider configuration"""
    
    issuer: str = Field(..., description="OIDC issuer URL")
    client_id: str = Field(..., description="Application client ID")
    client_secret: Optional[str] = Field(None, description="Client secret for confidential clients")
    redirect_uri: str = Field(..., description="Redirect URI after authentication")
    scopes: List[str] = Field(
        default=["openid", "profile", "email"],
        description="OAuth scopes to request"
    )
    
    # Auth0 specific
    audience: Optional[str] = Field(None, description="API identifier (Auth0)")
    
    # Discovery endpoints
    authorization_endpoint: Optional[str] = None
    token_endpoint: Optional[str] = None
    userinfo_endpoint: Optional[str] = None
    jwks_uri: Optional[str] = None


class OIDCToken(BaseModel):
    """OIDC token response"""
    
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    id_token: Optional[str] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def expires_at(self) -> datetime:
        """Calculate expiration time"""
        return self.issued_at + timedelta(seconds=self.expires_in)
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() >= self.expires_at


class OIDCUserInfo(BaseModel):
    """User information from OIDC provider"""
    
    sub: str = Field(..., description="Subject identifier (unique user ID)")
    email: str
    email_verified: bool = Field(default=False)
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    
    # Additional claims
    roles: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    
    # Custom namespace for Auth0 (e.g., https://app.example.com/roles)
    custom_claims: Dict[str, Any] = Field(default_factory=dict)


class OIDCProvider:
    """
    OIDC Provider Integration
    
    Supports Auth0, Okta, Azure AD, Google, and other OIDC-compliant providers.
    
    V1: Configuration and token validation structure
    V2+: Full OAuth flow, token refresh, JWKS validation
    """
    
    def __init__(self, config: OIDCConfig):
        """
        Initialize OIDC provider.
        
        Args:
            config: OIDC configuration
        """
        self.config = config
        self._tokens: Dict[str, OIDCToken] = {}  # user_id -> token
        self._user_cache: Dict[str, OIDCUserInfo] = {}  # sub -> user info
        
        logger.info(f"OIDC provider initialized: issuer={config.issuer}")
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate authorization URL for OAuth flow.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        if not self.config.authorization_endpoint:
            # Construct from issuer
            auth_endpoint = f"{self.config.issuer}/authorize"
        else:
            auth_endpoint = self.config.authorization_endpoint
        
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.config.scopes),
        }
        
        if state:
            params["state"] = state
        
        if self.config.audience:
            params["audience"] = self.config.audience
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{auth_endpoint}?{query_string}"
    
    def validate_token(self, token: str) -> Optional[OIDCUserInfo]:
        """
        Validate an OIDC token and extract user information.
        
        Args:
            token: Access token or ID token
            
        Returns:
            User information if valid, None otherwise
            
        Note:
            V1 Implementation: Basic token parsing for demo purposes.
            
            ⚠️ SECURITY WARNING: This implementation does NOT perform signature
            verification, expiration checking, or audience validation.
            
            For production use, implement proper JWT validation:
            1. Use python-jose or PyJWT library
            2. Fetch and cache JWKS from provider's jwks_uri
            3. Verify signature using public key from JWKS
            4. Validate issuer, audience, and expiration claims
            5. Check token revocation status
            
            Example production implementation:
            ```python
            from jose import jwt, JWTError
            
            try:
                # Fetch JWKS and verify signature
                jwks = requests.get(self.config.jwks_uri).json()
                token_data = jwt.decode(
                    token,
                    jwks,
                    algorithms=['RS256'],
                    audience=self.config.client_id,
                    issuer=self.config.issuer
                )
                # Extract user info from verified token
                return OIDCUserInfo(**token_data)
            except JWTError:
                return None
            ```
        """
        try:
            # V1: Simple base64 decode for demo purposes
            # ⚠️ DO NOT USE IN PRODUCTION - No signature verification!
            parts = token.split(".")
            if len(parts) != 3:
                logger.warning("Invalid JWT format")
                return None
            
            # Decode payload (add padding if needed)
            payload = parts[1]
            payload += "=" * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            claims = json.loads(decoded)
            
            # Extract user info from claims
            user_info = OIDCUserInfo(
                sub=claims.get("sub", ""),
                email=claims.get("email", ""),
                email_verified=claims.get("email_verified", False),
                name=claims.get("name"),
                given_name=claims.get("given_name"),
                family_name=claims.get("family_name"),
                picture=claims.get("picture"),
                roles=claims.get("roles", []),
                groups=claims.get("groups", []),
                permissions=claims.get("permissions", []),
                custom_claims={
                    k: v for k, v in claims.items()
                    if k.startswith("https://") or k.startswith("http://")
                },
            )
            
            # Cache user info
            self._user_cache[user_info.sub] = user_info
            
            logger.info(f"Token validated for user: {user_info.email}")
            return user_info
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return None
    
    def get_user_info(self, sub: str) -> Optional[OIDCUserInfo]:
        """
        Get cached user information.
        
        Args:
            sub: Subject identifier
            
        Returns:
            User information or None
        """
        return self._user_cache.get(sub)
    
    def exchange_code_for_token(self, code: str) -> Optional[OIDCToken]:
        """
        Exchange authorization code for tokens.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            OIDC tokens if successful, None otherwise
            
        Note:
            V1: Placeholder implementation
            V2+: Full OAuth code exchange with token endpoint
        """
        logger.warning("Code exchange not implemented in V1 - use validate_token directly")
        return None
    
    def refresh_token(self, refresh_token: str) -> Optional[OIDCToken]:
        """
        Refresh an access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New tokens if successful, None otherwise
            
        Note:
            V1: Placeholder implementation
            V2+: Full token refresh flow
        """
        logger.warning("Token refresh not implemented in V1")
        return None
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if successful
        """
        # Remove from cache
        for sub, cached_token in list(self._tokens.items()):
            if cached_token.access_token == token:
                del self._tokens[sub]
                logger.info(f"Token revoked for user: {sub}")
                return True
        
        return False


class OIDCService:
    """
    OIDC Service
    
    Manages OIDC providers and authentication.
    """
    
    def __init__(self):
        self._providers: Dict[str, OIDCProvider] = {}
        logger.info("OIDC service initialized")
    
    def add_provider(self, name: str, config: OIDCConfig) -> OIDCProvider:
        """
        Add an OIDC provider.
        
        Args:
            name: Provider name (e.g., "auth0", "okta")
            config: Provider configuration
            
        Returns:
            OIDC provider instance
        """
        provider = OIDCProvider(config)
        self._providers[name] = provider
        
        logger.info(f"OIDC provider added: {name}")
        return provider
    
    def get_provider(self, name: str) -> Optional[OIDCProvider]:
        """Get provider by name"""
        return self._providers.get(name)
    
    def authenticate(
        self,
        provider_name: str,
        token: str
    ) -> Optional[OIDCUserInfo]:
        """
        Authenticate a user with OIDC token.
        
        Args:
            provider_name: Provider name
            token: Access or ID token
            
        Returns:
            User information if authenticated
        """
        provider = self.get_provider(provider_name)
        if not provider:
            logger.warning(f"Provider not found: {provider_name}")
            return None
        
        return provider.validate_token(token)
