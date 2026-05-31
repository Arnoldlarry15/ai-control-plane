export type ArtifactType = "ai_generated" | "human_written" | "hybrid";

export interface CodeArtifact {
  artifactId: string;

  type: ArtifactType;

  content: {
    code: string;
    language: string;
    hash: string;
  };

  source: {
    model?: string;
    provider?: string;
    promptHash?: string;
    systemHash?: string;
  };

  lineage: {
    parentArtifactId?: string;
    derivedFrom?: string[];
  };

  metadata: {
    createdAt: string;
    createdBy: "ai" | "human" | "system";
  };
}