"""
Policy Parser: Load and parse policy definitions.

Policies are code. They live in version control. They're reviewed like code.
"""

import logging
import re
from typing import Dict, Any, List, Optional

import yaml

from policy.schemas import Policy, PolicyRule, PolicyCondition

logger = logging.getLogger(__name__)


class PolicyParser:
    """
    Parser for policy definitions.
    
    Loads policies from YAML and validates them.
    """
    
    def __init__(self):
        logger.info("Policy parser initialized")
    
    def parse_yaml(self, yaml_content: str) -> Policy:
        """
        Parse policy from YAML string.
        
        Args:
            yaml_content: YAML policy definition
        
        Returns:
            Parsed Policy object
        """
        try:
            data = yaml.safe_load(yaml_content)
            policy_data = data.get("policy", data)
            
            # Validate and create Policy object
            policy = Policy(**policy_data)
            
            logger.info(f"Policy parsed: {policy.id} v{policy.version}")
            return policy
        
        except Exception as e:
            logger.error(f"Policy parse error: {e}", exc_info=True)
            raise ValueError(f"Invalid policy YAML: {e}")
    
    def parse_file(self, file_path: str) -> Policy:
        """
        Parse policy from YAML file.
        
        Args:
            file_path: Path to policy file
        
        Returns:
            Parsed Policy object
        """
        with open(file_path, "r") as f:
            content = f.read()
        return self.parse_yaml(content)
    
    def validate_policy(self, policy: Policy) -> bool:
        """
        Validate policy structure and logic.
        
        Args:
            policy: Policy to validate
        
        Returns:
            True if valid
        
        Raises:
            ValueError: If policy is invalid
        """
        if not policy.rules:
            raise ValueError("Policy must have at least one rule")
        
        for rule in policy.rules:
            if rule.action not in ["allow", "block", "escalate", "redact"]:
                raise ValueError(f"Invalid action: {rule.action}")
            
            # Validate regex patterns if present
            if rule.condition.input_matches_pattern:
                try:
                    re.compile(rule.condition.input_matches_pattern)
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern: {e}")
        
        return True
