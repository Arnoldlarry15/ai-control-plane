"""
Tests for immutable audit trail with cryptographic verification.

Tests the tamper-proof, legally-defensible audit trail.
"""

import pytest
import time
from datetime import datetime, timedelta
from observability.immutable_audit import (
    ImmutableAuditLog,
    AuditTrailManager,
    AuditEventType,
)


class TestImmutableAuditLog:
    """Test immutable audit log."""
    
    def test_create_entry(self):
        """Test creating an audit entry."""
        log = ImmutableAuditLog(secret_key="test-key")
        
        entry = log.log_event(
            event_type="test.event",
            data={"key": "value"},
            request_id="req_123",
            agent_id="agent_1",
            user_id="user_1",
        )
        
        assert entry["event_type"] == "test.event"
        assert entry["request_id"] == "req_123"
        assert entry["data"]["key"] == "value"
        assert "hash" in entry
        assert "signature" in entry
        assert entry["sequence"] == 1
    
    def test_hash_chaining(self):
        """Test that entries are hash-chained."""
        log = ImmutableAuditLog()
        
        entry1 = log.log_event("event1", {"data": "first"})
        entry2 = log.log_event("event2", {"data": "second"})
        entry3 = log.log_event("event3", {"data": "third"})
        
        # First entry has no previous hash
        assert entry1["previous_hash"] is None
        
        # Second entry links to first
        assert entry2["previous_hash"] == entry1["hash"]
        
        # Third entry links to second
        assert entry3["previous_hash"] == entry2["hash"]
    
    def test_sequence_numbers(self):
        """Test sequential numbering."""
        log = ImmutableAuditLog()
        
        for i in range(1, 6):
            entry = log.log_event(f"event{i}", {})
            assert entry["sequence"] == i
    
    def test_verify_single_entry(self):
        """Test verifying a single entry."""
        log = ImmutableAuditLog(secret_key="test-key")
        
        entry = log.log_event("test", {"data": "value"})
        
        # Entry should be valid
        assert log.verify_entry(entry) is True
    
    def test_detect_tampered_hash(self):
        """Test detection of tampered entry hash."""
        log = ImmutableAuditLog(secret_key="test-key")
        
        entry = log.log_event("test", {"data": "value"})
        
        # Tamper with the hash
        entry["hash"] = "tampered_hash"
        
        # Should detect tampering
        assert log.verify_entry(entry) is False
    
    def test_detect_tampered_data(self):
        """Test detection of tampered data."""
        log = ImmutableAuditLog(secret_key="test-key")
        
        entry = log.log_event("test", {"data": "original"})
        
        # Tamper with data (but keep hash)
        entry["data"]["data"] = "tampered"
        
        # Should detect tampering when verifying
        assert log.verify_entry(entry) is False
    
    def test_chain_integrity_verification(self):
        """Test complete chain integrity verification."""
        log = ImmutableAuditLog()
        
        # Add multiple entries
        log.log_event("event1", {"data": "1"})
        log.log_event("event2", {"data": "2"})
        log.log_event("event3", {"data": "3"})
        
        # Verify integrity
        result = log.verify_integrity()
        
        assert result["valid"] is True
        assert result["total_entries"] == 3
        assert len(result["issues"]) == 0
    
    def test_detect_broken_chain(self):
        """Test detection of broken hash chain."""
        log = ImmutableAuditLog()
        
        log.log_event("event1", {})
        log.log_event("event2", {})
        log.log_event("event3", {})
        
        # Break the chain
        log.entries[1]["previous_hash"] = "wrong_hash"
        
        result = log.verify_integrity()
        
        assert result["valid"] is False
        assert len(result["issues"]) > 0
        assert any(issue["issue"] == "chain_broken" for issue in result["issues"])
    
    def test_detect_sequence_mismatch(self):
        """Test detection of sequence number tampering."""
        log = ImmutableAuditLog()
        
        log.log_event("event1", {})
        log.log_event("event2", {})
        
        # Tamper with sequence
        log.entries[1]["sequence"] = 999
        
        result = log.verify_integrity()
        
        assert result["valid"] is False
        assert any(issue["issue"] == "sequence_mismatch" for issue in result["issues"])
    
    def test_get_chain_of_custody(self):
        """Test getting chain of custody for a request."""
        log = ImmutableAuditLog()
        
        # Log events for different requests
        log.log_event("event1", {}, request_id="req_1")
        log.log_event("event2", {}, request_id="req_2")
        log.log_event("event3", {}, request_id="req_1")
        log.log_event("event4", {}, request_id="req_2")
        log.log_event("event5", {}, request_id="req_1")
        
        # Get chain for req_1
        chain = log.get_chain_of_custody("req_1")
        
        assert len(chain) == 3
        assert all(e["request_id"] == "req_1" for e in chain)
        assert [e["event_type"] for e in chain] == ["event1", "event3", "event5"]
    
    def test_export_for_compliance(self):
        """Test exporting audit log for compliance."""
        log = ImmutableAuditLog()
        
        # Add entries
        log.log_event("event1", {})
        time.sleep(0.01)
        log.log_event("event2", {})
        time.sleep(0.01)
        log.log_event("event3", {})
        
        # Export all
        export = log.export_for_compliance()
        
        assert "export_metadata" in export
        assert "integrity_report" in export
        assert "entries" in export
        assert export["export_metadata"]["total_entries"] == 3
        assert export["integrity_report"]["valid"] is True
    
    def test_export_with_time_filter(self):
        """Test exporting with time filters."""
        log = ImmutableAuditLog()
        
        now = datetime.utcnow()
        
        # Add entries
        log.log_event("event1", {})
        time.sleep(0.1)
        log.log_event("event2", {})
        time.sleep(0.1)
        log.log_event("event3", {})
        
        # Export with filter
        export = log.export_for_compliance(
            start_time=now + timedelta(seconds=0.05)
        )
        
        # Should filter out first entry
        assert export["export_metadata"]["total_entries"] <= 2
    
    def test_export_with_event_type_filter(self):
        """Test exporting with event type filters."""
        log = ImmutableAuditLog()
        
        log.log_event("type_a", {})
        log.log_event("type_b", {})
        log.log_event("type_a", {})
        
        export = log.export_for_compliance(event_types=["type_a"])
        
        assert export["export_metadata"]["total_entries"] == 2
    
    def test_statistics(self):
        """Test audit log statistics."""
        log = ImmutableAuditLog()
        
        log.log_event("type_a", {})
        log.log_event("type_b", {})
        log.log_event("type_a", {})
        log.log_event("type_c", {})
        
        stats = log.get_statistics()
        
        assert stats["total_entries"] == 4
        assert stats["event_types"]["type_a"] == 2
        assert stats["event_types"]["type_b"] == 1
        assert stats["event_types"]["type_c"] == 1
        assert "first_entry" in stats
        assert "last_entry" in stats


