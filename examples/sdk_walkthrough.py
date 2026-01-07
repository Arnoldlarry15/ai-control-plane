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
Complete SDK Walkthrough

End-to-end demonstration of AI Control Plane features.
Shows developers the full power of governed AI execution.

This is developer ergonomics at its finest:
"Safety for free, without slowing me down."
"""

import sys
import time
from datetime import datetime
from sdk.python.client import ControlPlaneClient
from sdk.python.exceptions import (
    ExecutionBlockedError,
    ApprovalPendingError,
    AgentNotFoundError,
)


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    """Complete SDK walkthrough"""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║          AI Control Plane - Complete SDK Walkthrough             ║
║                                                                  ║
║  This walkthrough demonstrates:                                  ║
║  1. Agent registration with governance                           ║
║  2. Safe execution with policy enforcement                       ║
║  3. Handling blocked requests gracefully                         ║
║  4. Approval workflows for high-risk operations                  ║
║  5. Audit trail queries and compliance                           ║
║  6. Kill switch emergency controls                               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    # Initialize client
    print_section("1. Initialize Control Plane Client")
    
    client = ControlPlaneClient(
        base_url="http://localhost:8000",
        timeout=30
    )
    
    try:
        health = client.health_check()
        print(f"✅ Gateway Status: {health.get('status', 'running')}")
        print(f"   Version: {health.get('version', 'unknown')}")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\n💡 Start the gateway with: python -m gateway.main")
        return
    
    # Register agents
    print_section("2. Register AI Agents")
    
    agents = {}
    
    # Low-risk agent for simple tasks
    print("\n📝 Registering low-risk agent...")
    try:
        agents['simple'] = client.register_agent(
            name="simple-assistant",
            model="gpt-3.5-turbo",
            risk_level="low",
            policies=["development"],
            environment="dev",
            metadata={"purpose": "simple queries"}
        )
        print(f"✅ Registered: {agents['simple']['agent_id']}")
        print(f"   Risk Level: {agents['simple']['risk_level']}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return
    
    # High-risk agent for sensitive operations
    print("\n📝 Registering high-risk agent...")
    try:
        agents['sensitive'] = client.register_agent(
            name="sensitive-data-handler",
            model="gpt-4",
            risk_level="high",
            policies=["safe_mode"],
            environment="production",
            metadata={"purpose": "sensitive data processing"}
        )
        print(f"✅ Registered: {agents['sensitive']['agent_id']}")
        print(f"   Risk Level: {agents['sensitive']['risk_level']}")
        print(f"   Policies: {', '.join(agents['sensitive']['policies'])}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return
    
    # Safe execution
    print_section("3. Execute Through Governance")
    
    print("\n🚀 Executing simple query...")
    try:
        result = client.execute(
            agent_id=agents['simple']['agent_id'],
            prompt="What is the capital of France?",
            user="demo@example.com",
            context={
                "purpose": "geography query",
                "session_id": "demo-session-001"
            }
        )
        
        print(f"✅ Execution successful!")
        print(f"   Execution ID: {result['execution_id']}")
        print(f"   Status: {result['status']}")
        if result.get('latency_ms'):
            print(f"   Latency: {result['latency_ms']}ms")
        
    except Exception as e:
        print(f"❌ Execution failed: {e}")
    
    # Demonstrate policy blocking
    print_section("4. Policy Enforcement in Action")
    
    print("\n🚫 Attempting to process PII (will be blocked)...")
    try:
        result = client.execute(
            agent_id=agents['sensitive']['agent_id'],
            prompt="Process this customer data: John Doe, SSN: 123-45-6789, Email: john@example.com",
            user="demo@example.com",
            context={"purpose": "data processing"}
        )
        print("⚠️  Execution was not blocked (unexpected)")
        
    except ExecutionBlockedError as e:
        print(f"✅ Policy blocked the request (as expected)")
        print(f"   Reason: {e.reason}")
        print(f"\n💡 This is governance working correctly:")
        print(f"   - PII was detected in the prompt")
        print(f"   - Safe mode policy blocked execution")
        print(f"   - No sensitive data was processed")
        print(f"   - Everything is logged for audit")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Demonstrate approval workflow
    print_section("5. Approval Workflows")
    
    print("\n⏸️  Attempting high-risk operation (requires approval)...")
    try:
        result = client.execute(
            agent_id=agents['sensitive']['agent_id'],
            prompt="Generate financial report for Q4",
            user="demo@example.com",
            context={
                "purpose": "financial analysis",
                "risk_level": "high",
                "estimated_cost": 150
            }
        )
        print("⚠️  Execution did not require approval (unexpected)")
        
    except ApprovalPendingError as e:
        print(f"✅ Approval required (as expected)")
        print(f"   Approval ID: {e.approval_id}")
        print(f"   Reason: {e.reason}")
        print(f"\n💡 This is human-in-the-loop governance:")
        print(f"   - High-risk operation detected")
        print(f"   - Request paused for human review")
        print(f"   - Decision will be stored permanently")
        print(f"   - Compliance requirements satisfied")
        
        # In a real scenario, you'd poll for approval
        print(f"\n📋 To check approval status:")
        print(f"   status = client.get_approval_status('{e.approval_id}')")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Query audit trail
    print_section("6. Audit Trail & Compliance")
    
    print("\n📋 Querying audit trail...")
    try:
        logs = client.get_logs(
            user="demo@example.com",
            limit=10
        )
        
        print(f"✅ Found {len(logs)} audit entries")
        
        if logs:
            print("\n   Recent executions:")
            for i, log in enumerate(logs[:3], 1):
                print(f"   {i}. ID: {log.get('execution_id', 'N/A')}")
                print(f"      Status: {log.get('status', 'N/A')}")
                print(f"      Agent: {log.get('agent_id', 'N/A')}")
                print(f"      Time: {log.get('timestamp', 'N/A')}")
        
        print(f"\n💡 Audit trail benefits:")
        print(f"   - Every AI decision is logged")
        print(f"   - Cryptographically verified integrity")
        print(f"   - Subpoena-ready exports available")
        print(f"   - Complete chain of custody")
        
    except Exception as e:
        print(f"❌ Failed to query logs: {e}")
    
    # Kill switch demonstration
    print_section("7. Emergency Kill Switch")
    
    print("\n🛑 Checking kill switch status...")
    try:
        status = client.get_kill_switch_status()
        print(f"✅ Kill Switch Status:")
        print(f"   Global: {status.get('global', {}).get('active', False)}")
        print(f"   Agent-specific: {len(status.get('agent_specific', {}))} active")
        
        print(f"\n💡 Kill switch is your 'oh shit' button:")
        print(f"   - Instant shutdown of all AI operations")
        print(f"   - Can be scoped to specific agents")
        print(f"   - All activation/deactivation logged")
        print(f"   - Emergency incident response")
        
        # Don't actually activate in demo
        print(f"\n   To activate: client.activate_kill_switch(")
        print(f"       scope='global',")
        print(f"       reason='Security incident detected'")
        print(f"   )")
        
    except Exception as e:
        print(f"❌ Failed to check kill switch: {e}")
    
    # List all agents
    print_section("8. Agent Registry")
    
    print("\n📋 Listing all registered agents...")
    try:
        all_agents = client.list_agents()
        print(f"✅ Total agents registered: {len(all_agents)}")
        
        if all_agents:
            print("\n   Registered agents:")
            for agent in all_agents[:5]:
                print(f"   • {agent.get('name', 'N/A')}")
                print(f"     ID: {agent.get('id', agent.get('agent_id', 'N/A'))}")
                print(f"     Model: {agent.get('model', 'N/A')}")
                print(f"     Risk: {agent.get('risk_level', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Failed to list agents: {e}")
    
    # Summary
    print_section("Summary: What You Just Learned")
    
    print("""
