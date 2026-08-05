import {
  armsAreSymmetric,
  classifyOutcome,
  scoreRubric
} from '../../test-designs/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-001/INSTRUMENT_REDESIGN_191/INSTRUMENT_CORE.mjs';

export const EXECUTION_ID = 'PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-005';
export const ATTEMPT = 'ATTEMPT-004';
export const REQUEST_LIMIT = 41;
export const RETRY_LIMIT = 0;
export const CANONICAL_CORE_DEPENDENCY = 'INSTRUMENT_REDESIGN_191/INSTRUMENT_CORE.mjs';

export function verifyArmPair(arms, allowedDeltaPaths) {
  return armsAreSymmetric(arms, allowedDeltaPaths);
}

export function scoreWithCanonicalCore(dimensions, flags) {
  return scoreRubric(dimensions, flags);
}

export function classifyWithCanonicalCore(input) {
  return classifyOutcome(input);
}

export function assertRequestEligibility({custodyPass, authenticationPass, requestsSent = 0, retries = 0}) {
  if (retries !== 0) throw new Error('STOP_RETRY_ATTEMPTED');
  if (requestsSent >= REQUEST_LIMIT) throw new Error('STOP_REQUEST_BUDGET_EXCEEDED');
  if (custodyPass !== true) throw new Error('STOP_CHAIN_OF_CUSTODY_BROKEN');
  if (authenticationPass !== true) throw new Error('STOP_EXACT_AUTHENTICATION_UNAVAILABLE');
  return true;
}

export function blockedBeforeRequests(reasonCodes) {
  return Object.freeze({
    execution_id: EXECUTION_ID,
    attempt: ATTEMPT,
    outcome: 'BLOCKED_BEFORE_MODEL_REQUESTS',
    reason_codes: [...reasonCodes],
    model_requests: 0,
    retries: 0
  });
}

// This adapter intentionally exposes no provider client and performs no request by itself.
// Provider execution was not eligible in ATTEMPT-004; the historical runner is never imported.
