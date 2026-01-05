"""
Pricing Service

Defines pricing tiers and manages pricing logic.
Implements the "Salesforce Playbook" - multiple pricing axes, open core model.
"""

from typing import Dict, List, Optional
from datetime import datetime
from pricing.models import (
    PricingTier,
    LicenseType,
    AuditTier,
    SubscriptionPlan,
    UsageMetrics,
)


class PricingService:
    """
    Pricing service - defines and manages pricing tiers.
    
    The Salesforce playbook:
    1. Open core - Free base, paid enterprise features
    2. Multiple pricing axes - Charge for value, not cost
    3. Clear upgrade path - From free to enterprise
    4. Land and expand - Start small, grow big
    """
    
    def __init__(self):
        """Initialize pricing service with tier definitions."""
        self.tiers = self._define_pricing_tiers()
    
    def _define_pricing_tiers(self) -> Dict[LicenseType, PricingTier]:
        """
        Define all pricing tiers.
        
        Clean. Proven. Scalable.
        """
        return {
            LicenseType.OPEN_SOURCE: PricingTier(
                tier=LicenseType.OPEN_SOURCE,
                name="Open Source",
                description="Community edition - Basic governance for learning and development",
                
                # Limits
                max_requests_per_month=10000,
                max_agents=5,
                max_seats=3,
                
                # Included features
                included_policy_packs=["basic"],
                included_compliance_modules=[],
                
                # Audit
                audit_tier=AuditTier.BASIC,
                audit_retention_days=7,
                
                # Features
                features={
                    "basic_policies": True,
                    "audit_logs": True,
                    "kill_switch": True,
                    "api_access": True,
                    "dashboard": True,
                    "compliance_modules": False,
                    "advanced_policies": False,
                    "rbac": False,
                    "sso": False,
                    "approval_workflows": False,
                    "custom_plugins": False,
                    "dedicated_support": False,
                },
                
                # Pricing
                base_price_monthly=0.0,
                per_request_price=None,
                per_seat_price=None,
                
                # Support
                support_level="community",
                sla_uptime=None,
            ),
            
            LicenseType.STARTER: PricingTier(
                tier=LicenseType.STARTER,
                name="Starter",
                description="Perfect for small teams getting serious about AI governance",
                
                # Limits
                max_requests_per_month=100000,
                max_agents=20,
                max_seats=10,
                
                # Included features
                included_policy_packs=["basic", "security"],
                additional_policy_pack_price=49.0,
                included_compliance_modules=["gdpr"],
                additional_compliance_module_price=99.0,
                
                # Audit
                audit_tier=AuditTier.STANDARD,
                audit_retention_days=30,
                
                # Features
                features={
                    "basic_policies": True,
                    "audit_logs": True,
                    "kill_switch": True,
                    "api_access": True,
                    "dashboard": True,
                    "compliance_modules": True,
                    "advanced_policies": True,
                    "rbac": True,
                    "sso": False,
                    "approval_workflows": True,
                    "custom_plugins": False,
                    "dedicated_support": False,
                },
                
                # Pricing
                base_price_monthly=299.0,
                per_request_price=0.001,  # $1 per 1000 requests
                per_seat_price=29.0,
                
                # Support
                support_level="email",
                sla_uptime="99.0%",
            ),
            
            LicenseType.PROFESSIONAL: PricingTier(
                tier=LicenseType.PROFESSIONAL,
                name="Professional",
                description="Full governance for growing teams and production deployments",
                
                # Limits
                max_requests_per_month=1000000,
                max_agents=100,
                max_seats=50,
                
                # Included features
                included_policy_packs=["basic", "security", "cost-control", "compliance"],
                additional_policy_pack_price=99.0,
                included_compliance_modules=["gdpr", "soc2", "hipaa"],
                additional_compliance_module_price=199.0,
                
                # Audit
                audit_tier=AuditTier.PREMIUM,
                audit_retention_days=90,
                
                # Features
                features={
                    "basic_policies": True,
                    "audit_logs": True,
                    "kill_switch": True,
                    "api_access": True,
                    "dashboard": True,
                    "compliance_modules": True,
                    "advanced_policies": True,
                    "rbac": True,
                    "sso": True,
                    "approval_workflows": True,
                    "custom_plugins": True,
                    "dedicated_support": False,
                },
                
                # Pricing
                base_price_monthly=999.0,
                per_request_price=0.0005,  # $1 per 2000 requests
                per_seat_price=49.0,
                
                # Support
                support_level="priority",
                sla_uptime="99.5%",
            ),
            
            LicenseType.ENTERPRISE: PricingTier(
                tier=LicenseType.ENTERPRISE,
                name="Enterprise",
                description="Enterprise-grade governance with unlimited scale and dedicated support",
                
                # Limits (unlimited)
                max_requests_per_month=None,
                max_agents=None,
                max_seats=None,
                
                # Included features (all)
                included_policy_packs=["all"],
                additional_policy_pack_price=0.0,
                included_compliance_modules=["all"],
                additional_compliance_module_price=0.0,
                
                # Audit
                audit_tier=AuditTier.ENTERPRISE,
                audit_retention_days=365,
                
                # Features (all)
                features={
                    "basic_policies": True,
                    "audit_logs": True,
                    "kill_switch": True,
                    "api_access": True,
                    "dashboard": True,
                    "compliance_modules": True,
                    "advanced_policies": True,
                    "rbac": True,
                    "sso": True,
                    "approval_workflows": True,
                    "custom_plugins": True,
                    "dedicated_support": True,
                    "custom_integrations": True,
                    "priority_roadmap": True,
                    "on_premise_deployment": True,
                    "air_gapped_deployment": True,
                },
                
                # Pricing (contact sales)
                base_price_monthly=4999.0,  # Starting price
                per_request_price=0.0002,  # $1 per 5000 requests (volume discount)
                per_seat_price=99.0,
                
                # Support
                support_level="dedicated",
                sla_uptime="99.9%",
            ),
        }
    
    def get_tier(self, tier: LicenseType) -> PricingTier:
        """Get pricing tier definition."""
        return self.tiers[tier]
    
    def list_tiers(self) -> List[PricingTier]:
        """List all pricing tiers."""
        return list(self.tiers.values())
    
    def calculate_monthly_cost(
        self,
        tier: LicenseType,
        requests: int,
        seats: int,
        additional_policy_packs: int = 0,
        additional_compliance_modules: int = 0,
        audit_tier_upgrade: Optional[AuditTier] = None,
    ) -> Dict[str, float]:
        """
        Calculate monthly cost for a given usage profile.
        
        Args:
            tier: License tier
            requests: Number of requests per month
            seats: Number of user seats
            additional_policy_packs: Additional policy packs beyond included
            additional_compliance_modules: Additional compliance modules beyond included
            audit_tier_upgrade: Upgrade to higher audit tier
        
        Returns:
            Cost breakdown with total
        """
        pricing = self.tiers[tier]
        
        # Base cost
        base_cost = pricing.base_price_monthly
        
        # Request cost (if metered)
        request_cost = 0.0
        if pricing.per_request_price:
            # Check if over limit for non-enterprise tiers
            if pricing.max_requests_per_month and requests > pricing.max_requests_per_month:
                # Charge for overage
                overage = requests - pricing.max_requests_per_month
                request_cost = overage * pricing.per_request_price
            elif not pricing.max_requests_per_month:
                # Enterprise: all requests are metered
                request_cost = requests * pricing.per_request_price
        
        # Seat cost
        seat_cost = 0.0
        if pricing.per_seat_price:
            # Check if over included seats
            included_seats = pricing.max_seats or 0
            if seats > included_seats:
                seat_cost = (seats - included_seats) * pricing.per_seat_price
        
        # Policy pack cost
        policy_pack_cost = 0.0
        if additional_policy_packs > 0 and pricing.additional_policy_pack_price:
            policy_pack_cost = additional_policy_packs * pricing.additional_policy_pack_price
        
        # Compliance module cost
        compliance_cost = 0.0
        if additional_compliance_modules > 0 and pricing.additional_compliance_module_price:
            compliance_cost = (
                additional_compliance_modules * pricing.additional_compliance_module_price
            )
        
        # Audit tier upgrade cost
        audit_cost = 0.0
        if audit_tier_upgrade and audit_tier_upgrade != pricing.audit_tier:
            audit_pricing = {
                AuditTier.BASIC: 0,
                AuditTier.STANDARD: 99,
                AuditTier.PREMIUM: 299,
                AuditTier.ENTERPRISE: 999,
            }
            current_cost = audit_pricing[pricing.audit_tier]
            upgrade_cost = audit_pricing[audit_tier_upgrade]
            audit_cost = max(0, upgrade_cost - current_cost)
        
        # Total
        total = (
            base_cost
            + request_cost
            + seat_cost
            + policy_pack_cost
            + compliance_cost
            + audit_cost
        )
        
        return {
            "base_cost": base_cost,
            "request_cost": request_cost,
            "seat_cost": seat_cost,
            "policy_pack_cost": policy_pack_cost,
            "compliance_module_cost": compliance_cost,
            "audit_tier_cost": audit_cost,
            "total": total,
            "tier": tier.value,
            "breakdown_details": {
                "requests": requests,
                "seats": seats,
                "additional_policy_packs": additional_policy_packs,
                "additional_compliance_modules": additional_compliance_modules,
            },
        }
    
    def recommend_tier(self, usage_metrics: UsageMetrics) -> LicenseType:
        """
        Recommend appropriate tier based on usage.
        
        Sales intelligence: Know when to upsell.
        """
        requests = usage_metrics.total_requests
        seats = usage_metrics.active_seats
        policy_packs = len(usage_metrics.active_policy_packs)
        compliance_modules = len(usage_metrics.active_compliance_modules)
        
        # Enterprise indicators
        if (
            requests > 1000000
            or seats > 50
            or compliance_modules > 3
            or policy_packs > 4
        ):
            return LicenseType.ENTERPRISE
        
        # Professional indicators
        if (
            requests > 100000
            or seats > 10
            or compliance_modules > 1
            or policy_packs > 2
        ):
            return LicenseType.PROFESSIONAL
        
        # Starter indicators
        if requests > 10000 or seats > 3 or compliance_modules > 0:
            return LicenseType.STARTER
        
        # Otherwise, open source is fine
        return LicenseType.OPEN_SOURCE
    
    def check_feature_access(self, tier: LicenseType, feature: str) -> bool:
        """
        Check if a tier has access to a feature.
        
        Feature gating - the key to monetization.
        """
        pricing = self.tiers[tier]
        return pricing.features.get(feature, False)
    
    def get_upgrade_benefits(
        self, current_tier: LicenseType, target_tier: LicenseType
    ) -> Dict[str, any]:
        """
        Get benefits of upgrading from current to target tier.
        
        Sales enablement: Show the value.
        """
        current = self.tiers[current_tier]
        target = self.tiers[target_tier]
        
        # New features
        new_features = []
        for feature, enabled in target.features.items():
            if enabled and not current.features.get(feature, False):
                new_features.append(feature)
        
        # Increased limits
        limits = {}
        if target.max_requests_per_month != current.max_requests_per_month:
            limits["requests"] = {
                "current": current.max_requests_per_month,
                "new": target.max_requests_per_month,
            }
        if target.max_agents != current.max_agents:
            limits["agents"] = {
                "current": current.max_agents,
                "new": target.max_agents,
            }
        if target.max_seats != current.max_seats:
            limits["seats"] = {
                "current": current.max_seats,
                "new": target.max_seats,
            }
        
        # Better support
        support_upgrade = target.support_level != current.support_level
        
        # Better SLA
        sla_upgrade = target.sla_uptime != current.sla_uptime
        
        return {
            "new_features": new_features,
            "increased_limits": limits,
            "support_upgrade": {
                "enabled": support_upgrade,
                "current": current.support_level,
                "new": target.support_level,
            },
            "sla_upgrade": {
                "enabled": sla_upgrade,
                "current": current.sla_uptime,
                "new": target.sla_uptime,
            },
            "current_tier": current_tier.value,
            "target_tier": target_tier.value,
        }
