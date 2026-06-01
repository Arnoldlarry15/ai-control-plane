#!/usr/bin/env node
import { allocateNextArtifact } from "./cps.js";

const artifactId = allocateNextArtifact();

if (process.argv.includes("--verbose")) {
  console.log("Next Artifact:");
  console.log(artifactId);
  console.log("");
  console.log("Suggested commit:");
  console.log(`feat(provenance):  [CPS:artifact=${artifactId}]`);
} else {
  console.log(artifactId);
}