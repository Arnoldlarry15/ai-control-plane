#!/usr/bin/env node
import { allocateNextArtifact, commitWithGit, formatSuggestedCommit, hasArtifactTag, promptForCommitSummary } from "./cps.js";

const args = process.argv.slice(2);
const messageFlagIndex = args.findIndex((arg) => arg === "-m" || arg === "--message");
const inlineSummary = args.find((arg) => !arg.startsWith("-"));
const providedSummary = messageFlagIndex >= 0 ? args[messageFlagIndex + 1] : inlineSummary;

const summary = providedSummary && providedSummary.trim().length > 0
  ? providedSummary.trim()
  : await promptForCommitSummary("feat(provenance): move runtime state");

const finalMessage = hasArtifactTag(summary)
  ? summary.trim()
  : formatSuggestedCommit(summary, allocateNextArtifact());

commitWithGit(finalMessage);