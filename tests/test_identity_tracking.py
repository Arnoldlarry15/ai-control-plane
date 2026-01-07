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
Tests for Phase 2: Identity and Authority tracking.

Tests that every request carries identity metadata and creates proper audit trails.
"""

import pytest
from datetime import datetime

from auth.identity import IdentityMetadata, ActionRecord
from auth.models import User, Role


def test_identity_metadata_creation():
    """Test creating identity metadata from a user."""
    user = User(
        id="alice",
        email="alice@company.test",
        full_name="Alice Developer",
        role=Role.DEVELOPER,
    )
    
    identity = IdentityMetadata.from_user(
        user=user,
        request_id="req-123",
        source_ip="192.168.1.1",
        user_agent="Mozilla/5.0",
    )
    
    assert identity.user_id == "alice"
    assert identity.user_email == "alice@company.test"
    assert identity.user_role == "developer"
    assert identity.user_name == "Alice Developer"
    assert identity.request_id == "req-123"
    assert identity.source_ip == "192.168.1.1"
    assert identity.user_agent == "Mozilla/5.0"
    assert identity.timestamp is not None


def test_action_record_creation():
    """Test creating a complete action record."""
    user = User(
        id="bob",
        email="bob@company.test",
        full_name="Bob Approver",
        role=Role.APPROVER,
    )
    
    identity = IdentityMetadata.from_user(user=user)
    
    record = ActionRecord(
        identity=identity,
        action_type="approve",
        action_id="action-123",
        agent_id="agent-456",
        decision="allow",
        policy_id="pol-789",
        policy_name="Approval Required Policy",
        reason="Request approved by approver",
        timestamp=datetime.utcnow().isoformat() + "Z",
        context={"cost": 50},
    )
    
    assert record.identity.user_id == "bob"
    assert record.action_type == "approve"
    assert record.decision == "allow"
    assert record.policy_id == "pol-789"
    assert record.reason == "Request approved by approver"


def test_action_record_audit_sentence_approve():
    """Test generating audit sentence for approval action."""
    user = User(
        id="charlie",
        email="charlie@company.test",
        full_name="Charlie Admin",
        role=Role.ADMIN,
    )
    
    identity = IdentityMetadata.from_user(user=user)
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    record = ActionRecord(
        identity=identity,
        action_type="approve",
        action_id="action-123",
        agent_id="agent-456",
        decision="allow",
        policy_id="pol-789",
        policy_name="High Risk Approval",
        reason="Approved after review",
        timestamp=timestamp,
    )
    
    sentence = record.to_audit_sentence()
    assert "Charlie Admin" in sentence
    assert "High Risk Approval" in sentence
    assert "admin" in sentence
    assert timestamp in sentence


def test_action_record_audit_sentence_block():
    """Test generating audit sentence for blocked action."""
    user = User(
        id="dave",
        email="dave@company.test",
        full_name="Dave Developer",
        role=Role.DEVELOPER,
    )
    
    identity = IdentityMetadata.from_user(user=user)
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    record = ActionRecord(
        identity=identity,
        action_type="execute",
        action_id="action-123",
        agent_id="agent-456",
        decision="block",
        policy_id="pol-pii",
        policy_name="PII Detection Policy",
        reason="Prompt contains PII",
        timestamp=timestamp,
    )
    
    sentence = record.to_audit_sentence()
    assert "Dave Developer" in sentence
    assert "blocked" in sentence
    assert "PII Detection Policy" in sentence
    assert "Prompt contains PII" in sentence


def test_action_record_audit_sentence_allow():
    """Test generating audit sentence for allowed action."""
    user = User(
        id="eve",
        email="eve@company.test",
        full_name="Eve User",
        role=Role.USER,
    )
    
    identity = IdentityMetadata.from_user(user=user)
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    record = ActionRecord(
        identity=identity,
        action_type="execute",
        action_id="action-123",
        agent_id="agent-456",
        decision="allow",
        policy_id="pol-default",
        policy_name="Default Allow Policy",
        reason="Request approved",
        timestamp=timestamp,
    )
    
    sentence = record.to_audit_sentence()
    assert "Eve User" in sentence
    assert "allowed" in sentence
    assert "Default Allow Policy" in sentence


def test_identity_metadata_additional_metadata():
    """Test adding additional metadata to identity."""
    user = User(
        id="frank",
        email="frank@company.test",
        full_name="Frank Auditor",
        role=Role.AUDITOR,
    )
    
    additional_metadata = {
        "department": "Security",
        "location": "US-East",
        "session_id": "sess-12345",
    }
    
    identity = IdentityMetadata.from_user(
        user=user,
        metadata=additional_metadata,
    )
    
    assert identity.metadata["department"] == "Security"
    assert identity.metadata["location"] == "US-East"
    assert identity.metadata["session_id"] == "sess-12345"
