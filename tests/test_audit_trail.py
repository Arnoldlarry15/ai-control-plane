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
Tests for Audit Trail and Chain of Custody

Tests the cryptographic integrity and immutability of audit logs.
"""

import pytest
from observability.audit_trail import AuditTrail, AuditEntry


def test_audit_trail_creation():
    """Test creating an audit trail."""
    trail = AuditTrail()
    assert trail._last_hash is None
    assert len(trail._entries) == 0


def test_audit_trail_append():
    """Test appending entries."""
    trail = AuditTrail()
    
    entry = trail.append(
        event_type="test_event",
        action="test_action",
        status="success",
        details={"key": "value"},
        execution_id="test-123",
        agent_id="agent-456",
        user="test@example.com",
    )
    
    assert entry.event_type == "test_event"
    assert entry.execution_id == "test-123"
    assert entry.entry_hash is not None
    assert entry.previous_hash is None  # First entry
    
    # Verify hash is valid
    assert entry.verify_hash() is True


def test_audit_trail_chaining():
    """Test hash chaining between entries."""
    trail = AuditTrail()
    
    # Add first entry
    entry1 = trail.append(
        event_type="event1",
        action="action1",
        status="success",
        details={},
    )
    
    # Add second entry
    entry2 = trail.append(
        event_type="event2",
        action="action2",
        status="success",
        details={},
    )
    
    # Second entry should reference first entry's hash
    assert entry2.previous_hash == entry1.entry_hash
    
    # Add third entry
    entry3 = trail.append(
        event_type="event3",
        action="action3",
        status="success",
        details={},
    )
    
    # Third entry should reference second entry's hash
    assert entry3.previous_hash == entry2.entry_hash


def test_audit_trail_integrity_verification():
    """Test verifying audit trail integrity."""
    trail = AuditTrail()
    
    # Empty trail is valid
    result = trail.verify_integrity()
    assert result["valid"] is True
    assert result["total_entries"] == 0
    
    # Add entries
    trail.append(event_type="e1", action="a1", status="s1", details={})
    trail.append(event_type="e2", action="a2", status="s2", details={})
    trail.append(event_type="e3", action="a3", status="s3", details={})
    
    # Verify integrity
    result = trail.verify_integrity()
    assert result["valid"] is True
    assert result["total_entries"] == 3
    assert len(result["invalid_entries"]) == 0
    assert len(result["broken_chains"]) == 0


def test_audit_entry_hash_verification():
    """Test individual entry hash verification."""
    trail = AuditTrail()
    
    entry = trail.append(
        event_type="test",
        action="test",
        status="success",
        details={"data": "test"},
    )
    
    # Original entry should verify
    assert entry.verify_hash() is True
    
    # Tampering with entry should fail verification
    entry.details["data"] = "tampered"
    assert entry.verify_hash() is False


def test_audit_trail_query():
    """Test querying audit entries."""
    trail = AuditTrail()
    
    # Add entries with different attributes
    trail.append(
        event_type="execution",
        action="start",
        status="success",
        details={},
        execution_id="exec-1",
        agent_id="agent-1",
        user="alice",
    )
    
    trail.append(
        event_type="execution",
        action="complete",
        status="success",
        details={},
        execution_id="exec-1",
        agent_id="agent-1",
        user="alice",
    )
    
    trail.append(
        event_type="execution",
        action="start",
        status="success",
        details={},
        execution_id="exec-2",
        agent_id="agent-2",
        user="bob",
    )
    
    # Query by execution_id
    results = trail.query(execution_id="exec-1")
    assert len(results) == 2
    
    # Query by user
    results = trail.query(user="alice")
    assert len(results) == 2
    
    # Query by agent_id
    results = trail.query(agent_id="agent-2")
    assert len(results) == 1
    
    # Query by event_type
    results = trail.query(event_type="execution")
    assert len(results) == 3


def test_audit_trail_timeline():
    """Test getting timeline for specific execution."""
    trail = AuditTrail()
    
    # Add entries for multiple executions
    trail.append(
        event_type="start",
        action="execute",
        status="initiated",
        details={},
        execution_id="exec-1",
    )
    
    trail.append(
        event_type="policy",
        action="evaluate",
        status="completed",
        details={},
        execution_id="exec-1",
    )
    
    trail.append(
        event_type="start",
        action="execute",
        status="initiated",
        details={},
        execution_id="exec-2",
    )
    
    trail.append(
        event_type="complete",
        action="execute",
        status="success",
        details={},
        execution_id="exec-1",
    )
    
    # Get timeline for exec-1
    timeline = trail.get_timeline("exec-1")
    assert len(timeline) == 3
    assert all(e.execution_id == "exec-1" for e in timeline)


def test_audit_trail_chain_of_custody():
    """Test chain of custody report."""
    trail = AuditTrail()
    
    # Add entries for an execution
    trail.append(
        event_type="execution_started",
        action="start",
        status="initiated",
        details={},
        execution_id="exec-1",
    )
    
    trail.append(
        event_type="policy_evaluated",
        action="evaluate",
        status="completed",
        details={},
        execution_id="exec-1",
    )
    
    trail.append(
        event_type="execution_completed",
        action="complete",
        status="success",
        details={},
        execution_id="exec-1",
    )
    
    # Get chain of custody
    chain = trail.get_chain_of_custody("exec-1")
    
    assert chain["execution_id"] == "exec-1"
    assert chain["status"] == "verified"
    assert chain["total_events"] == 3
    assert len(chain["timeline"]) == 3
    assert chain["integrity_check"]["all_hashes_valid"] is True


def test_audit_trail_export_json():
    """Test exporting audit trail as JSON."""
    trail = AuditTrail()
    
    trail.append(
        event_type="test",
        action="test",
        status="success",
        details={"key": "value"},
    )
    
    export = trail.export_for_compliance(format="json")
    
    assert isinstance(export, str)
    assert '"event_type": "test"' in export


def test_audit_trail_export_csv():
    """Test exporting audit trail as CSV."""
    trail = AuditTrail()
    
    trail.append(
        event_type="test",
        action="test",
        status="success",
        details={"key": "value"},
    )
    
    export = trail.export_for_compliance(format="csv")
    
    assert isinstance(export, str)
    assert "event_type" in export  # CSV header
    assert "test" in export  # CSV data


def test_audit_trail_statistics():
    """Test getting audit trail statistics."""
    trail = AuditTrail()
    
    # Add various entries
    trail.append(event_type="execution", action="start", status="success", details={}, user="alice", agent_id="agent-1")
    trail.append(event_type="policy", action="evaluate", status="success", details={}, user="alice", agent_id="agent-1")
    trail.append(event_type="execution", action="complete", status="success", details={}, user="bob", agent_id="agent-2")
    
    stats = trail.get_statistics()
    
    assert stats["total_entries"] == 3
    assert stats["unique_users"] == 2
    assert stats["unique_agents"] == 2
    assert "by_event_type" in stats
    assert "by_status" in stats


def test_audit_trail_not_found():
    """Test chain of custody for non-existent execution."""
    trail = AuditTrail()
    
    chain = trail.get_chain_of_custody("nonexistent")
    
    assert chain["status"] == "not_found"
    assert chain["execution_id"] == "nonexistent"
