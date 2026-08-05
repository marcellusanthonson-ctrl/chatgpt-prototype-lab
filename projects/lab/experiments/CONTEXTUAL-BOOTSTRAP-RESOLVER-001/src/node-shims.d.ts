declare module 'node:fs' {
  export function readFileSync(path: string, encoding: string): string;
  export function writeFileSync(path: string, data: string): void;
  export function mkdirSync(path: string, options?: { recursive?: boolean }): string | undefined;
}
declare module 'node:path' {
  export function resolve(...paths: string[]): string;
  export function dirname(path: string): string;
}
declare module 'node:crypto' {
  export function createHash(algorithm: string): {
    update(data: string): { digest(encoding: 'hex'): string };
  };
}
declare const performance: { now(): number };
declare const process: {
  argv: string[];
  cwd(): string;
  platform: string;
  version: string;
  exitCode?: number;
};

declare module 'node:zlib' {
  export function gzipSync(data: string): { toString(encoding: 'base64'): string };
  export function gunzipSync(data: unknown): { toString(encoding: 'utf-8'): string };
}
declare const Buffer: { from(data: string, encoding: 'base64'): unknown };
