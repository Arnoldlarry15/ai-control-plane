import { randomUUID } from "node:crypto";
import { AuditLogger } from "../audit/AuditLogger.js";
import { PolicyEngine } from "../policy/PolicyEngine.js";
import { TrustEngine } from "../trust/TrustEngine.js";
import type { AIProvider } from "../providers/AIProvider.js";
import type { ExecuteRequest, ExecutionBlocked, ExecutionSuccess } from "./types.js";
import { ProvenanceTracker, looksLikeCode } from "../provenance/tracker.js";
import type { CodeArtifact } from "../provenance/types.js";

export class ControlPlane {
  private readonly provider: AIProvider;
  private readonly audit: AuditLogger;
  private readonly policy: PolicyEngine;
  private readonly trust: TrustEngine;
  private readonly provenance: ProvenanceTracker;

  constructor(
    provider: AIProvider,
    audit = new AuditLogger(),
    policy?: PolicyEngine,
    trust?: TrustEngine,
    provenance?: ProvenanceTracker
  ) {
    this.provider = provider;
    this.audit = audit;
    this.policy = policy ?? new PolicyEngine();
    this.trust = trust ?? new TrustEngine();
    this.provenance = provenance ?? new ProvenanceTracker();
  }

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
      model: this.provider.name,
      provider: this.provider.type,
      promptHash,
      policyDecision: "allowed",
      riskScore: decision.riskScore
    });

    let provenance: CodeArtifact | undefined;

    if (looksLikeCode(response)) {
      provenance = this.provenance.trackAIOutput({
        code: response,
        language: "typescript",
        model: this.provider.name,
        provider: this.provider.type,
        prompt: req.prompt
      });

      this.audit.log({
        eventId: randomUUID(),
        agentId: req.agentId,
        orgId: req.orgId,
        action: "code_artifact_created",
        model: this.provider.name,
        provider: this.provider.type,
        promptHash,
        policyDecision: "allowed",
        riskScore: decision.riskScore
      });
    }

    const result: ExecutionSuccess = {
      status: "success",
      response
    };

    if (provenance) {
      result.provenance = provenance;
    }

    return result;
  }
}
