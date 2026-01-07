# Plugin Development Guide

## Overview

The AI Control Plane plugin system enables third parties to extend governance capabilities without modifying core code. This is the foundation of the ecosystem lock-in strategy.

## Plugin Types

### 1. Policy Evaluator Plugins

Drop-in evaluators that can replace or augment the default policy engine.

```python
from policy.plugins import PolicyEvaluatorPlugin

class MyEvaluator(PolicyEvaluatorPlugin):
    @property
    def plugin_id(self) -> str:
        return "my-evaluator"
    
    @property
    def plugin_name(self) -> str:
        return "My Custom Evaluator"
    
    def evaluate_policy(self, agent, prompt, context):
        # Your custom logic
        return {
            "action": "allow",  # or "block", "escalate"
            "reason": "Evaluation reason",
            "score": 50
        }
```

**Use Cases:**
- Industry-specific compliance rules
- Custom business logic
- Integration with external policy systems

### 2. Risk Engine Plugins

External risk assessment systems and ML models.

```python
from policy.plugins import RiskEnginePlugin

class MyRiskEngine(RiskEnginePlugin):
    @property
    def plugin_id(self) -> str:
        return "my-risk-engine"
    
    @property
    def plugin_name(self) -> str:
        return "My Risk Engine"
    
    def assess_risk(self, agent_id, prompt, context):
        # Your risk assessment logic
        return {
            "risk_score": 75.0,
            "risk_level": "high",
            "risk_factors": ["Factor 1", "Factor 2"],
            "recommendations": ["Action 1"]
        }
```

**Use Cases:**
- Third-party risk APIs
- ML-based risk models
- Real-time threat intelligence
- Multi-factor risk scoring

### 3. Lifecycle Hook Plugins

Intercept and augment at any stage of the execution pipeline.

```python
from policy.plugins import LifecycleHookPlugin

class MyHook(LifecycleHookPlugin):
    @property
    def plugin_id(self) -> str:
        return "my-hook"
    
    @property
    def plugin_name(self) -> str:
        return "My Lifecycle Hook"
    
    @property
    def hook_stage(self) -> str:
        return "pre_request"  # or "post_decision", "on_incident", etc.
    
    def on_pre_request(self, context):
        # Executed before request validation
        return {"status": "continue"}
```

**Available Hooks:**
- `pre_request` - Before request validation
- `pre_execute` - Before agent execution
- `post_decision` - After policy decision
- `post_execute` - After successful execution
- `on_error` - On execution error
- `on_block` - When request blocked
- `on_escalate` - When escalated for approval
- `on_incident` - When incident triggered

**Use Cases:**
- Request enrichment
- Notification systems
- Incident response
- Audit trail enhancement

### 4. Risk Scorer Plugins

Custom risk scoring logic.

```python
from policy.plugins import RiskScorerPlugin

class MyScorer(RiskScorerPlugin):
    @property
    def plugin_id(self) -> str:
        return "my-scorer"
    
    @property
    def plugin_name(self) -> str:
        return "My Risk Scorer"
    
    def calculate_risk_score(self, agent_id, prompt, context):
        # Your scoring logic
        return {
            "score": 60.0,
            "level": "medium",
            "factors": ["Length", "Keywords"],
            "recommendations": []
        }
```

### 5. Compliance Module Plugins

Industry-specific compliance standards.

```python
from policy.plugins import ComplianceModulePlugin

class MyCompliance(ComplianceModulePlugin):
    @property
    def plugin_id(self) -> str:
        return "my-compliance"
    
    @property
    def plugin_name(self) -> str:
        return "My Compliance Standard"
    
    @property
    def compliance_standard(self) -> str:
        return "MY-STANDARD"
    
    def check_compliance(self, context):
        # Your compliance checks
        return {
            "compliant": True,
            "violations": [],
            "recommendations": []
        }
```

## Plugin Discovery and Loading

### Method 1: Directory-based Discovery

Place your plugin in a directory and load all plugins:

```python
from policy.plugin_loader import PluginLoader

loader = PluginLoader()
loaded_ids = loader.load_from_directory("/path/to/plugins")
```

### Method 2: Module-based Loading

Load plugins from a Python module:

```python
loader = PluginLoader()
loaded_ids = loader.load_from_module("my_plugins.risk_engine")
```

### Method 3: Direct Registration

Register plugin instances directly:

