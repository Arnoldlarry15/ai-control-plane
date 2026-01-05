"""
Pricing and Monetization Models

Data models for the AI Control Plane monetization system.
Implements multiple pricing axes per the Salesforce playbook.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class LicenseType(str, Enum):
    """License types following open core model."""
    OPEN_SOURCE = "open_source"  # Free, community edition
    STARTER = "starter"  # Basic paid features
    PROFESSIONAL = "professional"  # Full features for teams
    ENTERPRISE = "enterprise"  # Advanced enterprise features
    CUSTOM = "custom"  # Custom enterprise agreements


class PricingAxis(str, Enum):
    """
    Pricing axes - multiple ways to charge.
    
    The Salesforce playbook: charge for value, not cost.
    """
    PER_REQUEST = "per_request"  # Per AI request governed
    PER_POLICY_PACK = "per_policy_pack"  # Per policy pack enabled
    PER_COMPLIANCE_MODULE = "per_compliance_module"  # Per compliance standard
    PER_SEAT = "per_seat"  # Per user seat
    PER_ORG = "per_org"  # Per organization (flat rate)
    AUDIT_TIER = "audit_tier"  # Audit & reporting tier


class AuditTier(str, Enum):
    """Audit and reporting tiers."""
    BASIC = "basic"  # 30 days retention, basic reports
    STANDARD = "standard"  # 90 days retention, advanced reports
    PREMIUM = "premium"  # 1 year retention, custom reports
    ENTERPRISE = "enterprise"  # Unlimited retention, compliance exports


class PricingTier(BaseModel):
    """
    Pricing tier definition.
    
    Defines what's included in each tier and the pricing model.
    """
    tier: LicenseType = Field(..., description="License tier")
    name: str = Field(..., description="Marketing name")
    description: str = Field(..., description="Tier description")
    
    # Feature flags
    max_requests_per_month: Optional[int] = Field(
        None,
        description="Maximum governed requests per month (None = unlimited)"
    )
    max_agents: Optional[int] = Field(
        None,
        description="Maximum agents (None = unlimited)"
    )
    max_seats: Optional[int] = Field(
        None,
        description="Maximum user seats (None = unlimited)"
    )
    
    # Policy packs
    included_policy_packs: List[str] = Field(
        default_factory=list,
        description="Included policy packs"
    )
    additional_policy_pack_price: Optional[float] = Field(
        None,
        description="Price per additional policy pack (USD/month)"
    )
    
    # Compliance modules
    included_compliance_modules: List[str] = Field(
        default_factory=list,
        description="Included compliance standards (e.g., GDPR, HIPAA)"
    )
    additional_compliance_module_price: Optional[float] = Field(
        None,
        description="Price per additional compliance module (USD/month)"
    )
    
    # Audit & reporting
    audit_tier: AuditTier = Field(
        default=AuditTier.BASIC,
        description="Audit and reporting tier"
    )
    audit_retention_days: int = Field(
        default=30,
        description="Audit log retention in days"
    )
    
    # Features
    features: Dict[str, bool] = Field(
        default_factory=dict,
        description="Feature flags"
    )
    
    # Pricing
    base_price_monthly: float = Field(
        default=0.0,
        description="Base monthly price (USD)"
    )
    per_request_price: Optional[float] = Field(
        None,
        description="Price per governed request (USD)"
    )
    per_seat_price: Optional[float] = Field(
        None,
        description="Price per user seat (USD/month)"
    )
    
    # Support
    support_level: str = Field(
        default="community",
        description="Support level: community, email, priority, dedicated"
    )
    sla_uptime: Optional[str] = Field(
        None,
        description="SLA uptime guarantee (e.g., '99.9%')"
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "tier": "professional",
                "name": "Professional",
                "description": "Full governance for growing teams",
                "max_requests_per_month": 1000000,
                "max_agents": 50,
                "max_seats": 25,
                "included_policy_packs": ["basic", "security", "cost-control"],
                "additional_policy_pack_price": 99.0,
                "included_compliance_modules": ["gdpr", "soc2"],
                "additional_compliance_module_price": 299.0,
                "audit_tier": "standard",
                "audit_retention_days": 90,
                "base_price_monthly": 999.0,
                "per_seat_price": 49.0,
                "support_level": "email",
                "sla_uptime": "99.5%",
            }
        }


class SubscriptionPlan(BaseModel):
    """
    Active subscription for an organization.
    """
    id: str = Field(..., description="Subscription ID")
    organization_id: str = Field(..., description="Organization ID")
    tier: LicenseType = Field(..., description="Current pricing tier")
    
    # Billing
    billing_cycle: str = Field(
        default="monthly",
        description="Billing cycle: monthly, annual"
    )
    current_period_start: datetime = Field(..., description="Current billing period start")
    current_period_end: datetime = Field(..., description="Current billing period end")
    
    # Usage limits
    request_limit: Optional[int] = Field(
        None,
        description="Request limit for current period"
    )
    seat_limit: Optional[int] = Field(
        None,
        description="Seat limit"
    )
    
    # Add-ons
    active_policy_packs: List[str] = Field(
        default_factory=list,
        description="Active policy pack IDs"
    )
    active_compliance_modules: List[str] = Field(
        default_factory=list,
        description="Active compliance module IDs"
    )
    audit_tier: AuditTier = Field(
        default=AuditTier.BASIC,
        description="Active audit tier"
    )
    
    # Status
    status: str = Field(
        default="active",
        description="Subscription status: active, past_due, cancelled, trial"
    )
    trial_end: Optional[datetime] = Field(
        None,
        description="Trial end date (if applicable)"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        use_enum_values = True


class UsageMetrics(BaseModel):
    """
    Usage metrics for billing and monitoring.
    
    Tracks usage across all pricing axes.
    """
    organization_id: str = Field(..., description="Organization ID")
    period_start: datetime = Field(..., description="Measurement period start")
    period_end: datetime = Field(..., description="Measurement period end")
    
    # Request metrics (per_request axis)
    total_requests: int = Field(default=0, description="Total governed requests")
    requests_by_agent: Dict[str, int] = Field(
        default_factory=dict,
        description="Requests broken down by agent"
    )
    
    # Seat metrics (per_seat axis)
    active_seats: int = Field(default=0, description="Active user seats")
    seat_details: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Details of active seats"
    )
    
    # Policy pack usage (per_policy_pack axis)
    active_policy_packs: List[str] = Field(
        default_factory=list,
        description="Active policy packs"
    )
    policy_pack_executions: Dict[str, int] = Field(
        default_factory=dict,
        description="Executions per policy pack"
    )
    
    # Compliance module usage (per_compliance_module axis)
    active_compliance_modules: List[str] = Field(
        default_factory=list,
        description="Active compliance modules"
    )
    compliance_validations: Dict[str, int] = Field(
        default_factory=dict,
        description="Validations per compliance module"
    )
    
    # Audit metrics (audit_tier axis)
    audit_logs_stored: int = Field(default=0, description="Audit logs stored")
    audit_queries_executed: int = Field(default=0, description="Audit queries run")
    compliance_reports_generated: int = Field(
        default=0,
        description="Compliance reports generated"
    )
    
    # Cost calculation
    calculated_cost: Optional[float] = Field(
        None,
        description="Calculated cost for this period (USD)"
    )
    
    # Metadata
    collected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When metrics were collected"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": "acme-corp",
                "period_start": "2026-01-01T00:00:00Z",
                "period_end": "2026-01-31T23:59:59Z",
                "total_requests": 500000,
                "active_seats": 25,
                "active_policy_packs": ["basic", "security", "cost-control"],
                "active_compliance_modules": ["gdpr", "soc2"],
                "audit_logs_stored": 500000,
                "calculated_cost": 1499.0,
            }
        }


class LicenseKey(BaseModel):
    """
    License key for enterprise deployments.
    """
    key: str = Field(..., description="License key")
    organization_id: str = Field(..., description="Organization ID")
    tier: LicenseType = Field(..., description="Licensed tier")
    
    # Validity
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(
        None,
        description="Expiration date (None = perpetual)"
    )
    
    # Features
    enabled_features: Dict[str, bool] = Field(
        default_factory=dict,
        description="Feature flags"
    )
    limits: Dict[str, int] = Field(
        default_factory=dict,
        description="Usage limits"
    )
    
    # Status
    active: bool = Field(default=True, description="Whether key is active")
    revoked: bool = Field(default=False, description="Whether key is revoked")
    revoked_at: Optional[datetime] = Field(None, description="Revocation timestamp")
    revoked_reason: Optional[str] = Field(None, description="Revocation reason")
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        use_enum_values = True


class BillingEvent(BaseModel):
    """
    Billable event for metering.
    """
    id: str = Field(..., description="Event ID")
    organization_id: str = Field(..., description="Organization ID")
    event_type: str = Field(..., description="Event type (request, seat_add, etc.)")
    pricing_axis: PricingAxis = Field(..., description="Which pricing axis this affects")
    
    # Event details
    resource_id: Optional[str] = Field(None, description="Resource ID (agent, user, etc.)")
    quantity: int = Field(default=1, description="Quantity (for batch events)")
    
    # Pricing
    unit_price: Optional[float] = Field(None, description="Unit price (USD)")
    total_price: Optional[float] = Field(None, description="Total price (USD)")
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    billing_period: str = Field(..., description="Billing period (YYYY-MM)")
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event metadata"
    )
    
    class Config:
        use_enum_values = True
