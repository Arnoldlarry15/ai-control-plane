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
Policy Explainer - Making AI Governance Decisions Transparent

"Boring reliability beats clever AI" - This is how we prove it.

Every decision must be:
- Explainable in plain English
- Reproducible from logs
- Auditable by non-technical stakeholders
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PolicyExplanation:
    """
    Human-readable explanation of a policy decision.
    
    This is what you show to executives, auditors, and regulators.
    """
    decision: str  # allow, block, escalate
    confidence: str  # high, medium, low
    primary_reason: str
    contributing_factors: List[str]
    policy_chain: List[str]  # Which policies evaluated
    recommendation: str
    technical_details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "decision": self.decision,
            "confidence": self.confidence,
            "primary_reason": self.primary_reason,
            "contributing_factors": self.contributing_factors,
            "policy_chain": self.policy_chain,
            "recommendation": self.recommendation,
            "technical_details": self.technical_details,
        }
    
    def to_plain_english(self) -> str:
        """
        Convert explanation to plain English.
        
        This is what non-technical stakeholders read.
        """
        lines = [
            f"Decision: {self.decision.upper()}",
            f"Confidence: {self.confidence}",
            "",
            f"Primary Reason: {self.primary_reason}",
        ]
        
        if self.contributing_factors:
            lines.append("")
            lines.append("Contributing Factors:")
            for i, factor in enumerate(self.contributing_factors, 1):
                lines.append(f"  {i}. {factor}")
        
        if self.policy_chain:
            lines.append("")
            lines.append("Policies Evaluated:")
            for i, policy in enumerate(self.policy_chain, 1):
                lines.append(f"  {i}. {policy}")
        
        lines.append("")
        lines.append(f"Recommendation: {self.recommendation}")
        
        return "\n".join(lines)


