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
Demo: Run normal execution (allowed).

This shows a successful execution through the control plane.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk.python.client import ControlPlaneClient


def main():
    print("=" * 60)
    print("DEMO: Normal Execution (Allowed)")
    print("=" * 60)
    
    # Initialize client
    client = ControlPlaneClient(base_url="http://localhost:8000")
    
    # Execute request
    print("\n🚀 Executing request...")
    print("   Agent: customer-support-bot")
    print("   Prompt: 'What are your business hours?'")
    print("   User: alice@company.test")
    
    try:
        response = client.execute(
            agent_id="customer-support-bot",
            prompt="What are your business hours?",
            user="alice@company.test",
            context={"source": "web-chat"},
        )
        
        print(f"\n✅ Execution successful!")
        print(f"   Status: {response['status']}")
        print(f"   Execution ID: {response['execution_id']}")
        print(f"   Latency: {response['latency_ms']}ms")
        print(f"\n   Response: {response['response']}")
        
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        raise
    
    print("\n" + "=" * 60)
    print("✅ Execution complete")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
