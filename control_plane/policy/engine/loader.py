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
    
    Loads files matching the pattern. Supports both YAML and JSON files.
    
    Args:
        directory: Path to directory containing policy files
        pattern: Glob pattern to match files (default: *.yaml)
                Commonly used patterns: "*.yaml", "*.json", "*.yml", "policy_*.yaml"
        
    Returns:
        List of PolicySchema instances
        
    Raises:
        FileNotFoundError: If directory doesn't exist
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Policy directory not found: {directory}")
    
    policies = []
    path = Path(directory)
    
    # Use the pattern to find files
    for filepath in path.glob(pattern):
        # Load based on file extension
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
