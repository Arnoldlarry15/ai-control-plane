"""
Compliance Validation API

Provides endpoints for validating compliance policies and generating reports.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from policy.compliance.loader import ComplianceLoader
from policy.evaluator import PolicyEvaluator
from policy.schemas import Policy

logger = logging.getLogger(__name__)


class ComplianceValidator:
    """
    Validates inputs against compliance policies and generates compliance reports.
    """
    
    def __init__(self):
        self.loader = ComplianceLoader()
        self.evaluator = PolicyEvaluator()
        self._policies_cache: Dict[str, Policy] = {}
        logger.info("Compliance validator initialized")
    
    def validate_input(
        self,
        input_text: str,
        standards: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate input against specified compliance standards.
        
        Args:
            input_text: Input text to validate
            standards: List of compliance standard IDs (gdpr, hipaa, soc2, pci-dss)
            context: Optional context for validation
            
        Returns:
            Validation result with compliance status and violations
        """
        if not standards:
            standards = list(self.loader.COMPLIANCE_STANDARDS.keys())
        
        results = {
            "compliant": True,
            "standards_checked": standards,
            "violations": [],
            "warnings": [],
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        for standard in standards:
            try:
                policy = self._get_policy(standard)
                
                # Create a fake agent with this policy for evaluation
                fake_agent = {
                    "id": "compliance-validator",
                    "name": "Compliance Validator",
                    "policies": [policy.id],
                }
                
                # Register policy with evaluator temporarily
                self.evaluator._policies[policy.id] = policy
                
                # Evaluate
                evaluation = self.evaluator.evaluate(
                    agent=fake_agent,
                    prompt=input_text,
                    context=context or {},
                    user="compliance-check"
                )
                
                if evaluation["action"] in ["block", "escalate"]:
                    violation = {
                        "standard": standard.upper(),
                        "severity": "critical" if evaluation["action"] == "block" else "warning",
                        "reason": evaluation.get("reason", "Policy violation"),
                        "action": evaluation["action"],
                    }
                    
                    if evaluation["action"] == "block":
                        results["compliant"] = False
                        results["violations"].append(violation)
                    else:
                        results["warnings"].append(violation)
                        
            except Exception as e:
                logger.error(f"Error validating {standard}: {e}")
                results["warnings"].append({
                    "standard": standard.upper(),
                    "severity": "error",
                    "reason": f"Validation error: {str(e)}",
                })
        
        return results
    
    def generate_compliance_report(
        self,
        agent_id: str,
        time_range_start: datetime,
        time_range_end: datetime,
        standards: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate compliance report for an agent over a time range.
        
        Args:
            agent_id: Agent identifier
            time_range_start: Start of time range
            time_range_end: End of time range
            standards: Optional list of standards to check
            
        Returns:
            Compliance report
        """
        if not standards:
            standards = list(self.loader.COMPLIANCE_STANDARDS.keys())
        
        report = {
            "agent_id": agent_id,
            "report_period": {
                "start": time_range_start.isoformat(),
                "end": time_range_end.isoformat(),
            },
            "standards": {},
            "overall_compliance": "compliant",
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        for standard in standards:
            try:
                policy = self._get_policy(standard)
                policy_info = self.loader.get_policy_info(standard)
                
                report["standards"][standard.upper()] = {
                    "standard_name": policy_info["name"],
                    "policy_version": policy_info["version"],
                    "rules_count": policy_info["rules_count"],
                    "status": "active",
                    "description": policy_info["description"],
                }
            except Exception as e:
                logger.error(f"Error generating report for {standard}: {e}")
                report["standards"][standard.upper()] = {
                    "status": "error",
                    "error": str(e),
                }
        
        return report
    
    def get_compliance_standards(self) -> Dict[str, str]:
        """
        Get list of available compliance standards.
        
        Returns:
            Dictionary of standard ID to description
        """
        return self.loader.list_standards()
    
    def get_standard_details(self, standard: str) -> Dict[str, Any]:
        """
        Get detailed information about a compliance standard.
        
        Args:
            standard: Compliance standard ID
            
        Returns:
            Detailed standard information
        """
        policy_info = self.loader.get_policy_info(standard)
        policy = self._get_policy(standard)
        
        return {
            **policy_info,
            "rules": [
                {
                    "condition": rule.condition,
                    "action": rule.action,
                    "reason": rule.reason,
                }
                for rule in policy.rules
            ],
        }
    
    def _get_policy(self, standard: str) -> Policy:
        """Get policy from cache or load it."""
        if standard not in self._policies_cache:
            self._policies_cache[standard] = self.loader.load_policy(standard)
        return self._policies_cache[standard]
    
    def _extract_reference(self, reason: str) -> Optional[str]:
        """Extract compliance reference from reason text."""
        # Simple extraction - look for patterns like "GDPR Art. 17"
        parts = reason.split(" - ")
        if len(parts) > 1:
            return parts[0]
        return None


# Singleton instance
_validator_instance: Optional[ComplianceValidator] = None


def get_compliance_validator() -> ComplianceValidator:
    """Get singleton compliance validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ComplianceValidator()
    return _validator_instance
