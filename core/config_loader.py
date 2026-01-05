"""
Terraform-style Configuration Support

Declarative configuration for AI Control Plane resources.
"""

import yaml
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Load and parse Terraform-style configuration files.
    
    Supports YAML and JSON formats with Terraform-like declarative syntax.
    """
    
    def __init__(self):
        """Initialize config loader."""
        self.config_cache: Dict[str, Any] = {}
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to config file (.yaml, .yml, or .json)
            
        Returns:
            Parsed configuration
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # Check cache
        if config_path in self.config_cache:
            return self.config_cache[config_path]
        
        # Load based on extension
        if path.suffix in ['.yaml', '.yml']:
            config = self._load_yaml(path)
        elif path.suffix == '.json':
            config = self._load_json(path)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")
        
        # Validate config structure
        self._validate_config(config)
        
        # Cache config
        self.config_cache[config_path] = config
        
        logger.info(f"Loaded config from {config_path}")
        return config
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration."""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON configuration."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def _validate_config(self, config: Dict[str, Any]):
        """
        Validate configuration structure.
        
        Args:
            config: Configuration to validate
        """
        # Check for required top-level keys
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")
        
        # Validate resource blocks
        if 'resource' in config:
            self._validate_resources(config['resource'])
        
        # Validate variable blocks
        if 'variable' in config:
            self._validate_variables(config['variable'])
    
    def _validate_resources(self, resources: Dict[str, Any]):
        """Validate resource blocks."""
        if not isinstance(resources, dict):
            raise ValueError("Resources must be a dictionary")
    
    def _validate_variables(self, variables: Dict[str, Any]):
        """Validate variable blocks."""
        if not isinstance(variables, dict):
            raise ValueError("Variables must be a dictionary")
    
    def extract_agents(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract agent configurations.
        
        Args:
            config: Loaded configuration
            
        Returns:
            List of agent configurations
        """
        agents = []
        
        resources = config.get('resource', {})
        agent_resources = resources.get('agent', {})
        
        for agent_id, agent_config in agent_resources.items():
            agents.append({
                'id': agent_id,
                **agent_config
            })
        
        return agents
    
    def extract_policies(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract policy configurations.
        
        Args:
            config: Loaded configuration
            
        Returns:
            List of policy configurations
        """
        policies = []
        
        resources = config.get('resource', {})
        policy_resources = resources.get('policy', {})
        
        for policy_id, policy_config in policy_resources.items():
            policies.append({
                'id': policy_id,
                **policy_config
            })
        
        return policies
    
    def extract_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract variable definitions.
        
        Args:
            config: Loaded configuration
            
        Returns:
            Variable definitions
        """
        return config.get('variable', {})
    
    def apply_variables(
        self, 
        config: Dict[str, Any], 
        var_values: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply variable substitution to configuration.
        
        Args:
            config: Configuration with variables
            var_values: Variable values to substitute
            
        Returns:
            Configuration with variables resolved
        """
        if var_values is None:
            var_values = {}
        
        # Get variable definitions
        var_defs = self.extract_variables(config)
        
        # Merge with defaults
        resolved_vars = {}
        for var_name, var_def in var_defs.items():
            if var_name in var_values:
                resolved_vars[var_name] = var_values[var_name]
            elif 'default' in var_def:
                resolved_vars[var_name] = var_def['default']
            else:
                raise ValueError(f"Variable '{var_name}' has no value and no default")
        
        # Substitute variables recursively
        def substitute_in_value(value):
            """Recursively substitute variables in a value."""
            if isinstance(value, str):
                # Replace variable references
                for var_name, var_value in resolved_vars.items():
                    placeholder = f"${{var.{var_name}}}"
                    if placeholder in value:
                        value = value.replace(placeholder, str(var_value))
                return value
            elif isinstance(value, dict):
                return {k: substitute_in_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_in_value(item) for item in value]
            else:
                return value
        
        return substitute_in_value(config)


class ConfigApplier:
    """
    Apply Terraform-style configurations to the control plane.
    """
    
    def __init__(self, client):
        """
        Initialize config applier.
        
        Args:
            client: ControlPlaneClient instance
        """
        self.client = client
        self.loader = ConfigLoader()
    
    def apply(
        self, 
        config_path: str, 
        var_values: Optional[Dict[str, Any]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Apply configuration from file.
        
        Args:
            config_path: Path to config file
            var_values: Variable values
            dry_run: If True, validate but don't apply
            
        Returns:
            Results of application
        """
        # Load config
        config = self.loader.load_config(config_path)
        
        # Apply variables
        config = self.loader.apply_variables(config, var_values)
        
        results = {
            'agents_created': [],
            'policies_created': [],
            'errors': []
        }
        
        # Apply agents
        agents = self.loader.extract_agents(config)
        for agent_config in agents:
            try:
                if not dry_run:
                    result = self.client.register_agent(
                        name=agent_config.get('name'),
                        model=agent_config.get('model'),
                        risk_level=agent_config.get('risk_level', 'medium'),
                        policies=agent_config.get('policies', []),
                        environment=agent_config.get('environment', 'dev'),
                        metadata=agent_config.get('metadata', {})
                    )
                    results['agents_created'].append(result)
                else:
                    logger.info(f"[DRY RUN] Would create agent: {agent_config.get('name')}")
            except Exception as e:
                logger.error(f"Failed to create agent {agent_config.get('name')}: {e}")
                results['errors'].append(str(e))
        
        # Apply policies (future enhancement)
        policies = self.loader.extract_policies(config)
        for policy_config in policies:
            logger.info(f"Policy application not yet implemented: {policy_config.get('id')}")
        
        return results
    
    def plan(self, config_path: str, var_values: Optional[Dict[str, Any]] = None):
        """
        Show what would be applied (like terraform plan).
        
        Args:
            config_path: Path to config file
            var_values: Variable values
        """
        config = self.loader.load_config(config_path)
        config = self.loader.apply_variables(config, var_values)
        
        print("Resources to be created:\n")
        
        # Show agents
        agents = self.loader.extract_agents(config)
        if agents:
            print(f"Agents ({len(agents)}):")
            for agent in agents:
                print(f"  + agent.{agent['id']}")
                print(f"      name        = \"{agent.get('name')}\"")
                print(f"      model       = \"{agent.get('model')}\"")
                print(f"      risk_level  = \"{agent.get('risk_level', 'medium')}\"")
                print()
        
        # Show policies
        policies = self.loader.extract_policies(config)
        if policies:
            print(f"Policies ({len(policies)}):")
            for policy in policies:
                print(f"  + policy.{policy['id']}")
                print(f"      name = \"{policy.get('name')}\"")
                print()
        
        print(f"\nPlan: {len(agents)} agents, {len(policies)} policies to add")
