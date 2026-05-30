import type { AIProvider } from "./AIProvider.js";

export class MockProvider implements AIProvider {
  async run(prompt: string): Promise<string> {
    return `[MOCK AI]: ${prompt}`;
  }
}
