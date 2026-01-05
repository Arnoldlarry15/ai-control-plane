"""
Populate test data for Phase 3 dashboard demonstration.

This script creates realistic sample data to showcase:
- Live AI traffic metrics
- Policy hits (blocked vs allowed)
- High-risk activity alerts
- Decision replay functionality
- Org-wide AI map
- Usage trends
"""

import time
import uuid
import random
from datetime import datetime

# Import services
from gateway.services import get_observability_logger
from observability.logger import ObservabilityLogger


def populate_sample_data():
    """Populate observability storage with realistic sample data."""
    
    print("Populating test data for Phase 3 dashboard...")
    
    obs_logger = get_observability_logger()
    
    if not obs_logger:
        print("Error: Observability logger not available")
        return
    
    # Sample users (representing different teams)
    users = [
        "alice@engineering.company.com",
        "bob@marketing.company.com", 
        "charlie@sales.company.com",
        "diana@support.company.com",
        "eve@executive.company.com",
    ]
    
    # Sample agents (representing different models)
    agents = [
        "gpt-4-customer-support",
        "claude-3-code-assistant",
        "gpt-3.5-marketing-writer",
        "gemini-pro-analyst",
        "llama-2-chatbot",
    ]
    
    # Sample prompts
    prompts = [
        "Help me write a customer email response",
        "Generate a marketing campaign idea",
        "Analyze this sales data",
        "Write code to implement a feature",
        "Summarize this document",
        "Create a social media post",
        "Debug this error message",
        "Translate this text",
    ]
    
    # Generate varied execution events
    num_events = 50
    
    for i in range(num_events):
        execution_id = str(uuid.uuid4())
        agent_id = random.choice(agents)
        user = random.choice(users)
        prompt = random.choice(prompts)
        
        # Vary the status to create interesting patterns
        # Most should be successful, some blocked, few escalated
        rand = random.random()
        if rand < 0.75:
            status = "success"
            response = "AI response generated successfully"
            reason = None
            policy_id = None
        elif rand < 0.90:
            status = "blocked"
            response = None
            reason = "PII detected in prompt"
            policy_id = "no-pii-policy"
        else:
            status = "escalated"
            response = None
            reason = "High-risk operation requires approval"
            policy_id = "high-risk-approval"
        
        # Vary latencies
        latency_ms = random.randint(50, 500)
        
        # Log the execution
        obs_logger.log_execution(
            execution_id=execution_id,
            agent_id=agent_id,
            prompt=prompt,
            response=response,
            status=status,
            latency_ms=latency_ms,
            user=user,
            context={"team": user.split("@")[1].split(".")[0]},
            reason=reason,
            policy_id=policy_id,
        )
        
        # Log policy events for blocked/escalated requests
        if status in ["blocked", "escalated"]:
            obs_logger.log_policy_event(
                execution_id=execution_id,
                policy_id=policy_id,
                action=status,
                agent_id=agent_id,
                reason=reason,
                user=user,
            )
        
        # Small delay to vary timestamps
        time.sleep(0.01)
    
    # Add some high-risk events
    for i in range(3):
        execution_id = str(uuid.uuid4())
        obs_logger.log_execution(
            execution_id=execution_id,
            agent_id="gpt-4-admin-assistant",
            prompt="Execute privileged system command",
            response=None,
            status="blocked",
            latency_ms=100,
            user="eve@executive.company.com",
            context={"risk_level": "critical"},
            reason="Privileged operation blocked by security policy",
            policy_id="privilege-escalation-prevention",
        )
        
        obs_logger.log_policy_event(
            execution_id=execution_id,
            policy_id="privilege-escalation-prevention",
            action="blocked",
            agent_id="gpt-4-admin-assistant",
            reason="Privileged operation blocked by security policy",
            user="eve@executive.company.com",
        )
    
    # Add a kill switch event for high-risk alert
    obs_logger.log_kill_switch_event(
        action="activated",
        scope="agent",
        agent_id="gpt-4-admin-assistant",
        reason="Multiple suspicious requests detected",
        activated_by="security-system",
    )
    
    print(f"✅ Successfully populated {num_events + 3} execution events")
    print(f"✅ Added {len([1 for _ in range(num_events) if random.random() > 0.75])} policy violation events")
    print(f"✅ Added 3 high-risk security events")
    print(f"✅ Added 1 kill switch event")
    print("\nTest data ready! Visit http://127.0.0.1:8000/dashboard to see the results")


if __name__ == "__main__":
    populate_sample_data()
