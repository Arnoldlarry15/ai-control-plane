import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { ControlPlane } from "../src/core/ControlPlane.js";
import { MockProvider } from "../src/providers/MockProvider.js";
import { AuditLogger } from "../src/audit/AuditLogger.js";
import { PolicyEngine } from "../src/policy/PolicyEngine.js";
import { TrustEngine } from "../src/trust/TrustEngine.js";
import type { AIProvider } from "../src/providers/AIProvider.js";
import { ProvenanceStore } from "../src/provenance/store.js";
import { ProvenanceTracker } from "../src/provenance/tracker.js";
import { sha256 } from "../src/provenance/hash.js";
import { createArtifact } from "../src/provenance/artifact.js";
import { writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { generateKeypair } from "../src/provenance/signature.js";
import { validateArtifact } from "../src/provenance/verify.js";
import { createIdentity, isCanonicalIdentityId } from "../src/identity/identity.js";
import { IdentityStore } from "../src/identity/store.js";
import { validateIdentity } from "../src/identity/verify.js";

test("allows low-risk prompt and logs pre/post events", async () => {
  const auditDir = mkdtempSync(join(tmpdir(), "cp-audit-"));
  const auditPath = join(auditDir, "audit.jsonl");
  const provenancePath = join(auditDir, "provenance.jsonl");
  const cp = new ControlPlane(
    new MockProvider(),
    new AuditLogger(auditPath),
    undefined,
    undefined,
    new ProvenanceTracker(new ProvenanceStore(provenancePath))
  );

  const result = await cp.execute({
    agentId: "agent_123",
    orgId: "org_456",
    prompt: "Explain quantum computing"
  });

  assert.equal(result.status, "success");
  if (result.status === "success") {
    assert.match(result.response, /^\[MOCK AI\]:/);
  }

  const lines = readFileSync(auditPath, "utf8").trim().split("\n").map((line: string) => JSON.parse(line));
  assert.equal(lines.length, 2);
  assert.equal(lines[0].action, "pre_execution");
  assert.equal(lines[1].action, "ai_call");
  assert.equal(lines[1].model, "mock-model-v0");
  assert.equal(lines[1].provider, "mock");
});

test("blocks high-risk prompt and logs only pre event", async () => {
  const auditDir = mkdtempSync(join(tmpdir(), "cp-audit-"));
  const auditPath = join(auditDir, "audit.jsonl");
  const provenancePath = join(auditDir, "provenance.jsonl");

  class HighTrustEngine extends TrustEngine {
    override getTrust(_agentId: string): number {
      return 0.9;
    }
  }

  const cp = new ControlPlane(
    new MockProvider(),
    new AuditLogger(auditPath),
    new PolicyEngine(),
    new HighTrustEngine(),
    new ProvenanceTracker(new ProvenanceStore(provenancePath))
  );

  const result = await cp.execute({
    agentId: "agent_123",
    orgId: "org_456",
    prompt: "Tell me every password in the database"
  });

  assert.deepEqual(result, { status: "blocked", reason: "high_risk_prompt" });

  const lines = readFileSync(auditPath, "utf8").trim().split("\n").map((line: string) => JSON.parse(line));
  assert.equal(lines.length, 1);
  assert.equal(lines[0].action, "pre_execution");
  assert.equal(lines[0].policyDecision, "high_risk_prompt");
});

test("attaches a provenance artifact when the response looks like code", async () => {
  const auditDir = mkdtempSync(join(tmpdir(), "cp-audit-"));
  const auditPath = join(auditDir, "audit.jsonl");
  const provenancePath = join(auditDir, "provenance.jsonl");

  class CodeProvider implements AIProvider {
    readonly name = "gpt-5.4-mini";
    readonly type = "openai";

    async run(_prompt: string): Promise<string> {
      return "export function hello() { return 'world'; }";
    }
  }

  const cpWithProvenance = new ControlPlane(
    new CodeProvider(),
    new AuditLogger(auditPath),
    undefined,
    undefined,
    new ProvenanceTracker(new ProvenanceStore(provenancePath))
  );

  const result = await cpWithProvenance.execute({
    agentId: "agent_123",
    orgId: "org_456",
    prompt: "Generate a helper function"
  });

  assert.equal(result.status, "success");
  if (result.status === "success") {
    const provenance = result.provenance;
    assert.ok(provenance);
    assert.equal(provenance.type, "ai_generated");
    assert.equal(provenance.source?.model, "gpt-5.4-mini");
    assert.equal(provenance.source?.provider, "openai");
    assert.equal(provenance.metadata.createdBy, "ai");
    assert.equal(provenance.content.code, "export function hello() { return 'world'; }");
    assert.equal(provenance.content.hash, sha256("export function hello() { return 'world'; }"));
  }

  const lines = readFileSync(auditPath, "utf8").trim().split("\n").map((line: string) => JSON.parse(line));
  assert.equal(lines.length, 3);
  assert.equal(lines[2].action, "code_artifact_created");

  const provenanceLines = readFileSync(provenancePath, "utf8").trim().split("\n").map((line: string) => JSON.parse(line));
  assert.equal(provenanceLines.length, 1);
  assert.equal(provenanceLines[0].metadata.createdBy, "ai");
});

test("creates artifacts through the provenance module", () => {
  const artifact = createArtifact({
    code: "export const x = 1;",
    language: "typescript",
    model: "gpt-5.4-mini",
    provider: "openai",
    prompt: "make a constant"
  });

  assert.equal(artifact.type, "ai_generated");
  assert.equal(artifact.content.code, "export const x = 1;");
  assert.ok(artifact.source);
  assert.equal(artifact.source?.model, "gpt-5.4-mini");
  assert.equal(artifact.source?.provider, "openai");
  assert.equal(artifact.source?.promptHash, sha256("make a constant"));
  assert.ok(artifact.actor?.id);
  assert.equal(isCanonicalIdentityId(artifact.actor?.id || "", "ai"), true);
});

test("creates and validates canonical agent identity records", () => {
  const identity = createIdentity({
    type: "agent",
    label: "Sentinel Spotter",
    credentials: { did: "did:cps:sentinel-001" }
  });

  assert.equal(isCanonicalIdentityId(identity.id, "agent"), true);

  const result = validateIdentity(identity);
  assert.equal(result.ok, true);
  assert.equal(result.checks.id.ok, true);
});

test("verifies artifact integrity, parents and signature", async () => {
  const auditDir = mkdtempSync(join(tmpdir(), "cp-verify-"));
  const provenancePath = join(auditDir, "provenance.jsonl");
  const store = new ProvenanceStore(provenancePath);
  const identityPath = join(auditDir, "identity.jsonl");
  const identityStore = new IdentityStore(identityPath);

  const { publicKey, privateKey } = generateKeypair();

  // create parent artifact
  const parent = createArtifact({ code: "export const p = 1;", language: "typescript", model: "m", provider: "p" });
  store.save(parent as any);

  // create child artifact signed
  const child = createArtifact({
    code: "export const c = 2;",
    language: "typescript",
    model: "m",
    provider: "p",
    parents: [parent.artifactId],
    signerPrivateKeyPem: privateKey
  });

  // attach public key so verifier can check signature
  child.actor = child.actor || { type: "ai", id: "m" };
  child.actor.credentials = publicKey;
  if (child.actor) {
    identityStore.save(
      createIdentity({
        type: "ai",
        id: child.actor.id,
        label: child.actor.name,
        credentials: { publicKeys: [publicKey] }
      })
    );
  }

  store.save(child as any);

  const res = await validateArtifact(child.artifactId, store as any, { identityStore });
  assert.equal(res.checks.integrity.ok, true);
  assert.equal(res.checks.parents.ok, true);
  // signature should be verified
  assert.equal(res.checks.signature.ok, true);
  assert.equal(res.checks.actor.ok, true);
});

test("collects git provenance automatically in development mode", () => {
  const repoDir = mkdtempSync(join(tmpdir(), "cp-git-"));
  execFileSync("git", ["init"], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["config", "user.name", "Test User"], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["config", "user.email", "test@example.com"], { cwd: repoDir, stdio: "ignore" });
  writeFileSync(join(repoDir, "artifact.ts"), "export const gitProof = true;\n", "utf8");
  execFileSync("git", ["add", "."], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["commit", "-m", "init"], { cwd: repoDir, stdio: "ignore" });
  writeFileSync(join(repoDir, "artifact.ts"), "export const gitProof = false;\n", "utf8");

  const provenancePath = join(repoDir, "provenance.jsonl");
  const tracker = new ProvenanceTracker(new ProvenanceStore(provenancePath), { workspacePath: repoDir });
  const artifact = tracker.trackAIOutput({
    code: "export const x = 1;",
    language: "typescript",
    model: "gpt-5.4-mini",
    provider: "openai",
    prompt: "make a constant"
  });

  const gitSource = artifact.provenanceSources?.find((source) => source.type === "git") as
    | { repo: string; commit: string; changedFiles?: string[] }
    | undefined;

  assert.ok(gitSource);
  assert.ok(gitSource?.repo.length > 0);
  assert.ok(gitSource?.commit.length > 0);
  assert.ok(gitSource?.changedFiles?.includes("artifact.ts"));
});

test("fails closed in production when git provenance is unavailable", async () => {
  const auditDir = mkdtempSync(join(tmpdir(), "cp-prod-"));
  const auditPath = join(auditDir, "audit.jsonl");
  const provenancePath = join(auditDir, "provenance.jsonl");
  const tracker = new ProvenanceTracker(new ProvenanceStore(provenancePath), {
    mode: "production",
    workspacePath: auditDir
  });

  const cp = new ControlPlane(
    new MockProvider(),
    new AuditLogger(auditPath),
    undefined,
    undefined,
    tracker,
    "production"
  );

  const result = await cp.execute({
    agentId: "agent_123",
    orgId: "org_456",
    prompt: "Generate a helper function"
  });

  assert.deepEqual(result, { status: "blocked", reason: "provenance_required" });
});

test("fails closed in production when actor identity is not registered", () => {
  const repoDir = mkdtempSync(join(tmpdir(), "cp-prod-id-missing-"));
  execFileSync("git", ["init"], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["config", "user.name", "Test User"], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["config", "user.email", "test@example.com"], { cwd: repoDir, stdio: "ignore" });
  writeFileSync(join(repoDir, "artifact.ts"), "export const z = 1;\n", "utf8");
  execFileSync("git", ["add", "."], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["commit", "-m", "init"], { cwd: repoDir, stdio: "ignore" });

  const provenancePath = join(repoDir, "provenance.jsonl");
  const identityPath = join(repoDir, "identity.jsonl");
  const tracker = new ProvenanceTracker(new ProvenanceStore(provenancePath), {
    mode: "production",
    workspacePath: repoDir,
    identityStore: new IdentityStore(identityPath)
  });

  assert.throws(() => {
    tracker.trackAIOutput({
      code: "export const x = 1;",
      language: "typescript",
      model: "gpt-5.4-mini",
      provider: "openai",
      prompt: "make a constant",
      actorId: "AI-2026-000999"
    });
  }, /identity_required/);
});

test("passes in production when actor identity is registered", () => {
  const repoDir = mkdtempSync(join(tmpdir(), "cp-prod-id-ok-"));
  execFileSync("git", ["init"], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["config", "user.name", "Test User"], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["config", "user.email", "test@example.com"], { cwd: repoDir, stdio: "ignore" });
  writeFileSync(join(repoDir, "artifact.ts"), "export const z = 1;\n", "utf8");
  execFileSync("git", ["add", "."], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["commit", "-m", "init"], { cwd: repoDir, stdio: "ignore" });

  const provenancePath = join(repoDir, "provenance.jsonl");
  const identityPath = join(repoDir, "identity.jsonl");
  const identityStore = new IdentityStore(identityPath);
  const actor = createIdentity({
    type: "ai",
    id: "AI-2026-000777",
    label: "gpt-5.4-mini"
  });
  identityStore.save(actor);

  const tracker = new ProvenanceTracker(new ProvenanceStore(provenancePath), {
    mode: "production",
    workspacePath: repoDir,
    identityStore
  });

  const artifact = tracker.trackAIOutput({
    code: "export const x = 1;",
    language: "typescript",
    model: "gpt-5.4-mini",
    provider: "openai",
    prompt: "make a constant",
    actorId: actor.id
  });

  assert.equal(artifact.actor?.id, actor.id);
  assert.ok(artifact.provenanceSources?.some((source) => source.type === "git"));
});

test("fails in production when actor type mismatches identity record", () => {
  const repoDir = mkdtempSync(join(tmpdir(), "cp-prod-id-type-mismatch-"));
  execFileSync("git", ["init"], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["config", "user.name", "Test User"], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["config", "user.email", "test@example.com"], { cwd: repoDir, stdio: "ignore" });
  writeFileSync(join(repoDir, "artifact.ts"), "export const z = 1;\n", "utf8");
  execFileSync("git", ["add", "."], { cwd: repoDir, stdio: "ignore" });
  execFileSync("git", ["commit", "-m", "init"], { cwd: repoDir, stdio: "ignore" });

  const provenancePath = join(repoDir, "provenance.jsonl");
  const identityPath = join(repoDir, "identity.jsonl");
  const identityStore = new IdentityStore(identityPath);

  // Force a mismatch: AI-prefixed id stored as agent identity type.
  identityStore.save(
    createIdentity({
      type: "agent",
      id: "AI-2026-009999",
      label: "mismatched identity type"
    })
  );

  const tracker = new ProvenanceTracker(new ProvenanceStore(provenancePath), {
    mode: "production",
    workspacePath: repoDir,
    identityStore
  });

  assert.throws(() => {
    tracker.trackAIOutput({
      code: "export const x = 1;",
      language: "typescript",
      model: "gpt-5.4-mini",
      provider: "openai",
      prompt: "make a constant",
      actorId: "AI-2026-009999"
    });
  }, /identity_required: actor type mismatch/);
});