✅ Agent Registration
   - Quick and easy registration
   - Automatic risk assessment
   - Policy bundles (safe_mode, production, development)

✅ Policy Enforcement
   - Declarative, not code
   - Blocks dangerous operations automatically
   - Clear error messages with fix suggestions

✅ Approval Workflows
   - Human-in-the-loop for high-risk operations
   - Configurable escalation rules
   - Permanent decision records

✅ Audit Trail
   - Every action logged immutably
   - Cryptographic integrity
   - Compliance-ready exports

✅ Kill Switch
   - Emergency shutdown capability
   - Global or agent-scoped
   - Instant and reliable

✅ Developer Experience
   - Safety for free
   - Clear, actionable errors
   - Doesn't slow you down

═══════════════════════════════════════════════════════════════════

🎯 Next Steps:

1. Explore the Dashboard
   → http://localhost:8000/dashboard
   
2. Read the Docs
   → docs/GETTING_STARTED.md
   → docs/policy-spec.md
   → docs/compliance-guide.md

3. Integrate Your App
   → Use the SDK in your application
   → Configure policies for your use case
   → Set up compliance reporting

4. Join the Community
   → GitHub: github.com/Arnoldlarry15/ai-control-plane
   → Docs: docs.ai-control-plane.dev

═══════════════════════════════════════════════════════════════════

This is responsible AI governance, made easy.
This is how you build trustworthy systems.
This is the AI Control Plane.
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Walkthrough interrupted. Thanks for trying AI Control Plane!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
