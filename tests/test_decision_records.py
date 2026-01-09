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
Tests for Phase 3: Human-Centric Observability.

Tests that answer human questions:
- Why was this blocked?
- Who approved this?
- Which policy fired?
"""

import pytest
from datetime import datetime

from observability.decision_records import DecisionRecordStore
from observability.events import DecisionRecord


def test_decision_record_store_creation():
    """Test creating and storing a decision record."""
    store = DecisionRecordStore()
    
    record = DecisionRecord(
        execution_id="exec-123",
        correlation_id="corr-123",
        request_timestamp="2024-01-01T12:00:00Z",
        decision_timestamp="2024-01-01T12:00:01Z",
        requester_id="alice",
        requester_name="Alice Developer",
        requester_role="developer",
        decision="allow",
        reason="Request approved",
        policy_id="pol-default",
        policy_name="Default Policy",
        agent_id="agent-456",
        status="success",
    )
    
    store.store_decision(record)
    
    retrieved = store.get_decision("exec-123")
    assert retrieved is not None
    assert retrieved.execution_id == "exec-123"
    assert retrieved.requester_id == "alice"
    assert retrieved.decision == "allow"


def test_why_blocked_query():
    """Test answering 'Why was this blocked?'"""
    store = DecisionRecordStore()
    
    # Store a blocked request
    record = DecisionRecord(
        execution_id="exec-block-1",
        correlation_id="corr-123",
        request_timestamp="2024-01-01T12:00:00Z",
        decision_timestamp="2024-01-01T12:00:01Z",
        requester_id="bob",
        requester_name="Bob User",
        requester_role="user",
        decision="block",
        reason="Prompt contains PII",
        policy_id="pol-pii",
        policy_name="PII Detection Policy",
        agent_id="agent-456",
        status="blocked",
    )
    
    store.store_decision(record)
    
    # Query why it was blocked
    result = store.why_blocked("exec-block-1")
    
    assert result["found"] is True
    assert result["blocked"] is True
    assert result["reason"] == "Prompt contains PII"
    assert result["policy_id"] == "pol-pii"
    assert result["policy_name"] == "PII Detection Policy"
    assert result["blocked_for"] == "Bob User"
    assert "PII Detection Policy" in result["summary"]
    assert "audit_sentence" in result


def test_why_blocked_not_blocked():
    """Test query when request was not blocked."""
    store = DecisionRecordStore()
    
    # Store an allowed request
    record = DecisionRecord(
        execution_id="exec-allow-1",
        correlation_id="corr-123",
        request_timestamp="2024-01-01T12:00:00Z",
        decision_timestamp="2024-01-01T12:00:01Z",
        requester_id="charlie",
        requester_name="Charlie Developer",
        requester_role="developer",
        decision="allow",
        reason="Request approved",
        policy_id="pol-default",
        policy_name="Default Policy",
        agent_id="agent-456",
        status="success",
    )
    
    store.store_decision(record)
    
    # Query why it was blocked (it wasn't)
    result = store.why_blocked("exec-allow-1")
    
    assert result["found"] is True
    assert result["blocked"] is False
    assert result["decision"] == "allow"


def test_who_approved_query():
    """Test answering 'Who approved this?'"""
    store = DecisionRecordStore()
    
    # Store an approved request
    record = DecisionRecord(
        execution_id="exec-approve-1",
        correlation_id="corr-123",
        request_timestamp="2024-01-01T12:00:00Z",
        decision_timestamp="2024-01-01T12:00:01Z",
        completion_timestamp="2024-01-01T12:05:00Z",
        requester_id="dave",
        requester_name="Dave User",
        requester_role="user",
        approver_id="eve",
        approver_name="Eve Approver",
        approver_role="approver",
        decision="allow",
        reason="High cost operation",
        policy_id="pol-approval",
        policy_name="Approval Required Policy",
        agent_id="agent-456",
        status="success",
    )
    
    store.store_decision(record)
    
    # Query who approved it
    result = store.who_approved("exec-approve-1")
    
    assert result["found"] is True
    assert result["approved"] is True
    assert result["approver_id"] == "eve"
    assert result["approver_name"] == "Eve Approver"
    assert result["approver_role"] == "approver"
    assert result["policy"] == "Approval Required Policy"
    assert "Eve Approver" in result["summary"]
    assert "audit_sentence" in result


def test_who_approved_no_approval():
    """Test query when request did not require approval."""
    store = DecisionRecordStore()
    
    # Store a request without approval
    record = DecisionRecord(
        execution_id="exec-no-approval",
        correlation_id="corr-123",
        request_timestamp="2024-01-01T12:00:00Z",
        decision_timestamp="2024-01-01T12:00:01Z",
        requester_id="frank",
        requester_name="Frank Developer",
        requester_role="developer",
        decision="allow",
        reason="Request approved",
        policy_id="pol-default",
        policy_name="Default Policy",
        agent_id="agent-456",
        status="success",
    )
    
    store.store_decision(record)
    
    # Query who approved it (nobody - it was automatic)
    result = store.who_approved("exec-no-approval")
    
    assert result["found"] is True
    assert result["approved"] is False
    assert result["decision"] == "allow"


def test_which_policy_fired_query():
    """Test answering 'Which policy fired?'"""
    store = DecisionRecordStore()
    
    # Store a request
    record = DecisionRecord(
        execution_id="exec-policy-1",
        correlation_id="corr-123",
        request_timestamp="2024-01-01T12:00:00Z",
        decision_timestamp="2024-01-01T12:00:01Z",
        requester_id="george",
        requester_name="George User",
        requester_role="user",
        decision="block",
        reason="Business hours only",
        policy_id="pol-hours",
        policy_name="Business Hours Policy",
        policies_evaluated=["pol-default", "pol-hours", "pol-cost"],
        agent_id="agent-456",
        status="blocked",
    )
    
    store.store_decision(record)
    
    # Query which policy fired
    result = store.which_policy_fired("exec-policy-1")
    
    assert result["found"] is True
    assert result["policy_id"] == "pol-hours"
    assert result["policy_name"] == "Business Hours Policy"
    assert result["decision"] == "block"
    assert result["reason"] == "Business hours only"
    assert len(result["policies_evaluated"]) == 3
    assert "Business Hours Policy" in result["summary"]


def test_get_timeline():
    """Test getting complete decision timeline."""
    store = DecisionRecordStore()
    
    # Store an approved request with timeline
    record = DecisionRecord(
        execution_id="exec-timeline-1",
        correlation_id="corr-123",
        request_timestamp="2024-01-01T12:00:00Z",
        decision_timestamp="2024-01-01T12:00:01Z",
        completion_timestamp="2024-01-01T12:05:00Z",
        requester_id="helen",
        requester_name="Helen User",
        requester_role="user",
        approver_id="ivan",
        approver_name="Ivan Approver",
        approver_role="approver",
        decision="allow",
        reason="High risk operation",
        policy_id="pol-risk",
        policy_name="High Risk Policy",
        agent_id="agent-456",
        status="success",
    )
    
    store.store_decision(record)
    
    # Get timeline
    result = store.get_timeline("exec-timeline-1")
    
    assert result["found"] is True
    assert result["execution_id"] == "exec-timeline-1"
    assert len(result["timeline"]) == 3  # Request, Decision, Approval
    
    # Check timeline events
    assert result["timeline"][0]["event"] == "Request initiated"
    assert result["timeline"][0]["actor"] == "Helen User"
    assert result["timeline"][1]["event"] == "Policy decision: allow"
    assert result["timeline"][1]["policy"] == "High Risk Policy"
    assert result["timeline"][2]["event"] == "Approved"
    assert result["timeline"][2]["actor"] == "Ivan Approver"


def test_query_decisions():
    """Test querying decisions with filters."""
    store = DecisionRecordStore()
    
    # Store multiple decisions
    for i in range(5):
        record = DecisionRecord(
            execution_id=f"exec-{i}",
            correlation_id=f"corr-{i}",
            request_timestamp=f"2024-01-01T12:00:{i:02d}Z",
            decision_timestamp=f"2024-01-01T12:00:{i:02d}Z",
            requester_id="alice" if i % 2 == 0 else "bob",
            requester_name="Alice" if i % 2 == 0 else "Bob",
            requester_role="developer",
            decision="allow" if i % 2 == 0 else "block",
            reason="Test reason",
            policy_id=f"pol-{i}",
            policy_name=f"Policy {i}",
            agent_id="agent-456",
            status="success" if i % 2 == 0 else "blocked",
        )
        store.store_decision(record)
    
    # Query for blocked decisions
    blocked = store.query_decisions(decision="block")
    assert len(blocked) == 2
    assert all(r.decision == "block" for r in blocked)
    
    # Query for alice's requests
    alice_requests = store.query_decisions(requester_id="alice")
    assert len(alice_requests) == 3
    assert all(r.requester_id == "alice" for r in alice_requests)


def test_get_statistics():
    """Test getting decision statistics."""
    store = DecisionRecordStore()
    
    # Helper function to create test decision
    def create_test_decision(index):
        # Approvers for indices 0, 1, 4, 5, 8, 9 (alternating between approver-0 and approver-1)
        has_approver = index % 4 in [0, 1]
        
        return DecisionRecord(
            execution_id=f"exec-{index}",
            correlation_id=f"corr-{index}",
            request_timestamp=f"2024-01-01T12:00:{index:02d}Z",
            decision_timestamp=f"2024-01-01T12:00:{index:02d}Z",
            requester_id=f"user-{index % 3}",  # 3 unique requesters (0, 1, 2)
            requester_name=f"User {index % 3}",
            requester_role="developer",
            approver_id=f"approver-{index % 2}" if has_approver else None,  # 2 unique approvers (0, 1)
            approver_name=f"Approver {index % 2}" if has_approver else None,
            approver_role="approver" if has_approver else None,
            decision="allow" if index % 3 == 0 else "block",
            reason="Test reason",
            policy_id=f"pol-{index % 5}",  # 5 unique policies
            policy_name=f"Policy {index % 5}",
            agent_id="agent-456",
            status="success" if index % 3 == 0 else "blocked",
        )
    
    # Store 10 test decisions
    for i in range(10):
        store.store_decision(create_test_decision(i))
    
    stats = store.get_statistics()
    
    assert stats["total_decisions"] == 10
    assert stats["unique_requesters"] == 3
    assert stats["unique_approvers"] == 2
    assert "by_decision" in stats
    assert "by_policy" in stats


def test_decision_record_audit_sentence():
    """Test generating audit sentence from decision record."""
    record = DecisionRecord(
        execution_id="exec-audit-1",
        correlation_id="corr-123",
        request_timestamp="2024-01-01T12:00:00Z",
        decision_timestamp="2024-01-01T12:00:01Z",
        completion_timestamp="2024-01-01T12:05:00Z",
        requester_id="judy",
        requester_name="Judy User",
        requester_role="user",
        approver_id="karl",
        approver_name="Karl Approver",
        approver_role="approver",
        decision="allow",
        reason="Approved after review",
        policy_id="pol-approval",
        policy_name="Approval Required Policy",
        agent_id="agent-456",
        status="success",
    )
    
    sentence = record.to_audit_sentence()
    
    # This is the gold standard sentence
    assert "Karl Approver" in sentence
    assert "approved" in sentence
    assert "Approval Required Policy" in sentence
    assert "2024-01-01T12:05:00Z" in sentence
