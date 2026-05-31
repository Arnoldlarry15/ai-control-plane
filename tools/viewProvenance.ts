import { existsSync, readFileSync, writeFileSync } from "node:fs";

const file = process.argv[2] || "provenance-log.jsonl";

if (!existsSync(file)) {
  console.error(`Provenance file not found: ${file}`);
  process.exit(1);
}

const lines = readFileSync(file, "utf8").trim().split("\n").filter(Boolean).map(l => JSON.parse(l));

const nodes = new Map();
const edges: [string, string][] = [];

for (const a of lines) {
  nodes.set(a.artifactId, a);
  if (a.lineage && a.lineage.parentArtifactId) {
    edges.push([a.lineage.parentArtifactId, a.artifactId]);
  }
  if (a.lineage && Array.isArray(a.lineage.derivedFrom)) {
    for (const d of a.lineage.derivedFrom) edges.push([d, a.artifactId]);
  }
}

const dot: string[] = [];
dot.push("digraph provenance {");
for (const [id, a] of nodes) {
  const label = `${id}\\n${a.source?.model || ""}`.replace(/"/g, "'");
  dot.push(`  "${id}" [label="${label}"];`);
}
for (const [s, t] of edges) {
  dot.push(`  "${s}" -> "${t}";`);
}
dot.push("}");

const out = "provenance-graph.dot";
writeFileSync(out, dot.join("\n"), "utf8");
console.log(`Wrote ${out} (${nodes.size} nodes, ${edges.length} edges)`);