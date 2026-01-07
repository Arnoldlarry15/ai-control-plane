#!/usr/bin/env python3
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
    print("   User: bob@company.test")
    
    try:
        response = client.execute(
            agent_id="customer-support-bot",
            prompt="My SSN is 123-45-6789 and I need help",
            user="bob@company.test",
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
