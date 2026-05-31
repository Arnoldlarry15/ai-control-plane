import { createArtifact } from "./artifact.js";
import { ProvenanceStore } from "./store.js";

export function looksLikeCode(text: string): boolean {
  return (
    text.includes("function") ||
    text.includes("export") ||
    text.includes("class") ||
    (text.includes("{") && text.includes(";"))
  );
}

export class ProvenanceTracker {
  constructor(private readonly store = new ProvenanceStore()) {}

  trackAIOutput(params: {
    code: string;
    language: string;
    model: string;
    provider: string;
    prompt: string;
  }) {
    const artifact = createArtifact(params);

    this.store.save(artifact);

    return artifact;
  }
}