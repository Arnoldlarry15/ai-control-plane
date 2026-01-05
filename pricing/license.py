"""
License Manager

Manages license keys and feature gates for enterprise deployments.
"""

import logging
import secrets
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from pricing.models import (
    LicenseKey,
    LicenseType,
    PricingTier,
)

logger = logging.getLogger(__name__)


class LicenseManager:
    """
    License manager - handles license keys and feature gating.
    
    The enforcement layer: no key, no enterprise features.
    """
    
    def __init__(self):
        """Initialize license manager."""
        # In-memory storage for demo
        # Production: Use encrypted database
        self.licenses: Dict[str, LicenseKey] = {}
        self.org_licenses: Dict[str, str] = {}  # org_id -> license_key
    
    def generate_license_key(
        self,
        organization_id: str,
        tier: LicenseType,
        pricing_tier: PricingTier,
        validity_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LicenseKey:
        """
        Generate a new license key.
        
        Args:
            organization_id: Organization ID
            tier: License tier
            pricing_tier: Full pricing tier definition
            validity_days: Validity in days (None = perpetual)
            metadata: Additional metadata
        
        Returns:
            Generated license key
        """
        # Generate random key
        key = self._generate_key_string(organization_id, tier)
        
        # Calculate expiration
        expires_at = None
        if validity_days:
            expires_at = datetime.utcnow() + timedelta(days=validity_days)
        
        # Extract feature flags from pricing tier
        enabled_features = pricing_tier.features.copy()
        
        # Extract limits
        limits = {}
        if pricing_tier.max_requests_per_month:
            limits["max_requests_per_month"] = pricing_tier.max_requests_per_month
        if pricing_tier.max_agents:
            limits["max_agents"] = pricing_tier.max_agents
        if pricing_tier.max_seats:
            limits["max_seats"] = pricing_tier.max_seats
        
        # Create license
        license_key = LicenseKey(
            key=key,
            organization_id=organization_id,
            tier=tier,
            issued_at=datetime.utcnow(),
            expires_at=expires_at,
            enabled_features=enabled_features,
            limits=limits,
            active=True,
            revoked=False,
            metadata=metadata or {},
        )
        
        # Store license
        self.licenses[key] = license_key
        self.org_licenses[organization_id] = key
        
        logger.info(
            f"Generated {tier.value} license for {organization_id}: {key[:16]}..."
        )
        
        return license_key
    
    def _generate_key_string(self, organization_id: str, tier: LicenseType) -> str:
        """
        Generate license key string.
        
        Format: ACP-{TIER}-{ORG_HASH}-{RANDOM}
        """
        # Hash org ID
        org_hash = hashlib.sha256(organization_id.encode()).hexdigest()[:8].upper()
        
        # Random suffix
        random_suffix = secrets.token_hex(16).upper()
        
        # Tier prefix
        tier_prefix = tier.value[:3].upper()
        
        return f"ACP-{tier_prefix}-{org_hash}-{random_suffix}"
    
    def validate_license(self, key: str) -> tuple[bool, Optional[str]]:
        """
        Validate a license key.
        
        Returns:
            Tuple of (valid, reason)
        """
        # Check if key exists
        if key not in self.licenses:
            return False, "Invalid license key"
        
        license_key = self.licenses[key]
        
        # Check if revoked
        if license_key.revoked:
            return False, f"License revoked: {license_key.revoked_reason}"
        
        # Check if active
        if not license_key.active:
            return False, "License is not active"
        
        # Check expiration
        if license_key.expires_at:
            if datetime.utcnow() > license_key.expires_at:
                return False, "License has expired"
        
        return True, None
    
    def get_license(self, key: str) -> Optional[LicenseKey]:
        """Get license by key."""
        return self.licenses.get(key)
    
    def get_license_by_org(self, organization_id: str) -> Optional[LicenseKey]:
        """Get license for an organization."""
        key = self.org_licenses.get(organization_id)
        if key:
            return self.licenses.get(key)
        return None
    
    def check_feature_access(
        self, key: str, feature: str
    ) -> tuple[bool, Optional[str]]:
        """
        Check if license has access to a feature.
        
        This is the feature gate: no access without the right license.
        
        Returns:
            Tuple of (has_access, reason)
        """
        # Validate license first
        valid, reason = self.validate_license(key)
        if not valid:
            return False, reason
        
        license_key = self.licenses[key]
        
        # Check feature flag
        if feature not in license_key.enabled_features:
            return False, f"Feature '{feature}' not available in license"
        
        if not license_key.enabled_features[feature]:
            tier_value = license_key.tier if isinstance(license_key.tier, str) else license_key.tier.value
            return False, f"Feature '{feature}' not enabled in {tier_value} tier"
        
        return True, None
    
    def check_limit(
        self, key: str, limit_type: str, current_value: int
    ) -> tuple[bool, Optional[str]]:
        """
        Check if within license limits.
        
        Args:
            key: License key
            limit_type: Type of limit (e.g., "max_requests_per_month")
            current_value: Current value to check
        
        Returns:
            Tuple of (within_limit, reason)
        """
        # Validate license first
        valid, reason = self.validate_license(key)
        if not valid:
            return False, reason
        
        license_key = self.licenses[key]
        
        # Check if limit exists
        if limit_type not in license_key.limits:
            # No limit = unlimited (enterprise)
            return True, None
        
        limit_value = license_key.limits[limit_type]
        
        if current_value > limit_value:
            return False, f"Exceeded {limit_type}: {current_value} > {limit_value}"
        
        return True, None
    
    def revoke_license(self, key: str, reason: str) -> bool:
        """
        Revoke a license.
        
        Args:
            key: License key to revoke
            reason: Reason for revocation
        
        Returns:
            True if revoked, False if not found
        """
        if key not in self.licenses:
            return False
        
        license_key = self.licenses[key]
        license_key.revoked = True
        license_key.revoked_at = datetime.utcnow()
        license_key.revoked_reason = reason
        license_key.active = False
        
        logger.warning(
            f"Revoked license {key[:16]}... for {license_key.organization_id}: {reason}"
        )
        
        return True
    
    def renew_license(self, key: str, additional_days: int) -> bool:
        """
        Renew a license.
        
        Args:
            key: License key to renew
            additional_days: Additional days to add
        
        Returns:
            True if renewed, False if not found
        """
        if key not in self.licenses:
            return False
        
        license_key = self.licenses[key]
        
        # If currently expired, renew from now
        # Otherwise, extend from current expiration
        if license_key.expires_at:
            if datetime.utcnow() > license_key.expires_at:
                license_key.expires_at = datetime.utcnow() + timedelta(days=additional_days)
            else:
                license_key.expires_at += timedelta(days=additional_days)
        else:
            # Was perpetual, now has expiration
            license_key.expires_at = datetime.utcnow() + timedelta(days=additional_days)
        
        logger.info(
            f"Renewed license {key[:16]}... until {license_key.expires_at}"
        )
        
        return True
    
    def update_license_features(
        self, key: str, features: Dict[str, bool]
    ) -> bool:
        """
        Update feature flags for a license.
        
        Args:
            key: License key
            features: Feature flags to update
        
        Returns:
            True if updated, False if not found
        """
        if key not in self.licenses:
            return False
        
        license_key = self.licenses[key]
        license_key.enabled_features.update(features)
        
        logger.info(f"Updated features for license {key[:16]}...")
        
        return True
    
    def list_licenses(
        self,
        organization_id: Optional[str] = None,
        tier: Optional[LicenseType] = None,
        active_only: bool = False,
    ) -> List[LicenseKey]:
        """
        List licenses with optional filters.
        
        Args:
            organization_id: Filter by organization
            tier: Filter by tier
            active_only: Only return active licenses
        
        Returns:
            List of licenses
        """
        licenses = list(self.licenses.values())
        
        if organization_id:
            licenses = [l for l in licenses if l.organization_id == organization_id]
        
        if tier:
            licenses = [l for l in licenses if l.tier == tier]
        
        if active_only:
            licenses = [
                l for l in licenses
                if l.active
                and not l.revoked
                and (not l.expires_at or datetime.utcnow() <= l.expires_at)
            ]
        
        return licenses
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get license statistics.
        
        For monitoring and reporting.
        """
        total_licenses = len(self.licenses)
        
        # By tier
        by_tier = {}
        for tier in LicenseType:
            by_tier[tier.value] = len([
                l for l in self.licenses.values()
                if l.tier == tier
            ])
        
        # Active vs inactive
        active = len([
            l for l in self.licenses.values()
            if l.active and not l.revoked
        ])
        revoked = len([
            l for l in self.licenses.values()
            if l.revoked
        ])
        expired = len([
            l for l in self.licenses.values()
            if l.expires_at and datetime.utcnow() > l.expires_at
        ])
        
        return {
            "total_licenses": total_licenses,
            "licenses_by_tier": by_tier,
            "active_licenses": active,
            "revoked_licenses": revoked,
            "expired_licenses": expired,
            "organizations": len(self.org_licenses),
        }
