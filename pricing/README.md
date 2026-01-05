# Pricing & Monetization Module

**Phase 5: Print Money Without Selling Models**

This module implements the complete monetization strategy for AI Control Plane following the Salesforce playbook.

## Overview

The pricing module provides:
- **Multiple Pricing Axes** - Charge for value across different dimensions
- **Open Core Model** - Free community edition with paid enterprise features
- **Usage Metering** - Automatic tracking of billable events
- **License Management** - Enterprise license keys and feature gating
- **Cost Calculation** - Real-time billing estimates

## Architecture

```
pricing/
├── __init__.py          # Module exports
├── models.py            # Data models for all pricing concepts
├── service.py           # Pricing tiers and cost calculation
├── metering.py          # Usage tracking and aggregation
├── license.py           # License key management
└── routes.py            # REST API endpoints
```

## Pricing Axes

### 1. Per AI Request Governed
Every AI execution that flows through the control plane is metered.

```python
from pricing.metering import MeteringService

metering = MeteringService()
metering.record_request(
    organization_id="acme-corp",
    agent_id="customer-bot",
    execution_id="exec-123"
)
```

**Pricing:**
- Open Source: Free up to 10K/month
- Starter: $0.001/request
- Professional: $0.0005/request
- Enterprise: $0.0002/request

### 2. Per Policy Pack
Pre-built governance bundles sold as add-ons.

```python
metering.record_policy_pack_usage(
    organization_id="acme-corp",
    policy_pack_id="security-pack",
    execution_id="exec-123"
)
```

**Pricing:** $49-$99/month per additional pack

### 3. Per Compliance Module
Regulatory compliance as a service (GDPR, HIPAA, SOC 2, PCI-DSS).

```python
metering.record_compliance_validation(
    organization_id="acme-corp",
    compliance_module="hipaa"
)
```

**Pricing:** $99-$199/month per additional module

### 4. Per Seat
Team-based pricing for user access.

```python
metering.record_seat_event(
    organization_id="acme-corp",
    user_id="alice@acme.com",
    event_type="seat_active"
)
```

**Pricing:** $29-$99/month per seat (varies by tier)

### 5. Audit & Reporting Tiers
Different retention periods and reporting capabilities.

| Tier | Retention | Price |
|------|-----------|-------|
| Basic | 7 days | Free |
| Standard | 30 days | +$99/mo |
| Premium | 90 days | +$299/mo |
| Enterprise | 1 year+ | +$999/mo |

## Pricing Tiers

### Open Source (Free)
- 10K requests/month
- 5 agents, 3 seats
- Basic features only
- Community support

### Starter ($299/month)
- 100K requests/month
- 20 agents, 10 seats
- 2 policy packs, 1 compliance module
- Email support, 99% SLA

### Professional ($999/month)
- 1M requests/month
- 100 agents, 50 seats
- 4 policy packs, 3 compliance modules
- SSO, custom plugins, priority support, 99.5% SLA

### Enterprise (Starting at $4,999/month)
- Unlimited everything
- All features included
- Dedicated support, 99.9% SLA

## Usage

### Get Pricing Information

```python
from pricing.service import PricingService

service = PricingService()

# List all tiers
tiers = service.list_tiers()

# Get specific tier
professional = service.get_tier(LicenseType.PROFESSIONAL)
print(f"Base price: ${professional.base_price_monthly}/month")
```

### Calculate Monthly Cost

```python
cost = service.calculate_monthly_cost(
    tier=LicenseType.PROFESSIONAL,
    requests=500000,
    seats=20,
    additional_policy_packs=2,
    additional_compliance_modules=1
)

print(f"Total: ${cost['total']}/month")
print(f"Breakdown:")
print(f"  Base: ${cost['base_cost']}")
print(f"  Requests: ${cost['request_cost']}")
print(f"  Seats: ${cost['seat_cost']}")
print(f"  Policy Packs: ${cost['policy_pack_cost']}")
print(f"  Compliance: ${cost['compliance_module_cost']}")
```

### Track Usage

