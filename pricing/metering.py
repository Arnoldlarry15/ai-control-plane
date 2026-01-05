"""
Metering Service

Tracks usage across all pricing axes for billing.
Records billable events and aggregates usage metrics.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from pricing.models import (
    BillingEvent,
    UsageMetrics,
    PricingAxis,
)

logger = logging.getLogger(__name__)


class MeteringService:
    """
    Metering service - tracks usage for billing.
    
    The key to monetization: accurate usage tracking.
    Every governed request, every policy pack, every compliance check.
    """
    
    def __init__(self):
        """Initialize metering service."""
        # In-memory storage for demo
        # Production: Use time-series DB (InfluxDB, TimescaleDB)
        self.events: List[BillingEvent] = []
        self.usage_cache: Dict[str, UsageMetrics] = {}
    
    def record_event(
        self,
        organization_id: str,
        event_type: str,
        pricing_axis: PricingAxis,
        resource_id: Optional[str] = None,
        quantity: int = 1,
        unit_price: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BillingEvent:
        """
        Record a billable event.
        
        Args:
            organization_id: Organization ID
            event_type: Type of event (request, seat_add, policy_pack_enable, etc.)
            pricing_axis: Which pricing axis this affects
            resource_id: Resource ID (agent ID, user ID, etc.)
            quantity: Quantity (for batch events)
            unit_price: Unit price if known
            metadata: Additional event metadata
        
        Returns:
            Created billing event
        """
        import uuid
        
        # Generate event ID
        event_id = f"evt_{uuid.uuid4().hex[:16]}"
        
        # Get billing period (YYYY-MM)
        now = datetime.utcnow()
        billing_period = now.strftime("%Y-%m")
        
        # Calculate total price
        total_price = None
        if unit_price is not None:
            total_price = unit_price * quantity
        
        # Create event
        event = BillingEvent(
            id=event_id,
            organization_id=organization_id,
            event_type=event_type,
            pricing_axis=pricing_axis,
            resource_id=resource_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            timestamp=now,
            billing_period=billing_period,
            metadata=metadata or {},
        )
        
        # Store event
        self.events.append(event)
        
        # Invalidate usage cache for this org
        cache_key = f"{organization_id}:{billing_period}"
        if cache_key in self.usage_cache:
            del self.usage_cache[cache_key]
        
        logger.debug(
            f"Recorded billing event: {event_type} for {organization_id} "
            f"(axis={pricing_axis}, quantity={quantity})"
        )
        
        return event
    
    def record_request(
        self,
        organization_id: str,
        agent_id: str,
        execution_id: str,
        unit_price: Optional[float] = None,
    ) -> BillingEvent:
        """
        Record a governed AI request.
        
        This is the core pricing axis: per request governed.
        """
        return self.record_event(
            organization_id=organization_id,
            event_type="ai_request",
            pricing_axis=PricingAxis.PER_REQUEST,
            resource_id=agent_id,
            quantity=1,
            unit_price=unit_price,
            metadata={
                "agent_id": agent_id,
                "execution_id": execution_id,
            },
        )
    
    def record_policy_pack_usage(
        self,
        organization_id: str,
        policy_pack_id: str,
        execution_id: str,
    ) -> BillingEvent:
        """
        Record policy pack usage.
        
        Tracks which policy packs are actively used.
        """
        return self.record_event(
            organization_id=organization_id,
            event_type="policy_pack_execution",
            pricing_axis=PricingAxis.PER_POLICY_PACK,
            resource_id=policy_pack_id,
            quantity=1,
            metadata={
                "policy_pack_id": policy_pack_id,
                "execution_id": execution_id,
            },
        )
    
    def record_compliance_validation(
        self,
        organization_id: str,
        compliance_module: str,
        execution_id: Optional[str] = None,
    ) -> BillingEvent:
        """
        Record compliance validation.
        
        Tracks compliance module usage.
        """
        return self.record_event(
            organization_id=organization_id,
            event_type="compliance_validation",
            pricing_axis=PricingAxis.PER_COMPLIANCE_MODULE,
            resource_id=compliance_module,
            quantity=1,
            metadata={
                "compliance_module": compliance_module,
                "execution_id": execution_id,
            },
        )
    
    def record_seat_event(
        self,
        organization_id: str,
        user_id: str,
        event_type: str,  # seat_add, seat_remove, seat_active
    ) -> BillingEvent:
        """
        Record seat-related event.
        
        Tracks user seat usage.
        """
        return self.record_event(
            organization_id=organization_id,
            event_type=event_type,
            pricing_axis=PricingAxis.PER_SEAT,
            resource_id=user_id,
            quantity=1,
            metadata={"user_id": user_id},
        )
    
    def record_audit_query(
        self,
        organization_id: str,
        query_type: str,
        result_count: int,
    ) -> BillingEvent:
        """
        Record audit/reporting usage.
        
        Tracks audit tier usage.
        """
        return self.record_event(
            organization_id=organization_id,
            event_type=f"audit_{query_type}",
            pricing_axis=PricingAxis.AUDIT_TIER,
            quantity=1,
            metadata={
                "query_type": query_type,
                "result_count": result_count,
            },
        )
    
    def get_usage_metrics(
        self,
        organization_id: str,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> UsageMetrics:
        """
        Get usage metrics for an organization.
        
        Aggregates usage across all pricing axes.
        
        Args:
            organization_id: Organization ID
            period_start: Start of period (default: start of current month)
            period_end: End of period (default: now)
        
        Returns:
            Usage metrics
        """
        # Default to current month
        now = datetime.utcnow()
        if period_start is None:
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if period_end is None:
            period_end = now
        
        # Check cache
        cache_key = f"{organization_id}:{period_start.strftime('%Y-%m')}"
        if cache_key in self.usage_cache:
            cached = self.usage_cache[cache_key]
            # Return cached if still valid (period_end matches or is earlier)
            if cached.period_end >= period_end:
                return cached
        
        # Filter events for this org and period
        org_events = [
            e for e in self.events
            if e.organization_id == organization_id
            and period_start <= e.timestamp <= period_end
        ]
        
        # Initialize metrics
        metrics = UsageMetrics(
            organization_id=organization_id,
            period_start=period_start,
            period_end=period_end,
        )
        
        # Aggregate by pricing axis
        requests_by_agent: Dict[str, int] = defaultdict(int)
        policy_pack_executions: Dict[str, int] = defaultdict(int)
        compliance_validations: Dict[str, int] = defaultdict(int)
        active_seats_set = set()
        active_policy_packs = set()
        active_compliance_modules = set()
        audit_logs = 0
        audit_queries = 0
        compliance_reports = 0
        
        for event in org_events:
            if event.pricing_axis == PricingAxis.PER_REQUEST:
                metrics.total_requests += event.quantity
                if event.resource_id:
                    requests_by_agent[event.resource_id] += event.quantity
            
            elif event.pricing_axis == PricingAxis.PER_POLICY_PACK:
                pack_id = event.resource_id or event.metadata.get("policy_pack_id")
                if pack_id:
                    active_policy_packs.add(pack_id)
                    policy_pack_executions[pack_id] += event.quantity
            
            elif event.pricing_axis == PricingAxis.PER_COMPLIANCE_MODULE:
                module = event.resource_id or event.metadata.get("compliance_module")
                if module:
                    active_compliance_modules.add(module)
                    compliance_validations[module] += event.quantity
            
            elif event.pricing_axis == PricingAxis.PER_SEAT:
                if event.event_type == "seat_active" and event.resource_id:
                    active_seats_set.add(event.resource_id)
            
            elif event.pricing_axis == PricingAxis.AUDIT_TIER:
                if "log" in event.event_type:
                    audit_logs += event.quantity
                elif "query" in event.event_type:
                    audit_queries += event.quantity
                elif "report" in event.event_type:
                    compliance_reports += event.quantity
        
        # Set aggregated metrics
        metrics.requests_by_agent = dict(requests_by_agent)
        metrics.policy_pack_executions = dict(policy_pack_executions)
        metrics.compliance_validations = dict(compliance_validations)
        metrics.active_seats = len(active_seats_set)
        metrics.active_policy_packs = list(active_policy_packs)
        metrics.active_compliance_modules = list(active_compliance_modules)
        metrics.audit_logs_stored = audit_logs
        metrics.audit_queries_executed = audit_queries
        metrics.compliance_reports_generated = compliance_reports
        
        # Cache it
        self.usage_cache[cache_key] = metrics
        
        return metrics
    
    def get_billing_events(
        self,
        organization_id: str,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        pricing_axis: Optional[PricingAxis] = None,
        event_type: Optional[str] = None,
    ) -> List[BillingEvent]:
        """
        Get billing events for an organization.
        
        Args:
            organization_id: Organization ID
            period_start: Start of period
            period_end: End of period
            pricing_axis: Filter by pricing axis
            event_type: Filter by event type
        
        Returns:
            List of billing events
        """
        # Default to current month
        now = datetime.utcnow()
        if period_start is None:
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if period_end is None:
            period_end = now
        
        # Filter events
        filtered = [
            e for e in self.events
            if e.organization_id == organization_id
            and period_start <= e.timestamp <= period_end
        ]
        
        if pricing_axis:
            filtered = [e for e in filtered if e.pricing_axis == pricing_axis]
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        return filtered
    
    def clear_events(self, before_date: Optional[datetime] = None):
        """
        Clear old events (for cleanup).
        
        Production: Archive to cold storage, don't delete.
        """
        if before_date is None:
            # Default: clear events older than 90 days
            before_date = datetime.utcnow() - timedelta(days=90)
        
        original_count = len(self.events)
        self.events = [e for e in self.events if e.timestamp >= before_date]
        cleared_count = original_count - len(self.events)
        
        logger.info(f"Cleared {cleared_count} billing events older than {before_date}")
        
        return cleared_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get metering statistics.
        
        For monitoring and debugging.
        """
        total_events = len(self.events)
        
        # Events by axis
        by_axis = defaultdict(int)
        for event in self.events:
            axis_value = event.pricing_axis if isinstance(event.pricing_axis, str) else event.pricing_axis.value
            by_axis[axis_value] += 1
        
        # Events by org
        by_org = defaultdict(int)
        for event in self.events:
            by_org[event.organization_id] += 1
        
        # Oldest and newest
        oldest = min((e.timestamp for e in self.events), default=None)
        newest = max((e.timestamp for e in self.events), default=None)
        
        return {
            "total_events": total_events,
            "events_by_pricing_axis": dict(by_axis),
            "events_by_organization": dict(by_org),
            "oldest_event": oldest.isoformat() if oldest else None,
            "newest_event": newest.isoformat() if newest else None,
            "organizations_tracked": len(by_org),
        }
