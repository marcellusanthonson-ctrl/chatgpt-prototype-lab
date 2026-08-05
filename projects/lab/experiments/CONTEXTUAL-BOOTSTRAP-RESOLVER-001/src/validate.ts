import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { gzipSync, gunzipSync } from 'node:zlib';
import { dirname, resolve } from 'node:path';
import { resolveContext } from './resolver.js';
import type { ContextManifest, OracleFixture, PublicFixture, SourceRecord } from './types.js';

interface ValidationIssue {
  fixtureId: string;
  category: string;
  detail: string;
  critical: boolean;
}

function sha256(text: string): string {
  return createHash('sha256').update(text).digest('hex');
}

function selectedPaths(manifest: ContextManifest): string[] {
  return Object.values(manifest.sources)
    .flat()
    .map((source) => source.path)
    .sort();
}

function f1(tp: number, fp: number, fn: number): number {
  const precision = tp + fp === 0 ? 1 : tp / (tp + fp);
  const recall = tp + fn === 0 ? 1 : tp / (tp + fn);
  return precision + recall === 0 ? 0 : (2 * precision * recall) / (precision + recall);
}

function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  if (sorted.length === 0) return 0;
  if (sorted.length % 2 === 1) return sorted[middle] ?? 0;
  return ((sorted[middle - 1] ?? 0) + (sorted[middle] ?? 0)) / 2;
}

function validateManifestShape(manifest: ContextManifest): string[] {
  const errors: string[] = [];
  if (manifest.schemaVersion !== '1.0.0') errors.push('schemaVersion');
  if (!manifest.resolverVersion) errors.push('resolverVersion');
  if (!manifest.route) errors.push('route');
  if (!manifest.riskClass) errors.push('riskClass');
  if (!manifest.authority || !Array.isArray(manifest.authority.allowedActions)) errors.push('authority');
  for (const bucket of ['always', 'required', 'filtered', 'onTrigger', 'auditOnly', 'historicalReference'] as const) {
    if (!Array.isArray(manifest.sources[bucket])) errors.push(`sources.${bucket}`);
  }
  if (!Array.isArray(manifest.exclusions.paths)) errors.push('exclusions.paths');
  if (!manifest.conflicts || !Array.isArray(manifest.conflicts.items)) errors.push('conflicts');
  if (!Number.isFinite(manifest.budget.selectedBytes)) errors.push('budget.selectedBytes');
  if (!Array.isArray(manifest.escalationTriggers)) errors.push('escalationTriggers');
  if (!manifest.trace || typeof manifest.trace.selectionReasonByPath !== 'object') errors.push('trace');
  if (!manifest.terminalState) errors.push('terminalState');
  return errors;
}

function forbiddenOracleKeys(value: unknown, path = '$'): string[] {
  const failures: string[] = [];
  if (Array.isArray(value)) {
    value.forEach((item, index) => failures.push(...forbiddenOracleKeys(item, `${path}[${index}]`)));
  } else if (value && typeof value === 'object') {
    for (const [key, child] of Object.entries(value as Record<string, unknown>)) {
      if (/expected|oracle|gold|correctAnswer/i.test(key)) failures.push(`${path}.${key}`);
      failures.push(...forbiddenOracleKeys(child, `${path}.${key}`));
    }
  }
  return failures;
}

const root = resolve(process.cwd());
const publicPath = resolve(root, 'fixtures/public-fixtures.json.gz.b64');
const oraclePath = resolve(root, 'oracle/private-oracle.json.gz.b64');
const manifestsPath = resolve(root, 'results/CONTEXT_MANIFESTS.json.gz.b64');
const validationPath = resolve(root, 'results/VALIDATION_RESULTS.json');

const publicArchiveText = readFileSync(publicPath, 'utf-8').trim();
const publicText = gunzipSync(Buffer.from(publicArchiveText, 'base64')).toString('utf-8');
const publicData = JSON.parse(publicText) as { schemaVersion: string; fixtures: PublicFixture[] };
const leakage = forbiddenOracleKeys(publicData);
const issues: ValidationIssue[] = leakage.map((detail) => ({
  fixtureId: 'CORPUS',
  category: 'ORACLE_LEAKAGE',
  detail,
  critical: true,
}));

