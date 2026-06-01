import { isCanonicalIdentityId } from "./identity.js";
import type { IdentityRecord } from "./types.js";

export interface IdentityValidationResult {
  ok: boolean;
  checks: Record<string, { ok: boolean; message?: string }>;
}

export function validateIdentity(identity: IdentityRecord): IdentityValidationResult {
  const checks: Record<string, { ok: boolean; message?: string }> = {
    schema: { ok: true },
    id: { ok: true },
    credentials: { ok: true }
  };

  if (!identity.id || !identity.type || !identity.createdAt) {
    checks.schema = { ok: false, message: "missing required identity fields" };
  }

  if (!isCanonicalIdentityId(identity.id, identity.type)) {
    checks.id = { ok: false, message: `invalid canonical id for type ${identity.type}` };
  }

  if (identity.credentials?.did && !identity.credentials.did.startsWith("did:")) {
    checks.credentials = { ok: false, message: "did must start with did:" };
  }

  const ok = Object.values(checks).every((c) => c.ok);
  return { ok, checks };
}
