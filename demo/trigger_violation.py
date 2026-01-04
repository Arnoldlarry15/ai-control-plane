#!/usr/bin/env python3
"""
Demo: Trigger policy violation (blocked).

This shows how policies block prohibited content.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk.python.client import ControlPlaneClient
from sdk.python.exceptions import ExecutionBlockedError


def main():
    print("=" * 60)
    print("DEMO: Policy Violation (Blocked)")
    print("=" * 60)
    
    # Initialize client
    client = ControlPlaneClient(base_url="http://localhost:8000")
    
    # Execute request with PII
    print("\n🚨 Executing request with PII...")
    print("   Agent: customer-support-bot")
    print("   Prompt: 'My SSN is 123-45-6789 and I need help'")
    print("   User: bob@example.com")
    
    try:
        response = client.execute(
            agent_id="customer-support-bot",
            prompt="My SSN is 123-45-6789 and I need help",
            user="bob@example.com",
            context={"source": "web-chat"},
        )
        
        print(f"\n⚠️  Execution succeeded (unexpected!)")
        print(f"   This should have been blocked by policy!")
        
    except ExecutionBlockedError as e:
        print(f"\n❌ Execution blocked (as expected)")
        print(f"   Reason: {e.message}")
        print(f"   Details: {e.details}")
        print(f"\n   ✅ Policy enforcement working correctly!")
        print(f"   The AI model never saw this request.")
    
    print("\n" + "=" * 60)
    print("✅ Policy violation demo complete")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except ExecutionBlockedError:
        # Expected - exit successfully
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
