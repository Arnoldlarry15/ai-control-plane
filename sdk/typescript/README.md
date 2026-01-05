# AI Control Plane TypeScript SDK

Enterprise-grade AI governance for JavaScript/TypeScript applications.

## Installation

```bash
npm install @ai-control-plane/sdk
# or
yarn add @ai-control-plane/sdk
```

## Quick Start

```typescript
import { ControlPlaneClient } from '@ai-control-plane/sdk';

// Initialize client
const client = new ControlPlaneClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your-api-key' // optional
});

// Register an AI agent
const agent = await client.registerAgent({
  name: 'my-assistant',
  model: 'gpt-4',
  riskLevel: 'medium',
  policies: ['no-pii', 'business-hours']
});

// Execute through control plane
const response = await client.execute({
  agentId: agent.agentId,
  prompt: 'Analyze this customer data...',
  context: { user: 'alice@company.com' }
});

console.log(response.response);
```

## Features

- **Full TypeScript Support** - Complete type definitions
- **Promise-based API** - Modern async/await patterns
- **Error Handling** - Structured error types
- **Governance Built-in** - Policy enforcement, audit trails
- **Drop-in Replacement** - Easy migration from direct LLM calls

## API Reference

### Constructor

```typescript
new ControlPlaneClient(config?: ControlPlaneConfig)
```

**Config Options:**
- `baseURL?: string` - Control plane gateway URL (default: `http://localhost:8000`)
- `apiKey?: string` - API key for authentication
- `timeout?: number` - Request timeout in milliseconds (default: `30000`)

### Methods

#### `registerAgent(config: AgentConfig): Promise<Agent>`

Register an AI agent with the control plane.

```typescript
const agent = await client.registerAgent({
  name: 'customer-support-bot',
  model: 'gpt-3.5-turbo',
  riskLevel: 'low',
  policies: ['no-pii'],
  environment: 'production',
  metadata: { team: 'support' }
});
```

#### `execute(request: ExecutionRequest): Promise<ExecutionResponse>`

Execute an AI agent through the control plane.

```typescript
try {
  const response = await client.execute({
    agentId: agent.agentId,
    prompt: 'Hello, world!',
    context: { sessionId: '123' },
    user: 'user@example.com'
  });
  
  console.log('Response:', response.response);
} catch (error) {
  if (error instanceof ExecutionBlockedError) {
    console.error('Blocked:', error.reason);
  }
}
```

#### `getAgent(agentId: string): Promise<Agent>`

Get agent details.

```typescript
const agent = await client.getAgent('agent-123');
```

#### `listAgents(): Promise<Agent[]>`

List all registered agents.

```typescript
const agents = await client.listAgents();
```

#### `activateKillSwitch(config: KillSwitchConfig): Promise<void>`

Activate emergency kill switch.

```typescript
await client.activateKillSwitch({
  scope: 'global',
  reason: 'Security incident detected'
});
```

#### `deactivateKillSwitch(scope, agentId?): Promise<void>`

Deactivate kill switch.

```typescript
await client.deactivateKillSwitch('global');
```

#### `getLogs(filters?): Promise<AuditLog[]>`

Query audit logs.

```typescript
const logs = await client.getLogs({
  user: 'alice@company.com',
  limit: 50
});
```

#### `getExecutionLog(executionId: string): Promise<AuditLog>`

Get detailed execution log.

```typescript
const log = await client.getExecutionLog('exec-123');
```

#### `healthCheck(): Promise<any>`

Check gateway health.

```typescript
const health = await client.healthCheck();
```

## Error Handling

The SDK provides structured error types:

```typescript
import {
  ExecutionBlockedError,
  AgentNotFoundError,
  ApprovalPendingError
} from '@ai-control-plane/sdk';

try {
  await client.execute({ agentId, prompt });
} catch (error) {
  if (error instanceof ExecutionBlockedError) {
    // Handle blocked execution
    console.error('Blocked:', error.reason, error.details);
  } else if (error instanceof AgentNotFoundError) {
    // Handle missing agent
    console.error('Agent not found:', error.agentId);
  } else if (error instanceof ApprovalPendingError) {
    // Handle approval required
    console.log('Approval ID:', error.approvalId);
  }
}
```

## TypeScript Types

All types are fully documented and exported:

```typescript
import type {
  ControlPlaneConfig,
  AgentConfig,
  Agent,
  ExecutionRequest,
  ExecutionResponse,
  AuditLog,
  KillSwitchConfig
} from '@ai-control-plane/sdk';
```

## License

MIT
