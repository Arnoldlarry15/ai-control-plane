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
}