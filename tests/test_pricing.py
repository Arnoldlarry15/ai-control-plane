"""
Tests for pricing and monetization features.

Tests the Salesforce playbook implementation:
- Multiple pricing axes
- License management
- Usage metering
- Feature gating
"""

import pytest
from datetime import datetime, timedelta

from pricing.models import (
    LicenseType,
    PricingAxis,
    AuditTier,
    UsageMetrics,
)
from pricing.service import PricingService
from pricing.metering import MeteringService
from pricing.license import LicenseManager


class TestPricingService:
    """Test pricing service functionality."""
    
    def test_pricing_tiers_defined(self):
        """Test that all pricing tiers are defined."""
        service = PricingService()
        tiers = service.list_tiers()
        
        assert len(tiers) == 4
        tier_types = {t.tier for t in tiers}
        assert LicenseType.OPEN_SOURCE in tier_types
        assert LicenseType.STARTER in tier_types
        assert LicenseType.PROFESSIONAL in tier_types
        assert LicenseType.ENTERPRISE in tier_types
    
    def test_open_source_tier(self):
        """Test open source tier is free."""
        service = PricingService()
        tier = service.get_tier(LicenseType.OPEN_SOURCE)
        
        assert tier.base_price_monthly == 0.0
        assert tier.per_request_price is None
        assert tier.per_seat_price is None
        assert tier.max_requests_per_month == 10000
        assert tier.max_seats == 3
    
    def test_enterprise_tier_unlimited(self):
        """Test enterprise tier has no limits."""
        service = PricingService()
        tier = service.get_tier(LicenseType.ENTERPRISE)
        
        assert tier.max_requests_per_month is None
        assert tier.max_agents is None
        assert tier.max_seats is None
        assert tier.base_price_monthly > 0
    
    def test_calculate_cost_basic(self):
        """Test basic cost calculation."""
        service = PricingService()
        
        # Starter tier with basic usage
        cost = service.calculate_monthly_cost(
            tier=LicenseType.STARTER,
            requests=50000,
            seats=5,
        )
        
        assert cost["base_cost"] == 299.0
        assert cost["total"] >= 299.0
        assert "breakdown_details" in cost
    
    def test_calculate_cost_with_overages(self):
        """Test cost calculation with overages."""
        service = PricingService()
        
        # Starter tier with requests over limit
        tier = service.get_tier(LicenseType.STARTER)
        over_limit = tier.max_requests_per_month + 10000
        
        cost = service.calculate_monthly_cost(
            tier=LicenseType.STARTER,
            requests=over_limit,
            seats=5,
        )
        
        # Should have request overage cost
        assert cost["request_cost"] > 0
        assert cost["total"] > cost["base_cost"]
    
    def test_calculate_cost_with_addons(self):
        """Test cost calculation with add-ons."""
        service = PricingService()
        
        cost = service.calculate_monthly_cost(
            tier=LicenseType.PROFESSIONAL,
            requests=500000,
            seats=20,
            additional_policy_packs=2,
            additional_compliance_modules=1,
        )
        
        # Should have add-on costs
        assert cost["policy_pack_cost"] > 0
        assert cost["compliance_module_cost"] > 0
        assert cost["total"] > cost["base_cost"]
    
    def test_recommend_tier_open_source(self):
        """Test tier recommendation for low usage."""
        service = PricingService()
        
        metrics = UsageMetrics(
            organization_id="test-org",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            total_requests=5000,
            active_seats=2,
            active_policy_packs=["basic"],
            active_compliance_modules=[],
        )
        
        recommended = service.recommend_tier(metrics)
        assert recommended == LicenseType.OPEN_SOURCE
    
    def test_recommend_tier_starter(self):
        """Test tier recommendation for moderate usage."""
        service = PricingService()
        
        metrics = UsageMetrics(
            organization_id="test-org",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            total_requests=50000,
            active_seats=5,
            active_policy_packs=["basic", "security"],
            active_compliance_modules=["gdpr"],
        )
        
        recommended = service.recommend_tier(metrics)
        assert recommended == LicenseType.STARTER
    
    def test_recommend_tier_enterprise(self):
        """Test tier recommendation for high usage."""
        service = PricingService()
        
        metrics = UsageMetrics(
            organization_id="test-org",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            total_requests=2000000,
            active_seats=100,
            active_policy_packs=["basic", "security", "compliance", "advanced"],
            active_compliance_modules=["gdpr", "hipaa", "soc2", "pci-dss"],
        )
        
        recommended = service.recommend_tier(metrics)
        assert recommended == LicenseType.ENTERPRISE
    
    def test_feature_access_gating(self):
        """Test feature access checking."""
        service = PricingService()
        
        # Open source doesn't have SSO
        assert not service.check_feature_access(LicenseType.OPEN_SOURCE, "sso")
        
        # Professional has SSO
        assert service.check_feature_access(LicenseType.PROFESSIONAL, "sso")
        
        # All tiers have basic policies
        assert service.check_feature_access(LicenseType.OPEN_SOURCE, "basic_policies")
        assert service.check_feature_access(LicenseType.ENTERPRISE, "basic_policies")
    
    def test_upgrade_benefits(self):
        """Test upgrade benefits calculation."""
        service = PricingService()
        
        benefits = service.get_upgrade_benefits(
            LicenseType.STARTER,
            LicenseType.PROFESSIONAL
        )
        
        assert "new_features" in benefits
        assert "increased_limits" in benefits
        assert "support_upgrade" in benefits
        assert len(benefits["new_features"]) > 0


