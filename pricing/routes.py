"""
Pricing and Billing API Routes

Endpoints for pricing information, usage metrics, and billing.
Part of Phase 5: Monetization.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from pricing.service import PricingService
from pricing.metering import MeteringService
from pricing.license import LicenseManager
from pricing.models import LicenseType, PricingAxis, AuditTier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pricing", tags=["pricing"])

# Initialize services
pricing_service = PricingService()
metering_service = MeteringService()
license_manager = LicenseManager()


# Request/Response models

class CalculateCostRequest(BaseModel):
    """Request to calculate estimated monthly cost."""
    tier: LicenseType = Field(..., description="Pricing tier")
    requests_per_month: int = Field(..., description="Expected requests per month")
    seats: int = Field(..., description="Number of user seats")
    additional_policy_packs: int = Field(
        default=0,
        description="Additional policy packs beyond included"
    )
    additional_compliance_modules: int = Field(
        default=0,
        description="Additional compliance modules beyond included"
    )
    audit_tier_upgrade: Optional[AuditTier] = Field(
        None,
        description="Upgrade to higher audit tier"
    )


class GenerateLicenseRequest(BaseModel):
    """Request to generate a license key."""
    organization_id: str = Field(..., description="Organization ID")
    tier: LicenseType = Field(..., description="License tier")
    validity_days: Optional[int] = Field(
        None,
        description="Validity in days (None = perpetual)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class ValidateLicenseRequest(BaseModel):
    """Request to validate a license key."""
    license_key: str = Field(..., description="License key to validate")


class CheckFeatureRequest(BaseModel):
    """Request to check feature access."""
    license_key: str = Field(..., description="License key")
    feature: str = Field(..., description="Feature name")


# Pricing endpoints

@router.get("/tiers")
async def list_pricing_tiers():
    """
    List all pricing tiers.
    
    Returns complete pricing information for all tiers.
    """
    try:
        tiers = pricing_service.list_tiers()
        return {
            "tiers": [tier.model_dump() for tier in tiers],
            "count": len(tiers),
        }
    except Exception as e:
        logger.error(f"Failed to list pricing tiers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tiers/{tier}")
async def get_pricing_tier(tier: LicenseType):
    """
    Get details for a specific pricing tier.
    
    Returns pricing, features, and limits for the tier.
    """
    try:
        pricing = pricing_service.get_tier(tier)
        return {"tier": pricing.model_dump()}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Tier not found: {tier}")
    except Exception as e:
        logger.error(f"Failed to get pricing tier: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-cost")
async def calculate_cost(request: CalculateCostRequest):
    """
    Calculate estimated monthly cost.
    
    Returns cost breakdown across all pricing axes.
    """
    try:
        cost = pricing_service.calculate_monthly_cost(
            tier=request.tier,
            requests=request.requests_per_month,
            seats=request.seats,
            additional_policy_packs=request.additional_policy_packs,
            additional_compliance_modules=request.additional_compliance_modules,
            audit_tier_upgrade=request.audit_tier_upgrade,
        )
        return {"cost": cost}
    except Exception as e:
        logger.error(f"Failed to calculate cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tiers/compare/{current_tier}/{target_tier}")
async def compare_tiers(current_tier: LicenseType, target_tier: LicenseType):
    """
    Compare two pricing tiers.
    
    Shows benefits of upgrading from current to target tier.
    Sales intelligence: Know what to pitch.
    """
    try:
        benefits = pricing_service.get_upgrade_benefits(current_tier, target_tier)
        return {"upgrade_benefits": benefits}
    except Exception as e:
        logger.error(f"Failed to compare tiers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Usage & metering endpoints

@router.get("/usage/{organization_id}")
async def get_usage_metrics(
    organization_id: str,
    period_start: Optional[str] = Query(
        None,
        description="Period start (ISO 8601)"
    ),
    period_end: Optional[str] = Query(
        None,
        description="Period end (ISO 8601)"
    ),
):
    """
    Get usage metrics for an organization.
    
    Returns usage across all pricing axes for billing calculation.
    """
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        if period_start:
            start_dt = datetime.fromisoformat(period_start.replace('Z', '+00:00'))
        if period_end:
            end_dt = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
        
        metrics = metering_service.get_usage_metrics(
            organization_id=organization_id,
            period_start=start_dt,
            period_end=end_dt,
        )
        
        return {"usage": metrics.model_dump()}
    except Exception as e:
        logger.error(f"Failed to get usage metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/{organization_id}/recommend-tier")
async def recommend_tier(organization_id: str):
    """
    Recommend appropriate tier based on usage.
    
    Sales intelligence: Know when to upsell.
    """
    try:
        metrics = metering_service.get_usage_metrics(organization_id)
        recommended = pricing_service.recommend_tier(metrics)
        
        # Get benefits of upgrading
        current_tier = LicenseType.OPEN_SOURCE  # Default assumption
        benefits = {}
        if recommended != current_tier:
            benefits = pricing_service.get_upgrade_benefits(current_tier, recommended)
        
        return {
            "recommended_tier": recommended.value,
            "current_usage": metrics.model_dump(),
            "upgrade_benefits": benefits,
        }
    except Exception as e:
        logger.error(f"Failed to recommend tier: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/{organization_id}/events")
async def get_billing_events(
    organization_id: str,
    period_start: Optional[str] = Query(None, description="Period start (ISO 8601)"),
    period_end: Optional[str] = Query(None, description="Period end (ISO 8601)"),
    pricing_axis: Optional[PricingAxis] = Query(None, description="Filter by pricing axis"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
):
    """
    Get billing events for an organization.
    
    Returns detailed event log for billing audit.
    """
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        if period_start:
            start_dt = datetime.fromisoformat(period_start.replace('Z', '+00:00'))
        if period_end:
            end_dt = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
        
        events = metering_service.get_billing_events(
            organization_id=organization_id,
            period_start=start_dt,
            period_end=end_dt,
            pricing_axis=pricing_axis,
            event_type=event_type,
        )
        
        return {
            "events": [e.model_dump() for e in events],
            "count": len(events),
        }
    except Exception as e:
        logger.error(f"Failed to get billing events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metering/statistics")
async def get_metering_statistics():
    """
    Get metering statistics.
    
    For monitoring and debugging.
    """
    try:
        stats = metering_service.get_statistics()
        return {"statistics": stats}
    except Exception as e:
        logger.error(f"Failed to get metering statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# License management endpoints

@router.post("/licenses/generate")
async def generate_license(request: GenerateLicenseRequest):
    """
    Generate a new license key.
    
    Enterprise feature: License key management.
    """
    try:
        # Get pricing tier details
        pricing_tier = pricing_service.get_tier(request.tier)
        
        # Generate license
        license_key = license_manager.generate_license_key(
            organization_id=request.organization_id,
            tier=request.tier,
            pricing_tier=pricing_tier,
            validity_days=request.validity_days,
            metadata=request.metadata,
        )
        
        return {
            "license": license_key.model_dump(),
            "message": f"Generated {request.tier.value} license for {request.organization_id}",
        }
    except Exception as e:
        logger.error(f"Failed to generate license: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/licenses/validate")
async def validate_license(request: ValidateLicenseRequest):
    """
    Validate a license key.
    
    Returns validation status and license details if valid.
    """
    try:
        valid, reason = license_manager.validate_license(request.license_key)
        
        if valid:
            license_key = license_manager.get_license(request.license_key)
            return {
                "valid": True,
                "license": license_key.model_dump() if license_key else None,
            }
        else:
            return {
                "valid": False,
                "reason": reason,
            }
    except Exception as e:
        logger.error(f"Failed to validate license: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/licenses/check-feature")
async def check_feature_access(request: CheckFeatureRequest):
    """
    Check if license has access to a feature.
    
    Feature gating: The key to monetization.
    """
    try:
        has_access, reason = license_manager.check_feature_access(
            request.license_key,
            request.feature,
        )
        
        return {
            "has_access": has_access,
            "feature": request.feature,
            "reason": reason,
        }
    except Exception as e:
        logger.error(f"Failed to check feature access: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/licenses/organization/{organization_id}")
async def get_organization_license(organization_id: str):
    """
    Get license for an organization.
    
    Returns active license details.
    """
    try:
        license_key = license_manager.get_license_by_org(organization_id)
        
        if not license_key:
            raise HTTPException(
                status_code=404,
                detail=f"No license found for organization: {organization_id}"
            )
        
        return {"license": license_key.model_dump()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get organization license: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/licenses")
async def list_licenses(
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    tier: Optional[LicenseType] = Query(None, description="Filter by tier"),
    active_only: bool = Query(False, description="Only return active licenses"),
):
    """
    List licenses with optional filters.
    
    For license management and reporting.
    """
    try:
        licenses = license_manager.list_licenses(
            organization_id=organization_id,
            tier=tier,
            active_only=active_only,
        )
        
        return {
            "licenses": [l.model_dump() for l in licenses],
            "count": len(licenses),
        }
    except Exception as e:
        logger.error(f"Failed to list licenses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/licenses/{license_key}/revoke")
async def revoke_license(license_key: str, reason: str):
    """
    Revoke a license key.
    
    Enterprise control: Instant license revocation.
    """
    try:
        success = license_manager.revoke_license(license_key, reason)
        
        if not success:
            raise HTTPException(status_code=404, detail="License not found")
        
        return {
            "revoked": True,
            "license_key": license_key[:16] + "...",
            "reason": reason,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke license: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/licenses/statistics")
async def get_license_statistics():
    """
    Get license statistics.
    
    For monitoring and reporting.
    """
    try:
        stats = license_manager.get_statistics()
        return {"statistics": stats}
    except Exception as e:
        logger.error(f"Failed to get license statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Summary endpoint

@router.get("/summary")
async def pricing_summary():
    """
    Get pricing and monetization summary.
    
    High-level overview of the entire monetization system.
    """
    try:
        return {
            "model": "Salesforce Playbook",
            "tagline": "Print money without selling models",
            "pricing_axes": [
                {
                    "axis": "per_request",
                    "description": "Per AI request governed",
                    "unit": "request",
                },
                {
                    "axis": "per_policy_pack",
                    "description": "Per policy pack enabled",
                    "unit": "policy pack",
                },
                {
                    "axis": "per_compliance_module",
                    "description": "Per compliance module (GDPR, HIPAA, etc.)",
                    "unit": "module",
                },
                {
                    "axis": "per_seat",
                    "description": "Per user seat",
                    "unit": "seat",
                },
                {
                    "axis": "per_org",
                    "description": "Per organization (base fee)",
                    "unit": "organization",
                },
                {
                    "axis": "audit_tier",
                    "description": "Audit & reporting tier",
                    "unit": "tier",
                },
            ],
            "tiers": [
                {
                    "name": "Open Source",
                    "tier": "open_source",
                    "price": "Free",
                    "target": "Community, learning, development",
                },
                {
                    "name": "Starter",
                    "tier": "starter",
                    "price": "$299/month + usage",
                    "target": "Small teams getting serious",
                },
                {
                    "name": "Professional",
                    "tier": "professional",
                    "price": "$999/month + usage",
                    "target": "Growing teams, production",
                },
                {
                    "name": "Enterprise",
                    "tier": "enterprise",
                    "price": "$4,999/month + usage",
                    "target": "Unlimited scale, dedicated support",
                },
            ],
            "approach": "Open core, paid enterprise control. Clean. Proven. Scalable.",
        }
    except Exception as e:
        logger.error(f"Failed to get pricing summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
