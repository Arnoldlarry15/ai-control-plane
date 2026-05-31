export interface AIProvider {
  readonly name: string;
  readonly type: string;

  run(prompt: string): Promise<string>;
}
