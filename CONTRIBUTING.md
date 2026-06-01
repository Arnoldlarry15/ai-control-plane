# Contributing

## Commit Requirements

Code changes must include a CPS artifact tag in the commit message.

Format:

```text
[CPS:artifact=<ID>]
```

Example:

```text
feat(provenance): add verification [CPS:artifact=PROV-2026-000002]
```

## Developer Workflow

- `npm run cps:new-artifact` prints the next artifact id and a suggested commit message.
- `npm run cps:commit` prompts for a summary, appends the next artifact tag, and runs `git commit`.
- `git config alias.cps '!node scripts/new-artifact.js'` gives a short Git alias for the next artifact id.
- In VS Code, run the `Generate CPS Artifact` task from the Task Runner.