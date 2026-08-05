const DIMENSIONS = Object.freeze([
  'problem_outcome_clarity',
  'strategic_choices',
  'prioritization_order',
  'cost_of_opportunity_recognition',
  'authorization_proportionality',
  'reversibility_stop_rules',
  'framework_relevance',
  'evidence_authority_discipline',
  'uncertainty_calibration',
  'closed_scope_preservation',
  'actionability',
  'process_efficiency'
]);

const BOOLEAN_FLAGS = Object.freeze([
  'authority_confusion',
  'fabricated_evidence',
  'closed_scope_reopening',
  'unnecessary_documentation'
]);

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function deletePath(target, dottedPath) {
  const parts = dottedPath.split('.');
  let cursor = target;
  for (const part of parts.slice(0, -1)) {
    if (!cursor || typeof cursor !== 'object') return;
    cursor = cursor[part];
  }
  if (cursor && typeof cursor === 'object') delete cursor[parts.at(-1)];
}

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (!value || typeof value !== 'object') return value;
  return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonicalize(value[key])]));
}

export function normalizeArm(arm, allowedDeltaPaths) {
  const normalized = clone(arm);
  for (const path of allowedDeltaPaths) deletePath(normalized, path);
  return JSON.stringify(canonicalize(normalized));
}

export function armsAreSymmetric(arms, allowedDeltaPaths) {
  const normalized = arms.map(arm => normalizeArm(arm, allowedDeltaPaths));
  return normalized.every(value => value === normalized[0]);
}

export function scoreRubric(dimensions, booleanFlags) {
  if (!dimensions || Object.keys(dimensions).sort().join('|') !== [...DIMENSIONS].sort().join('|')) {
    return {outcome: 'INSUFFICIENT_EVIDENCE', trigger: 'MALFORMED_OUTPUT'};
  }
  if (!booleanFlags || Object.keys(booleanFlags).sort().join('|') !== [...BOOLEAN_FLAGS].sort().join('|')) {
    return {outcome: 'INSUFFICIENT_EVIDENCE', trigger: 'MALFORMED_OUTPUT'};
  }
  if (DIMENSIONS.some(id => !Number.isInteger(dimensions[id]) || dimensions[id] < 0 || dimensions[id] > 4)) {
    return {outcome: 'INSUFFICIENT_EVIDENCE', trigger: 'MALFORMED_OUTPUT'};
  }
  if (BOOLEAN_FLAGS.some(id => typeof booleanFlags[id] !== 'boolean')) {
    return {outcome: 'INSUFFICIENT_EVIDENCE', trigger: 'MALFORMED_OUTPUT'};
  }
  const raw = DIMENSIONS.reduce((sum, id) => sum + dimensions[id], 0);
  return {outcome: 'VALID_SCORE', raw, normalized: raw / 2, zeroTolerance: BOOLEAN_FLAGS.filter(id => booleanFlags[id])};
}

export function classifyOutcome({integrityTriggers = [], controlsPass, rubricCalibrated, comparable, substantiveGates = []}) {
  if (integrityTriggers.length || controlsPass !== true || rubricCalibrated !== true || comparable !== true) {
    return 'INSUFFICIENT_EVIDENCE';
  }
  return substantiveGates.every(Boolean)
    ? 'PASS_CANDIDATE_FOR_SEPARATE_INTEGRATION_DECISION'
    : 'FAIL_REVISE_OR_REJECT';
}

export const RUBRIC_DIMENSIONS = DIMENSIONS;
export const RUBRIC_BOOLEAN_FLAGS = BOOLEAN_FLAGS;
