#!/usr/bin/env python3
"""
Seed demo data into the control plane.

Registers sample agents and policies for testing.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk.python.client import ControlPlaneClient


def seed_agents(client):
    """Seed sample agents."""
    agents = [
        {
            "name": "Customer Support Bot",
            "model": "gpt-3.5-turbo",
            "risk_level": "medium",
            "policies": ["no-pii"],
            "environment": "prod",
        },
        {
            "name": "Code Review Assistant",
            "model": "gpt-4",
            "risk_level": "low",
            "policies": ["allow-all"],
            "environment": "dev",
        },
        {
            "name": "Data Analysis Agent",
            "model": "gpt-4",
            "risk_level": "high",
            "policies": ["no-pii"],
            "environment": "prod",
        },
    ]
    
    print("Registering sample agents...")
    for agent_data in agents:
        try:
            agent = client.register_agent(**agent_data)
            print(f"  ✅ {agent['agent_id']}")
        except Exception as e:
            print(f"  ⚠️  {agent_data['name']}: {e}")


def main():
    print("=" * 60)
    print("Seeding Demo Data")
    print("=" * 60)
    
    client = ControlPlaneClient(base_url="http://localhost:8000")
    
    # Check gateway health
    try:
        health = client.health_check()
        print(f"\n✅ Gateway is healthy: {health['status']}")
    except Exception as e:
        print(f"\n❌ Gateway not available: {e}")
        print("   Make sure the gateway is running: python -m gateway.main")
        sys.exit(1)
    
    # Seed agents
    print("\n" + "-" * 60)
    seed_agents(client)
    
    # List all agents
    print("\n" + "-" * 60)
    print("Registered agents:")
    agents = client.list_agents()
    for agent in agents:
        print(f"  • {agent['id']} ({agent['model']}) - {agent['risk_level']}")
    
    print("\n" + "=" * 60)
    print("✅ Demo data seeded successfully")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
