"""
Developer-Friendly Error Messages

Clear failure messages that teach users what went wrong.

This is Phase 5: Developer Ergonomics
"This tool makes me look responsible without slowing me down."
"""

from typing import Dict, Any, Optional, List


class ErrorMessageFormatter:
    """
    Format error messages to be helpful, not cryptic.
    
    Good error messages:
    1. Explain what happened
    2. Explain why it happened
    3. Suggest how to fix it
    4. Provide relevant documentation links
    """
    
    @staticmethod
    def format_execution_blocked(
        reason: str,
        policy_id: Optional[str] = None,
        violated_rules: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format execution blocked error with actionable guidance.
        
        Args:
            reason: Why execution was blocked
            policy_id: Policy that blocked execution
            violated_rules: Specific rules violated
            context: Additional context
        
        Returns:
            Formatted error message
        """
        message = {
            "error": "Execution Blocked",
            "reason": reason,
            "what_happened": "Your AI request was blocked by a governance policy.",
            "why_it_happened": "",
            "how_to_fix": [],
            "policy_details": {},
            "docs": "https://docs.ai-control-plane.dev/errors/execution-blocked",
        }
        
        # Customize based on reason
        if "pii" in reason.lower():
            message["why_it_happened"] = (
                "The request contains personally identifiable information (PII) "
                "which is not allowed by your current policy configuration."
            )
            message["how_to_fix"] = [
                "Remove PII from your prompt (emails, SSNs, phone numbers, etc.)",
                "Use anonymized or synthetic test data",
                "Request a policy exception from your administrator",
                "Use a lower-risk environment (e.g., development instead of production)",
            ]
            message["examples"] = {
                "bad": "Process user data: john@example.com, SSN 123-45-6789",
                "good": "Process user data: [USER_EMAIL], [USER_ID]"
            }
        
        elif "risk" in reason.lower():
            message["why_it_happened"] = (
                "Your request was classified as high-risk and requires human approval "
                "before execution."
            )
            message["how_to_fix"] = [
                "Wait for approval from an authorized reviewer",
                "Check approval status with the approval_id provided",
                "Consider using a lower-risk model or configuration",
                "Review your agent's risk_level setting",
            ]
        
        elif "cost" in reason.lower():
            message["why_it_happened"] = (
                "The estimated cost of this operation exceeds your configured threshold."
            )
            message["how_to_fix"] = [
                "Reduce the scope of your request",
                "Use a more cost-effective model",
                "Request a higher cost threshold from your administrator",
                "Break the request into smaller chunks",
            ]
        
        elif "rate" in reason.lower():
            message["why_it_happened"] = (
                "You have exceeded the rate limit for AI requests."
            )
            message["how_to_fix"] = [
                "Wait before making more requests",
                "Implement exponential backoff in your code",
                "Request a higher rate limit from your administrator",
                "Use batch processing for multiple requests",
            ]
            message["code_example"] = """
# Implement retry with exponential backoff
import time

def execute_with_retry(client, agent_id, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.execute(agent_id=agent_id, prompt=prompt)
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
"""
        
        else:
            message["why_it_happened"] = reason
            message["how_to_fix"] = [
                "Review the policy details below",
                "Contact your administrator for guidance",
                "Check the documentation for this error",
            ]
        
        # Add policy details if available
        if policy_id:
            message["policy_details"]["policy_id"] = policy_id
        
        if violated_rules:
            message["policy_details"]["violated_rules"] = violated_rules
        
        if context:
            message["context"] = context
        
        return message
    
    @staticmethod
    def format_approval_pending(
        approval_id: str,
        reason: str,
        workflow: Optional[str] = None,
        estimated_wait_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Format approval pending message with clear next steps.
        
        Args:
            approval_id: Approval request ID
            reason: Why approval is needed
            workflow: Workflow type
            estimated_wait_time: Estimated wait time in seconds
        
        Returns:
            Formatted message
        """
        message = {
            "status": "Pending Approval",
            "approval_id": approval_id,
            "reason": reason,
            "what_happened": "Your request requires human approval before execution.",
            "why_approval_needed": reason,
            "what_to_do": [
                f"Your approval ID is: {approval_id}",
                "A reviewer will evaluate your request shortly",
                "You can check status with: client.get_approval_status(approval_id)",
                "You will be notified when a decision is made",
            ],
            "code_example": f"""
# Check approval status
status = client.get_approval_status("{approval_id}")
print(f"Status: {{status['status']}}")

# Poll for completion
import time

while True:
    status = client.get_approval_status("{approval_id}")
    if status['status'] in ['approved', 'rejected']:
        break
    time.sleep(30)  # Check every 30 seconds

if status['status'] == 'approved':
    # Re-execute your request
    result = client.execute(agent_id=agent_id, prompt=prompt)
""",
            "docs": "https://docs.ai-control-plane.dev/approval-workflows",
        }
        
        if estimated_wait_time:
            minutes = estimated_wait_time // 60
            message["estimated_wait_time"] = f"{minutes} minutes"
            message["what_to_do"].append(
                f"Typical approval time: ~{minutes} minutes"
            )
        
        if workflow:
            message["workflow"] = workflow
        
        return message
    
    @staticmethod
    def format_agent_not_found(agent_id: str) -> Dict[str, Any]:
        """
        Format agent not found error with registration guidance.
        
        Args:
            agent_id: Agent ID that was not found
        
        Returns:
            Formatted error message
        """
        return {
            "error": "Agent Not Found",
            "agent_id": agent_id,
            "what_happened": f"No agent registered with ID: {agent_id}",
            "why_it_happened": (
                "You're trying to execute an agent that doesn't exist in the registry. "
                "This usually means you haven't registered your agent yet, or you're "
                "using the wrong agent_id."
            ),
            "how_to_fix": [
                "Register your agent first using client.register_agent()",
                "Double-check the agent_id you're using",
                "List all registered agents with client.list_agents()",
            ],
            "code_example": """
# Register your agent first
agent = client.register_agent(
    name="my-agent",
    model="gpt-3.5-turbo",
    risk_level="medium",
    policies=["standard"]
)

# Then use the returned agent_id
result = client.execute(
    agent_id=agent['agent_id'],  # Use this ID
    prompt="Hello, world!"
)

# Or list existing agents
agents = client.list_agents()
for agent in agents:
    print(f"Agent: {agent['name']} - ID: {agent['agent_id']}")
""",
            "docs": "https://docs.ai-control-plane.dev/agent-registration",
        }
    
    @staticmethod
    def format_kill_switch_active(
        scope: str,
        reason: str,
        activated_at: str
    ) -> Dict[str, Any]:
        """
        Format kill switch active error.
        
        Args:
            scope: Kill switch scope (global or agent)
            reason: Why it was activated
            activated_at: When it was activated
        
        Returns:
            Formatted error message
        """
        return {
            "error": "Kill Switch Active",
            "scope": scope,
            "what_happened": f"The {scope} kill switch is currently active. All executions are blocked.",
            "why_it_happened": f"Kill switch was activated: {reason}",
            "activated_at": activated_at,
            "what_to_do": [
                "Contact your system administrator immediately",
                "Do not attempt to bypass the kill switch",
                "Wait for the kill switch to be deactivated",
                "Review the incident that triggered activation",
            ],
            "severity": "CRITICAL",
            "docs": "https://docs.ai-control-plane.dev/kill-switch",
        }
    
    @staticmethod
    def format_policy_violation(
        policy_id: str,
        policy_name: str,
        violation_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format policy violation error with policy details.
        
        Args:
            policy_id: Policy identifier
            policy_name: Human-readable policy name
            violation_details: Details of violation
        
        Returns:
            Formatted error message
        """
        return {
            "error": "Policy Violation",
            "policy_id": policy_id,
            "policy_name": policy_name,
            "what_happened": f"Your request violated the '{policy_name}' policy.",
            "violation_details": violation_details,
            "how_to_fix": [
                "Review the policy requirements",
                "Modify your request to comply with the policy",
                "Contact your administrator if you need a policy exception",
                "Consider using a different environment with less strict policies",
            ],
            "docs": f"https://docs.ai-control-plane.dev/policies/{policy_id}",
        }
    
    @staticmethod
    def format_configuration_error(
        error_type: str,
        details: str,
        field: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format configuration error with fix suggestions.
        
        Args:
            error_type: Type of configuration error
            details: Error details
            field: Field that has configuration error
        
        Returns:
            Formatted error message
        """
        message = {
            "error": "Configuration Error",
            "error_type": error_type,
            "what_happened": details,
            "how_to_fix": [],
        }
        
        if field:
            message["field"] = field
        
        # Add specific guidance based on error type
        if "risk_level" in error_type.lower():
            message["how_to_fix"] = [
                "Use one of: 'low', 'medium', 'high', 'critical'",
                "Choose based on your use case:",
                "  - low: Simple queries, no sensitive data",
                "  - medium: Standard operations",
                "  - high: Sensitive data or critical decisions",
                "  - critical: Financial, healthcare, or life-safety",
            ]
        
        elif "model" in error_type.lower():
            message["how_to_fix"] = [
                "Specify a valid AI model (e.g., 'gpt-4', 'claude-3', 'gpt-3.5-turbo')",
                "Check with your organization which models are approved",
            ]
        
        elif "policy" in error_type.lower():
            message["how_to_fix"] = [
                "Verify the policy ID exists",
                "List available policies with: client.list_policies()",
                "Use pre-configured bundles: 'safe_mode', 'production', 'development'",
            ]
        
        return message


def format_helpful_error(
    error_type: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Format any error in a developer-friendly way.
    
    This is the main entry point for error formatting.
    
    Args:
        error_type: Type of error
        **kwargs: Error-specific parameters
    
    Returns:
        Formatted error message
    
    Example:
        >>> error = format_helpful_error(
        ...     "execution_blocked",
        ...     reason="PII detected in prompt",
        ...     policy_id="pii-protection"
        ... )
        >>> print(error['how_to_fix'])
        ['Remove PII from your prompt...', ...]
    """
    formatter = ErrorMessageFormatter()
    
    if error_type == "execution_blocked":
        return formatter.format_execution_blocked(**kwargs)
    elif error_type == "approval_pending":
        return formatter.format_approval_pending(**kwargs)
    elif error_type == "agent_not_found":
        return formatter.format_agent_not_found(**kwargs)
    elif error_type == "kill_switch_active":
        return formatter.format_kill_switch_active(**kwargs)
    elif error_type == "policy_violation":
        return formatter.format_policy_violation(**kwargs)
    elif error_type == "configuration_error":
        return formatter.format_configuration_error(**kwargs)
    else:
        return {
            "error": error_type,
            "details": kwargs,
            "docs": "https://docs.ai-control-plane.dev/errors",
        }