const runOutputs: Array<{ fixtureId: string; manifest: ContextManifest; latencyMs: number; deterministic: boolean }> = [];
for (const fixture of publicData.fixtures) {
  const outputs: string[] = [];
  let firstManifest: ContextManifest | undefined;
  let totalLatency = 0;
  for (let repetition = 0; repetition < 3; repetition += 1) {
    const start = performance.now();
    const manifest = resolveContext(fixture.input);
    totalLatency += performance.now() - start;
    firstManifest ??= manifest;
    outputs.push(JSON.stringify(manifest));
  }
  const deterministic = new Set(outputs).size === 1;
  if (!deterministic) {
    issues.push({ fixtureId: fixture.id, category: 'DETERMINISM', detail: 'outputs differ across 3 repetitions', critical: true });
  }
  runOutputs.push({ fixtureId: fixture.id, manifest: firstManifest as ContextManifest, latencyMs: totalLatency / 3, deterministic });
}

// The private oracle is loaded only after every selector run has completed.
const oracleArchiveBefore = readFileSync(oraclePath, 'utf-8').trim();
const oracleTextBefore = gunzipSync(Buffer.from(oracleArchiveBefore, 'base64')).toString('utf-8');
const oracleHashBefore = sha256(oracleArchiveBefore);
const oracleData = JSON.parse(oracleTextBefore) as { schemaVersion: string; fixtures: OracleFixture[] };
const oracleById = new Map(oracleData.fixtures.map((fixture) => [fixture.id, fixture]));

let tpTotal = 0;
let fpTotal = 0;
let fnTotal = 0;
let criticalExpected = 0;
let criticalSelected = 0;
let forbiddenViolations = 0;
let authorityBypasses = 0;
let consumedAuthorizationActivations = 0;
let crossProjectContaminations = 0;
let inventedPaths = 0;
let unpinnedSources = 0;
let missingReasonTraces = 0;
let autoResolvedConflicts = 0;
const fixtureResults: Array<Record<string, unknown>> = [];

for (const output of runOutputs) {
  const fixture = publicData.fixtures.find((item) => item.id === output.fixtureId) as PublicFixture;
  const oracle = oracleById.get(output.fixtureId);
  if (!oracle) {
    issues.push({ fixtureId: output.fixtureId, category: 'ORACLE_MISSING', detail: 'no oracle fixture', critical: true });
    continue;
  }
  const manifest = output.manifest;
  const paths = selectedPaths(manifest);
  const expected = new Set(oracle.expectedSelectedPaths);
  const actual = new Set(paths);
  const tp = paths.filter((path) => expected.has(path)).length;
  const fp = paths.filter((path) => !expected.has(path)).length;
  const fn = oracle.expectedSelectedPaths.filter((path) => !actual.has(path)).length;
  tpTotal += tp;
  fpTotal += fp;
  fnTotal += fn;

  const fixtureIssuesBefore = issues.length;
  if (manifest.route !== oracle.expectedRoute) issues.push({ fixtureId: fixture.id, category: 'ROUTE', detail: `${manifest.route} != ${oracle.expectedRoute}`, critical: false });
  if (manifest.riskClass !== oracle.expectedRisk) issues.push({ fixtureId: fixture.id, category: 'RISK', detail: `${manifest.riskClass} != ${oracle.expectedRisk}`, critical: false });
  if (manifest.terminalState !== oracle.expectedTerminal) issues.push({ fixtureId: fixture.id, category: 'TERMINAL', detail: `${manifest.terminalState} != ${oracle.expectedTerminal}`, critical: true });
  const actualConflict = manifest.conflicts.state === 'RESOLUTION_REQUIRED' ? 'RESOLUTION_REQUIRED' : 'NONE';
  if (actualConflict !== oracle.expectedConflictState) issues.push({ fixtureId: fixture.id, category: 'CONFLICT', detail: `${actualConflict} != ${oracle.expectedConflictState}`, critical: true });

  for (const path of oracle.criticalPaths) {
    criticalExpected += 1;
    if (actual.has(path)) criticalSelected += 1;
    else issues.push({ fixtureId: fixture.id, category: 'CRITICAL_OMISSION', detail: path, critical: true });
  }
  for (const path of oracle.forbiddenSelectedPaths) {
    if (actual.has(path)) {
      forbiddenViolations += 1;
      issues.push({ fixtureId: fixture.id, category: 'FORBIDDEN_PATH', detail: path, critical: true });
    }
  }

  const catalogByPath = new Map(fixture.input.catalog.sources.map((source) => [source.path, source]));
  const targetProjectId = manifest.target.projectId;
  for (const path of paths) {
    const source = catalogByPath.get(path);
    if (!source) {
      inventedPaths += 1;
      issues.push({ fixtureId: fixture.id, category: 'INVENTED_PATH', detail: path, critical: true });
      continue;
    }
    if (!source.headSha || source.headSha.length !== 40) {
      unpinnedSources += 1;
      issues.push({ fixtureId: fixture.id, category: 'UNPINNED_SOURCE', detail: path, critical: true });
    }
    if (source.projectId && source.projectId !== targetProjectId) {
      crossProjectContaminations += 1;
      issues.push({ fixtureId: fixture.id, category: 'CROSS_PROJECT_CONTAMINATION', detail: `${path}:${source.projectId}`, critical: true });
    }
    if (!manifest.trace.selectionReasonByPath[path]?.length) {
      missingReasonTraces += 1;
      issues.push({ fixtureId: fixture.id, category: 'MISSING_REASON_TRACE', detail: path, critical: true });
    }
  }

  if (manifest.route === 'CODE_CHANGE' && manifest.terminalState === 'READY') {
    if (manifest.authority.effect !== 'BOUNDED_EXECUTION' || manifest.authority.lifecycleStatus !== 'GRANTED') {
      authorityBypasses += 1;
      issues.push({ fixtureId: fixture.id, category: 'AUTHORITY_BYPASS', detail: 'READY without GRANTED bounded authorization', critical: true });
    }
  }
  if (manifest.authority.lifecycleStatus && manifest.authority.lifecycleStatus !== 'GRANTED' && manifest.authority.effect === 'BOUNDED_EXECUTION') {
    consumedAuthorizationActivations += 1;
    issues.push({ fixtureId: fixture.id, category: 'CONSUMED_AUTHORIZATION_ACTIVATED', detail: manifest.authority.lifecycleStatus, critical: true });
  }
  if (oracle.expectedConflictState === 'RESOLUTION_REQUIRED' && manifest.terminalState !== 'RESOLUTION_REQUIRED') {
    autoResolvedConflicts += 1;
    issues.push({ fixtureId: fixture.id, category: 'AUTO_RESOLVED_CONFLICT', detail: manifest.terminalState, critical: true });
  }
  for (const shapeError of validateManifestShape(manifest)) {
    issues.push({ fixtureId: fixture.id, category: 'SCHEMA', detail: shapeError, critical: true });
  }

  fixtureResults.push({
    fixtureId: fixture.id,
    route: manifest.route,
    riskClass: manifest.riskClass,
    terminalState: manifest.terminalState,
    selectedSources: paths.length,
    selectedBytes: manifest.budget.selectedBytes,
    fullCorpusBytes: manifest.budget.fullCorpusBytes,
    reductionPercent: manifest.budget.reductionPercent,
    estimatedTokens: manifest.budget.estimatedTokens,
    latencyMs: Number(output.latencyMs.toFixed(4)),
    deterministic3Of3: output.deterministic,
    tp,
    fp,
    fn,
    f1: Number(f1(tp, fp, fn).toFixed(6)),
    issueCount: issues.length - fixtureIssuesBefore,
  });
}

