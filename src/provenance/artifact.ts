import { randomUUID } from "node:crypto";
import { sha256, hashObjectSha256 } from "./hash.js";
import type { CodeArtifact } from "./types.js";
import allocateId from "./idAllocator.js";
import { signBuffer } from "./signature.js";
import { allocateIdentityId, isCanonicalIdentityId } from "../identity/identity.js";

export function createArtifact(params: {
  code?: string;
  language?: string;
  model?: string;
  provider?: string;
  prompt?: string;
  actorId?: string;
  parents?: string[];
  type?: string;
  canonicalId?: string;
  signerPrivateKeyPem?: string;
}): CodeArtifact {
  const now = new Date().toISOString();
  const artifactType = params.type ?? "ai_generated";
  const contentHash = params.code ? sha256(params.code) : sha256(artifactType + now + randomUUID());

  let artifactId = params.canonicalId;
  try {
    if (!artifactId) {
      // map some known types to canonical prefixes
      const t = artifactType.toLowerCase();
      if (t.includes("policy")) artifactId = allocateId("POL");
      else if (t.includes("trust")) artifactId = allocateId("TRUST");
      else if (t.includes("audit")) artifactId = allocateId("AUDIT");
      else if (t.includes("agent")) artifactId = allocateId("AGENT");
      else artifactId = allocateId("ART");
    }
  } catch {
    artifactId = `cps:${artifactType}:${new Date().getFullYear()}:${randomUUID().slice(0, 8)}`;
  }

  let actorId: string | undefined;
  let actorLabel: string | undefined;
  if (params.actorId) {
    if (isCanonicalIdentityId(params.actorId, "ai")) {
      actorId = params.actorId;
    } else {
      actorId = allocateIdentityId("ai");
      actorLabel = params.actorId;
    }
  } else if (params.model) {
    actorId = allocateIdentityId("ai");
    actorLabel = params.model;
  }

  const artifact: CodeArtifact = {
    artifactId: artifactId,
    type: artifactType,
    version: "1",
    content: {
      code: params.code,
      language: params.language,
      hash: contentHash
    },
    source: {
      model: params.model,
      provider: params.provider,
      promptHash: params.prompt ? sha256(params.prompt) : undefined
    },
    actor: actorId
      ? { type: "ai", id: actorId, name: actorLabel }
      : undefined,
    parents: params.parents,
    provenanceSources: [
      {
        type: "model-inference",
        provider: params.provider,
        model: params.model,
        promptHash: params.prompt ? sha256(params.prompt) : undefined
      }
    ],
    integrity: {
      hashAlgorithm: "sha256",
      hash: hashObjectSha256({ code: params.code, language: params.language })
    },
    metadata: {
      createdAt: now,
      createdBy: params.model ? "ai" : "human"
    }
  };

  // digital signature when a signer key is configured
  if (params.signerPrivateKeyPem) {
    try {
      const sig = signBuffer(params.signerPrivateKeyPem, artifact.integrity.hash);
      artifact.integrity.signature = sig;
      artifact.integrity.signedBy = actorId ?? "unknown";
    } catch {
      // ignore signature failures
    }
  }

  return artifact;
}