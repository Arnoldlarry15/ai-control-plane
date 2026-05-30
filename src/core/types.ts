export type AgentType = "llm" | "workflow" | "autonomous" | "tool";

export interface Agent {
  agentId: string;
  orgId: string;
  trustScore: number;
}

export interface PolicyDecision {
  allowed: boolean;
  reason: string;
  riskScore: number;
}

export interface AuditEvent {
  eventId: string;
  timestamp?: string;
  agentId: string;
  orgId: string;
  action: string;
  model?: string;
  promptHash: string;
  policyDecision: string;
  riskScore: number;
}

export interface ExecuteRequest {
  agentId: string;
  orgId: string;
  prompt: string;
}

export interface ExecutionBlocked {
  status: "blocked";
  reason: string;
}

export interface ExecutionSuccess {
  status: "success";
  response: string;
}