```python
from policy.plugin_loader import PluginLoader
from my_plugins import MyPlugin

loader = PluginLoader()
plugin = MyPlugin()
loader.register_plugin(plugin)
```

## Plugin Configuration

Plugins can validate their configuration:

```python
class MyPlugin(PolicyPlugin):
    def validate_config(self, config):
        # Validate required fields
        if "api_key" not in config:
            raise ValueError("api_key is required")
        
        if "endpoint" not in config:
            raise ValueError("endpoint is required")
        
        return True
```

## Best Practices

### 1. Fail-Closed Architecture

Always fail closed - if your plugin errors, return a blocking decision:

```python
def evaluate_policy(self, agent, prompt, context):
    try:
        # Your logic here
        pass
    except Exception as e:
        logger.error(f"Plugin error: {e}")
        return {
            "action": "block",
            "reason": "Plugin error - failing closed for safety"
        }
```

### 2. Performance

Keep plugin execution fast (<100ms):

```python
import time

def assess_risk(self, agent_id, prompt, context):
    start = time.time()
    
    # Your logic
    
    elapsed = time.time() - start
    if elapsed > 0.1:
        logger.warning(f"Plugin took {elapsed}s - optimize for performance")
```

### 3. Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

def execute(self, context):
    logger.info(
        f"[{self.plugin_id}] Executing",
        extra={
            "agent_id": context.get("agent_id"),
            "user": context.get("user")
        }
    )
```

### 4. Error Handling

Handle errors gracefully:

```python
def execute(self, context):
    try:
        # Your logic
        pass
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return {"status": "error", "message": "Internal error"}
```

### 5. Testing

Write comprehensive tests for your plugins:

```python
import pytest
from my_plugins import MyPlugin

def test_plugin_basic():
    plugin = MyPlugin()
    
    context = {
        "agent_id": "test-agent",
        "prompt": "test prompt",
        "user": "test@example.com"
    }
    
    result = plugin.execute(context)
    
    assert result["status"] == "success"
    assert "risk_score" in result
```

## Examples

See the `examples/plugins/` directory for complete examples:

- `risk_engine_example.py` - External risk engines
- `evaluator_example.py` - Custom policy evaluators
- `hooks_example.py` - Lifecycle hooks

## Plugin Distribution

### Publishing to PyPI

Package your plugin as a Python package:

```
my-control-plane-plugin/
├── setup.py
├── README.md
├── my_plugin/
│   ├── __init__.py
│   └── plugin.py
└── tests/
    └── test_plugin.py
```

```python
# setup.py
from setuptools import setup

setup(
    name="my-control-plane-plugin",
    version="1.0.0",
    description="My custom plugin for AI Control Plane",
    packages=["my_plugin"],
    install_requires=[
        "ai-control-plane>=1.0.0",
    ],
)
```

Install via pip:

```bash
pip install my-control-plane-plugin
```

### Plugin Marketplace (Future)

The AI Control Plane will support a plugin marketplace where developers can:
- Publish plugins
- Discover plugins
- Rate and review plugins
- Install with one command

## Security Considerations

### 1. Input Validation

Always validate inputs:

```python
def assess_risk(self, agent_id, prompt, context):
    if not agent_id:
        raise ValueError("agent_id is required")
    
    if not isinstance(prompt, str):
        raise TypeError("prompt must be a string")
```

### 2. Secrets Management

Never hardcode secrets:

```python
import os

class MyPlugin(PolicyPlugin):
    def __init__(self):
        self.api_key = os.getenv("MY_PLUGIN_API_KEY")
        if not self.api_key:
            raise ValueError("MY_PLUGIN_API_KEY not set")
```

### 3. Rate Limiting

Implement rate limiting for external API calls:

```python
from time import time

class MyPlugin(PolicyPlugin):
    def __init__(self):
        self.last_call = 0
        self.min_interval = 0.1  # 100ms
    
    def assess_risk(self, agent_id, prompt, context):
        now = time()
        if now - self.last_call < self.min_interval:
            raise Exception("Rate limit exceeded")
        
        self.last_call = now
        # Your logic
```

## Support

- **Documentation**: https://github.com/Arnoldlarry15/ai-control-plane/docs
- **Examples**: https://github.com/Arnoldlarry15/ai-control-plane/examples
- **Issues**: https://github.com/Arnoldlarry15/ai-control-plane/issues
- **Discussions**: https://github.com/Arnoldlarry15/ai-control-plane/discussions

## License

Plugins can use any license compatible with Apache 2.0.
