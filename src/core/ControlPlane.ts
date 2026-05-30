import { randomUUID } from "node:crypto";
import { AuditLogger } from "../audit/AuditLogger.js";
import { PolicyEngine } from "../policy/PolicyEngine.js";
import { TrustEngine } from "../trust/TrustEngine.js";
import type { AIProvider } from "../providers/AIProvider.js";
import type { ExecuteRequest, ExecutionBlocked, ExecutionSuccess } from "./types.js";

export class ControlPlane {
  constructor(
    private readonly provider: AIProvider,
    private readonly audit = new AuditLogger(),
    private readonly policy = new PolicyEngine(),
    private readonly trust = new TrustEngine()
  ) {}

  async execute(req: ExecuteRequest): Promise<ExecutionBlocked | ExecutionSuccess> {
    const trustScore = this.trust.getTrust(req.agentId);
    const decision = this.policy.evaluate(trustScore, req.prompt);
    const promptHash = this.audit.hashPrompt(req.prompt);

    this.audit.log({
      eventId: randomUUID(),
      agentId: req.agentId,
      orgId: req.orgId,
      action: "pre_execution",
      promptHash,
      policyDecision: decision.reason,
      riskScore: decision.riskScore
    });

    if (!decision.allowed) {
      return {
        status: "blocked",
        reason: decision.reason
      };
    }

    const response = await this.provider.run(req.prompt);

    this.audit.log({
      eventId: randomUUID(),
      agentId: req.agentId,
      orgId: req.orgId,
      action: "ai_call",
      model: "mock-model-v0",
      promptHash,
      policyDecision: "allowed",
      riskScore: decision.riskScore
    });

    return {
      status: "success",
      response
    };
  }
}