class TestAuditTrailManager:
    """Test audit trail manager."""
    
    def test_log_request_submitted(self):
        """Test logging request submission."""
        manager = AuditTrailManager(secret_key="test")
        
        entry = manager.log_request_submitted(
            request_id="req_123",
            agent_id="agent_1",
            user_id="user_1",
            prompt="Test prompt",
            model="gpt-4",
            context={"key": "value"},
        )
        
        assert entry["event_type"] == AuditEventType.REQUEST_SUBMITTED
        assert entry["request_id"] == "req_123"
        assert entry["data"]["prompt"] == "Test prompt"
        assert entry["data"]["model"] == "gpt-4"
    
    def test_log_policy_evaluated(self):
        """Test logging policy evaluation."""
        manager = AuditTrailManager()
        
        entry = manager.log_policy_evaluated(
            request_id="req_123",
            agent_id="agent_1",
            policy_id="policy_1",
            decision="block",
            reason="High risk",
        )
        
        assert entry["event_type"] == AuditEventType.POLICY_EVALUATED
        assert entry["data"]["policy_id"] == "policy_1"
        assert entry["data"]["decision"] == "block"
    
    def test_log_risk_assessed(self):
        """Test logging risk assessment."""
        manager = AuditTrailManager()
        
        entry = manager.log_risk_assessed(
            request_id="req_123",
            agent_id="agent_1",
            risk_score=75.5,
            risk_level="high",
            factors=["pii", "cost"],
        )
        
        assert entry["event_type"] == AuditEventType.RISK_ASSESSED
        assert entry["data"]["risk_score"] == 75.5
        assert entry["data"]["risk_level"] == "high"
    
    def test_log_request_completed(self):
        """Test logging request completion."""
        manager = AuditTrailManager()
        
        entry = manager.log_request_completed(
            request_id="req_123",
            agent_id="agent_1",
            status="success",
            latency_ms=1500,
            tokens_used=150,
            cost=0.005,
        )
        
        assert entry["event_type"] == AuditEventType.REQUEST_COMPLETED
        assert entry["data"]["status"] == "success"
        assert entry["data"]["latency_ms"] == 1500
    
    def test_get_request_timeline(self):
        """Test getting complete request timeline."""
        manager = AuditTrailManager()
        
        # Simulate request lifecycle
        manager.log_request_submitted(
            request_id="req_123",
            agent_id="agent_1",
            user_id="user_1",
            prompt="Test",
            model="gpt-4",
            context={},
        )
        
        manager.log_policy_evaluated(
            request_id="req_123",
            agent_id="agent_1",
            policy_id="policy_1",
            decision="allow",
            reason="Passed",
        )
        
        manager.log_risk_assessed(
            request_id="req_123",
            agent_id="agent_1",
            risk_score=25.0,
            risk_level="low",
            factors=[],
        )
        
        manager.log_request_completed(
            request_id="req_123",
            agent_id="agent_1",
            status="success",
            latency_ms=1000,
            tokens_used=100,
            cost=0.002,
        )
        
        # Get timeline
        timeline = manager.get_request_timeline("req_123")
        
        assert len(timeline) == 4
        assert timeline[0]["event_type"] == AuditEventType.REQUEST_SUBMITTED
        assert timeline[1]["event_type"] == AuditEventType.POLICY_EVALUATED
        assert timeline[2]["event_type"] == AuditEventType.RISK_ASSESSED
        assert timeline[3]["event_type"] == AuditEventType.REQUEST_COMPLETED


