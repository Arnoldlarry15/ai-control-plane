import { randomUUID } from "node:crypto";
import { sha256 } from "./hash.js";
import type { CodeArtifact } from "./types.js";

export function createArtifact(params: {
  code: string;
  language: string;
  model?: string;
  provider?: string;
  prompt?: string;
}): CodeArtifact {
  return {
    artifactId: randomUUID(),
    type: "ai_generated",
    content: {
      code: params.code,
      language: params.language,
      hash: sha256(params.code)
    },
    source: {
      model: params.model,
      provider: params.provider,
      promptHash: params.prompt ? sha256(params.prompt) : undefined
    },
    lineage: {},
    metadata: {
      createdAt: new Date().toISOString(),
      createdBy: "ai"
    }
  };
}