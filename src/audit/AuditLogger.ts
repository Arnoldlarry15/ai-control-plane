import { createHash } from "node:crypto";
import { appendFileSync } from "node:fs";
import type { AuditEvent } from "../core/types.js";

export class AuditLogger {
  constructor(private readonly filePath = "audit-log.jsonl") {}

  log(event: AuditEvent): void {
    const enriched = {
      ...event,
      timestamp: new Date().toISOString()
    };

    appendFileSync(this.filePath, `${JSON.stringify(enriched)}\n`, "utf8");
  }

  hashPrompt(prompt: string): string {
    return createHash("sha256").update(prompt).digest("hex");
  }
}
