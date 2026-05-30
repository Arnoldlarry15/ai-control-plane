import { ControlPlane, MockProvider } from "../src/index.js";

const controlPlane = new ControlPlane(new MockProvider());

const result = await controlPlane.execute({
  agentId: "agent_123",
  orgId: "org_456",
  prompt: "Explain quantum computing"
});

console.log(result);