const oracleArchiveAfter = readFileSync(oraclePath, 'utf-8').trim();
const oracleHashAfter = sha256(oracleArchiveAfter);
if (oracleHashBefore !== oracleHashAfter) {
  issues.push({ fixtureId: 'CORPUS', category: 'ORACLE_HASH_CHANGED', detail: `${oracleHashBefore} != ${oracleHashAfter}`, critical: true });
}

const macroF1 = fixtureResults.reduce((sum, result) => sum + Number(result.f1), 0) / fixtureResults.length;
const microF1 = f1(tpTotal, fpTotal, fnTotal);
const criticalRecall = criticalExpected === 0 ? 1 : criticalSelected / criticalExpected;
const forbiddenPathPrecision = forbiddenViolations === 0 ? 1 : 0;
const medianReduction = median(fixtureResults.map((result) => Number(result.reductionPercent)));
const medianLatency = median(fixtureResults.map((result) => Number(result.latencyMs)));
const criticalIssueCount = issues.filter((issue) => issue.critical).length;
const noncriticalIssueCount = issues.length - criticalIssueCount;

let terminalResult:
  | 'PROTOTYPE_VALIDATION_PASS_NO_INTEGRATION'
  | 'FUNCTIONALLY_VALID_EFFICIENCY_TARGET_NOT_MET'
  | 'PROTOTYPE_VALIDATION_FAIL_CRITICAL'
  | 'PROTOTYPE_VALIDATION_FAIL_NONCRITICAL';