class TestTamperResistance:
    """Test tamper resistance."""
    
    def test_cannot_modify_past_entries(self):
        """Test that past entries cannot be modified undetected."""
        log = ImmutableAuditLog()
        
        # Add entries
        log.log_event("event1", {"value": "original1"})
        log.log_event("event2", {"value": "original2"})
        log.log_event("event3", {"value": "original3"})
        
        # Integrity should be valid
        assert log.verify_integrity()["valid"] is True
        
        # Try to modify middle entry
        log.entries[1]["data"]["value"] = "tampered"
        
        # Should detect tampering
        result = log.verify_integrity()
        assert result["valid"] is False
    
    def test_cannot_insert_entries(self):
        """Test that inserting entries breaks the chain."""
        log = ImmutableAuditLog()
        
        log.log_event("event1", {})
        log.log_event("event2", {})
        log.log_event("event3", {})
        
        # Try to insert an entry in the middle
        fake_entry = {
            "sequence": 2,
            "event_type": "fake",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {},
            "previous_hash": log.entries[0]["hash"],
            "hash": "fake_hash",
            "signature": "fake_sig",
        }
        
        log.entries.insert(1, fake_entry)
        
        # Should detect the break in chain
        result = log.verify_integrity()
        assert result["valid"] is False
    
    def test_cannot_delete_entries(self):
        """Test that deleting entries breaks the chain."""
        log = ImmutableAuditLog()
        
        log.log_event("event1", {})
        log.log_event("event2", {})
        log.log_event("event3", {})
        
        # Try to delete middle entry
        deleted_hash = log.entries[1]["hash"]
        log.entries.pop(1)
        
        # Chain should be broken (entry 3's previous_hash points to deleted entry)
        result = log.verify_integrity()
        assert result["valid"] is False


class TestRealWorldScenarios:
    """Test real-world audit scenarios."""
    
    def test_complete_request_audit(self):
        """Test complete audit of a request lifecycle."""
        manager = AuditTrailManager(secret_key="production-key")
        
        request_id = "req_customer_query_001"
        
        # 1. Request submitted
        manager.log_request_submitted(
            request_id=request_id,
            agent_id="customer-support-bot",
            user_id="support_agent_1",
            prompt="What is the customer's order status?",
            model="gpt-4",
            context={"customer_id": "cust_123"},
        )
        
        # 2. Policies evaluated
        manager.log_policy_evaluated(
            request_id=request_id,
            agent_id="customer-support-bot",
            policy_id="no-pii",
            decision="allow",
            reason="No PII detected",
        )
        
        manager.log_policy_evaluated(
            request_id=request_id,
            agent_id="customer-support-bot",
            policy_id="cost-control",
            decision="allow",
            reason="Within budget",
        )
        
        # 3. Risk assessed
        manager.log_risk_assessed(
            request_id=request_id,
            agent_id="customer-support-bot",
            risk_score=18.5,
            risk_level="low",
            factors=["standard_query", "low_cost"],
        )
        
        # 4. Request completed
        manager.log_request_completed(
            request_id=request_id,
            agent_id="customer-support-bot",
            status="success",
            latency_ms=1250,
            tokens_used=125,
            cost=0.003,
        )
        
        # Verify complete timeline
        timeline = manager.get_request_timeline(request_id)
        assert len(timeline) == 5  # 1 submit + 2 policy + 1 risk + 1 complete
        
        # Verify integrity
        integrity = manager.verify_integrity()
        assert integrity["valid"] is True
        
        # Export for compliance
        export = manager.export_for_compliance()
        assert export["integrity_report"]["valid"] is True
