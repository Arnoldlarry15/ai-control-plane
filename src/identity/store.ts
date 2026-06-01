import fs from "node:fs";
import type { IdentityRecord } from "./types.js";

export class IdentityStore {
  constructor(private readonly file = "identity-log.jsonl") {}

  save(identity: IdentityRecord): void {
    fs.appendFileSync(this.file, `${JSON.stringify(identity)}\n`, "utf8");
  }

  getAll(): IdentityRecord[] {
    if (!fs.existsSync(this.file)) {
      return [];
    }

    return fs
      .readFileSync(this.file, "utf8")
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line) as IdentityRecord);
  }

  getById(id: string): IdentityRecord | undefined {
    return this.getAll().find((x) => x.id === id);
  }
}