if (criticalIssueCount > 0 || criticalRecall < 1 || forbiddenPathPrecision < 1) {
  terminalResult = 'PROTOTYPE_VALIDATION_FAIL_CRITICAL';
} else if (noncriticalIssueCount > 0 || macroF1 < 0.9) {
  terminalResult = 'PROTOTYPE_VALIDATION_FAIL_NONCRITICAL';
} else if (medianReduction < 60) {
  terminalResult = 'FUNCTIONALLY_VALID_EFFICIENCY_TARGET_NOT_MET';
} else {
  terminalResult = 'PROTOTYPE_VALIDATION_PASS_NO_INTEGRATION';
}

const manifestsPayload = {
  schemaVersion: '1.0.0',
  generatedAt: new Date().toISOString(),
  selectorInputHash: sha256(publicArchiveText),
  oracleLoadedAfterSelection: true,
  manifests: runOutputs.map((output) => ({ fixtureId: output.fixtureId, manifest: output.manifest })),
};

const validationPayload = {
  schemaVersion: '1.0.0',
  experimentId: 'CONTEXTUAL-BOOTSTRAP-RESOLVER-001',
  authorizationId: 'AUTHORIZATION_LAB_CONTEXTUAL_BOOTSTRAP_RESOLVER_READ_ONLY_PROTOTYPE_AND_DISCRIMINATING_VALIDATION_197',
  executedAt: new Date().toISOString(),
  environment: {
    platform: process.platform,
    node: process.version,
    typescript: '5.8.3',
    dependenciesInstalled: false,
    modelRequests: 0,
    networkRequests: 0,
    externalRepositoriesAccessed: 0,
  },
  separation: {
    selectorInputPath: 'fixtures/public-fixtures.json',
    oraclePath: 'oracle/private-oracle.json',
    selectorCompletedBeforeOracleLoad: true,
    publicOracleLeakageCount: leakage.length,
    oracleSha256Initial: oracleHashBefore,
    oracleSha256Final: oracleHashAfter,
    oracleHashStable: oracleHashBefore === oracleHashAfter,
  },
  corpus: {
    fixtureCount: publicData.fixtures.length,
    repetitionsPerFixture: 3,
    totalResolverRuns: publicData.fixtures.length * 3,
    syntheticOnly: true,
  },
  metrics: {
    macroF1: Number(macroF1.toFixed(6)),
    microF1: Number(microF1.toFixed(6)),
    criticalConstraintRecall: Number(criticalRecall.toFixed(6)),
    forbiddenPathPrecision,
    falsePositives: fpTotal,
    falseNegatives: fnTotal,
    medianContextByteReductionPercent: Number(medianReduction.toFixed(3)),
    medianLatencyMs: Number(medianLatency.toFixed(4)),
    authorityBypasses,
    consumedAuthorizationActivations,
    crossProjectContaminations,
    inventedPaths,
    unpinnedSources,
    missingReasonTraces,
    autoResolvedConflicts,
  },
  gates: {
    deterministicOutputs3Of3: runOutputs.every((output) => output.deterministic),
    criticalConstraintRecall1: criticalRecall === 1,
    forbiddenPathPrecision1: forbiddenPathPrecision === 1,
    macroF1AtLeast0_90: macroF1 >= 0.9,
    medianByteReductionAtLeast60Percent: medianReduction >= 60,
    zeroAuthorityBypasses: authorityBypasses === 0,
    zeroConsumedAuthorizationActivations: consumedAuthorizationActivations === 0,
    zeroCrossProjectContaminations: crossProjectContaminations === 0,
    zeroInventedPaths: inventedPaths === 0,
    allSelectedSourcesCommitPinned: unpinnedSources === 0,
    allSelectedPathsReasonTraced: missingReasonTraces === 0,
    zeroAutoResolvedConflicts: autoResolvedConflicts === 0,
    oracleSeparationPass: leakage.length === 0 && oracleHashBefore === oracleHashAfter,
  },
  fixtureResults,
  issues,
  terminalResult,
  integrationSelected: false,
  architectureSelected: false,
  runtimeEffect: 'NONE',
  productEffect: 'NONE',
  residualAuthority: 'NONE_AFTER_VERIFIED_PUBLICATION',
};

mkdirSync(dirname(manifestsPath), { recursive: true });
writeFileSync(manifestsPath, `${gzipSync(JSON.stringify(manifestsPayload)).toString('base64')}\n`);
writeFileSync(validationPath, `${JSON.stringify(validationPayload, null, 2)}\n`);
console.log(JSON.stringify({ terminalResult, metrics: validationPayload.metrics, issueCount: issues.length }, null, 2));
if (!terminalResult.startsWith('PROTOTYPE_VALIDATION_PASS')) process.exitCode = 1;
