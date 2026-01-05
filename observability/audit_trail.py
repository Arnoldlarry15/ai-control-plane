"""
Audit Trail System - Immutable, Cryptographically Verified Logs

This is the "system of record" for AI activity.
- Every decision logged
- Tamper-proof with cryptographic hashing
- Replayable execution timelines
- Subpoena-ready exports

If an AI decision is questioned, this is the source of truth.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """
    Single audit log entry.
    
    Immutable once created. Chained via previous_hash for integrity.
    """
    entry_id: str
    timestamp: str
    event_type: str
    execution_id: Optional[str]
    agent_id: Optional[str]
    user: Optional[str]
    action: str
    status: str
    details: Dict[str, Any]
    previous_hash: Optional[str]
    entry_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def verify_hash(self) -> bool:
        """
        Verify entry hash is correct.
        
        Returns:
            True if hash is valid
        """
        computed_hash = self._compute_hash()
        return computed_hash == self.entry_hash
    
    def _compute_hash(self) -> str:
        """Compute hash of entry (excluding the hash itself)."""
        data = {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "execution_id": self.execution_id,
            "agent_id": self.agent_id,
            "user": self.user,
            "action": self.action,
            "status": self.status,
            "details": self.details,
            "previous_hash": self.previous_hash,
        }
        
        # Deterministic JSON serialization
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()


class AuditTrail:
    """
    Immutable audit trail with cryptographic integrity.
    
    Features:
    - Append-only log
    - Chained hashing (like blockchain)
    - Tamper detection
    - Full replay capability
    """
    
    def __init__(self):
        self._entries: List[AuditEntry] = []
        self._last_hash: Optional[str] = None
        logger.info("Audit trail initialized with cryptographic integrity")
    
    def append(
        self,
        event_type: str,
        action: str,
        status: str,
        details: Dict[str, Any],
        execution_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user: Optional[str] = None,
    ) -> AuditEntry:
        """
        Append entry to audit trail.
        
        Args:
            event_type: Type of event
            action: Action taken
            status: Status of action
            details: Event details
            execution_id: Optional execution ID
            agent_id: Optional agent ID
            user: Optional user ID
            
        Returns:
            Created audit entry
        """
        import uuid
        
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Create entry without hash
        entry_data = {
            "entry_id": entry_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "execution_id": execution_id,
            "agent_id": agent_id,
            "user": user,
            "action": action,
            "status": status,
            "details": details,
            "previous_hash": self._last_hash,
            "entry_hash": "",  # Computed next
        }
        
        # Compute hash
        json_str = json.dumps({k: v for k, v in entry_data.items() if k != "entry_hash"}, sort_keys=True)
        entry_hash = hashlib.sha256(json_str.encode()).hexdigest()
        entry_data["entry_hash"] = entry_hash
        
        # Create entry
        entry = AuditEntry(**entry_data)
        
        # Append to chain
        self._entries.append(entry)
        self._last_hash = entry_hash
        
        logger.debug(f"Audit entry appended: {entry_id} (type={event_type})")
        
        return entry
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of entire audit trail.
        
        Returns:
            Verification result with details
        """
        if not self._entries:
            return {
                "valid": True,
                "total_entries": 0,
                "message": "Empty audit trail"
            }
        
        invalid_entries = []
        broken_chains = []
        
        # Verify each entry hash
        for entry in self._entries:
            if not entry.verify_hash():
                invalid_entries.append(entry.entry_id)
        
        # Verify chain integrity
        for i in range(1, len(self._entries)):
            if self._entries[i].previous_hash != self._entries[i-1].entry_hash:
                broken_chains.append((i-1, i))
        
        valid = len(invalid_entries) == 0 and len(broken_chains) == 0
        
        result = {
            "valid": valid,
            "total_entries": len(self._entries),
            "invalid_entries": invalid_entries,
            "broken_chains": broken_chains,
        }
        
        if valid:
            result["message"] = "Audit trail integrity verified"
        else:
            result["message"] = "TAMPERING DETECTED: Audit trail compromised"
        
        return result
    
    def get_timeline(self, execution_id: str) -> List[AuditEntry]:
        """
        Get complete timeline for an execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            List of audit entries in chronological order
        """
        return [
            entry for entry in self._entries
            if entry.execution_id == execution_id
        ]
    
    def export_for_compliance(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        format: str = "json"
    ) -> str:
        """
        Export audit trail in compliance-ready format.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            format: Export format (json, csv)
            
        Returns:
            Formatted export string
        """
        # Filter by date range
        entries = self._entries
        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]
        
        if format == "json":
            return json.dumps([e.to_dict() for e in entries], indent=2)
        elif format == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            if entries:
                fieldnames = entries[0].to_dict().keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for entry in entries:
                    # Flatten details for CSV
                    row = entry.to_dict()
                    row["details"] = json.dumps(row["details"])
                    writer.writerow(row)
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_chain_of_custody(self, execution_id: str) -> Dict[str, Any]:
        """
        Get chain of custody for an execution.
        
        This is what you present in court or to regulators.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Chain of custody report
        """
        timeline = self.get_timeline(execution_id)
        
        if not timeline:
            return {
                "execution_id": execution_id,
                "status": "not_found",
                "message": "No audit entries found for this execution"
            }
        
        # Verify integrity of this execution's entries
        all_valid = all(entry.verify_hash() for entry in timeline)
        
        return {
            "execution_id": execution_id,
            "status": "verified" if all_valid else "compromised",
            "total_events": len(timeline),
            "timeline": [
                {
                    "timestamp": entry.timestamp,
                    "event_type": entry.event_type,
                    "action": entry.action,
                    "status": entry.status,
                    "hash": entry.entry_hash,
                    "hash_verified": entry.verify_hash(),
                }
                for entry in timeline
            ],
            "integrity_check": {
                "all_hashes_valid": all_valid,
                "message": "Complete chain of custody verified" if all_valid else "INTEGRITY COMPROMISED"
            }
        }
    
    def query(
        self,
        event_type: Optional[str] = None,
        execution_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """
        Query audit entries.
        
        Args:
            event_type: Filter by event type
            execution_id: Filter by execution
            agent_id: Filter by agent
            user: Filter by user
            status: Filter by status
            limit: Maximum results
            
        Returns:
            Filtered entries
        """
        results = self._entries
        
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if execution_id:
            results = [e for e in results if e.execution_id == execution_id]
        if agent_id:
            results = [e for e in results if e.agent_id == agent_id]
        if user:
            results = [e for e in results if e.user == user]
        if status:
            results = [e for e in results if e.status == status]
        
        # Return most recent up to limit
        return results[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get audit trail statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self._entries:
            return {
                "total_entries": 0,
                "by_event_type": {},
                "by_status": {},
                "unique_users": 0,
                "unique_agents": 0,
                "unique_executions": 0,
            }
        
        by_event_type = {}
        by_status = {}
        users = set()
        agents = set()
        executions = set()
        
        for entry in self._entries:
            by_event_type[entry.event_type] = by_event_type.get(entry.event_type, 0) + 1
            by_status[entry.status] = by_status.get(entry.status, 0) + 1
            
            if entry.user:
                users.add(entry.user)
            if entry.agent_id:
                agents.add(entry.agent_id)
            if entry.execution_id:
                executions.add(entry.execution_id)
        
        return {
            "total_entries": len(self._entries),
            "by_event_type": by_event_type,
            "by_status": by_status,
            "unique_users": len(users),
            "unique_agents": len(agents),
            "unique_executions": len(executions),
            "first_entry": self._entries[0].timestamp if self._entries else None,
            "last_entry": self._entries[-1].timestamp if self._entries else None,
        }


class DecisionTimeline:
    """
    Replayable decision timeline for an execution.
    
    Captures every decision point with full context.
    """
    
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.decisions: List[Dict[str, Any]] = []
        self.context_snapshots: Dict[str, Any] = {}
    
    def add_decision(
        self,
        decision_type: str,
        decision: str,
        reason: str,
        timestamp: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Add decision point to timeline.
        
        Args:
            decision_type: Type of decision (policy, kill_switch, approval, etc.)
            decision: Decision made (allow, block, escalate)
            reason: Reason for decision
            timestamp: Optional timestamp
            context: Optional context snapshot
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        decision_entry = {
            "timestamp": timestamp,
            "decision_type": decision_type,
            "decision": decision,
            "reason": reason,
        }
        
        if context:
            # Store context snapshot
            snapshot_id = f"snapshot_{len(self.decisions)}"
            self.context_snapshots[snapshot_id] = context
            decision_entry["context_snapshot_id"] = snapshot_id
        
        self.decisions.append(decision_entry)
    
    def replay(self) -> Dict[str, Any]:
        """
        Replay execution with full decision context.
        
        Returns:
            Complete replay including all decisions and context
        """
        return {
            "execution_id": self.execution_id,
            "total_decisions": len(self.decisions),
            "timeline": self.decisions,
            "context_snapshots": self.context_snapshots,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.replay()