class TestMeteringService:
    """Test metering service functionality."""
    
    def test_record_request_event(self):
        """Test recording a request event."""
        service = MeteringService()
        
        event = service.record_request(
            organization_id="test-org",
            agent_id="test-agent",
            execution_id="exec-123",
        )
        
        assert event.organization_id == "test-org"
        assert event.pricing_axis == PricingAxis.PER_REQUEST
        assert event.event_type == "ai_request"
        assert event.resource_id == "test-agent"
    
    def test_record_policy_pack_usage(self):
        """Test recording policy pack usage."""
        service = MeteringService()
        
        event = service.record_policy_pack_usage(
            organization_id="test-org",
            policy_pack_id="security-pack",
            execution_id="exec-123",
        )
        
        assert event.pricing_axis == PricingAxis.PER_POLICY_PACK
        assert event.resource_id == "security-pack"
    
    def test_record_compliance_validation(self):
        """Test recording compliance validation."""
        service = MeteringService()
        
        event = service.record_compliance_validation(
            organization_id="test-org",
            compliance_module="gdpr",
        )
        
        assert event.pricing_axis == PricingAxis.PER_COMPLIANCE_MODULE
        assert event.resource_id == "gdpr"
    
    def test_get_usage_metrics_aggregation(self):
        """Test usage metrics aggregation."""
        service = MeteringService()
        
        # Record some events
        org_id = "test-org"
        for i in range(10):
            service.record_request(org_id, f"agent-{i % 3}", f"exec-{i}")
        
        service.record_policy_pack_usage(org_id, "security", "exec-1")
        service.record_policy_pack_usage(org_id, "compliance", "exec-2")
        service.record_compliance_validation(org_id, "gdpr")
        
        # Get metrics
        metrics = service.get_usage_metrics(org_id)
        
        assert metrics.total_requests == 10
        assert len(metrics.requests_by_agent) == 3
        assert len(metrics.active_policy_packs) == 2
        assert len(metrics.active_compliance_modules) == 1
    
    def test_get_usage_metrics_by_period(self):
        """Test usage metrics for specific period."""
        service = MeteringService()
        
        org_id = "test-org"
        
        # Record event now
        service.record_request(org_id, "agent-1", "exec-1")
        
        # Get metrics for current month
        now = datetime.utcnow()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        metrics = service.get_usage_metrics(org_id, period_start=start)
        
        assert metrics.total_requests == 1
    
    def test_get_billing_events_filtering(self):
        """Test billing events with filters."""
        service = MeteringService()
        
        org_id = "test-org"
        
        # Record different types of events
        service.record_request(org_id, "agent-1", "exec-1")
        service.record_policy_pack_usage(org_id, "security", "exec-2")
        service.record_compliance_validation(org_id, "gdpr")
        
        # Get all events
        all_events = service.get_billing_events(org_id)
        assert len(all_events) == 3
        
        # Filter by pricing axis
        request_events = service.get_billing_events(
            org_id,
            pricing_axis=PricingAxis.PER_REQUEST
        )
        assert len(request_events) == 1
        
        # Filter by event type
        compliance_events = service.get_billing_events(
            org_id,
            event_type="compliance_validation"
        )
        assert len(compliance_events) == 1
    
    def test_metering_statistics(self):
        """Test metering statistics."""
        service = MeteringService()
        
        # Record some events
        service.record_request("org-1", "agent-1", "exec-1")
        service.record_request("org-2", "agent-2", "exec-2")
        
        stats = service.get_statistics()
        
        assert stats["total_events"] == 2
        assert stats["organizations_tracked"] == 2
        assert "events_by_pricing_axis" in stats


