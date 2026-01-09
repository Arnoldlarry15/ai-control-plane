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