```python
from pricing.metering import MeteringService

metering = MeteringService()

# Get usage metrics for current month
metrics = metering.get_usage_metrics(
    organization_id="acme-corp"
)

print(f"Requests: {metrics.total_requests}")
print(f"Active seats: {metrics.active_seats}")
print(f"Policy packs: {len(metrics.active_policy_packs)}")
print(f"Compliance modules: {len(metrics.active_compliance_modules)}")
```

### Recommend Tier Based on Usage

```python
# Automatically recommend best tier for usage
recommended = service.recommend_tier(metrics)
print(f"Recommended tier: {recommended}")

# Get upgrade benefits
benefits = service.get_upgrade_benefits(
    current_tier=LicenseType.STARTER,
    target_tier=recommended
)
print(f"New features: {benefits['new_features']}")
```

### License Management

```python
from pricing.license import LicenseManager

manager = LicenseManager()

# Generate license
license_key = manager.generate_license_key(
    organization_id="acme-corp",
    tier=LicenseType.ENTERPRISE,
    pricing_tier=service.get_tier(LicenseType.ENTERPRISE)
)

print(f"License key: {license_key.key}")

# Validate license
valid, reason = manager.validate_license(license_key.key)
if valid:
    print("License is valid!")
else:
    print(f"License invalid: {reason}")

# Check feature access
has_access, reason = manager.check_feature_access(
    license_key.key,
    "sso"
)
if has_access:
    print("SSO feature enabled")
else:
    print(f"SSO not available: {reason}")
```

## API Endpoints

All pricing endpoints are available at `/api/pricing/*`:

### Pricing Information
- `GET /api/pricing/tiers` - List all pricing tiers
- `GET /api/pricing/tiers/{tier}` - Get specific tier details
- `POST /api/pricing/calculate-cost` - Calculate estimated cost
- `GET /api/pricing/tiers/compare/{current}/{target}` - Compare tiers
- `GET /api/pricing/summary` - Get pricing overview

### Usage & Metering
- `GET /api/pricing/usage/{org_id}` - Get usage metrics
- `GET /api/pricing/usage/{org_id}/events` - Get billing events
- `GET /api/pricing/usage/{org_id}/recommend-tier` - Get tier recommendation
- `GET /api/pricing/metering/statistics` - Get metering stats

### License Management
- `POST /api/pricing/licenses/generate` - Generate license key
- `POST /api/pricing/licenses/validate` - Validate license
- `POST /api/pricing/licenses/check-feature` - Check feature access
- `GET /api/pricing/licenses/organization/{org_id}` - Get org license
- `GET /api/pricing/licenses` - List licenses
- `POST /api/pricing/licenses/{key}/revoke` - Revoke license
- `GET /api/pricing/licenses/statistics` - Get license stats

## Examples

### Run the Demo

```bash
python examples/monetization_demo.py
```

This demonstrates:
- All pricing tiers
- Cost calculations
- Usage metering
- Tier recommendations
- License management
- Statistics

### Integration with Gateway

The pricing module is automatically integrated with the gateway executor. Every AI request is automatically metered:

```python
# In gateway/executor.py
result = await executor.execute(
    agent_id="customer-bot",
    prompt="Hello",
    context={},
    user="alice@company.com"
)
# Request is automatically recorded for billing
```

## Testing

```bash
# Run pricing tests
pytest tests/test_pricing.py -v

# All 29 tests pass ✅
```

## Documentation

See [PHASE_5_MONETIZATION.md](../PHASE_5_MONETIZATION.md) for complete documentation including:
- Detailed pricing strategy
- Sales playbook
- Competitive positioning
- Implementation details
- Success metrics

## The Salesforce Playbook

This implementation follows the proven Salesforce strategy:

1. **Land and Expand** - Start free, grow into paid
2. **Multiple Revenue Streams** - Charge across multiple axes
3. **Value-Based Pricing** - Charge for outcomes, not costs
4. **Ecosystem Lock-In** - High switching costs through system of record

**Result:** Print money without selling models. Clean. Proven. Scalable.
