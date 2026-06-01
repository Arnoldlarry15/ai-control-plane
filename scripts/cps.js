import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { createInterface } from "node:readline/promises";

const DEFAULT_SEQ_FILE = ".cps-state/prov-id-seq.json";

export function resolveSequenceFilePath() {
  return path.resolve(process.cwd(), process.env.PROV_ID_SEQ_FILE || DEFAULT_SEQ_FILE);
}

export function allocateNextArtifact(kind = "PROV") {
  const year = new Date().getFullYear();
  const sequenceFilePath = resolveSequenceFilePath();
  let data = {};

  if (fs.existsSync(sequenceFilePath)) {
    try {
      data = JSON.parse(fs.readFileSync(sequenceFilePath, "utf8"));
    } catch {
      data = {};
    }
  }

  const key = kind.toUpperCase();
  data[key] = data[key] || {};
  data[key][year] = (data[key][year] || 0) + 1;

  fs.mkdirSync(path.dirname(sequenceFilePath), { recursive: true });
  fs.writeFileSync(sequenceFilePath, JSON.stringify(data, null, 2), "utf8");

  const sequence = String(data[key][year]).padStart(6, "0");
  return `${key}-${year}-${sequence}`;
}

export function formatSuggestedCommit(summary, artifactId) {
  const cleanSummary = summary.trim();
  return cleanSummary.length > 0 ? `${cleanSummary} [CPS:artifact=${artifactId}]` : `[CPS:artifact=${artifactId}]`;
}

export function hasArtifactTag(message) {
  return /\[CPS:artifact=[^\]]+\]/.test(message);
}

export async function promptForCommitSummary(defaultSummary) {
  if (!process.stdin.isTTY) {
    throw new Error("No commit summary was provided. Run the command in an interactive terminal or pass --message.");
  }

  const prompt = createInterface({ input: process.stdin, output: process.stdout });
  try {
    const answer = await prompt.question(`Commit summary [${defaultSummary}]: `);
    const summary = answer.trim() || defaultSummary.trim();

    if (!summary) {
      throw new Error("Commit summary is required.");
    }

    return summary;
  } finally {
    prompt.close();
  }
}

export function commitWithGit(message) {
  execFileSync("git", ["commit", "-m", message], { stdio: "inherit" });
}