/**
 * AI Control Plane TypeScript SDK
 * 
 * Enterprise-grade AI governance for JavaScript/TypeScript applications.
 * Drop-in replacement for direct LLM API calls with built-in governance.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

/**
 * Configuration options for the Control Plane client
 */
export interface ControlPlaneConfig {
  /** Base URL of the control plane gateway */
  baseURL?: string;
  /** API key for authentication */
  apiKey?: string;
  /** Request timeout in milliseconds */
  timeout?: number;
}

/**
 * Agent registration configuration
 */
export interface AgentConfig {
  /** Human-readable agent name */
  name: string;
  /** AI model identifier (e.g., gpt-4, claude-3) */
  model: string;
  /** Risk level: low, medium, high, critical */
  riskLevel?: string;
  /** List of policy IDs to apply */
  policies?: string[];
  /** Deployment environment */
  environment?: string;
  /** Additional metadata */
  metadata?: Record<string, any>;
}

/**
 * Agent information
 */
export interface Agent {
  agentId: string;
  name: string;
  model: string;
  riskLevel: string;
  policies: string[];
  environment: string;
  metadata: Record<string, any>;
  createdAt: string;
}

/**
 * Execution request
 */
export interface ExecutionRequest {
  /** Registered agent ID */
  agentId: string;
  /** User prompt/input */
  prompt: string;
  /** Execution context */
  context?: Record<string, any>;
  /** User identifier */
  user?: string;
}

/**
 * Execution response
 */
export interface ExecutionResponse {
  status: 'success' | 'blocked' | 'pending_approval';
  executionId: string;
  response?: string;
  reason?: string;
  approvalId?: string;
  metadata?: Record<string, any>;
}

/**
 * Audit log entry
 */
export interface AuditLog {
  executionId: string;
  agentId: string;
  user?: string;
  prompt: string;
  status: string;
  decision: string;
  timestamp: string;
  metadata: Record<string, any>;
}

/**
 * Kill switch configuration
 */
export interface KillSwitchConfig {
  /** Scope: global or agent */
  scope: 'global' | 'agent';
  /** Reason for activation */
  reason: string;
  /** Agent ID (required if scope is agent) */
  agentId?: string;
}

/**
 * Custom error for execution blocked
 */
export class ExecutionBlockedError extends Error {
  public readonly reason: string;
  public readonly details: any;

  constructor(reason: string, details?: any) {
    super(`Execution blocked: ${reason}`);
    this.name = 'ExecutionBlockedError';
    this.reason = reason;
    this.details = details;
  }
}

/**
 * Custom error for agent not found
 */
export class AgentNotFoundError extends Error {
  public readonly agentId: string;

  constructor(agentId: string) {
    super(`Agent not found: ${agentId}`);
    this.name = 'AgentNotFoundError';
    this.agentId = agentId;
  }
}

/**
 * Custom error for approval pending
 */
export class ApprovalPendingError extends Error {
  public readonly approvalId: string;
  public readonly reason: string;

  constructor(approvalId: string, reason: string) {
    super(`Approval pending: ${reason}`);
    this.name = 'ApprovalPendingError';
    this.approvalId = approvalId;
    this.reason = reason;
  }
}

/**
 * AI Control Plane Client
 * 
 * @example
 * ```typescript
 * const client = new ControlPlaneClient({
 *   baseURL: 'http://localhost:8000',
 *   apiKey: 'your-api-key'
 * });
 * 
 * // Register an agent
 * const agent = await client.registerAgent({
 *   name: 'my-assistant',
 *   model: 'gpt-4',
 *   policies: ['no-pii', 'business-hours']
 * });
 * 
 * // Execute through control plane
 * const response = await client.execute({
 *   agentId: agent.agentId,
 *   prompt: 'Hello, world!'
 * });
 * ```
 */
export class ControlPlaneClient {
  private client: AxiosInstance;

