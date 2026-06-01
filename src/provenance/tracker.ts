import { createArtifact } from "./artifact.js";
import { ProvenanceStore } from "./store.js";
import { sha256 } from "./hash.js";
import { collectGitProvenance, type GitProvenance } from "./git.js";
import type { IdentityStore } from "../identity/store.js";

export type ProvenanceMode = "development" | "production";

export function looksLikeCode(text: string): boolean {
  return (
    text.includes("function") ||
    text.includes("export") ||
    text.includes("class") ||
    (text.includes("{") && text.includes(";"))
  );
}

export class ProvenanceTracker {
  constructor(
    private readonly store = new ProvenanceStore(),
    private readonly options: {
      mode?: ProvenanceMode;
      workspacePath?: string;
      signerPrivateKeyPem?: string;
      identityStore?: IdentityStore;
    } = {}
  ) {}

  trackAIOutput(params: {
    code: string;
    language: string;
    model: string;
    provider: string;
    prompt: string;
    actorId?: string;
    parents?: string[];
    git?: GitProvenance;
    signerPrivateKeyPem?: string;
  }) {
    const mode = this.options.mode ?? "development";
    const git = params.git ?? collectGitProvenance(this.options.workspacePath ?? process.cwd());

    if (mode === "production" && !git) {
      throw new Error("provenance_required: git provenance is mandatory in production mode");
    }

    const artifact = createArtifact({
      code: params.code,
      language: params.language,
      model: params.model,
      provider: params.provider,
      prompt: params.prompt,
      actorId: params.actorId ?? params.model,
      parents: params.parents,
      type: "ai_generated",
      signerPrivateKeyPem: params.signerPrivateKeyPem ?? this.options.signerPrivateKeyPem
    });

    // attach inference provenance first
    artifact.provenanceSources = artifact.provenanceSources || [];
    artifact.provenanceSources.push({
      type: "inference_record",
      model: params.model,
      provider: params.provider,
      promptHash: sha256(params.prompt)
    });

    if (git) {
      artifact.provenanceSources.push({
        type: "git",
        repo: git.repo,
        commit: git.commit,
        branch: git.branch,
        author: git.author,
        path: git.path,
        changedFiles: git.changedFiles,
        repositoryRoot: git.repositoryRoot
      });
    }

    if (mode === "production" && !artifact.provenanceSources.some((source) => source.type === "git")) {
      throw new Error("provenance_required: artifact is missing git provenance");
    }

    if (mode === "production") {
      const identityStore = this.options.identityStore;
      if (!identityStore) {
        throw new Error("identity_required: identity store is mandatory in production mode");
      }

      const actorId = artifact.actor?.id;
      if (!actorId) {
        throw new Error("identity_required: artifact actor identity is missing");
      }

      const identity = identityStore.getById(actorId);
      if (!identity) {
        throw new Error(`identity_required: actor identity not found for ${actorId}`);
      }

      if (identity.type !== artifact.actor.type) {
        throw new Error(
          `identity_required: actor type mismatch for ${actorId} expected=${identity.type} actual=${artifact.actor.type}`
        );
      }
    }

    this.store.save(artifact);

    return artifact;
  }
}