class TestLicenseManager:
    """Test license manager functionality."""
    
    def test_generate_license_key(self):
        """Test license key generation."""
        manager = LicenseManager()
        service = PricingService()
        
        pricing_tier = service.get_tier(LicenseType.PROFESSIONAL)
        
        license_key = manager.generate_license_key(
            organization_id="test-org",
            tier=LicenseType.PROFESSIONAL,
            pricing_tier=pricing_tier,
        )
        
        assert license_key.key.startswith("ACP-")
        assert license_key.organization_id == "test-org"
        assert license_key.tier == LicenseType.PROFESSIONAL
        assert license_key.active
        assert not license_key.revoked
    
    def test_validate_license_valid(self):
        """Test validating a valid license."""
        manager = LicenseManager()
        service = PricingService()
        
        pricing_tier = service.get_tier(LicenseType.PROFESSIONAL)
        license_key = manager.generate_license_key(
            organization_id="test-org",
            tier=LicenseType.PROFESSIONAL,
            pricing_tier=pricing_tier,
        )
        
        valid, reason = manager.validate_license(license_key.key)
        
        assert valid
        assert reason is None
    
    def test_validate_license_invalid_key(self):
        """Test validating an invalid license."""
        manager = LicenseManager()
        
        valid, reason = manager.validate_license("INVALID-KEY")
        
        assert not valid
        assert "Invalid" in reason
    
    def test_validate_license_expired(self):
        """Test validating an expired license."""
        manager = LicenseManager()
        service = PricingService()
        
        pricing_tier = service.get_tier(LicenseType.STARTER)
        
        # Create license with 0 days validity (already expired)
        license_key = manager.generate_license_key(
            organization_id="test-org",
            tier=LicenseType.STARTER,
            pricing_tier=pricing_tier,
            validity_days=0,
        )
        
        # Manually set expiration to past
        license_key.expires_at = datetime.utcnow() - timedelta(days=1)
        manager.licenses[license_key.key] = license_key
        
        valid, reason = manager.validate_license(license_key.key)
        
        assert not valid
        assert "expired" in reason.lower()
    
    def test_check_feature_access(self):
        """Test feature access checking."""
        manager = LicenseManager()
        service = PricingService()
        
        pricing_tier = service.get_tier(LicenseType.PROFESSIONAL)
        license_key = manager.generate_license_key(
            organization_id="test-org",
            tier=LicenseType.PROFESSIONAL,
            pricing_tier=pricing_tier,
        )
        
        # Professional has SSO
        has_access, reason = manager.check_feature_access(license_key.key, "sso")
        assert has_access
        
        # Professional has custom plugins
        has_access, reason = manager.check_feature_access(
            license_key.key,
            "custom_plugins"
        )
        assert has_access
    
    def test_check_feature_access_denied(self):
        """Test feature access denial."""
        manager = LicenseManager()
        service = PricingService()
        
        pricing_tier = service.get_tier(LicenseType.OPEN_SOURCE)
        license_key = manager.generate_license_key(
            organization_id="test-org",
            tier=LicenseType.OPEN_SOURCE,
            pricing_tier=pricing_tier,
        )
        
        # Open source doesn't have SSO
        has_access, reason = manager.check_feature_access(license_key.key, "sso")
        assert not has_access
        assert "not enabled" in reason
    
    def test_check_limit(self):
        """Test limit checking."""
        manager = LicenseManager()
        service = PricingService()
        
        pricing_tier = service.get_tier(LicenseType.STARTER)
        license_key = manager.generate_license_key(
            organization_id="test-org",
            tier=LicenseType.STARTER,
            pricing_tier=pricing_tier,
        )
        
        # Within limit
        within, reason = manager.check_limit(
            license_key.key,
            "max_agents",
            10
        )
        assert within
        
        # Over limit
        within, reason = manager.check_limit(
            license_key.key,
            "max_agents",
            50
        )
        assert not within
        assert "Exceeded" in reason
    
    def test_revoke_license(self):
        """Test license revocation."""
        manager = LicenseManager()
        service = PricingService()
        
        pricing_tier = service.get_tier(LicenseType.PROFESSIONAL)
        license_key = manager.generate_license_key(
            organization_id="test-org",
            tier=LicenseType.PROFESSIONAL,
            pricing_tier=pricing_tier,
        )
        
        # Revoke license
        success = manager.revoke_license(license_key.key, "Policy violation")
        assert success
        
        # Validate should fail
        valid, reason = manager.validate_license(license_key.key)
        assert not valid
        assert "revoked" in reason.lower()
    
    def test_get_license_by_org(self):
        """Test getting license by organization."""
        manager = LicenseManager()
        service = PricingService()
        
        org_id = "test-org"
        pricing_tier = service.get_tier(LicenseType.PROFESSIONAL)
        
        license_key = manager.generate_license_key(
            organization_id=org_id,
            tier=LicenseType.PROFESSIONAL,
            pricing_tier=pricing_tier,
        )
        
        # Get by org
        retrieved = manager.get_license_by_org(org_id)
        
        assert retrieved is not None
        assert retrieved.organization_id == org_id
        assert retrieved.key == license_key.key
    
    def test_list_licenses_filtering(self):
        """Test listing licenses with filters."""
        manager = LicenseManager()
        service = PricingService()
        
        # Generate multiple licenses
        for i in range(3):
            pricing_tier = service.get_tier(LicenseType.STARTER)
            manager.generate_license_key(
                organization_id=f"org-{i}",
                tier=LicenseType.STARTER,
                pricing_tier=pricing_tier,
            )
        
        # Generate one professional license
        pricing_tier = service.get_tier(LicenseType.PROFESSIONAL)
        manager.generate_license_key(
            organization_id="org-pro",
            tier=LicenseType.PROFESSIONAL,
            pricing_tier=pricing_tier,
        )
        
        # List all
        all_licenses = manager.list_licenses()
        assert len(all_licenses) == 4
        
        # Filter by tier
        starter_licenses = manager.list_licenses(tier=LicenseType.STARTER)
        assert len(starter_licenses) == 3
        
        # Filter by org
        org_licenses = manager.list_licenses(organization_id="org-1")
        assert len(org_licenses) == 1
    
    def test_license_statistics(self):
        """Test license statistics."""
        manager = LicenseManager()
        service = PricingService()
        
        # Generate some licenses
        for tier in [LicenseType.STARTER, LicenseType.PROFESSIONAL]:
            pricing_tier = service.get_tier(tier)
            manager.generate_license_key(
                organization_id=f"org-{tier.value}",
                tier=tier,
                pricing_tier=pricing_tier,
            )
        
        stats = manager.get_statistics()
        
        assert stats["total_licenses"] == 2
        assert stats["active_licenses"] == 2
        assert stats["revoked_licenses"] == 0
        assert stats["organizations"] == 2
