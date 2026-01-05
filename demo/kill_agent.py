#!/usr/bin/env python3
"""
Demo: Activate kill switch.

This shows the emergency shutdown capability.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk.python.client import ControlPlaneClient
from sdk.python.exceptions import ExecutionBlockedError


def main():
    print("=" * 60)
    print("DEMO: Kill Switch")
    print("=" * 60)
    
    # Initialize client
    client = ControlPlaneClient(base_url="http://localhost:8000")
    
    # Step 1: Normal execution (should work)
    print("\n📍 Step 1: Execute before kill switch")
    try:
        response = client.execute(
            agent_id="customer-support-bot",
            prompt="Hello, world!",
            user="test@company.test",
        )
        print(f"   ✅ Execution successful (ID: {response['execution_id']})")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Step 2: Activate kill switch
    print("\n🛑 Step 2: Activate kill switch (GLOBAL)")
    result = client.activate_kill_switch(
        scope="global",
        reason="Emergency maintenance - demo",
    )
    print(f"   ✅ Kill switch activated")
    print(f"   Scope: {result['scope']}")
    print(f"   Reason: {result['reason']}")
    
    # Step 3: Try to execute (should be blocked)
    print("\n🚫 Step 3: Try to execute with kill switch active")
    try:
        response = client.execute(
            agent_id="customer-support-bot",
            prompt="Hello, world!",
            user="test@company.test",
        )
        print(f"   ⚠️  Execution succeeded (unexpected!)")
    except ExecutionBlockedError as e:
        print(f"   ✅ Execution blocked (as expected)")
        print(f"   Reason: {e.message}")
    
    # Step 4: Deactivate kill switch
    print("\n✅ Step 4: Deactivate kill switch")
    result = client.deactivate_kill_switch(scope="global")
    print(f"   ✅ Kill switch deactivated")
    
    # Step 5: Execute again (should work)
    print("\n📍 Step 5: Execute after deactivation")
    try:
        response = client.execute(
            agent_id="customer-support-bot",
            prompt="Hello, world!",
            user="test@company.test",
        )
        print(f"   ✅ Execution successful (ID: {response['execution_id']})")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Kill switch demo complete")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
