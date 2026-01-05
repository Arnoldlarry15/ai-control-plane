"""
Example Custom Policy Evaluator Plugin

Demonstrates how to create a drop-in policy evaluator.
"""

from typing import Dict, Any
from policy.plugins import PolicyEvaluatorPlugin


class IndustryComplianceEvaluator(PolicyEvaluatorPlugin):
    """
    Industry-specific compliance evaluator.
    
    Example: Financial services compliance checks.
    """
    
    @property
    def plugin_id(self) -> str:
        return "finserv-compliance-evaluator"
    
    @property
    def plugin_name(self) -> str:
        return "Financial Services Compliance Evaluator"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_description(self) -> str:
        return "Evaluates policies for financial services compliance"
    
    def evaluate_policy(
        self,
        agent: Dict[str, Any],
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate financial services compliance.
        
        Checks for:
        - Financial advice without disclaimers
        - Investment recommendations
        - Regulated information handling
        """
        prompt_lower = prompt.lower()
        
        # Check for financial advice
        advice_keywords = ['invest', 'buy', 'sell', 'recommend', 'portfolio']
        contains_advice = any(kw in prompt_lower for kw in advice_keywords)
        
        # Check for disclaimers
        has_disclaimer = context.get('disclaimer_shown', False)
        
        if contains_advice and not has_disclaimer:
            return {
                "action": "escalate",
                "reason": "Financial advice requires compliance review and disclaimer",
                "score": 85,
                "metadata": {
                    "compliance_standard": "SEC Regulation",
                    "required_action": "Add disclaimer and get approval"
                }
            }
        
        # Check for regulated data
        regulated_keywords = ['ssn', 'tax id', 'ein', 'account number']
        contains_regulated = any(kw in prompt_lower for kw in regulated_keywords)
        
        if contains_regulated:
            return {
                "action": "block",
                "reason": "Regulated financial information detected",
                "score": 95,
                "metadata": {
                    "compliance_standard": "GLBA",
                    "violation_type": "PII_EXPOSURE"
                }
            }
        
        # Allow if all checks pass
        return {
            "action": "allow",
            "reason": "Compliance checks passed",
            "score": 10,
            "metadata": {}
        }


class CustomBusinessRulesEvaluator(PolicyEvaluatorPlugin):
    """
    Custom business rules evaluator.
    
    Example: Company-specific approval workflows.
    """
    
    @property
    def plugin_id(self) -> str:
        return "custom-business-rules"
    
    @property
    def plugin_name(self) -> str:
        return "Custom Business Rules Evaluator"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_description(self) -> str:
        return "Enforces custom business rules and approval workflows"
    
    def evaluate_policy(
        self,
        agent: Dict[str, Any],
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate custom business rules.
        
        Example rules:
        - Customer data requires manager approval
        - External sharing needs security review
        - High-value operations need VP approval
        """
        # Check for customer data access
        if 'customer_data' in context:
            user_role = context.get('user_role', 'user')
            if user_role not in ['manager', 'admin']:
                return {
                    "action": "escalate",
                    "reason": "Customer data access requires manager approval",
                    "score": 70,
                    "metadata": {
                        "approval_required_from": "manager",
                        "business_rule": "customer-data-protection"
                    }
                }
        
        # Check for external sharing
        if context.get('sharing_scope') == 'external':
            return {
                "action": "escalate",
                "reason": "External sharing requires security review",
                "score": 80,
                "metadata": {
                    "approval_required_from": "security-team",
                    "business_rule": "external-sharing-control"
                }
            }
        
        # Check for high-value operations
        estimated_cost = context.get('estimated_cost', 0)
        if estimated_cost > 1000:
            return {
                "action": "escalate",
                "reason": f"High-value operation (${estimated_cost}) requires VP approval",
                "score": 75,
                "metadata": {
                    "approval_required_from": "vp",
                    "business_rule": "cost-control",
                    "estimated_cost": estimated_cost
                }
            }
        
        return {
            "action": "allow",
            "reason": "Business rules compliance verified",
            "score": 5,
            "metadata": {}
        }
