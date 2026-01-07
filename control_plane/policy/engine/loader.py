"""
Policy Loader - Load policies from YAML/JSON files.

This module provides utilities to load policy definitions from
configuration files, making it easy to manage policies without code changes.
"""

import os
import yaml
import json
from typing import List, Dict, Any
from pathlib import Path

from control_plane.policy.schemas.policy_schema import PolicySchema


def load_policy_from_yaml_file(filepath: str) -> PolicySchema:
    """
    Load a policy from a YAML file.
    
    Args:
        filepath: Path to YAML file
        
    Returns:
        PolicySchema instance
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML is invalid or policy is malformed
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")
    
    with open(filepath, 'r') as f:
        policy_dict = yaml.safe_load(f)
    
    return PolicySchema(policy_dict)


def load_policy_from_json_file(filepath: str) -> PolicySchema:
    """
    Load a policy from a JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        PolicySchema instance
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid or policy is malformed
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")
    
    with open(filepath, 'r') as f:
        policy_dict = json.load(f)
    
    return PolicySchema(policy_dict)


def load_policies_from_directory(directory: str, pattern: str = "*.yaml") -> List[PolicySchema]:
    """
    Load all policies from a directory.
    
    Args:
        directory: Path to directory containing policy files
        pattern: File pattern to match (default: *.yaml)
        
    Returns:
        List of PolicySchema instances
        
    Raises:
        FileNotFoundError: If directory doesn't exist
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Policy directory not found: {directory}")
    
    policies = []
    path = Path(directory)
    
    for filepath in path.glob(pattern):
        if filepath.suffix in ['.yaml', '.yml']:
            policy = load_policy_from_yaml_file(str(filepath))
            policies.append(policy)
        elif filepath.suffix == '.json':
            policy = load_policy_from_json_file(str(filepath))
            policies.append(policy)
    
    return policies


def load_example_policies() -> List[PolicySchema]:
    """
    Load example policies from the examples directory.
    
    Returns:
        List of example PolicySchema instances
    """
    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    examples_dir = os.path.join(current_dir, "..", "policies", "examples")
    
    if os.path.exists(examples_dir):
        return load_policies_from_directory(examples_dir)
    
    return []
