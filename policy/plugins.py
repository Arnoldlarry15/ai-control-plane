"""
Policy Plugin System

Extensibility layer for custom policy logic, risk scoring, and compliance modules.

This is what makes the control plane a platform, not just a tool.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins supported."""
    POLICY_EVALUATOR = "policy_evaluator"
    RISK_SCORER = "risk_scorer"
    RISK_ENGINE = "risk_engine"
    COMPLIANCE_MODULE = "compliance_module"
    LIFECYCLE_HOOK = "lifecycle_hook"
    DATA_SANITIZER = "data_sanitizer"


class PolicyPlugin(ABC):
    """
    Base class for all policy plugins.
    
    Plugins extend the control plane with custom logic without modifying core code.
    Think: Salesforce AppExchange, but for AI governance.
    """
    
    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique plugin identifier."""
        pass
    
    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Human-readable plugin name."""
        pass
    
    @property
    @abstractmethod
    def plugin_type(self) -> PluginType:
        """Type of plugin."""
        pass
    
    @property
    def plugin_version(self) -> str:
        """Plugin version."""
        return "1.0.0"
    
    @property
    def plugin_description(self) -> str:
        """Plugin description."""
        return ""
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute plugin logic.
        
        Args:
            context: Execution context
            
        Returns:
            Result dictionary
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration.
        
        Args:
            config: Plugin configuration
            
        Returns:
            True if valid
        """
        return True


class RiskScorerPlugin(PolicyPlugin):
    """
    Plugin for custom risk scoring logic.
    
    Example use cases:
    - Industry-specific risk models
    - ML-based risk prediction
    - Context-aware risk adjustment
    """
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.RISK_SCORER
    
    @abstractmethod
    def calculate_risk_score(
        self,
        agent_id: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate risk score for execution.
        
        Args:
            agent_id: Agent identifier
            prompt: User prompt
            context: Execution context
            
        Returns:
            Dictionary with:
                - score: float (0-100)
                - level: str (low, medium, high, critical)
                - factors: List[str] (what contributed to score)
                - recommendations: List[str] (suggested actions)
        """
        pass
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute risk scoring."""
        return self.calculate_risk_score(
            agent_id=context.get("agent_id", ""),
            prompt=context.get("prompt", ""),
            context=context
        )


class LifecycleHookPlugin(PolicyPlugin):
    """
    Plugin for agent lifecycle hooks.
    
    Hooks:
    - pre_request: Before request validation (earliest intervention point)
    - pre_execute: Before agent execution
    - post_decision: After policy decision is made
    - post_execute: After successful execution
    - on_error: On execution error
    - on_block: When request is blocked
    - on_escalate: When request is escalated
    - on_incident: When incident is triggered (security/compliance)
    """
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.LIFECYCLE_HOOK
    
    @property
    @abstractmethod
    def hook_stage(self) -> str:
        """
        Hook stage identifier.
        
        Available stages:
        - pre_request: Before request validation
        - pre_execute: Before agent execution
        - post_decision: After policy decision
        - post_execute: After successful execution
        - on_error: On execution error
        - on_block: When request blocked
        - on_escalate: When escalated for approval
        - on_incident: When incident triggered
        """
        pass
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute lifecycle hook."""
        stage = self.hook_stage
        
        if stage == "pre_request":
            return self.on_pre_request(context)
        elif stage == "pre_execute":
            return self.on_pre_execute(context)
        elif stage == "post_decision":
            return self.on_post_decision(context)
        elif stage == "post_execute":
            return self.on_post_execute(context)
        elif stage == "on_error":
            return self.on_error(context)
        elif stage == "on_block":
            return self.on_block(context)
        elif stage == "on_escalate":
            return self.on_escalate(context)
        elif stage == "on_incident":
            return self.on_incident(context)
        else:
            logger.warning(f"Unknown hook stage: {stage}")
            return {"status": "skipped"}
    
    def on_pre_request(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called before request validation.
        
        First interception point in the pipeline.
        Use for: request enrichment, early filtering, logging.
        
        Returns:
            - status: "continue" (proceed) or "abort" (stop execution)
            - context: Updated context (optional)
        """
        return {"status": "continue"}
    
    def on_pre_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Called before execution."""
        return {"status": "continue"}
    
    def on_post_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called after policy decision is made.
        
        Use for: logging decisions, triggering workflows, notifications.
        
        Context includes:
            - decision: Policy decision (allow/block/escalate)
            - reason: Decision reason
            - policies_evaluated: List of policies checked
        """
        return {"status": "continue"}
    
    def on_post_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Called after successful execution."""
        return {"status": "continue"}
    
    def on_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Called on execution error."""
        return {"status": "continue"}
    
    def on_block(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Called when request is blocked."""
        return {"status": "continue"}
    
    def on_escalate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Called when request is escalated."""
        return {"status": "continue"}
    
    def on_incident(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called when a security or compliance incident is triggered.
        
        Use for: alerting, incident response, forensics collection.
        
        Context includes:
            - incident_type: Type of incident (security/compliance/policy)
            - severity: Incident severity (low/medium/high/critical)
            - details: Incident details
            - agent_id: Affected agent
            - user: Affected user
        """
        return {"status": "continue"}


class ComplianceModulePlugin(PolicyPlugin):
    """
    Plugin for compliance modules.
    
    Example: GDPR, HIPAA, SOC2, PCI-DSS, custom industry standards.
    """
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.COMPLIANCE_MODULE
    
    @property
    @abstractmethod
    def compliance_standard(self) -> str:
        """Compliance standard name (e.g., 'GDPR', 'HIPAA')."""
        pass
    
    @abstractmethod
    def check_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check compliance requirements.
        
        Args:
            context: Execution context
            
        Returns:
            Dictionary with:
                - compliant: bool
                - violations: List[str]
                - requirements: List[str]
                - recommendations: List[str]
        """
        pass
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute compliance check."""
        return self.check_compliance(context)


class DataSanitizerPlugin(PolicyPlugin):
    """
    Plugin for data sanitization and redaction.
    
    Example use cases:
    - PII masking
    - Sensitive data redaction
    - Output filtering
    """
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.DATA_SANITIZER
    
    @abstractmethod
    def sanitize(self, data: str, context: Dict[str, Any]) -> str:
        """
        Sanitize data by redacting sensitive information.
        
        Args:
            data: Data to sanitize
            context: Execution context
            
        Returns:
            Sanitized data
        """
        pass
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sanitization."""
        data = context.get("data", "")
        sanitized = self.sanitize(data, context)
        return {"sanitized_data": sanitized}


class PolicyEvaluatorPlugin(PolicyPlugin):
    """
    Plugin for custom policy evaluation logic.
    
    Drop-in evaluators that can replace or augment the default policy engine.
    
    Example use cases:
    - Custom business logic
    - Integration with external policy systems
    - Industry-specific evaluation rules
    """
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.POLICY_EVALUATOR
    
    @abstractmethod
    def evaluate_policy(
        self,
        agent: Dict[str, Any],
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate custom policy.
        
        Args:
            agent: Agent configuration
            prompt: User prompt
            context: Execution context
            
        Returns:
            Dictionary with:
                - action: str (allow, block, escalate)
                - reason: str
                - score: Optional[float]
                - metadata: Optional[Dict]
        """
        pass
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute policy evaluation."""
        return self.evaluate_policy(
            agent=context.get("agent", {}),
            prompt=context.get("prompt", ""),
            context=context
        )


class RiskEnginePlugin(PolicyPlugin):
    """
    Plugin for external risk engines.
    
    Integrates external risk assessment systems and ML models.
    
    Example use cases:
    - Third-party risk APIs
    - ML-based risk models
    - Multi-factor risk scoring
    - Real-time threat intelligence
    """
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.RISK_ENGINE
    
    @abstractmethod
    def assess_risk(
        self,
        agent_id: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess risk using external engine.
        
        Args:
            agent_id: Agent identifier
            prompt: User prompt
            context: Execution context
            
        Returns:
            Dictionary with:
                - risk_score: float (0-100)
                - risk_level: str (low, medium, high, critical)
                - risk_factors: List[str]
                - threat_indicators: Optional[List[str]]
                - recommendations: List[str]
                - external_ref: Optional[str] (reference to external system)
        """
        pass
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute risk assessment."""
        return self.assess_risk(
            agent_id=context.get("agent_id", ""),
            prompt=context.get("prompt", ""),
            context=context
        )


class PluginRegistry:
    """
    Registry for managing plugins.
    
    This is the plugin ecosystem foundation.
    """
    
    def __init__(self):
        self._plugins: Dict[str, PolicyPlugin] = {}
        self._plugins_by_type: Dict[PluginType, List[PolicyPlugin]] = {
            ptype: [] for ptype in PluginType
        }
        logger.info("Plugin registry initialized")
    
    def register(self, plugin: PolicyPlugin):
        """
        Register a plugin.
        
        Args:
            plugin: Plugin to register
        """
        plugin_id = plugin.plugin_id
        
        if plugin_id in self._plugins:
            logger.warning(f"Plugin already registered: {plugin_id}")
            return
        
        self._plugins[plugin_id] = plugin
        self._plugins_by_type[plugin.plugin_type].append(plugin)
        
        logger.info(
            f"Registered plugin: {plugin_id} ({plugin.plugin_type.value}) "
            f"v{plugin.plugin_version}"
        )
    
    def unregister(self, plugin_id: str):
        """
        Unregister a plugin.
        
        Args:
            plugin_id: Plugin identifier
        """
        if plugin_id not in self._plugins:
            logger.warning(f"Plugin not found: {plugin_id}")
            return
        
        plugin = self._plugins[plugin_id]
        del self._plugins[plugin_id]
        self._plugins_by_type[plugin.plugin_type].remove(plugin)
        
        logger.info(f"Unregistered plugin: {plugin_id}")
    
    def get_plugin(self, plugin_id: str) -> Optional[PolicyPlugin]:
        """
        Get plugin by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin or None
        """
        return self._plugins.get(plugin_id)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PolicyPlugin]:
        """
        Get all plugins of a specific type.
        
        Args:
            plugin_type: Type of plugins to retrieve
            
        Returns:
            List of plugins
        """
        return self._plugins_by_type.get(plugin_type, []).copy()
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all registered plugins.
        
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
            for plugin in self._plugins.values()
        ]
    
    def execute_hooks(
        self,
        stage: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute all lifecycle hooks for a specific stage.
        
        Args:
            stage: Hook stage
            context: Execution context
            
        Returns:
            List of hook results
        """
        hooks = [
            p for p in self.get_plugins_by_type(PluginType.LIFECYCLE_HOOK)
            if hasattr(p, 'hook_stage') and p.hook_stage == stage
        ]
        
        results = []
        for hook in hooks:
            try:
                result = hook.execute(context)
                results.append({
                    "plugin_id": hook.plugin_id,
                    "status": "success",
                    "result": result,
                })
            except Exception as e:
                logger.error(f"Hook execution failed: {hook.plugin_id} - {e}")
                results.append({
                    "plugin_id": hook.plugin_id,
                    "status": "error",
                    "error": str(e),
                })
        
        return results


# Example plugin implementations

class ContentFilterPlugin(RiskScorerPlugin):
    """Example: Content-based risk scoring."""
    
    @property
    def plugin_id(self) -> str:
        return "content-filter-risk-scorer"
    
    @property
    def plugin_name(self) -> str:
        return "Content Filter Risk Scorer"
    
    @property
    def plugin_description(self) -> str:
        return "Scores risk based on prompt content patterns"
    
    def calculate_risk_score(
        self,
        agent_id: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate risk based on content."""
        score = 0.0
        factors = []
        
        # Check for high-risk keywords
        high_risk_keywords = ["delete", "transfer", "payment", "confidential"]
        for keyword in high_risk_keywords:
            if keyword in prompt.lower():
                score += 20
                factors.append(f"Contains high-risk keyword: {keyword}")
        
        # Check prompt length
        if len(prompt) > 1000:
            score += 10
            factors.append("Long prompt (potential data exfiltration)")
        
        # Determine level
        if score < 30:
            level = "low"
        elif score < 60:
            level = "medium"
        elif score < 80:
            level = "high"
        else:
            level = "critical"
        
        return {
            "score": min(score, 100),
            "level": level,
            "factors": factors,
            "recommendations": ["Review prompt content", "Enable audit logging"]
        }


class AuditLogHookPlugin(LifecycleHookPlugin):
    """Example: Additional audit logging hook."""
    
    @property
    def plugin_id(self) -> str:
        return "audit-log-hook"
    
    @property
    def plugin_name(self) -> str:
        return "Enhanced Audit Logger"
    
    @property
    def hook_stage(self) -> str:
        return "post_execute"
    
    @property
    def plugin_description(self) -> str:
        return "Adds detailed audit logging after execution"
    
    def on_post_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Log additional audit information."""
        logger.info(f"[AUDIT] Execution completed: {context.get('execution_id')}")
        return {"status": "continue", "logged": True}
