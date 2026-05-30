import type { PolicyDecision } from "../core/types.js";

export class PolicyEngine {
  evaluate(trustScore: number, prompt: string): PolicyDecision {
    let riskScore = 0.2;

    if (prompt.toLowerCase().includes("password")) {
      riskScore = 0.95;
    }

    if (trustScore < 0.5) {
      return { allowed: false, reason: "low_trust", riskScore };
    }

    if (riskScore > 0.8) {
      return { allowed: false, reason: "high_risk_prompt", riskScore };
    }

    return { allowed: true, reason: "allowed", riskScore };
  }
}
