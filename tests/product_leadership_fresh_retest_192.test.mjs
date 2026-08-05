import assert from 'node:assert/strict';
import {
  ATTEMPT,
  CANONICAL_CORE_DEPENDENCY,
  EXECUTION_ID,
  REQUEST_LIMIT,
  RETRY_LIMIT,
  assertRequestEligibility,
  blockedBeforeRequests,
  classifyWithCanonicalCore,
  scoreWithCanonicalCore,
  verifyArmPair
} from '../projects/lab/test-executions/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-005/RUN_TEST003_REDESIGNED.mjs';

assert.equal(EXECUTION_ID, 'PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-005');
assert.equal(ATTEMPT, 'ATTEMPT-004');
assert.equal(REQUEST_LIMIT, 41);
assert.equal(RETRY_LIMIT, 0);
assert.equal(CANONICAL_CORE_DEPENDENCY, 'INSTRUMENT_REDESIGN_191/INSTRUMENT_CORE.mjs');

const common = {task_context: {TASK_OBJECTIVE: 'Choose one step.'}, length_budget: 420};
assert.equal(verifyArmPair([
  {...common, treatment: {package_materials: 'ABSENT'}},
  {...common, treatment: {package_materials: 'PRESENT_FROZEN_EXACT_BYTES'}}
], ['treatment.package_materials']), true);

assert.throws(() => assertRequestEligibility({custodyPass: false, authenticationPass: true}), /STOP_CHAIN_OF_CUSTODY_BROKEN/);
assert.throws(() => assertRequestEligibility({custodyPass: true, authenticationPass: false}), /STOP_EXACT_AUTHENTICATION_UNAVAILABLE/);
assert.throws(() => assertRequestEligibility({custodyPass: true, authenticationPass: true, retries: 1}), /STOP_RETRY_ATTEMPTED/);

const dimensions = Object.fromEntries([
  'problem_outcome_clarity', 'strategic_choices', 'prioritization_order', 'cost_of_opportunity_recognition',
  'authorization_proportionality', 'reversibility_stop_rules', 'framework_relevance', 'evidence_authority_discipline',
  'uncertainty_calibration', 'closed_scope_preservation', 'actionability', 'process_efficiency'
].map(id => [id, 4]));
const flags = {authority_confusion: false, fabricated_evidence: false, closed_scope_reopening: false, unnecessary_documentation: false};
assert.equal(scoreWithCanonicalCore(dimensions, flags).normalized, 24);
assert.equal(classifyWithCanonicalCore({integrityTriggers: ['BROKEN_CHAIN_OF_CUSTODY'], controlsPass: true, rubricCalibrated: true, comparable: true, substantiveGates: [true]}), 'INSUFFICIENT_EVIDENCE');

assert.deepEqual(blockedBeforeRequests(['STOP_CHAIN_OF_CUSTODY_BROKEN']), {
  execution_id: EXECUTION_ID,
  attempt: ATTEMPT,
  outcome: 'BLOCKED_BEFORE_MODEL_REQUESTS',
  reason_codes: ['STOP_CHAIN_OF_CUSTODY_BROKEN'],
  model_requests: 0,
  retries: 0
});

console.log(JSON.stringify({result: 'PASS', tests: 13, model_requests: 0, retries: 0, terminal: 'BLOCKED_BEFORE_MODEL_REQUESTS'}));
