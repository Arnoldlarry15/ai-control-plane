import type { AIProvider } from "./AIProvider.js";

export class MockProvider implements AIProvider {
  readonly name = "mock-model-v0";
  readonly type = "mock";

  async run(prompt: string): Promise<string> {
    return `[MOCK AI]: ${prompt}`;
  }
}
