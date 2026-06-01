export type ArtifactType =
  | "ai_generated"
  | "human_written"
  | "hybrid"
  | "policy"
  | "model"
  | "bundle";

export interface ActorIdentity {
  type: "ai" | "human" | "agent";
  id: string;
  name?: string;
  credentials?: string;
}

export interface IntegrityInfo {
  hashAlgorithm: string;
  hash: string;
  signedBy?: string;
  signature?: string;
}

export interface StorageInfo {
  location?: string;
  contentType?: string;
}

export interface CodeArtifact {
  // canonical id
  artifactId: string;

  // human-friendly type (keeps legacy `type` field)
  type: ArtifactType | string;

  version?: string;

  // legacy compatibility: content.code + content.hash
  content: {
    code?: string;
    language?: string;
    hash?: string;
  };

  // legacy source info (kept for compatibility)
  source?: {
    model?: string;
    provider?: string;
    promptHash?: string;
    systemHash?: string;
  };

  // new first-class actor and parents for lineage
  actor?: ActorIdentity;
  parents?: string[];

  // provenance sources such as git commits or model inference records
  provenanceSources?: Array<Record<string, any>>;

  integrity: IntegrityInfo;

  storage?: StorageInfo;

  metadata: {
    createdAt: string;
    createdBy: "ai" | "human" | "system";
    [k: string]: any;
  };
}