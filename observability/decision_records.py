"""
Decision Records: Human-Centric Observability

Answer human questions, not machine questions:
- Why was this blocked?
- Who approved this?
- Which policy fired?
- What would have happened under a different policy?

This transforms logs into a truth oracle for AI behavior.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from observability.events import DecisionRecord

logger = logging.getLogger(__name__)


class DecisionRecordStore:
    """
    Store and query decision records.
    
    This is the interface for human-centric observability.
    """
    
    def __init__(self):
        self._records: Dict[str, DecisionRecord] = {}
        logger.info("Decision record store initialized")
    
    def store_decision(self, record: DecisionRecord):
        """
        Store a decision record.
        
        Args:
            record: Decision record to store
        """
        self._records[record.execution_id] = record
        logger.debug(f"Decision record stored: {record.execution_id}")
    
    def get_decision(self, execution_id: str) -> Optional[DecisionRecord]:
        """
        Get a decision record by execution ID.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Decision record or None
        """
        return self._records.get(execution_id)
    
    def why_blocked(self, execution_id: str) -> Dict[str, Any]:
        """
        Answer: Why was this blocked?
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Human-readable explanation of why the request was blocked
        """
        record = self._records.get(execution_id)
        
        if not record:
            return {
                "found": False,
                "message": "No decision record found for this execution"
            }
        
        if record.decision != "block":
            return {
                "found": True,
                "blocked": False,
                "decision": record.decision,
                "message": f"Request was not blocked (decision: {record.decision})"
            }
        
        return {
            "found": True,
            "blocked": True,
            "reason": record.reason,
            "policy_id": record.policy_id,
            "policy_name": record.policy_name,
            "blocked_at": record.decision_timestamp,
            "blocked_for": record.requester_name or record.requester_id,
            "summary": f"Blocked by policy '{record.policy_name or record.policy_id}': {record.reason}",
            "audit_sentence": record.to_audit_sentence(),
        }
    
    def who_approved(self, execution_id: str) -> Dict[str, Any]:
        """
        Answer: Who approved this?
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Information about who approved the request
        """
        record = self._records.get(execution_id)
        
        if not record:
            return {
                "found": False,
                "message": "No decision record found for this execution"
            }
        
        if not record.approver_id:
            return {
                "found": True,
                "approved": False,
                "message": "Request did not require approval or was not approved",
                "decision": record.decision,
            }
        
        return {
            "found": True,
            "approved": True,
            "approver_id": record.approver_id,
            "approver_name": record.approver_name,
            "approver_role": record.approver_role,
            "approved_at": record.completion_timestamp,
            "policy": record.policy_name or record.policy_id,
            "summary": (
                f"Approved by {record.approver_name or record.approver_id} "
                f"({record.approver_role}) under policy '{record.policy_name or record.policy_id}' "
                f"at {record.completion_timestamp}"
            ),
            "audit_sentence": record.to_audit_sentence(),
        }
    
    def which_policy_fired(self, execution_id: str) -> Dict[str, Any]:
        """
        Answer: Which policy fired?
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Information about which policy made the decision
        """
        record = self._records.get(execution_id)
        
        if not record:
            return {
                "found": False,
                "message": "No decision record found for this execution"
            }
        
        return {
            "found": True,
            "policy_id": record.policy_id,
            "policy_name": record.policy_name,
            "decision": record.decision,
            "reason": record.reason,
            "policies_evaluated": record.policies_evaluated,
            "decided_at": record.decision_timestamp,
            "summary": (
                f"Policy '{record.policy_name or record.policy_id}' decided to "
                f"{record.decision}: {record.reason}"
            ),
        }
    
    def get_timeline(self, execution_id: str) -> Dict[str, Any]:
        """
        Get complete decision timeline for a request.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Complete timeline with all decision points
        """
        record = self._records.get(execution_id)
        
        if not record:
            return {
                "found": False,
                "message": "No decision record found for this execution"
            }
        
        timeline = [
            {
                "timestamp": record.request_timestamp,
                "event": "Request initiated",
                "actor": record.requester_name or record.requester_id,
                "role": record.requester_role,
            },
            {
                "timestamp": record.decision_timestamp,
                "event": f"Policy decision: {record.decision}",
                "policy": record.policy_name or record.policy_id,
                "reason": record.reason,
            },
        ]
        
        if record.approver_id and record.completion_timestamp:
            timeline.append({
                "timestamp": record.completion_timestamp,
                "event": "Approved",
                "actor": record.approver_name or record.approver_id,
                "role": record.approver_role,
            })
        
        return {
            "found": True,
            "execution_id": execution_id,
            "timeline": timeline,
            "audit_sentence": record.to_audit_sentence(),
        }
    
    def query_decisions(
        self,
        decision: Optional[str] = None,
        policy_id: Optional[str] = None,
        requester_id: Optional[str] = None,
        approver_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[DecisionRecord]:
        """
        Query decision records with filters.
        
        Args:
            decision: Filter by decision (allow, block, escalate)
            policy_id: Filter by policy
            requester_id: Filter by requester
            approver_id: Filter by approver
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            limit: Maximum results
            
        Returns:
            List of matching decision records
        """
        results = list(self._records.values())
        
        if decision:
            results = [r for r in results if r.decision == decision]
        if policy_id:
            results = [r for r in results if r.policy_id == policy_id]
        if requester_id:
            results = [r for r in results if r.requester_id == requester_id]
        if approver_id:
            results = [r for r in results if r.approver_id == approver_id]
        if start_time:
            results = [r for r in results if r.request_timestamp >= start_time]
        if end_time:
            results = [r for r in results if r.request_timestamp <= end_time]
        
        # Sort by timestamp (most recent first)
        results.sort(key=lambda r: r.request_timestamp, reverse=True)
        
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get decision statistics.
        
        Returns:
            Statistics about decisions
        """
        if not self._records:
            return {
                "total_decisions": 0,
                "by_decision": {},
                "by_policy": {},
                "unique_requesters": 0,
                "unique_approvers": 0,
            }
        
        by_decision = {}
        by_policy = {}
        requesters = set()
        approvers = set()
        
        for record in self._records.values():
            by_decision[record.decision] = by_decision.get(record.decision, 0) + 1
            
            if record.policy_id:
                by_policy[record.policy_id] = by_policy.get(record.policy_id, 0) + 1
            
            requesters.add(record.requester_id)
            
            if record.approver_id:
                approvers.add(record.approver_id)
        
        return {
            "total_decisions": len(self._records),
            "by_decision": by_decision,
            "by_policy": by_policy,
            "unique_requesters": len(requesters),
            "unique_approvers": len(approvers),
        }


