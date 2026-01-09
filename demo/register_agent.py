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
Demo: Register an AI agent.

This shows how to register an agent in the control plane.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk.python.client import ControlPlaneClient


def main():
    print("=" * 60)
    print("DEMO: Register AI Agent")
    print("=" * 60)
    
    # Initialize client
    client = ControlPlaneClient(base_url="http://localhost:8000")
    
    # Register agent
    print("\n📝 Registering agent: customer-support-bot")
    
    agent = client.register_agent(
        name="Customer Support Bot",
        model="gpt-3.5-turbo",
        risk_level="medium",
        policies=["no-pii"],
        environment="prod",
        metadata={
            "description": "Customer support chatbot",
            "owner": "support-team",
        },
    )
    
    print(f"\n✅ Agent registered successfully!")
    print(f"   Agent ID: {agent['agent_id']}")
    print(f"   Risk Level: {agent['risk_level']}")
    print(f"   Policies: {', '.join(agent['policies'])}")
    
    print("\n" + "=" * 60)
    print("✅ Registration complete")
    print("=" * 60)
    
    return agent


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