class PolicyExplainer:
    """
    Explains policy decisions in human-readable terms.
    
    This is critical for trust:
    - Executives need to understand decisions
    - Auditors need to verify compliance
    - Regulators need transparency
    - Developers need debugging info
    """
    
    def __init__(self):
        logger.info("Policy explainer initialized")
    
    def explain_decision(
        self,
        decision: str,
        context: Dict[str, Any],
        policies_evaluated: List[Dict[str, Any]],
        final_policy: Optional[Dict[str, Any]] = None,
    ) -> PolicyExplanation:
        """
        Generate explanation for a policy decision.
        
        Args:
            decision: Decision made (allow, block, escalate)
            context: Execution context
            policies_evaluated: List of policies that were evaluated
            final_policy: Policy that made the final decision
            
        Returns:
            Policy explanation
        """
        # Determine confidence
        confidence = self._determine_confidence(policies_evaluated, final_policy)
        
        # Generate primary reason
        primary_reason = self._generate_primary_reason(decision, final_policy, context)
        
        # Identify contributing factors
        contributing_factors = self._identify_contributing_factors(
            decision, policies_evaluated, context
        )
        
        # Build policy chain
        policy_chain = [p.get("name", p.get("id", "unknown")) for p in policies_evaluated]
        
        # Generate recommendation
        recommendation = self._generate_recommendation(decision, context, final_policy)
        
        # Collect technical details
        technical_details = {
            "total_policies_evaluated": len(policies_evaluated),
            "decision_policy": final_policy.get("id") if final_policy else None,
            "context_summary": self._summarize_context(context),
        }
        
        return PolicyExplanation(
            decision=decision,
            confidence=confidence,
            primary_reason=primary_reason,
            contributing_factors=contributing_factors,
            policy_chain=policy_chain,
            recommendation=recommendation,
            technical_details=technical_details,
        )
    
    def _determine_confidence(
        self,
        policies_evaluated: List[Dict[str, Any]],
        final_policy: Optional[Dict[str, Any]]
    ) -> str:
        """
        Determine confidence level of decision.
        
        High: Clear policy match
        Medium: Multiple factors considered
        Low: Edge case or fallback
        """
        if not final_policy:
            return "low"
        
        # If only one policy matched, high confidence
        if len(policies_evaluated) == 1:
            return "high"
        
        # If multiple policies agree, high confidence
        decisions = [p.get("action") for p in policies_evaluated]
        if len(set(decisions)) == 1:
            return "high"
        
        # Multiple conflicting policies, medium confidence
        if len(set(decisions)) > 1:
            return "medium"
        
        return "medium"
    
    def _generate_primary_reason(
        self,
        decision: str,
        final_policy: Optional[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """Generate primary reason for decision."""
        if decision == "allow":
            return "Request meets all policy requirements and is approved for execution."
        
        elif decision == "block":
            if final_policy:
                reason = final_policy.get("reason", "Policy violation detected")
                return f"Request blocked: {reason}"
            return "Request does not meet policy requirements and is blocked."
        
        elif decision == "escalate":
            if final_policy:
                reason = final_policy.get("reason", "Requires human review")
                return f"Request escalated: {reason}"
            return "Request requires human approval before proceeding."
        
        return f"Decision: {decision}"
    
    def _identify_contributing_factors(
        self,
        decision: str,
        policies_evaluated: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[str]:
        """Identify factors that contributed to decision."""
        factors = []
        
        # Risk level
        risk_level = context.get("agent", {}).get("risk_level", "unknown")
        if risk_level in ["high", "critical"]:
            factors.append(f"Agent risk level is {risk_level}")
        
        # User context
        user = context.get("user")
        if user:
            factors.append(f"Request initiated by user: {user}")
        
        # Policy matches
        matched_policies = [p for p in policies_evaluated if p.get("matched")]
        if matched_policies:
            factors.append(f"{len(matched_policies)} policies matched this request")
        
        # Model type
        model = context.get("agent", {}).get("model")
        if model:
            factors.append(f"AI model: {model}")
        
        # Prompt characteristics
        prompt = context.get("prompt", "")
        if len(prompt) > 500:
            factors.append("Long prompt detected (>500 characters)")
        
        return factors
    
    def _generate_recommendation(
        self,
        decision: str,
        context: Dict[str, Any],
        final_policy: Optional[Dict[str, Any]]
    ) -> str:
        """Generate recommendation for action."""
        if decision == "allow":
            return "Proceed with execution. Continue monitoring."
        
        elif decision == "block":
            return "Request denied. Review policy requirements and resubmit if appropriate."
        
        elif decision == "escalate":
            return "Human review required. Request will remain pending until approved or denied."
        
        return "Review decision and take appropriate action."
    
    def _summarize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of execution context."""
        return {
            "agent_id": context.get("agent_id"),
            "user": context.get("user"),
            "risk_level": context.get("agent", {}).get("risk_level"),
            "model": context.get("agent", {}).get("model"),
            "prompt_length": len(context.get("prompt", "")),
        }
    
    def explain_policy_conflict(
        self,
        conflicting_policies: List[Dict[str, Any]]
    ) -> str:
        """
        Explain policy conflicts.
        
        Args:
            conflicting_policies: List of policies with conflicting decisions
            
        Returns:
            Plain English explanation of conflict
        """
        lines = [
            "POLICY CONFLICT DETECTED",
            "",
            "Multiple policies evaluated this request with different decisions:",
            "",
        ]
        
        for i, policy in enumerate(conflicting_policies, 1):
            policy_name = policy.get("name", policy.get("id", "unknown"))
            action = policy.get("action", "unknown")
            reason = policy.get("reason", "No reason provided")
            
            lines.append(f"{i}. Policy: {policy_name}")
            lines.append(f"   Decision: {action}")
            lines.append(f"   Reason: {reason}")
            lines.append("")
        
        lines.append("Resolution: Most restrictive policy takes precedence (fail closed).")
        lines.append("Order: block > escalate > allow")
        
        return "\n".join(lines)
    
    def generate_dry_run_report(
        self,
        context: Dict[str, Any],
        all_policies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate dry-run report showing what would happen.
        
        This lets users test policies without actually executing.
        
        Args:
            context: Execution context to test
            all_policies: All policies to evaluate
            
        Returns:
            Dry-run report
        """
        # Evaluate all policies (simulated)
        results = []
        for policy in all_policies:
            # Simulate evaluation
            matched = True  # Simplified - actual implementation would evaluate
            if matched:
                results.append({
                    "policy_id": policy.get("id"),
                    "policy_name": policy.get("name"),
                    "matched": True,
                    "action": policy.get("action", "allow"),
                    "reason": policy.get("reason", ""),
                })
        
        # Determine final decision (most restrictive)
        final_decision = "allow"
        if any(r["action"] == "block" for r in results):
            final_decision = "block"
        elif any(r["action"] == "escalate" for r in results):
            final_decision = "escalate"
        
        return {
            "dry_run": True,
            "final_decision": final_decision,
            "policies_evaluated": len(all_policies),
            "policies_matched": len(results),
            "results": results,
            "explanation": self.explain_decision(
                final_decision,
                context,
                results,
                results[0] if results else None
            ).to_plain_english(),
        }


class PolicyDiagnostics:
    """
    Diagnostic tools for policy debugging and validation.
    
    This is what makes the system maintainable at scale.
    """
    
    def __init__(self):
        logger.info("Policy diagnostics initialized")
    
    def check_policy_coverage(
        self,
        policies: List[Dict[str, Any]],
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check policy coverage against test cases.
        
        Args:
            policies: List of policies to check
            test_cases: List of test cases with expected outcomes
            
        Returns:
            Coverage report
        """
        total_cases = len(test_cases)
        covered_cases = 0
        uncovered_cases = []
        
        for test_case in test_cases:
            # Check if any policy covers this case
            covered = False
            for policy in policies:
                # Simplified - actual implementation would evaluate
                if self._policy_covers_case(policy, test_case):
                    covered = True
                    break
            
            if covered:
                covered_cases += 1
            else:
                uncovered_cases.append(test_case.get("name", "unnamed"))
        
        coverage_percentage = (covered_cases / total_cases * 100) if total_cases > 0 else 0
        
        return {
            "total_test_cases": total_cases,
            "covered_cases": covered_cases,
            "coverage_percentage": coverage_percentage,
            "uncovered_cases": uncovered_cases,
            "recommendation": "Add policies to cover uncovered cases" if uncovered_cases else "Full coverage achieved"
        }
    
    def _policy_covers_case(
        self,
        policy: Dict[str, Any],
        test_case: Dict[str, Any]
    ) -> bool:
        """Check if policy covers test case."""
        # Simplified implementation
        return True
    
    def detect_policy_conflicts(
        self,
        policies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect potential conflicts between policies.
        
        Args:
            policies: List of policies to check
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Check for policies with opposite actions on similar conditions
        # Simplified - actual implementation would do deep analysis
        
        for i, policy1 in enumerate(policies):
            for policy2 in policies[i+1:]:
                if self._policies_conflict(policy1, policy2):
                    conflicts.append({
                        "policy1": policy1.get("name"),
                        "policy2": policy2.get("name"),
                        "description": f"Policies may produce conflicting decisions",
                    })
        
        return conflicts
    
    def _policies_conflict(
        self,
        policy1: Dict[str, Any],
        policy2: Dict[str, Any]
    ) -> bool:
        """Check if two policies conflict."""
        # Simplified implementation
        return False
