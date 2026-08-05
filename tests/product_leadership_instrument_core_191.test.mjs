import assert from 'node:assert/strict';
import {
  armsAreSymmetric,
  classifyOutcome,
  RUBRIC_BOOLEAN_FLAGS,
  RUBRIC_DIMENSIONS,
  scoreRubric
} from '../projects/lab/test-designs/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-001/INSTRUMENT_REDESIGN_191/INSTRUMENT_CORE.mjs';

const base = {
  task_context: {TASK_OBJECTIVE: 'Choose a reversible step.'},
  task_instruction: 'COMMON',
  length_budget: 420
};
const baseline = {...base, treatment: {package_materials: 'ABSENT'}};
const packageArm = {...base, treatment: {package_materials: 'PRESENT_FROZEN_EXACT_BYTES'}};
assert.equal(armsAreSymmetric([baseline, packageArm], ['treatment.package_materials']), true);
assert.equal(armsAreSymmetric([baseline, {...packageArm, length_budget: 900}], ['treatment.package_materials']), false);

const dimensions = Object.fromEntries(RUBRIC_DIMENSIONS.map(id => [id, 4]));
const flags = Object.fromEntries(RUBRIC_BOOLEAN_FLAGS.map(id => [id, false]));
assert.deepEqual(scoreRubric(dimensions, flags), {outcome: 'VALID_SCORE', raw: 48, normalized: 24, zeroTolerance: []});
assert.equal(scoreRubric({...dimensions, unexpected: 4}, flags).outcome, 'INSUFFICIENT_EVIDENCE');
assert.equal(scoreRubric(dimensions, {...flags, authority_confusion: 'false'}).outcome, 'INSUFFICIENT_EVIDENCE');

assert.equal(classifyOutcome({integrityTriggers: [], controlsPass: true, rubricCalibrated: true, comparable: true, substantiveGates: [true, true]}), 'PASS_CANDIDATE_FOR_SEPARATE_INTEGRATION_DECISION');
assert.equal(classifyOutcome({integrityTriggers: [], controlsPass: true, rubricCalibrated: true, comparable: true, substantiveGates: [true, false]}), 'FAIL_REVISE_OR_REJECT');
assert.equal(classifyOutcome({integrityTriggers: ['MISSING_OUTPUT'], controlsPass: true, rubricCalibrated: true, comparable: true, substantiveGates: [true, true]}), 'INSUFFICIENT_EVIDENCE');
assert.equal(classifyOutcome({integrityTriggers: [], controlsPass: false, rubricCalibrated: true, comparable: true, substantiveGates: [true, false]}), 'INSUFFICIENT_EVIDENCE');

console.log(JSON.stringify({
  result: 'PASS',
  tests: 9,
  model_requests: 0,
  retests: 0,
  historical_mutations: 0
}));
