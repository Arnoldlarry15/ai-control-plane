# ai-control-plane

A universal governance and audit format for all AI systems, models, and agents.

## Minimal TypeScript reference implementation (v0.1)

Every call flows through one middleware entrypoint:

```ts
await controlPlane.execute({ agentId, orgId, prompt });
```

Behavior:

- intercepts every AI request
- evaluates deterministic policy rules
- logs append-only JSONL audit events
- enforces allow/block decisions
- returns provider response on success

## Quick start

```bash
npm install
npm test
npm run demo
```
