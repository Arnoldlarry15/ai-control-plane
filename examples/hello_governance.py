"""
Hello Governance - The Canonical Example

This is the "hello world" for AI Control Plane.
Shows developers how governance can feel like safety for free.

Run this to see:
1. Agent registration
2. Policy-governed execution
3. Audit trail preservation
4. Clear error messages

This is the experience that makes developers say:
"This tool makes me look responsible without slowing me down."
"""

import sys
from sdk.python.client import ControlPlaneClient
from sdk.python.exceptions import ExecutionBlockedError, ApprovalPendingError

def main():
    """
    The canonical hello governance example.
    End-to-end in under 50 lines.
    """
    print("=" * 70)
    print("AI Control Plane - Hello Governance")
    print("The simplest path to responsible AI")
    print("=" * 70)
    print()
    
    # Step 1: Connect to the control plane
    print("📡 Connecting to AI Control Plane...")
    client = ControlPlaneClient(base_url="http://localhost:8000")
    
    try:
        health = client.health_check()
        print(f"✅ Connected - Gateway is {health.get('status', 'running')}")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\n💡 Tip: Make sure the gateway is running:")
        print("   python -m gateway.main")
        sys.exit(1)
    
    print()
    
    # Step 2: Register your AI agent
    print("🤖 Registering AI agent...")
    try:
        agent = client.register_agent(
            name="hello-bot",
            model="gpt-3.5-turbo",
            risk_level="low",
            policies=["standard"],  # Apply standard governance policies
        )
        print(f"✅ Agent registered: {agent['agent_id']}")
        print(f"   Risk Level: {agent['risk_level']}")
        print(f"   Policies: {', '.join(agent['policies']) if agent['policies'] else 'default'}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        sys.exit(1)
    
    print()
    
    # Step 3: Execute through governance
    print("🚀 Executing AI request with governance...")
    try:
        result = client.execute(
            agent_id=agent['agent_id'],
            prompt="What is 2+2?",
            user="demo@example.com",
            context={"purpose": "hello-world-demo"}
        )
        
        print(f"✅ Execution successful!")
        print(f"   Execution ID: {result['execution_id']}")
        print(f"   Status: {result['status']}")
        if result.get('response'):
            print(f"   Response: {result['response']}")
        if result.get('latency_ms'):
            print(f"   Latency: {result['latency_ms']}ms")
        
    except ExecutionBlockedError as e:
        print(f"🚫 Execution blocked by policy")
        print(f"   Reason: {e.reason}")
        print(f"   Details: {e.details}")
        print()
        print("💡 This is governance working as intended.")
        print("   The policy prevented something that shouldn't happen.")
        
    except ApprovalPendingError as e:
        print(f"⏸️  Execution requires approval")
        print(f"   Approval ID: {e.approval_id}")
        print(f"   Reason: {e.reason}")
        print()
        print("💡 High-risk operations need human review.")
        print("   This is compliance working for you, not against you.")
    
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        sys.exit(1)
    
    print()
    
    # Step 4: Query audit trail
    print("📋 Checking audit trail...")
    try:
        logs = client.get_logs(user="demo@example.com", limit=5)
        print(f"✅ Found {len(logs)} audit entries for this user")
        
        if logs:
            latest = logs[0]
            print(f"   Latest execution: {latest.get('execution_id', 'N/A')}")
            print(f"   Timestamp: {latest.get('timestamp', 'N/A')}")
            print(f"   Status: {latest.get('status', 'N/A')}")
    except Exception as e:
        print(f"⚠️  Could not query logs: {e}")
    
    print()
    print("=" * 70)
    print("🎉 Success! Your first governed AI execution is complete.")
    print()
    print("What just happened:")
    print("  1. Agent registered with automatic risk assessment")
    print("  2. Request evaluated against policies")
    print("  3. Execution logged with full audit trail")
    print("  4. All evidence preserved forever")
    print()
    print("Next steps:")
    print("  • Try examples/sdk_walkthrough.py for more features")
    print("  • Read docs/GETTING_STARTED.md for deep dive")
    print("  • Explore dashboard at http://localhost:8000/dashboard")
    print("=" * 70)


if __name__ == "__main__":
    main()
