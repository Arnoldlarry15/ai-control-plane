import { execFileSync } from "node:child_process";
import type { ProvenanceStore } from "./store.js";
import { hashObjectSha256 } from "./hash.js";
import { verifyBuffer } from "./signature.js";
import { isCanonicalIdentityId } from "../identity/identity.js";
import type { IdentityStore } from "../identity/store.js";

export interface ValidationResult {
  ok: boolean;
  checks: Record<string, { ok: boolean; message?: string }>;
}

export async function validateArtifact(
  id: string,
  store: ProvenanceStore,
  options?: { identityStore?: IdentityStore }
): Promise<ValidationResult> {
  const checks: Record<string, { ok: boolean; message?: string }> = {};

  const artifact = store.getByArtifactId(id as any);
  if (!artifact) {
    return { ok: false, checks: { found: { ok: false, message: "artifact not found" } } };
  }

  // schema checks
  checks.schema = { ok: true };
  if (!artifact.artifactId) checks.schema = { ok: false, message: "missing artifactId" };
  if (!artifact.integrity || !artifact.integrity.hash || !artifact.integrity.hashAlgorithm)
    checks.schema = { ok: false, message: "missing integrity fields" };
  if (!artifact.metadata || !artifact.metadata.createdAt)
    checks.schema = { ok: false, message: "missing metadata.createdAt" };

  // actor identity checks
  if (!artifact.actor || !artifact.actor.id || !artifact.actor.type) {
    checks.actor = { ok: false, message: "missing actor identity" };
  } else {
    const canonical = isCanonicalIdentityId(artifact.actor.id, artifact.actor.type);
    if (!canonical) {
      checks.actor = { ok: false, message: "actor id is not canonical" };
    } else if (options?.identityStore) {
      const found = options.identityStore.getById(artifact.actor.id);
      if (!found) {
        checks.actor = { ok: false, message: "actor identity not found in identity store" };
      } else if (found.type !== artifact.actor.type) {
        checks.actor = {
          ok: false,
          message: `actor type mismatch expected=${found.type} actual=${artifact.actor.type}`
        };
      } else {
        checks.actor = { ok: true };
      }
    } else {
      checks.actor = { ok: true };
    }
  }

  // integrity
  try {
    const expected = hashObjectSha256({ code: artifact.content?.code, language: artifact.content?.language });
    if (expected === artifact.integrity.hash) {
      checks.integrity = { ok: true };
    } else {
      checks.integrity = { ok: false, message: `hash_mismatch expected=${expected} actual=${artifact.integrity.hash}` };
    }
  } catch (err: any) {
    checks.integrity = { ok: false, message: `integrity_error ${String(err)}` };
  }

  // parents
  if (artifact.parents && artifact.parents.length > 0) {
    const missing: string[] = [];
    for (const p of artifact.parents) {
      if (!store.getByArtifactId(p as any)) missing.push(p);
    }
    if (missing.length === 0) checks.parents = { ok: true };
    else checks.parents = { ok: false, message: `missing_parents ${missing.join(",")}` };
  } else {
    checks.parents = { ok: true, message: "no parents" };
  }

  // signature
  if (artifact.integrity?.signature) {
    const sig = artifact.integrity.signature;
    // look for public key in actor.credentials
    const pub = artifact.actor?.credentials as string | undefined;
    if (!pub) {
      checks.signature = { ok: false, message: "missing public key for signature verification" };
    } else {
      try {
        const verified = verifyBuffer(pub, artifact.integrity.hash, sig);
        checks.signature = { ok: !!verified };
        if (!verified) checks.signature.message = "signature_verification_failed";
      } catch (err: any) {
        checks.signature = { ok: false, message: `signature_error ${String(err)}` };
      }
    }
  } else {
    checks.signature = { ok: true, message: "unsigned" };
  }

  // git provenance verification
  const gitSource = artifact.provenanceSources?.find((s: any) => s.type === "git");
  if (gitSource) {
    const repoRoot = gitSource.repositoryRoot as string | undefined;
    const commit = gitSource.commit as string | undefined;
    if (!repoRoot || !commit) {
      checks.git = { ok: false, message: "git provenance missing repositoryRoot or commit" };
    } else {
      try {
        // verify commit exists
        execFileSync("git", ["cat-file", "-t", commit], { cwd: repoRoot, stdio: ["ignore", "ignore", "ignore"] });
        checks.git = { ok: true };
      } catch (err: any) {
        checks.git = { ok: false, message: `git_commit_missing ${String(err)}` };
      }
    }
  } else {
    checks.git = { ok: true, message: "no git provenance" };
  }

  const ok = Object.values(checks).every((c) => c.ok === true);
  return { ok, checks };
}

export default validateArtifact;
