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
Reset environment by clearing all state.

WARNING: This clears all agents, logs, and state. Use with caution.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    print("=" * 60)
    print("Reset Environment")
    print("=" * 60)
    
    print("\n⚠️  WARNING: This will clear all state:")
    print("   • All registered agents")
    print("   • All audit logs")
    print("   • All approval queues")
    print("   • Kill switch state")
    
    response = input("\n   Continue? (yes/no): ")
    if response.lower() != "yes":
        print("\n❌ Reset cancelled")
        sys.exit(0)
    
    print("\n🔄 Resetting environment...")
    
    # Simply restart the gateway to reset in-memory state
    print("   In-memory state will be cleared on next gateway restart")
    print("   Run: python -m gateway.main")
    
    print("\n" + "=" * 60)
    print("✅ Environment reset instructions provided")
    print("=" * 60)
    print("\nTo reset, restart the gateway:")
    print("   1. Stop the current gateway (Ctrl+C)")
    print("   2. Start it again: python -m gateway.main")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Reset cancelled")
        sys.exit(1)
