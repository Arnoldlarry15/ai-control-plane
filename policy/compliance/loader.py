"""
Compliance Policy Loader

Loads pre-built compliance policy modules for major standards.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any

from policy.parser import PolicyParser
from policy.schemas import Policy

logger = logging.getLogger(__name__)


class ComplianceLoader:
    """
    Loader for compliance policy modules.
    
    Provides easy access to pre-built policies for:
    - GDPR (General Data Protection Regulation)
    - HIPAA (Health Insurance Portability and Accountability Act)
    - SOC 2 (Service Organization Control 2)
    - PCI-DSS (Payment Card Industry Data Security Standard)
    """
    
    COMPLIANCE_STANDARDS = {
        "gdpr": "GDPR (EU General Data Protection Regulation)",
        "hipaa": "HIPAA (US Health Insurance Portability and Accountability Act)",
        "soc2": "SOC 2 (Trust Services Criteria)",
        "pci-dss": "PCI-DSS (Payment Card Industry Data Security Standard)",
    }
    
    def __init__(self):
        self.parser = PolicyParser()
        self.compliance_dir = Path(__file__).parent
        logger.info(f"Compliance loader initialized from {self.compliance_dir}")
    
    def list_standards(self) -> Dict[str, str]:
        """
        List available compliance standards.
        
        Returns:
            Dictionary of standard ID to description
        """
        return self.COMPLIANCE_STANDARDS.copy()
    
    def load_policy(self, standard: str) -> Policy:
        """
        Load a compliance policy by standard name.
        
        Args:
            standard: Compliance standard ID (gdpr, hipaa, soc2, pci-dss)
            
        Returns:
            Loaded policy
            
        Raises:
            ValueError: If standard is not found
        """
        if standard not in self.COMPLIANCE_STANDARDS:
            available = ", ".join(self.COMPLIANCE_STANDARDS.keys())
            raise ValueError(
                f"Unknown compliance standard: {standard}. "
                f"Available: {available}"
            )
        
        policy_file = self.compliance_dir / f"{standard}.yaml"
        
        if not policy_file.exists():
            raise FileNotFoundError(
                f"Compliance policy file not found: {policy_file}"
            )
        
        with open(policy_file, 'r') as f:
            policy_yaml = f.read()
        
        policy = self.parser.parse_yaml(policy_yaml)
        
        logger.info(f"Loaded compliance policy: {standard}")
        
        return policy
    
    def load_all(self) -> List[Policy]:
        """
        Load all compliance policies.
        
        Returns:
            List of all compliance policies
        """
        policies = []
        
        for standard in self.COMPLIANCE_STANDARDS.keys():
            try:
                policy = self.load_policy(standard)
                policies.append(policy)
            except Exception as e:
                logger.error(f"Error loading {standard} policy: {e}")
        
        logger.info(f"Loaded {len(policies)} compliance policies")
        
        return policies
    
    def get_policy_info(self, standard: str) -> Dict[str, Any]:
        """
        Get information about a compliance policy without loading it.
        
        Args:
            standard: Compliance standard ID
            
        Returns:
            Policy metadata
        """
        policy = self.load_policy(standard)
        
        return {
            "id": policy.id,
            "name": policy.name,
            "version": policy.version,
            "description": policy.description,
            "standard": standard.upper(),
            "rules_count": len(policy.rules),
        }