  /**
   * Create a new Control Plane client
   * 
   * @param config - Client configuration
   */
  constructor(config: ControlPlaneConfig = {}) {
    const {
      baseURL = 'http://localhost:8000',
      apiKey,
      timeout = 30000,
    } = config;

    this.client = axios.create({
      baseURL,
      timeout,
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey && { Authorization: `Bearer ${apiKey}` }),
      },
    });
  }

  /**
   * Register an AI agent with the control plane
   * 
   * @param config - Agent configuration
   * @returns Registered agent information
   */
  async registerAgent(config: AgentConfig): Promise<Agent> {
    const {
      name,
      model,
      riskLevel = 'medium',
      policies = [],
      environment = 'dev',
      metadata = {},
    } = config;

    const response = await this.client.post<Agent>('/api/agents', {
      name,
      model,
      risk_level: riskLevel,
      policies,
      environment,
      metadata,
    });

    return response.data;
  }

  /**
   * Execute an AI agent through the control plane
   * 
   * @param request - Execution request
   * @returns Execution response
   * @throws {ExecutionBlockedError} If execution is blocked
   * @throws {AgentNotFoundError} If agent is not found
   * @throws {ApprovalPendingError} If approval is required
   */
  async execute(request: ExecutionRequest): Promise<ExecutionResponse> {
    try {
      const response = await this.client.post<ExecutionResponse>('/api/execute', {
        agent_id: request.agentId,
        prompt: request.prompt,
        context: request.context || {},
        user: request.user,
      });

      const { status, reason, approvalId } = response.data;

      if (status === 'blocked') {
        throw new ExecutionBlockedError(reason || 'Unknown', response.data);
      }

      if (status === 'pending_approval') {
        throw new ApprovalPendingError(approvalId || '', reason || 'Unknown');
      }

      return response.data;
    } catch (error) {
      if (error instanceof ExecutionBlockedError || error instanceof ApprovalPendingError) {
        throw error;
      }

      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;
        if (axiosError.response?.status === 404) {
          throw new AgentNotFoundError(request.agentId);
        }
        if (axiosError.response?.status === 403) {
          const errorData = axiosError.response.data as any;
          throw new ExecutionBlockedError(
            errorData?.error || 'Forbidden',
            errorData?.details
          );
        }
      }

      throw error;
    }
  }

  /**
   * Get agent details
   * 
   * @param agentId - Agent identifier
   * @returns Agent information
   */
  async getAgent(agentId: string): Promise<Agent> {
    const response = await this.client.get<Agent>(`/api/agents/${agentId}`);
    return response.data;
  }

  /**
   * List all registered agents
   * 
   * @returns List of agents
   */
  async listAgents(): Promise<Agent[]> {
    const response = await this.client.get<{ agents: Agent[] }>('/api/agents');
    return response.data.agents;
  }

  /**
   * Activate kill switch
   * 
   * @param config - Kill switch configuration
   */
  async activateKillSwitch(config: KillSwitchConfig): Promise<void> {
    await this.client.post('/api/kill-switch/activate', {
      scope: config.scope,
      reason: config.reason,
      ...(config.agentId && { agent_id: config.agentId }),
    });
  }

  /**
   * Deactivate kill switch
   * 
   * @param scope - Kill switch scope
   * @param agentId - Agent ID (if scope is agent)
   */
  async deactivateKillSwitch(scope: 'global' | 'agent', agentId?: string): Promise<void> {
    await this.client.post('/api/kill-switch/deactivate', null, {
      params: {
        scope,
        ...(agentId && { agent_id: agentId }),
      },
    });
  }

  /**
   * Get kill switch status
   * 
   * @returns Kill switch status
   */
  async getKillSwitchStatus(): Promise<any> {
    const response = await this.client.get('/api/kill-switch/status');
    return response.data;
  }

  /**
   * Query audit logs
   * 
   * @param filters - Log filters
   * @returns List of audit logs
   */
  async getLogs(filters?: {
    user?: string;
    agentId?: string;
    status?: string;
    limit?: number;
  }): Promise<AuditLog[]> {
    const response = await this.client.get<AuditLog[]>('/api/logs', {
      params: {
        user: filters?.user,
        agent_id: filters?.agentId,
        status: filters?.status,
        limit: filters?.limit || 100,
      },
    });
    return response.data;
  }

  /**
   * Get detailed execution log
   * 
   * @param executionId - Execution identifier
   * @returns Execution log details
   */
  async getExecutionLog(executionId: string): Promise<AuditLog> {
    const response = await this.client.get<AuditLog>(`/api/logs/${executionId}`);
    return response.data;
  }

  /**
   * Check gateway health
   * 
   * @returns Health status
   */
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Export all types
export * from './types';
