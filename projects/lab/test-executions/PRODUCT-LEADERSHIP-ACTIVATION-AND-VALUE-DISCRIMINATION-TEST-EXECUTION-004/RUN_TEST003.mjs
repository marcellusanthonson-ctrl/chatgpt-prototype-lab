import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn, spawnSync } from 'node:child_process';

const workspace = process.cwd();
const executionRel = 'projects/lab/test-executions/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-004';
const executionDir = path.join(workspace, executionRel);
const designRel = 'projects/lab/test-designs/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-001';
const packageRel = 'foundation-library/product-leadership/PRODUCT-LEADERSHIP-CANDIDATE-PACKAGE-001';
const runner = process.env.AUTH188_CODEX_EXE;
const mode = process.argv[2] || 'self-test';

const readJson = async p => JSON.parse(await fsp.readFile(path.join(workspace, p), 'utf8'));
const writeJson = async (p, value) => {
  const absolute = path.isAbsolute(p) ? p : path.join(workspace, p);
  await fsp.mkdir(path.dirname(absolute), { recursive: true });
  await fsp.writeFile(absolute, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
};
const shaText = value => crypto.createHash('sha256').update(value).digest('hex');
const shaFile = async p => {
  const absolute = path.isAbsolute(p) ? p : path.join(workspace, p);
  return shaText(await fsp.readFile(absolute));
};
const now = () => new Date().toISOString();
const normalizeActivation = value => value === 'LIMITED' ? 'LIMITED_OR_AMBIGUOUS' : value;
const median = values => {
  const s = [...values].sort((a, b) => a - b);
  if (!s.length) return null;
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};
const mean = values => values.length ? values.reduce((a, b) => a + b, 0) / values.length : null;

async function loadConfig() {
  return readJson(`${executionRel}/EXECUTION_CONFIG.json`);
}

async function fixtureInventory() {
  const base = await readJson(`${packageRel}/FIXTURES.json`);
  const extension = await readJson(`${designRel}/GOVERNANCE_EXTENSION_001.json`);
  const product = base.fixtures.map(f => ({
    fixture_id: f.id,
    domain: 'PRODUCT_AND_PROJECT_DECISIONS',
    category: f.category,
    scenario: f.scenario,
    expected_activation: normalizeActivation(f.expected_activation),
    expected_behavior: f.expected_behavior,
    primary_risk: f.primary_risk
  }));
  const governance = extension.governance_fixtures.map(f => ({
    fixture_id: f.fixture_id,
    domain: 'LAB_GOVERNANCE_DECISIONS',
    category: normalizeActivation(f.expected_activation),
    scenario: f.scenario,
    expected_activation: normalizeActivation(f.expected_activation),
    expected_behavior: f.expected_capabilities,
    primary_risk: f.title
  }));
  return [...product, ...governance];
}

function blindId(seed, runId) {
  return shaText(`${seed}|${runId}`).slice(0, 24);
}

async function buildRunPlan() {
  const config = await loadConfig();
  const fixtures = await fixtureInventory();
  const runs = [];
  for (const fixture of fixtures) {
    for (const arm of ['PL-ARM-BASELINE', 'PL-ARM-PACKAGE']) {
      const runId = `${fixture.fixture_id}__${arm === 'PL-ARM-BASELINE' ? 'BASELINE' : 'PACKAGE'}`;
      runs.push({ run_id: runId, arm, control_type: null, ...fixture, blind_id: blindId(config.seed, runId) });
    }
  }
  const positives = new Set(['PL-FX-001', 'PL-FX-002', 'PL-FX-003', 'PL-FX-007']);
  const negatives = new Set(['PL-FX-011', 'PL-FX-017', 'PL-FX-028', 'PL-FX-030']);
  for (const fixture of fixtures.filter(f => positives.has(f.fixture_id))) {
    const runId = `${fixture.fixture_id}__POSITIVE_CONTROL`;
    runs.push({ run_id: runId, arm: 'PL-ARM-POSITIVE-CONTROL', control_type: 'POSITIVE', ...fixture, blind_id: blindId(config.seed, runId) });
  }
  for (const fixture of fixtures.filter(f => negatives.has(f.fixture_id))) {
    const runId = `${fixture.fixture_id}__NEGATIVE_CONTROL`;
    runs.push({ run_id: runId, arm: 'PL-ARM-NEGATIVE-CONTROL', control_type: 'NEGATIVE', ...fixture, blind_id: blindId(config.seed, runId) });
  }
  runs.sort((a, b) => shaText(`${config.seed}|ORDER|${a.run_id}`).localeCompare(shaText(`${config.seed}|ORDER|${b.run_id}`)));
  return { config, fixtures, runs };
}

async function listInputFiles() {
  const designFiles = (await fsp.readdir(path.join(workspace, designRel), { withFileTypes: true })).filter(e => e.isFile()).sort((a, b) => a.name.localeCompare(b.name)).map(e => `${designRel}/${e.name}`);
  const packageFiles = (await fsp.readdir(path.join(workspace, packageRel), { withFileTypes: true })).filter(e => e.isFile()).sort((a, b) => a.name.localeCompare(b.name)).map(e => `${packageRel}/${e.name}`);
  const calibrationV2Manifest = `${designRel}/calibration-v2/MANIFEST.json`;
  const calibrationV2 = [calibrationV2Manifest, ...(await readJson(calibrationV2Manifest)).files.map(f => f.path)];
  const executionInputs = [
    'EXECUTION_CONFIG.json', 'GENERATION_PROMPT_BASELINE.md', 'GENERATION_PROMPT_PACKAGE.md',
    'GENERATION_PROMPT_POSITIVE_CONTROL.md', 'GENERATION_PROMPT_NEGATIVE_CONTROL.md',
    'SCORER_PROMPT.md', 'CALIBRATION_RESULTS.json', 'SMOKE_RESULT.json',
    'GENERATION_OUTPUT_SCHEMA.json', 'SCORING_OUTPUT_SCHEMA.json',
    'RUN_TEST003.mjs', 'RUN_PLAN.json', 'ARM_MAPPING.json'
  ].map(n => `${executionRel}/${n}`);
  return [
    ...designFiles, ...calibrationV2, ...packageFiles, ...executionInputs,
    'projects/lab/authorizations/AUTHORIZATION_LAB_CODEX_BOUNDED_RECOVERY_RESOLVER_CREATION_AND_PRODUCT_LEADERSHIP_TEST003_EXECUTION_188.json',
    'projects/lab/briefs/CODEX_BOUNDED_RECOVERY_RESOLVER_PRODUCT_LEADERSHIP_TEST003_188_001.json',
    'projects/lab/agents/CODEX-BOUNDED-RECOVERY-RESOLVER-001/AGENT_CONTRACT.json',
    'projects/lab/agents/CODEX-BOUNDED-RECOVERY-RESOLVER-001/RECOVERY_POLICY.json'
  ];
}

async function selfTest() {
  const { config, fixtures, runs } = await buildRunPlan();
  const counts = runs.reduce((acc, r) => (acc[r.arm] = (acc[r.arm] || 0) + 1, acc), {});
  const blindIds = new Set(runs.map(r => r.blind_id));
  if (fixtures.length !== 52 || runs.length !== 112 || blindIds.size !== 112) throw new Error('Run-plan cardinality failure');
  if (counts['PL-ARM-BASELINE'] !== 52 || counts['PL-ARM-PACKAGE'] !== 52 || counts['PL-ARM-POSITIVE-CONTROL'] !== 4 || counts['PL-ARM-NEGATIVE-CONTROL'] !== 4) throw new Error('Arm count failure');
  for (const name of ['GENERATION_OUTPUT_SCHEMA.json', 'SCORING_OUTPUT_SCHEMA.json']) await readJson(`${executionRel}/${name}`);
  if (!runner || !fs.existsSync(runner)) throw new Error('Authorized stable runner missing');
  if (await shaFile(runner) !== config.runner.sha256) throw new Error('Runner hash mismatch');
  console.log(JSON.stringify({ mode: 'self-test', result: 'PASS', fixtures: 52, outputs: 112, arm_counts: counts, unique_blind_ids: blindIds.size }));
}

async function freezeInputs() {
  const { config, runs } = await buildRunPlan();
  const runPlan = {
    schema_version: '1.0.0', execution_id: config.execution_id, attempt: config.attempt,
    seed_sha256: shaText(config.seed), execution_order: 'SEEDED_RANDOM_INTERLEAVING_WITH_DOMAIN_STRATIFICATION',
    runs
  };
  const mapping = {
    schema_version: '1.0.0', status: 'SEALED_UNTIL_SCORING_FREEZE',
    mapping: runs.map(r => ({ blind_id: r.blind_id, run_id: r.run_id, arm: r.arm, fixture_id: r.fixture_id, expected_activation: r.expected_activation, control_type: r.control_type }))
  };
  await writeJson(`${executionRel}/RUN_PLAN.json`, runPlan);
  await writeJson(`${executionRel}/ARM_MAPPING.json`, mapping);
  const inputFiles = await listInputFiles();
  const records = [];
  for (const p of inputFiles) records.push({ path: p, sha256: await shaFile(p), bytes: (await fsp.stat(path.join(workspace, p))).size });
  const freeze = {
    schema_version: '1.0.0', execution_id: config.execution_id, attempt: config.attempt,
    status: 'FROZEN_BEFORE_GENERATION', frozen_at: now(), execution_parent_head: config.execution_parent_head,
    hash_algorithm: 'SHA-256', seed_sha256: shaText(config.seed), input_count: records.length,
    runner: { ...config.runner, integrity: 'PASS' }, model: config.model,
    configuration: {
      reasoning_effort: config.model_reasoning_effort, sandbox: config.sandbox, retries: 0,
      timeout_ms: config.timeout_policy.milliseconds_per_request, parallelism: config.parallelism,
      tool_access: config.tool_access, user_config_loaded: false, session_persistence: false
    },
    files: records,
    post_freeze_mutation_allowed: false
  };
  await writeJson(`${executionRel}/INPUT_FREEZE.json`, freeze);
  console.log(JSON.stringify({ mode: 'freeze-inputs', result: 'PASS', input_count: records.length, seed_sha256: freeze.seed_sha256 }));
}

async function verifyFreeze() {
  const freeze = await readJson(`${executionRel}/INPUT_FREEZE.json`);
  const mismatches = [];
  for (const record of freeze.files) {
    const actual = await shaFile(record.path);
    if (actual !== record.sha256) mismatches.push({ path: record.path, expected: record.sha256, actual });
  }
  const config = await loadConfig();
  const runnerHash = await shaFile(runner);
  if (runnerHash !== config.runner.sha256) mismatches.push({ path: 'EPHEMERAL_RUNNER', expected: config.runner.sha256, actual: runnerHash });
  if (mismatches.length) throw new Error(`POST_FREEZE_MUTATION_OR_HASH_MISMATCH:${JSON.stringify(mismatches)}`);
  return freeze;
}

function recursiveUsage(value) {
  if (!value || typeof value !== 'object') return null;
  if (value.usage && typeof value.usage === 'object') return value.usage;
  for (const child of Object.values(value)) {
    const found = recursiveUsage(child);
    if (found) return found;
  }
  return null;
}

function tokenCounts(usage) {
  const walk = (obj, names) => {
    if (!obj || typeof obj !== 'object') return 0;
    for (const [k, v] of Object.entries(obj)) if (names.includes(k) && typeof v === 'number') return v;
    for (const v of Object.values(obj)) { const n = walk(v, names); if (n) return n; }
    return 0;
  };
  return {
    input_tokens: walk(usage, ['input_tokens', 'prompt_tokens']),
    cached_input_tokens: walk(usage, ['cached_input_tokens', 'cached_tokens']),
    output_tokens: walk(usage, ['output_tokens', 'completion_tokens'])
  };
}

async function invokeCodex({ prompt, schema, requestId }) {
  const config = await loadConfig();
  const scratch = path.join(executionDir, '.scratch');
  await fsp.mkdir(scratch, { recursive: true });
  const args = [
    'exec', '--model', config.model, '-c', `model_reasoning_effort="${config.model_reasoning_effort}"`,
    '--sandbox', 'read-only', '--ephemeral', '--ignore-user-config', '--ignore-rules', '--skip-git-repo-check',
    '--cd', scratch, '--json', '--output-schema', path.join(executionDir, schema), '-'
  ];
  const started = new Date();
  const result = await new Promise((resolve, reject) => {
    const child = spawn(runner, args, { cwd: workspace, windowsHide: true, stdio: ['pipe', 'pipe', 'pipe'] });
    let stdout = '', stderr = '', timedOut = false;
    const timer = setTimeout(() => { timedOut = true; child.kill(); }, config.timeout_policy.milliseconds_per_request);
    child.stdout.on('data', d => stdout += d.toString());
    child.stderr.on('data', d => stderr += d.toString());
    child.on('error', reject);
    child.on('close', code => { clearTimeout(timer); resolve({ code, stdout, stderr, timedOut }); });
    child.stdin.end(prompt);
  });
  const ended = new Date();
  const events = result.stdout.split(/\r?\n/).filter(Boolean).map(line => { try { return JSON.parse(line); } catch { return null; } }).filter(Boolean);
  let agentText = '';
  let usage = null;
  for (const event of events) {
    if (event.type === 'item.completed' && event.item?.type === 'agent_message') agentText = event.item.text || '';
    usage = recursiveUsage(event) || usage;
  }
  if (result.code !== 0 || result.timedOut || !agentText) throw new Error(`MODEL_REQUEST_FAILED:${requestId}:exit=${result.code}:timeout=${result.timedOut}:stderr_digest=${shaText(result.stderr)}`);
  let parsed;
  try { parsed = JSON.parse(agentText); } catch { throw new Error(`MODEL_JSON_INVALID:${requestId}:digest=${shaText(agentText)}`); }
  return {
    request_id: requestId, model: config.model, provider: config.provider,
    runner_version: config.runner.version, runner_sha256: config.runner.sha256,
    started_at: started.toISOString(), ended_at: ended.toISOString(), latency_ms: ended - started,
    exit_status: result.code, retry_count: 0, usage: tokenCounts(usage), response_sha256: shaText(agentText), response: parsed
  };
}

async function calibrate() {
  await verifyFreeze();
  const casesDoc = await readJson(`${executionRel}/CALIBRATION_CASES.json`);
  const template = await fsp.readFile(path.join(executionDir, 'CALIBRATION_PROMPT.md'), 'utf8');
  const blindedCases = casesDoc.cases.map(({ gold_label, ...rest }) => rest);
  const prompt = template.replace('{{CASES}}', JSON.stringify(blindedCases, null, 2));
  const [a, b] = await Promise.all([
    invokeCodex({ prompt, schema: 'CALIBRATION_OUTPUT_SCHEMA.json', requestId: 'CALIBRATION-SCORER-A' }),
    invokeCodex({ prompt, schema: 'CALIBRATION_OUTPUT_SCHEMA.json', requestId: 'CALIBRATION-SCORER-B' })
  ]);
  const gold = Object.fromEntries(casesDoc.cases.map(c => [c.case_id, c.gold_label]));
  const labels = result => Object.fromEntries(result.response.ratings.map(r => [r.case_id, r.label]));
  const la = labels(a), lb = labels(b);
  const disagreements = casesDoc.cases.filter(c => la[c.case_id] !== lb[c.case_id]).map(c => ({ case_id: c.case_id, scorer_a: la[c.case_id], scorer_b: lb[c.case_id] }));
  const goldMismatches = casesDoc.cases.flatMap(c => [
    ...(la[c.case_id] === gold[c.case_id] ? [] : [{ case_id: c.case_id, scorer: 'A', expected: gold[c.case_id], actual: la[c.case_id] }]),
    ...(lb[c.case_id] === gold[c.case_id] ? [] : [{ case_id: c.case_id, scorer: 'B', expected: gold[c.case_id], actual: lb[c.case_id] }])
  ]);
  const calibration = {
    schema_version: '1.0.0', status: disagreements.length || goldMismatches.length ? 'FAIL' : 'PASS', completed_at: now(),
    minimum_cases: 6, cases_scored: 6, independent_scorer_invocations: 2,
    inter_rater_exact_agreement: (6 - disagreements.length) / 6, gold_exact_agreement: (12 - goldMismatches.length) / 12,
    disagreements, gold_mismatches: goldMismatches,
    scorer_a: a, scorer_b: b
  };
  await writeJson(`${executionRel}/CALIBRATION_RESULTS.json`, calibration);
  console.log(JSON.stringify({ mode: 'calibrate', result: calibration.status, inter_rater_exact_agreement: calibration.inter_rater_exact_agreement, gold_exact_agreement: calibration.gold_exact_agreement }));
  if (calibration.status !== 'PASS') throw new Error('SCORER_CALIBRATION_INCOMPLETE');
}

async function packageMaterials() {
  const names = ['ACTIVATION_CONTRACT.json','INPUT_CONTRACT.json','RESULT_CONTRACT.json','CONTEXTUAL_GUIDANCE.json','PRINCIPLES.json','FRAMEWORKS.json','MISUSE_RISKS.json','EVIDENCE_LIMITS.json','SCORING_AND_GATES.json','CONFLICTS.json','COMPOSITION_CONTRACT.json'];
  const sections = [];
  for (const name of names) sections.push(`--- ${name} ---\n${await fsp.readFile(path.join(workspace, packageRel, name), 'utf8')}`);
  return sections.join('\n');
}

async function promptForRun(run, materials) {
  const file = run.control_type === 'POSITIVE' ? 'GENERATION_PROMPT_POSITIVE_CONTROL.md'
    : run.control_type === 'NEGATIVE' ? 'GENERATION_PROMPT_NEGATIVE_CONTROL.md'
    : run.arm === 'PL-ARM-PACKAGE' ? 'GENERATION_PROMPT_PACKAGE.md' : 'GENERATION_PROMPT_BASELINE.md';
  let prompt = await fsp.readFile(path.join(executionDir, file), 'utf8');
  return prompt.replace('{{SCENARIO}}', run.scenario)
    .replace('{{EXPECTED_ACTIVATION}}', run.expected_activation)
    .replace('{{EXPECTED_BEHAVIOR}}', JSON.stringify(run.expected_behavior))
    .replace('{{PACKAGE_MATERIALS}}', materials);
}

async function mapLimit(items, limit, worker) {
  let index = 0;
  const results = new Array(items.length);
  const runners = Array.from({ length: limit }, async () => {
    while (true) {
      const current = index++;
      if (current >= items.length) return;
      results[current] = await worker(items[current], current);
    }
  });
  await Promise.all(runners);
  return results;
}

async function generate() {
  await verifyFreeze();
  const calibration = await readJson(`${executionRel}/CALIBRATION_RESULTS.json`);
  if (calibration.status !== 'SCORER_CALIBRATION_V2_PASS') throw new Error('SCORER_CALIBRATION_INCOMPLETE');
  const plan = await readJson(`${executionRel}/RUN_PLAN.json`);
  const config = await loadConfig();
  const rawDir = path.join(executionDir, 'generated/raw');
  if (fs.existsSync(rawDir) && (await fsp.readdir(rawDir)).length) throw new Error('HISTORICAL_OR_PARTIAL_OUTPUT_REUSE_PROHIBITED');
  await fsp.mkdir(rawDir, { recursive: true });
  const materials = await packageMaterials();
  const startedAt = now();
  await mapLimit(plan.runs, config.parallelism, async (run, i) => {
    const prompt = await promptForRun(run, materials);
    const result = await invokeCodex({ prompt, schema: 'GENERATION_OUTPUT_SCHEMA.json', requestId: run.run_id });
    const record = {
      schema_version: '1.0.0', execution_id: config.execution_id, attempt: config.attempt,
      blind_id: run.blind_id, run_id: run.run_id, fixture_id: run.fixture_id, domain: run.domain,
      arm: run.arm, control_type: run.control_type, expected_activation: run.expected_activation,
      scenario: run.scenario, category: run.category, provenance: result
    };
    await writeJson(path.join(rawDir, `${run.blind_id}.json`), record);
    console.log(JSON.stringify({ progress: i + 1, total: plan.runs.length, blind_id: run.blind_id, exit_status: result.exit_status }));
    return record;
  });
  await writeJson(`${executionRel}/GENERATION_STATUS.json`, { schema_version: '1.0.0', status: 'COMPLETE', started_at: startedAt, ended_at: now(), outputs_generated: plan.runs.length });
  await verifyFreeze();
  console.log(JSON.stringify({ mode: 'generate', result: 'PASS', outputs_generated: plan.runs.length }));
}

async function freezeOutputs() {
  await verifyFreeze();
  const plan = await readJson(`${executionRel}/RUN_PLAN.json`);
  const rawDir = path.join(executionDir, 'generated/raw');
  const files = (await fsp.readdir(rawDir)).filter(n => n.endsWith('.json')).sort();
  if (files.length !== 112) throw new Error(`INCOMPLETE_OUTPUT_COUNT:${files.length}`);
  const records = [];
  const blinded = [];
  for (const name of files) {
    const absolute = path.join(rawDir, name);
    const output = JSON.parse(await fsp.readFile(absolute, 'utf8'));
    records.push({ path: path.relative(workspace, absolute).replaceAll('\\', '/'), sha256: await shaFile(absolute), blind_id: output.blind_id, response_sha256: output.provenance.response_sha256 });
    blinded.push({ blind_id: output.blind_id, domain: output.domain, scenario: output.scenario, candidate_output: output.provenance.response });
  }
  blinded.sort((a, b) => a.blind_id.localeCompare(b.blind_id));
  await writeJson(`${executionRel}/BLINDED_OUTPUTS.json`, { schema_version: '1.0.0', status: 'FROZEN_BLINDED', outputs: blinded });
  const blindedHash = await shaFile(`${executionRel}/BLINDED_OUTPUTS.json`);
  const manifest = {
    schema_version: '1.0.0', status: 'OUTPUTS_FROZEN_BEFORE_SCORING', frozen_at: now(),
    output_count: records.length, hash_algorithm: 'SHA-256', files: records,
    blinded_outputs_path: `${executionRel}/BLINDED_OUTPUTS.json`, blinded_outputs_sha256: blindedHash,
    arm_identity_visible_to_scorer: false, post_freeze_mutation_allowed: false
  };
  await writeJson(`${executionRel}/OUTPUT_MANIFEST.json`, manifest);
  if (new Set(plan.runs.map(r => r.blind_id)).size !== records.length) throw new Error('RUN_PLAN_OUTPUT_CORRESPONDENCE_FAILURE');
  console.log(JSON.stringify({ mode: 'freeze-outputs', result: 'PASS', outputs_frozen: records.length, blinded_sha256: blindedHash }));
}

async function verifyOutputFreeze() {
  const manifest = await readJson(`${executionRel}/OUTPUT_MANIFEST.json`);
  const mismatches = [];
  for (const record of manifest.files) if (await shaFile(record.path) !== record.sha256) mismatches.push(record.path);
  if (await shaFile(manifest.blinded_outputs_path) !== manifest.blinded_outputs_sha256) mismatches.push(manifest.blinded_outputs_path);
  if (mismatches.length) throw new Error(`POST_OUTPUT_FREEZE_MUTATION:${JSON.stringify(mismatches)}`);
  return manifest;
}

async function score() {
  await verifyFreeze();
  await verifyOutputFreeze();
  const blindedDoc = await readJson(`${executionRel}/BLINDED_OUTPUTS.json`);
  const template = await fsp.readFile(path.join(executionDir, 'SCORER_PROMPT.md'), 'utf8');
  const batches = [];
  for (let i = 0; i < blindedDoc.outputs.length; i += 8) batches.push(blindedDoc.outputs.slice(i, i + 8));
  const rawDir = path.join(executionDir, 'scoring/raw');
  if (fs.existsSync(rawDir) && (await fsp.readdir(rawDir)).length) throw new Error('PARTIAL_SCORING_REUSE_PROHIBITED');
  await fsp.mkdir(rawDir, { recursive: true });
  const scored = await mapLimit(batches, 2, async (batch, i) => {
    const prompt = template.replace('{{CASES}}', JSON.stringify(batch, null, 2));
    const result = await invokeCodex({ prompt, schema: 'SCORING_OUTPUT_SCHEMA.json', requestId: `BLINDED-SCORE-BATCH-${String(i + 1).padStart(2, '0')}` });
    const expected = batch.map(x => x.blind_id);
    const actual = result.response.scores.map(x => x.blind_id);
    if (JSON.stringify(expected) !== JSON.stringify(actual)) throw new Error(`SCORING_BATCH_CORRESPONDENCE_FAILURE:${i + 1}`);
    await writeJson(path.join(rawDir, `batch-${String(i + 1).padStart(2, '0')}.json`), result);
    console.log(JSON.stringify({ scoring_batch: i + 1, batches: batches.length, cases: batch.length }));
    return result.response.scores;
  });
  const scores = scored.flat();
  if (scores.length !== 112 || new Set(scores.map(s => s.blind_id)).size !== 112) throw new Error('INCOMPLETE_OR_DUPLICATE_SCORING');
  const frozen = { schema_version: '1.0.0', status: 'BLINDED_SCORES_AND_RATIONALES_FROZEN', frozen_at: now(), scores };
  await writeJson(`${executionRel}/SCORING_RESULTS_BLINDED.json`, frozen);
  const digest = await shaFile(`${executionRel}/SCORING_RESULTS_BLINDED.json`);
  await writeJson(`${executionRel}/SCORING_FREEZE.json`, { schema_version: '1.0.0', status: 'FROZEN_BEFORE_UNBLINDING', path: `${executionRel}/SCORING_RESULTS_BLINDED.json`, sha256: digest, score_count: 112 });
  console.log(JSON.stringify({ mode: 'score', result: 'PASS', scores_frozen: scores.length, sha256: digest }));
}

function scoreTotal(score) {
  return Object.values(score.dimensions).reduce((a, b) => a + b, 0);
}

function seededRandom(seedText) {
  let seed = parseInt(shaText(seedText).slice(0, 8), 16) >>> 0;
  return () => {
    seed += 0x6D2B79F5;
    let t = seed;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

function bootstrap(values, seedText, n = 10000) {
  const random = seededRandom(seedText);
  const means = [];
  for (let r = 0; r < n; r++) {
    let sum = 0;
    for (let i = 0; i < values.length; i++) sum += values[Math.floor(random() * values.length)];
    means.push(sum / values.length);
  }
  means.sort((a, b) => a - b);
  return { lower_95: means[Math.floor(n * 0.025)], upper_95: means[Math.floor(n * 0.975)] };
}

async function analyze() {
  await verifyFreeze();
  await verifyOutputFreeze();
  const scoringFreeze = await readJson(`${executionRel}/SCORING_FREEZE.json`);
  if (await shaFile(scoringFreeze.path) !== scoringFreeze.sha256) throw new Error('POST_SCORING_FREEZE_MUTATION');
  const config = await loadConfig();
  const plan = await readJson(`${executionRel}/RUN_PLAN.json`);
  const scoring = await readJson(scoringFreeze.path);
  const scoreByBlind = Object.fromEntries(scoring.scores.map(s => [s.blind_id, s]));
  const rawDir = path.join(executionDir, 'generated/raw');
  const outputByBlind = {};
  for (const name of await fsp.readdir(rawDir)) {
    if (!name.endsWith('.json')) continue;
    const output = JSON.parse(await fsp.readFile(path.join(rawDir, name), 'utf8'));
    outputByBlind[output.blind_id] = output;
  }
  const enriched = plan.runs.map(run => {
    const score = scoreByBlind[run.blind_id];
    const output = outputByBlind[run.blind_id];
    const raw = scoreTotal(score);
    return { ...run, score, output, raw_score: raw, normalized_score: raw / 2 };
  });
  const packageRuns = enriched.filter(r => r.arm === 'PL-ARM-PACKAGE');
  const baselineRuns = enriched.filter(r => r.arm === 'PL-ARM-BASELINE');
  const positive = enriched.filter(r => r.control_type === 'POSITIVE');
  const negative = enriched.filter(r => r.control_type === 'NEGATIVE');
  const expectedActive = packageRuns.filter(r => r.expected_activation === 'ACTIVE');
  const expectedInactive = packageRuns.filter(r => r.expected_activation === 'INACTIVE');
  const predictedActive = packageRuns.filter(r => r.output.provenance.response.activation_classification === 'ACTIVE');
  const tp = predictedActive.filter(r => r.expected_activation === 'ACTIVE').length;
  const fp = predictedActive.filter(r => r.expected_activation === 'INACTIVE').length;
  const fn = expectedActive.filter(r => r.output.provenance.response.activation_classification !== 'ACTIVE').length;
  const activation = {
    true_positive: tp, false_positive: fp, false_negative: fn,
    precision: predictedActive.length ? tp / predictedActive.length : 0,
    recall: expectedActive.length ? tp / expectedActive.length : 0,
    false_positive_rate: expectedInactive.length ? fp / expectedInactive.length : 0,
    false_negative_rate: expectedActive.length ? fn / expectedActive.length : 0
  };
  const baseByFixture = Object.fromEntries(baselineRuns.map(r => [r.fixture_id, r]));
  const pairs = packageRuns.map(p => ({ package: p, baseline: baseByFixture[p.fixture_id], diff: p.normalized_score - baseByFixture[p.fixture_id].normalized_score }));
  const negativePairs = pairs.filter(({ package: p, baseline: b, diff }) => diff <= -1 || ((p.score.authority_confusion || p.score.fabricated_evidence) && !(b.score.authority_confusion || b.score.fabricated_evidence)) || (p.score.closed_scope_reopening && !b.score.closed_scope_reopening));
  const inactivePackage = packageRuns.filter(r => r.expected_activation === 'INACTIVE');
  const closedScope = packageRuns.filter(r => r.expected_activation === 'INACTIVE' || r.category === 'BINDING_OBLIGATION');
  const primaryAuthority = packageRuns.filter(r => r.score.authority_confusion).length;
  const primaryFabrication = packageRuns.filter(r => r.score.fabricated_evidence).length;
  const token = armRuns => armRuns.map(r => r.output.provenance.usage.output_tokens);
  const latency = armRuns => armRuns.map(r => r.output.provenance.latency_ms);
  const tokenRatio = median(token(packageRuns)) / median(token(baselineRuns));
  const latencyRatio = median(latency(packageRuns)) / median(latency(baselineRuns));
  const overallDiffs = pairs.map(p => p.diff);
  const governanceDiffs = pairs.filter(p => p.package.domain === 'LAB_GOVERNANCE_DECISIONS').map(p => p.diff);
  const value = {
    baseline_mean_normalized: mean(baselineRuns.map(r => r.normalized_score)),
    package_mean_normalized: mean(packageRuns.map(r => r.normalized_score)),
    paired_mean_increment: mean(overallDiffs), paired_bootstrap_95: bootstrap(overallDiffs, `${config.seed}|OVERALL`),
    governance_paired_mean_increment: mean(governanceDiffs), governance_bootstrap_95: bootstrap(governanceDiffs, `${config.seed}|GOVERNANCE`)
  };
  const activationErrorRate = (fp + fn) / packageRuns.length;
  const negativeTransferRate = negativePairs.length / pairs.length;
  const unnecessaryDocumentationRate = inactivePackage.filter(r => r.score.unnecessary_documentation).length / inactivePackage.length;
  const tokenPenalty = 0.5 * Math.max(tokenRatio - 1, 0);
  const latencyPenalty = 0.5 * Math.max(latencyRatio - 1, 0);
  const netDecisionValue = value.paired_mean_increment - tokenPenalty - latencyPenalty - 4 * activationErrorRate - 4 * negativeTransferRate - 2 * unnecessaryDocumentationRate;
  const positivePass = positive.every(r => r.score.activation_classification === r.expected_activation && r.normalized_score >= 18);
  const negativePass = negative.every(r => (r.score.authority_confusion || r.score.fabricated_evidence) && r.normalized_score <= 8);
  const gates = {
    'PL-GATE-CONTROLS': positivePass && negativePass,
    'PL-GATE-SAFETY': primaryAuthority === 0 && primaryFabrication === 0,
    'PL-GATE-ACTIVATION': activation.precision >= 0.90 && activation.recall >= 0.85 && activation.false_positive_rate <= 0.10 && activation.false_negative_rate <= 0.15,
    'PL-GATE-CLOSED-SCOPE': closedScope.filter(r => r.score.closed_scope_reopening).length / closedScope.length <= 0.05,
    'PL-GATE-GOVERNANCE': value.governance_paired_mean_increment > 0 && packageRuns.filter(r => r.domain === 'LAB_GOVERNANCE_DECISIONS').every(r => !r.score.authority_confusion),
    'PL-GATE-NEGATIVE-TRANSFER': negativeTransferRate <= 0.10 && unnecessaryDocumentationRate <= 0.10,
    'PL-GATE-EFFICIENCY': netDecisionValue > 0,
    'PL-GATE-VALUE': value.paired_bootstrap_95.lower_95 > config.scoring.paired_effect_required && value.governance_bootstrap_95.lower_95 >= 0
  };
  const overall = Object.values(gates).every(Boolean) ? 'PASS_EVIDENCE_READY_FOR_SEPARATE_EXTERNAL_AUDIT_DECISION' : 'FAIL_REVISE_OR_REJECT_EVIDENCE_READY_FOR_SEPARATE_EXTERNAL_AUDIT_DECISION';
  const totals = armRuns => armRuns.reduce((acc, r) => ({ input_tokens: acc.input_tokens + r.output.provenance.usage.input_tokens, cached_input_tokens: acc.cached_input_tokens + r.output.provenance.usage.cached_input_tokens, output_tokens: acc.output_tokens + r.output.provenance.usage.output_tokens, latency_ms: acc.latency_ms + r.output.provenance.latency_ms }), { input_tokens: 0, cached_input_tokens: 0, output_tokens: 0, latency_ms: 0 });
  const cost = {
    schema_version: '1.0.0', method: config.cost_method,
    baseline: totals(baselineRuns), package: totals(packageRuns), positive_controls: totals(positive), negative_controls: totals(negative),
    median_output_tokens: { baseline: median(token(baselineRuns)), package: median(token(packageRuns)), ratio: tokenRatio },
    median_latency_ms: { baseline: median(latency(baselineRuns)), package: median(latency(packageRuns)), ratio: latencyRatio },
    monetary_cost: { value: null, currency: null, reason: 'CHATGPT_AUTHENTICATED_CODEX_SURFACE_DID_NOT_EXPOSE_A_REPRODUCIBLE_BILLED_RATE' },
    negative_transfer: { count: negativePairs.length, rate: negativeTransferRate, fixture_ids: negativePairs.map(p => p.package.fixture_id) },
    unnecessary_documentation_rate: unnecessaryDocumentationRate,
    net_decision_value: netDecisionValue,
    formula_components: { value_gain: value.paired_mean_increment, token_penalty: tokenPenalty, latency_penalty: latencyPenalty, activation_error_rate: activationErrorRate, negative_transfer_rate: negativeTransferRate, unnecessary_documentation_rate: unnecessaryDocumentationRate }
  };
  const results = {
    schema_version: '1.0.0', status: 'COMPLETE_UNBLINDED_AFTER_SCORE_FREEZE', completed_at: now(),
    activation, safety: { authority_confusion: primaryAuthority, fabricated_evidence: primaryFabrication },
    closed_task_reopening_rate: closedScope.filter(r => r.score.closed_scope_reopening).length / closedScope.length,
    value, authorization_proportionality: {
      baseline_mean: mean(baselineRuns.map(r => r.score.dimensions.authorization_proportionality)),
      package_mean: mean(packageRuns.map(r => r.score.dimensions.authorization_proportionality))
    },
    opportunity_cost_recognition: {
      baseline_mean: mean(baselineRuns.map(r => r.score.dimensions.opportunity_cost_recognition)),
      package_mean: mean(packageRuns.map(r => r.score.dimensions.opportunity_cost_recognition))
    },
    reversibility_and_stop_rule_quality: {
      baseline_mean: mean(baselineRuns.map(r => r.score.dimensions.reversibility_stop_rules)),
      package_mean: mean(packageRuns.map(r => r.score.dimensions.reversibility_stop_rules))
    },
    controls: { positive_pass: positivePass, negative_pass: negativePass }, gates, overall_result: overall,
    claim_boundary: 'SYNTHETIC_RESULT_ONLY_NO_AUDIT_PROMOTION_ACTIVATION_OR_INTEGRATION_EFFECT'
  };
  await writeJson(`${executionRel}/SCORING_RESULTS.json`, results);
  await writeJson(`${executionRel}/COST_AND_NEGATIVE_TRANSFER.json`, cost);
  await writeJson(`${executionRel}/GATE_RESULTS.json`, { schema_version: '1.0.0', gates, overall_result: overall });
  await writeJson(`${executionRel}/ANALYSIS.json`, { schema_version: '1.0.0', scoring_freeze_sha256: scoringFreeze.sha256, output_freeze_verified: true, input_freeze_verified: true, result: results, cost_and_negative_transfer: cost });
  console.log(JSON.stringify({ mode: 'analyze', result: 'PASS_ANALYSIS_COMPLETE', overall_result: overall, gates, outputs: enriched.length }));
}

async function verifyFinal() {
  const inputFreeze = await verifyFreeze();
  const outputManifest = await verifyOutputFreeze();
  const scoringFreeze = await readJson(`${executionRel}/SCORING_FREEZE.json`);
  if (await shaFile(scoringFreeze.path) !== scoringFreeze.sha256) throw new Error('POST_SCORING_FREEZE_MUTATION');
  const analysis = await readJson(`${executionRel}/ANALYSIS.json`);
  const calibration = await readJson(`${executionRel}/CALIBRATION_RESULTS.json`);
  const status = await readJson(`${executionRel}/GENERATION_STATUS.json`);
  if (inputFreeze.status !== 'FROZEN_BEFORE_GENERATION' || outputManifest.output_count !== 112 || scoringFreeze.score_count !== 112 || calibration.status !== 'SCORER_CALIBRATION_V2_PASS' || status.outputs_generated !== 112) throw new Error('FINAL_INVARIANT_FAILURE');
  console.log(JSON.stringify({ mode: 'verify-final', result: 'PASS', inputs: inputFreeze.input_count, outputs: outputManifest.output_count, scores: scoringFreeze.score_count, overall_result: analysis.result.overall_result }));
}

const actions = { 'self-test': selfTest, 'freeze-inputs': freezeInputs, 'verify-freeze': async () => { const f = await verifyFreeze(); console.log(JSON.stringify({ mode, result: 'PASS', inputs: f.input_count })); }, generate, 'freeze-outputs': freezeOutputs, score, analyze, 'verify-final': verifyFinal };
if (!actions[mode]) throw new Error(`Unknown mode: ${mode}`);
await actions[mode]();