class DryRunSimulator:
    """
    Simulate what would have happened under different policies.
    
    Answers: "What would have happened under a different policy?"
    """
    
    def __init__(self, policy_evaluator):
        """
        Initialize dry run simulator.
        
        Args:
            policy_evaluator: Policy evaluator instance
        """
        self.policy_evaluator = policy_evaluator
        logger.info("Dry run simulator initialized")
    
    def simulate_policy_change(
        self,
        agent: Dict[str, Any],
        prompt: str,
        context: Dict[str, Any],
        alternative_policies: List[str],
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Simulate what would happen with different policies.
        
        Args:
            agent: Agent configuration
            prompt: Request prompt
            context: Request context
            alternative_policies: List of alternative policy IDs to test
            user: User identifier
            
        Returns:
            Simulation results showing outcomes under different policies
        """
        results = {
            "original_policy": None,
            "alternative_outcomes": [],
        }
        
        # Get original decision
        try:
            original_decision = self.policy_evaluator.evaluate(
                agent=agent,
                prompt=prompt,
                context=context,
                user=user,
            )
            results["original_policy"] = {
                "decision": original_decision["action"],
                "reason": original_decision.get("reason"),
                "policy_id": original_decision.get("policy_id"),
            }
        except Exception as e:
            logger.error(f"Original policy evaluation failed: {e}")
            results["original_policy"] = {"error": str(e)}
        
        # Simulate alternatives
        for alt_policy in alternative_policies:
            try:
                # In a real implementation, we'd temporarily swap policies
                # For now, we'll note that this requires policy engine support
                results["alternative_outcomes"].append({
                    "policy_id": alt_policy,
                    "note": "Simulation requires policy engine support for policy swapping",
                })
            except Exception as e:
                logger.error(f"Alternative policy {alt_policy} simulation failed: {e}")
                results["alternative_outcomes"].append({
                    "policy_id": alt_policy,
                    "error": str(e),
                })
        
        return results
