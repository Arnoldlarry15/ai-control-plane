import allocateId from "../provenance/idAllocator.js";
import type { IdentityRecord, IdentityType } from "./types.js";

function prefixFor(type: IdentityType): "HUMAN" | "AI" | "AGENT" | "ORG" {
  if (type === "human") return "HUMAN";
  if (type === "ai") return "AI";
  if (type === "agent") return "AGENT";
  return "ORG";
}

export function allocateIdentityId(type: IdentityType): string {
  return allocateId(prefixFor(type));
}

export function isCanonicalIdentityId(id: string, type?: IdentityType): boolean {
  const pattern = /^(HUMAN|AI|AGENT|ORG)-\d{4}-\d{6}$/;
  if (!pattern.test(id)) {
    return false;
  }
  if (!type) {
    return true;
  }
  const expected = prefixFor(type);
  return id.startsWith(`${expected}-`);
}

export function createIdentity(params: {
  type: IdentityType;
  label?: string;
  orgId?: string;
  credentials?: IdentityRecord["credentials"];
  trustAnchors?: string[];
  metadata?: Record<string, any>;
  id?: string;
}): IdentityRecord {
  const id = params.id ?? allocateIdentityId(params.type);

  return {
    id,
    type: params.type,
    label: params.label,
    orgId: params.orgId,
    credentials: params.credentials,
    trustAnchors: params.trustAnchors,
    createdAt: new Date().toISOString(),
    metadata: params.metadata
  };
}
