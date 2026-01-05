#!/usr/bin/env python3
"""
Monetization Demo Script

Demonstrates the Phase 5 monetization features:
- Multiple pricing tiers
- Usage metering
- Cost calculation
- License management

Run this to see the Salesforce playbook in action.
"""

import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '/home/runner/work/ai-control-plane/ai-control-plane')

from pricing.service import PricingService
from pricing.metering import MeteringService
from pricing.license import LicenseManager
from pricing.models import LicenseType, UsageMetrics


def print_header(text: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def demo_pricing_tiers():
    """Demo: Show all pricing tiers."""
    print_header("PRICING TIERS - The Salesforce Playbook")
    
    service = PricingService()
    
    for tier in service.list_tiers():
        tier_value = tier.tier if isinstance(tier.tier, str) else tier.tier.value
        print(f"🎯 {tier.name} ({tier_value})")
        print(f"   {tier.description}")
        print(f"   Base Price: ${tier.base_price_monthly:,.2f}/month")
        
        if tier.max_requests_per_month:
            print(f"   Requests: {tier.max_requests_per_month:,}/month")
        else:
            print(f"   Requests: Unlimited")
        
        if tier.max_seats:
            print(f"   Seats: {tier.max_seats}")
        else:
            print(f"   Seats: Unlimited")
        
        print(f"   Policy Packs: {', '.join(tier.included_policy_packs)}")
        print(f"   Compliance: {', '.join(tier.included_compliance_modules) or 'None'}")
        print(f"   Support: {tier.support_level}")
        if tier.sla_uptime:
            print(f"   SLA: {tier.sla_uptime}")
        print()


def demo_cost_calculation():
    """Demo: Calculate costs for different usage profiles."""
    print_header("COST CALCULATION - What You'll Pay")
    
    service = PricingService()
    
    # Small team scenario
    print("📊 Scenario 1: Small Team")
    print("   50K requests/month, 5 seats, no add-ons")
    
    cost = service.calculate_monthly_cost(
        tier=LicenseType.STARTER,
        requests=50000,
        seats=5,
    )
    
    print(f"   Base Cost: ${cost['base_cost']:,.2f}")
    print(f"   Request Cost: ${cost['request_cost']:,.2f}")
    print(f"   Seat Cost: ${cost['seat_cost']:,.2f}")
    print(f"   TOTAL: ${cost['total']:,.2f}/month")
    print()
    
    # Growing company scenario
    print("📊 Scenario 2: Growing Company")
    print("   500K requests/month, 20 seats, +2 policy packs, +1 compliance module")
    
    cost = service.calculate_monthly_cost(
        tier=LicenseType.PROFESSIONAL,
        requests=500000,
        seats=20,
        additional_policy_packs=2,
        additional_compliance_modules=1,
    )
    
    print(f"   Base Cost: ${cost['base_cost']:,.2f}")
    print(f"   Request Cost: ${cost['request_cost']:,.2f}")
    print(f"   Seat Cost: ${cost['seat_cost']:,.2f}")
    print(f"   Policy Packs: ${cost['policy_pack_cost']:,.2f}")
    print(f"   Compliance: ${cost['compliance_module_cost']:,.2f}")
    print(f"   TOTAL: ${cost['total']:,.2f}/month")
    print()
    
    # Enterprise scenario
    print("📊 Scenario 3: Enterprise")
    print("   5M requests/month, 100 seats, all features")
    
    cost = service.calculate_monthly_cost(
        tier=LicenseType.ENTERPRISE,
        requests=5000000,
        seats=100,
    )
    
    print(f"   Base Cost: ${cost['base_cost']:,.2f}")
    print(f"   Request Cost: ${cost['request_cost']:,.2f}")
    print(f"   Seat Cost: ${cost['seat_cost']:,.2f}")
    print(f"   TOTAL: ${cost['total']:,.2f}/month")
    print()


def demo_usage_metering():
    """Demo: Record and aggregate usage."""
    print_header("USAGE METERING - Track Every Request")
    
    metering = MeteringService()
    org_id = "demo-company"
    
    print(f"📈 Recording usage for {org_id}...")
    print()
    
    # Simulate usage
    print("Recording 100 AI requests...")
    for i in range(100):
        metering.record_request(org_id, f"agent-{i % 5}", f"exec-{i}")
    
    print("Recording policy pack usage...")
    metering.record_policy_pack_usage(org_id, "security-pack", "exec-1")
    metering.record_policy_pack_usage(org_id, "compliance-pack", "exec-2")
    
    print("Recording compliance validations...")
    metering.record_compliance_validation(org_id, "gdpr")
    metering.record_compliance_validation(org_id, "hipaa")
    print()
    
    # Get metrics
    metrics = metering.get_usage_metrics(org_id)
    
    print(f"📊 Usage Summary:")
    print(f"   Total Requests: {metrics.total_requests:,}")
    print(f"   Unique Agents: {len(metrics.requests_by_agent)}")
    print(f"   Policy Packs Used: {len(metrics.active_policy_packs)}")
    print(f"   Compliance Modules: {len(metrics.active_compliance_modules)}")
    print()
    
    print(f"   Requests by Agent:")
    for agent_id, count in sorted(metrics.requests_by_agent.items()):
        print(f"      {agent_id}: {count}")
    print()


def demo_tier_recommendation():
    """Demo: Recommend tier based on usage."""
    print_header("TIER RECOMMENDATION - Upsell Intelligence")
    
    service = PricingService()
    
    # Simulate different usage patterns
    scenarios = [
        {
            "name": "Hobby Project",
            "requests": 5000,
            "seats": 2,
            "policy_packs": ["basic"],
            "compliance": [],
        },
        {
            "name": "Small Startup",
            "requests": 75000,
            "seats": 8,
            "policy_packs": ["basic", "security"],
            "compliance": ["gdpr"],
        },
        {
            "name": "Growth Stage",
            "requests": 500000,
            "seats": 30,
            "policy_packs": ["basic", "security", "compliance"],
            "compliance": ["gdpr", "soc2"],
        },
        {
            "name": "Enterprise",
            "requests": 5000000,
            "seats": 150,
            "policy_packs": ["basic", "security", "compliance", "advanced"],
            "compliance": ["gdpr", "hipaa", "soc2", "pci-dss"],
        },
    ]
    
    for scenario in scenarios:
        metrics = UsageMetrics(
            organization_id="test",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            total_requests=scenario["requests"],
            active_seats=scenario["seats"],
            active_policy_packs=scenario["policy_packs"],
            active_compliance_modules=scenario["compliance"],
        )
        
        recommended = service.recommend_tier(metrics)
        
        print(f"🎯 {scenario['name']}")
        print(f"   Requests: {scenario['requests']:,}/month")
        print(f"   Seats: {scenario['seats']}")
        print(f"   → Recommended: {recommended.value.upper()}")
        print()


def demo_license_management():
    """Demo: Generate and validate licenses."""
    print_header("LICENSE MANAGEMENT - Enterprise Control")
    
    manager = LicenseManager()
    pricing = PricingService()
    
    # Generate licenses for different tiers
    print("🔑 Generating License Keys...")
    print()
    
    for tier in [LicenseType.STARTER, LicenseType.PROFESSIONAL, LicenseType.ENTERPRISE]:
        pricing_tier = pricing.get_tier(tier)
        license = manager.generate_license_key(
            organization_id=f"{tier.value}-company",
            tier=tier,
            pricing_tier=pricing_tier,
        )
        
        print(f"   {tier.value.upper()}: {license.key[:40]}...")
        print(f"      Organization: {license.organization_id}")
        print(f"      Features: {len(license.enabled_features)} enabled")
        
        # Validate license
        valid, reason = manager.validate_license(license.key)
        print(f"      Valid: {'✅ Yes' if valid else f'❌ No ({reason})'}")
        print()
    
    # Demo feature gating
    print("🔒 Feature Gating Examples:")
    print()
    
    # Get a professional license
    prof_tier = pricing.get_tier(LicenseType.PROFESSIONAL)
    prof_license = manager.generate_license_key(
        organization_id="test-company",
        tier=LicenseType.PROFESSIONAL,
        pricing_tier=prof_tier,
    )
    
    features_to_check = ["basic_policies", "sso", "custom_plugins", "dedicated_support"]
    
    for feature in features_to_check:
        has_access, reason = manager.check_feature_access(prof_license.key, feature)
        status = "✅ Allowed" if has_access else "❌ Denied"
        print(f"   {feature}: {status}")
    
    print()


def demo_statistics():
    """Demo: Show metering and license statistics."""
    print_header("STATISTICS - Monitor the Money")
    
    metering = MeteringService()
    manager = LicenseManager()
    
    # Record some activity
    for i in range(50):
        metering.record_request(f"org-{i % 3}", f"agent-{i % 5}", f"exec-{i}")
    
    meter_stats = metering.get_statistics()
    
    print("📊 Metering Statistics:")
    print(f"   Total Events: {meter_stats['total_events']:,}")
    print(f"   Organizations: {meter_stats['organizations_tracked']}")
    print(f"   By Pricing Axis:")
    for axis, count in meter_stats['events_by_pricing_axis'].items():
        print(f"      {axis}: {count}")
    print()
    
    # Generate some licenses
    pricing = PricingService()
    for tier in [LicenseType.STARTER, LicenseType.PROFESSIONAL]:
        for i in range(2):
            pricing_tier = pricing.get_tier(tier)
            manager.generate_license_key(
                organization_id=f"{tier.value}-org-{i}",
                tier=tier,
                pricing_tier=pricing_tier,
            )
    
    license_stats = manager.get_statistics()
    
    print("🔑 License Statistics:")
    print(f"   Total Licenses: {license_stats['total_licenses']}")
    print(f"   Active: {license_stats['active_licenses']}")
    print(f"   By Tier:")
    for tier, count in license_stats['licenses_by_tier'].items():
        print(f"      {tier}: {count}")
    print()


def main():
    """Run all demos."""
    print("\n" + "🎯" * 35)
    print("  PHASE 5: MONETIZATION DEMO")
    print("  The Salesforce Playbook for AI Control Plane")
    print("🎯" * 35)
    
    try:
        demo_pricing_tiers()
        demo_cost_calculation()
        demo_usage_metering()
        demo_tier_recommendation()
        demo_license_management()
        demo_statistics()
        
        print_header("DEMO COMPLETE")
        print("✅ All monetization features working!")
        print()
        print("💰 Ready to print money without selling models.")
        print("📈 Open core, paid enterprise control.")
        print("🎯 Clean. Proven. Scalable.")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
