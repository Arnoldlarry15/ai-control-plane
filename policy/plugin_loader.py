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
Plugin Loader for Dynamic Discovery

Enables third-party plugins to be discovered and loaded without modifying core code.
"""

import logging
import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Type

from policy.plugins import PolicyPlugin, PluginRegistry

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Dynamic plugin loader for third-party extensions.
    
    Supports:
    - Auto-discovery from plugin directories
    - Dynamic import of Python modules
    - Plugin validation before registration
    - Hot-reload capabilities (future)
    """
    
    def __init__(self, registry: Optional[PluginRegistry] = None):
        """
        Initialize plugin loader.
        
        Args:
            registry: Plugin registry instance (creates new if None)
        """
        self.registry = registry or PluginRegistry()
        self._loaded_plugins: Dict[str, PolicyPlugin] = {}
        logger.info("Plugin loader initialized")
    
    def load_from_directory(self, directory: str) -> List[str]:
        """
        Load all plugins from a directory.
        
        Args:
            directory: Path to plugin directory
            
        Returns:
            List of loaded plugin IDs
        """
        plugin_dir = Path(directory)
        
        if not plugin_dir.exists() or not plugin_dir.is_dir():
            logger.warning(f"Plugin directory not found: {directory}")
            return []
        
        loaded_ids = []
        
        # Add directory to Python path
        if str(plugin_dir) not in sys.path:
            sys.path.insert(0, str(plugin_dir))
        
        # Discover Python modules
        for file_path in plugin_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            module_name = file_path.stem
            
            try:
                plugin_ids = self.load_from_module(module_name)
                loaded_ids.extend(plugin_ids)
            except Exception as e:
                logger.error(f"Failed to load plugin from {file_path}: {e}")
        
        logger.info(f"Loaded {len(loaded_ids)} plugins from {directory}")
        return loaded_ids
    
    def load_from_module(self, module_name: str) -> List[str]:
        """
        Load plugins from a Python module.
        
        Args:
            module_name: Fully qualified module name
            
        Returns:
            List of loaded plugin IDs
        """
        try:
            # Import module
            module = importlib.import_module(module_name)
            
            # Find all plugin classes
            plugin_classes = []
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PolicyPlugin) and 
                    obj != PolicyPlugin and
                    not inspect.isabstract(obj)):
                    plugin_classes.append(obj)
            
            # Instantiate and register plugins
            loaded_ids = []
            for plugin_class in plugin_classes:
                try:
                    plugin = plugin_class()
                    self.register_plugin(plugin)
                    loaded_ids.append(plugin.plugin_id)
                    logger.info(f"Loaded plugin: {plugin.plugin_id} from {module_name}")
                except Exception as e:
                    logger.error(f"Failed to instantiate plugin {plugin_class.__name__}: {e}")
            
            return loaded_ids
        
        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}")
            return []
    
    def register_plugin(self, plugin: PolicyPlugin):
        """
        Register a plugin instance.
        
        Args:
            plugin: Plugin to register
        """
        plugin_id = plugin.plugin_id
        
        # Validate plugin
        if not self._validate_plugin(plugin):
            logger.error(f"Plugin validation failed: {plugin_id}")
            return
        
        # Register with registry
        self.registry.register(plugin)
        self._loaded_plugins[plugin_id] = plugin
        
        logger.info(
            f"Registered plugin: {plugin_id} "
            f"({plugin.plugin_type.value}) v{plugin.plugin_version}"
        )
    
    def unload_plugin(self, plugin_id: str):
        """
        Unload a plugin.
        
        Args:
            plugin_id: Plugin identifier
        """
        if plugin_id not in self._loaded_plugins:
            logger.warning(f"Plugin not loaded: {plugin_id}")
            return
        
        self.registry.unregister(plugin_id)
        del self._loaded_plugins[plugin_id]
        
        logger.info(f"Unloaded plugin: {plugin_id}")
    
    def reload_plugin(self, plugin_id: str):
        """
        Reload a plugin (future feature).
        
        Args:
            plugin_id: Plugin identifier
        """
        logger.warning("Hot-reload not yet implemented")
    
    def _validate_plugin(self, plugin: PolicyPlugin) -> bool:
        """
        Validate plugin before registration.
        
        Args:
            plugin: Plugin to validate
            
        Returns:
            True if valid
        """
        try:
            # Check required properties
            _ = plugin.plugin_id
            _ = plugin.plugin_name
            _ = plugin.plugin_type
            _ = plugin.plugin_version
            
            # Check execute method
            if not callable(getattr(plugin, 'execute', None)):
                logger.error(f"Plugin {plugin.plugin_id} has invalid execute method")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Plugin validation error: {e}")
            return False
    
    def get_loaded_plugins(self) -> List[Dict[str, Any]]:
        """
        Get list of loaded plugins.
        
        Returns:
            List of plugin metadata
        """
        return [
            {
                "id": plugin.plugin_id,
                "name": plugin.plugin_name,
                "type": plugin.plugin_type.value,
                "version": plugin.plugin_version,
                "description": plugin.plugin_description,
            }
            for plugin in self._loaded_plugins.values()
        ]
