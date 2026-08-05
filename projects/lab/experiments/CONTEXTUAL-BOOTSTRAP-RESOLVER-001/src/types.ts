export type Route =
  | 'CONTINUITY_RESUME'
  | 'PROJECT_CONTINUATION'
  | 'NEW_DESIGN'
  | 'CODE_CHANGE'
  | 'STATUS_OR_AUTHORITY'
  | 'AUDIT_OR_REASSESSMENT'
  | 'UNKNOWN_ESCALATION';

export type RiskClass = 'SMALL_CLEAR' | 'MEDIUM' | 'UNCERTAIN' | 'CRITICAL';
export type TerminalState =
  | 'READY'
  | 'READ_ONLY_READY'
  | 'AWAITING_AUTHORIZATION'
  | 'RESOLUTION_REQUIRED'
  | 'INSUFFICIENT_CONTEXT'
  | 'BLOCKED_HEAD_MISMATCH'
  | 'BLOCKED_UNKNOWN_OWNER'
  | 'BLOCKED_INVALID_MANIFEST';

export type SourceBucket = 'always' | 'required' | 'filtered' | 'onTrigger' | 'auditOnly' | 'historicalReference';

export interface ProjectRecord {
  id: string;
  aliases: string[];
  repository: string;
  branch: string;
  headSha: string;
  namespace: string;
}

export interface SourceRecord {
  path: string;
  repository: string;
  branch: string;
  headSha: string;
  projectId?: string;
  namespace: string;
  kind: string;
  status: string;
  authorityClass: string;
  tags: string[];
  surfaces: string[];
  bytes: number;
  digest: string;
  references?: string[];
  canonicalKey?: string;
  canonicalValue?: string;
  current?: boolean;
}

export interface AuthorizationRecord {
  id: string;
  status: 'GRANTED' | 'CONSUMED' | 'REVOKED' | 'EXPIRED' | 'PROPOSED';
  repository: string;
  branch: string;
  headSha: string;
  allowedActions: string[];
  allowedPaths: string[];
  forbiddenActions: string[];
}

export interface FixtureCatalog {
  projects: ProjectRecord[];
  sources: SourceRecord[];
  authorizations: AuthorizationRecord[];
}

export interface ResolverInput {
  prompt: string;
  executionSurface: 'CHATGPT' | 'CODEX_DESKTOP' | 'CLI' | 'CI';
  repositoryHint?: string;
  projectHint?: string;
  continuityHint?: string;
  explicitPaths?: string[];
  verifiedHeads?: Record<string, string>;
  catalog: FixtureCatalog;
}

export interface ResolvedSource {
  path: string;
  repository: string;
  commitSha: string;
  namespace: string;
  reason: string[];
  bytes: number;
  digest: string;
}

export interface ConflictRecord {
  key: string;
  paths: string[];
  values: string[];
}

export interface ContextManifest {
  schemaVersion: '1.0.0';
  resolverVersion: string;
  route: Route;
  riskClass: RiskClass;
  target: {
    projectId?: string;
    repository?: string;
    branch?: string;
    headSha?: string;
    namespace?: string;
  };
  authority: {
    effect: 'READ_ONLY' | 'BOUNDED_EXECUTION' | 'NONE';
    authorizationId?: string;
    lifecycleStatus?: string;
    allowedActions: string[];
    allowedPaths: string[];
    forbiddenActions: string[];
  };
  sources: Record<SourceBucket, ResolvedSource[]>;
  exclusions: {
    namespaces: string[];
    repositories: string[];
    paths: string[];
    reasons: string[];
  };
  conflicts: {
    state: 'NONE' | 'CONFIRMED' | 'RESOLUTION_REQUIRED';
    items: ConflictRecord[];
  };
  budget: {
    selectedSources: number;
    selectedBytes: number;
    fullCorpusBytes: number;
    reductionPercent: number;
    estimatedTokens: number;
  };
  escalationTriggers: string[];
  trace: {
    selectionReasonByPath: Record<string, string[]>;
    omittedCandidatePaths: string[];
    canonicalParentDigests: Record<string, string>;
  };
  terminalState: TerminalState;
}

export interface PublicFixture {
  id: string;
  description: string;
  input: ResolverInput;
}

export interface OracleFixture {
  id: string;
  expectedRoute: Route;
  expectedRisk: RiskClass;
  expectedTerminal: TerminalState;
  expectedSelectedPaths: string[];
  forbiddenSelectedPaths: string[];
  criticalPaths: string[];
  expectedConflictState: 'NONE' | 'RESOLUTION_REQUIRED';
}
