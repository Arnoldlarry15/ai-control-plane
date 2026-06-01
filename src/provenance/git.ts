import { execFileSync } from "node:child_process";

export interface GitProvenance {
  type: "git";
  repo: string;
  branch?: string;
  commit: string;
  author?: string;
  path?: string;
  changedFiles?: string[];
  repositoryRoot?: string;
}

function runGit(args: string[], cwd: string): string | undefined {
  try {
    return execFileSync("git", args, {
      cwd,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"]
    }).trim();
  } catch {
    return undefined;
  }
}

export function collectGitProvenance(cwd = process.cwd(), path?: string): GitProvenance | undefined {
  const repoRoot = runGit(["rev-parse", "--show-toplevel"], cwd);
  if (!repoRoot) {
    return undefined;
  }

  const commit = runGit(["rev-parse", "HEAD"], repoRoot);
  if (!commit) {
    return undefined;
  }

  const branch = runGit(["branch", "--show-current"], repoRoot);
  const author = runGit(["log", "-1", "--format=%an <%ae>"], repoRoot);
  const remote = runGit(["config", "--get", "remote.origin.url"], repoRoot) || repoRoot;
  const changedFilesRaw = runGit(path ? ["diff", "--name-only", "HEAD", "--", path] : ["diff", "--name-only", "HEAD"], repoRoot);

  return {
    type: "git",
    repo: remote,
    branch: branch || undefined,
    commit,
    author: author || undefined,
    path,
    changedFiles: changedFilesRaw ? changedFilesRaw.split("\n").filter(Boolean) : [],
    repositoryRoot: repoRoot
  };
}

export function makeGitProvenance(params: {
  repo: string;
  commit: string;
  branch?: string;
  author?: string;
  path?: string;
  changedFiles?: string[];
  repositoryRoot?: string;
}): GitProvenance {
  return {
    type: "git",
    repo: params.repo,
    commit: params.commit,
    branch: params.branch,
    author: params.author,
    path: params.path,
    changedFiles: params.changedFiles,
    repositoryRoot: params.repositoryRoot
  };
}

export default collectGitProvenance;
