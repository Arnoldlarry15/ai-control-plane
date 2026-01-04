#!/usr/bin/env python3
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
