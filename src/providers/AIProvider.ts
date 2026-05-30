export interface AIProvider {
  run(prompt: string): Promise<string>;
}
