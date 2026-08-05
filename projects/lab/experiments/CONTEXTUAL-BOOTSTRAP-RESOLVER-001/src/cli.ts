import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { resolveContext } from './resolver.js';
import type { ResolverInput } from './types.js';

function value(flag: string): string | undefined {
  const index = process.argv.indexOf(flag);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

const inputPath = value('--input');
const outputPath = value('--output');
if (!inputPath || !outputPath) {
  throw new Error('Usage: node dist/cli.js --input <resolver-input.json> --output <context-manifest.json>');
}

const input = JSON.parse(readFileSync(resolve(inputPath), 'utf-8')) as ResolverInput;
const manifest = resolveContext(input);
writeFileSync(resolve(outputPath), `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`${manifest.route} ${manifest.terminalState} ${manifest.budget.reductionPercent}%`);
