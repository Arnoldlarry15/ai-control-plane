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
AI Control Plane CLI

Command-line interface for AI governance operations.
"""

import os
import sys
import json
import argparse
from typing import Optional, Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk.python.client import ControlPlaneClient
from sdk.python.exceptions import (
    ControlPlaneException,
    ExecutionBlockedError,
    AgentNotFoundError,
    ApprovalPendingError,
)


class CLI:
    """Command-line interface for AI Control Plane."""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize CLI."""
        # Get from environment if not provided
        self.base_url = base_url or os.getenv("CONTROL_PLANE_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("CONTROL_PLANE_API_KEY")
        
        self.client = ControlPlaneClient(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    def register_agent(self, args):
        """Register a new agent."""
        try:
            # Parse metadata if provided
            metadata = {}
            if args.metadata:
                for item in args.metadata:
                    key, value = item.split("=", 1)
                    metadata[key] = value
            
            # Parse policies
            policies = args.policies.split(",") if args.policies else []
            
            agent = self.client.register_agent(
                name=args.name,
                model=args.model,
                risk_level=args.risk_level,
                policies=policies,
                environment=args.environment,
                metadata=metadata
            )
            
            print(f"✓ Agent registered successfully")
            print(f"  Agent ID: {agent['agent_id']}")
            print(f"  Name: {agent['name']}")
            print(f"  Model: {agent['model']}")
            print(f"  Risk Level: {agent['risk_level']}")
            
            if args.json:
                print("\nJSON:")
                print(json.dumps(agent, indent=2))
        
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def execute(self, args):
        """Execute an agent."""
        try:
            # Parse context if provided
            context = {}
            if args.context:
                for item in args.context:
                    key, value = item.split("=", 1)
                    context[key] = value
            
            # Get prompt from file or argument
            if args.prompt_file:
                with open(args.prompt_file, 'r') as f:
                    prompt = f.read()
            else:
                prompt = args.prompt
            
            response = self.client.execute(
                agent_id=args.agent_id,
                prompt=prompt,
                context=context,
                user=args.user
            )
            
            print(f"✓ Execution successful")
            print(f"  Execution ID: {response['execution_id']}")
            print(f"  Status: {response['status']}")
            
            if args.json:
                print("\nJSON:")
                print(json.dumps(response, indent=2))
            elif 'response' in response:
                print(f"\nResponse:\n{response['response']}")
        
        except ExecutionBlockedError as e:
            print(f"✗ Execution blocked: {e.reason}", file=sys.stderr)
            if args.json:
                print(json.dumps(e.details, indent=2), file=sys.stderr)
            sys.exit(2)
        
        except ApprovalPendingError as e:
            print(f"⏳ Approval required: {e.reason}")
            print(f"  Approval ID: {e.approval_id}")
            sys.exit(3)
        
        except AgentNotFoundError as e:
            print(f"✗ Agent not found: {e.agent_id}", file=sys.stderr)
            sys.exit(1)
        
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def list_agents(self, args):
        """List all agents."""
        try:
            agents = self.client.list_agents()
            
            if args.json:
                print(json.dumps(agents, indent=2))
            else:
                print(f"Total agents: {len(agents)}\n")
                for agent in agents:
                    print(f"• {agent['name']} ({agent['agent_id']})")
                    print(f"  Model: {agent['model']}")
                    print(f"  Risk: {agent['risk_level']}")
                    print(f"  Policies: {', '.join(agent['policies']) or 'none'}")
                    print()
        
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_agent(self, args):
        """Get agent details."""
        try:
            agent = self.client.get_agent(args.agent_id)
            
            if args.json:
                print(json.dumps(agent, indent=2))
            else:
                print(f"Agent: {agent['name']}")
                print(f"  ID: {agent['agent_id']}")
                print(f"  Model: {agent['model']}")
                print(f"  Risk Level: {agent['risk_level']}")
                print(f"  Environment: {agent['environment']}")
                print(f"  Policies: {', '.join(agent['policies']) or 'none'}")
                print(f"  Created: {agent.get('created_at', 'N/A')}")
        
        except AgentNotFoundError as e:
            print(f"✗ Agent not found: {e.agent_id}", file=sys.stderr)
            sys.exit(1)
        
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def get_logs(self, args):
        """Query audit logs."""
        try:
            logs = self.client.get_logs(
                user=args.user,
                agent_id=args.agent_id,
                status=args.status,
                limit=args.limit
            )
            
            if args.json:
                print(json.dumps(logs, indent=2))
            else:
                print(f"Total logs: {len(logs)}\n")
                for log in logs:
                    print(f"• Execution: {log['execution_id']}")
                    print(f"  Agent: {log.get('agent_id', 'N/A')}")
                    print(f"  User: {log.get('user', 'N/A')}")
                    print(f"  Status: {log['status']}")
                    print(f"  Time: {log.get('timestamp', 'N/A')}")
                    print()
        
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def kill_switch(self, args):
        """Manage kill switch."""
        try:
            if args.action == "activate":
                self.client.activate_kill_switch(
                    scope=args.scope,
                    reason=args.reason or "Manual activation via CLI",
                    agent_id=args.agent_id
                )
                print(f"✓ Kill switch activated ({args.scope})")
            
            elif args.action == "deactivate":
                self.client.deactivate_kill_switch(
                    scope=args.scope,
                    agent_id=args.agent_id
                )
                print(f"✓ Kill switch deactivated ({args.scope})")
            
            elif args.action == "status":
                status = self.client.get_kill_switch_status()
                if args.json:
                    print(json.dumps(status, indent=2))
                else:
                    print(f"Kill Switch Status:")
                    print(f"  Global: {'ACTIVE' if status.get('global_active') else 'INACTIVE'}")
                    print(f"  Agent-specific: {len(status.get('agent_switches', []))} active")
        
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def health(self, args):
        """Check gateway health."""
        try:
            health = self.client.health_check()
            
            if args.json:
                print(json.dumps(health, indent=2))
            else:
                status = health.get("status", "unknown")
                print(f"Gateway Status: {status}")
                
                if status == "healthy":
                    print("✓ Control plane is operational")
                else:
                    print("✗ Control plane may have issues")
        
        except Exception as e:
            print(f"✗ Gateway unreachable: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Control Plane CLI - Enterprise AI Governance",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--url",
        help="Control plane URL (default: $CONTROL_PLANE_URL or http://localhost:8000)"
    )
    parser.add_argument(
        "--api-key",
        help="API key (default: $CONTROL_PLANE_API_KEY)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Register agent
    register_parser = subparsers.add_parser("register", help="Register a new agent")
    register_parser.add_argument("name", help="Agent name")
    register_parser.add_argument("model", help="AI model (e.g., gpt-4)")
    register_parser.add_argument("--risk-level", default="medium", 
                                 choices=["low", "medium", "high", "critical"])
    register_parser.add_argument("--policies", help="Comma-separated policy IDs")
    register_parser.add_argument("--environment", default="dev", help="Environment")
    register_parser.add_argument("--metadata", action="append", 
                                 help="Metadata (key=value)")
    register_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Execute agent
    execute_parser = subparsers.add_parser("execute", help="Execute an agent")
    execute_parser.add_argument("agent_id", help="Agent ID")
    execute_parser.add_argument("--prompt", help="Prompt text")
    execute_parser.add_argument("--prompt-file", help="Read prompt from file")
    execute_parser.add_argument("--context", action="append", help="Context (key=value)")
    execute_parser.add_argument("--user", help="User identifier")
    execute_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # List agents
    list_parser = subparsers.add_parser("list", help="List all agents")
    list_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Get agent
    get_parser = subparsers.add_parser("get", help="Get agent details")
    get_parser.add_argument("agent_id", help="Agent ID")
    get_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Query logs
    logs_parser = subparsers.add_parser("logs", help="Query audit logs")
    logs_parser.add_argument("--user", help="Filter by user")
    logs_parser.add_argument("--agent-id", help="Filter by agent")
    logs_parser.add_argument("--status", help="Filter by status")
    logs_parser.add_argument("--limit", type=int, default=100, help="Result limit")
    logs_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Kill switch
    kill_parser = subparsers.add_parser("kill-switch", help="Manage kill switch")
    kill_parser.add_argument("action", choices=["activate", "deactivate", "status"])
    kill_parser.add_argument("--scope", default="global", choices=["global", "agent"])
    kill_parser.add_argument("--agent-id", help="Agent ID (for agent scope)")
    kill_parser.add_argument("--reason", help="Reason for activation")
    kill_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Health check
    health_parser = subparsers.add_parser("health", help="Check gateway health")
    health_parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize CLI
    cli = CLI(base_url=args.url, api_key=args.api_key)
    
    # Route to command handler
    if args.command == "register":
        cli.register_agent(args)
    elif args.command == "execute":
        if not args.prompt and not args.prompt_file:
            print("Error: Either --prompt or --prompt-file is required", file=sys.stderr)
            sys.exit(1)
        cli.execute(args)
    elif args.command == "list":
        cli.list_agents(args)
    elif args.command == "get":
        cli.get_agent(args)
    elif args.command == "logs":
        cli.get_logs(args)
    elif args.command == "kill-switch":
        cli.kill_switch(args)
    elif args.command == "health":
        cli.health(args)


if __name__ == "__main__":
    main()
