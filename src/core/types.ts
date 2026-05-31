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
  provider?: string;
  promptHash: string;
  policyDecision: string;
  riskScore: number;
}

export type { CodeArtifact } from "../provenance/types.js";

export interface CodeArtifactAuditEvent {
  eventId: string;
  timestamp?: string;
  event_type: "code_generation" | "code_edit" | "code_merge";
  artifact_id: string;
  diff_hash: string;
  actor: {
    type: "human" | "agent";
    id: string;
  };
  model: string;
  provider: string;
  prompt_hash: string;
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
  provenance?: import("../provenance/types.js").CodeArtifact;
}
