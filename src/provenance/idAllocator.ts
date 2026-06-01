import fs from "node:fs";
import { dirname } from "node:path";

const DEFAULT_SEQ_FILE = process.env.PROV_ID_SEQ_FILE || ".cps-state/prov-id-seq.json";

export function allocateId(kind: string): string {
  const year = new Date().getFullYear();
  const seqFile = process.env.PROV_ID_SEQ_FILE || DEFAULT_SEQ_FILE;

  let data: Record<string, Record<number, number>> = {};
  if (fs.existsSync(seqFile)) {
    try {
      data = JSON.parse(fs.readFileSync(seqFile, "utf8"));
    } catch {
      data = {};
    }
  }

  const key = kind.toUpperCase();
  data[key] = data[key] || {};
  data[key][year] = (data[key][year] || 0) + 1;
  try {
    fs.mkdirSync(dirname(seqFile), { recursive: true });
    fs.writeFileSync(seqFile, JSON.stringify(data, null, 2), "utf8");
  } catch {
    // best-effort persistence; ignore errors
  }

  const seq = String(data[key][year]).padStart(6, "0");

  return `${key}-${year}-${seq}`;
}

export function nextForTesting(kind: string, year: number, seq: number) {
  // helper used only in advanced tests if needed
  const seqFile = process.env.PROV_ID_SEQ_FILE || DEFAULT_SEQ_FILE;
  const data: any = {};
  data[kind] = {};
  data[kind][year] = seq;
  fs.mkdirSync(dirname(seqFile), { recursive: true });
  fs.writeFileSync(seqFile, JSON.stringify(data, null, 2), "utf8");
}

export default allocateId;
