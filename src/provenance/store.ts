import fs from "node:fs";
import type { CodeArtifact } from "./types.js";

export class ProvenanceStore {
  constructor(private readonly file = "provenance-log.jsonl") {}

  save(artifact: CodeArtifact): void {
    fs.appendFileSync(this.file, `${JSON.stringify(artifact)}\n`, "utf8");
  }

  getAll(): CodeArtifact[] {
    if (!fs.existsSync(this.file)) {
      return [];
    }

    const raw = fs.readFileSync(this.file, "utf8");

    return raw
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line) as CodeArtifact);
  }

  getByArtifactId(id: string): CodeArtifact | undefined {
    return this.getAll().find((a) => a.artifactId === id);
  }

  getChildren(id: string): CodeArtifact[] {
    return this.getAll().filter((a) => (a.parents || []).includes(id));
  }

  // simple ancestor walk (non-optimized)
  getAncestors(id: string): CodeArtifact[] {
    const seen = new Set<string>();
    const results: CodeArtifact[] = [];
    const byId = new Map(this.getAll().map((a) => [a.artifactId, a]));

    function walk(currentId: string) {
      if (seen.has(currentId)) return;
      seen.add(currentId);
      const node = byId.get(currentId);
      if (!node) return;
      (node.parents || []).forEach((p) => {
        const parent = byId.get(p);
        if (parent) {
          results.push(parent);
          walk(parent.artifactId);
        }
      });
    }

    walk(id);

    return results;
  }
}