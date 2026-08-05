import type {
  AuthorizationRecord,
  ConflictRecord,
  ContextManifest,
  ProjectRecord,
  ResolvedSource,
  ResolverInput,
  RiskClass,
  Route,
  SourceBucket,
  SourceRecord,
  TerminalState,
} from './types.js';

const RESOLVER_VERSION = '0.1.0-experimental';
const BUCKETS: SourceBucket[] = ['always', 'required', 'filtered', 'onTrigger', 'auditOnly', 'historicalReference'];

function normalize(value: string): string {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();
}

function hasAny(text: string, needles: string[]): boolean {
  return needles.some((needle) => text.includes(needle));
}

function unique<T>(values: T[]): T[] {
  return [...new Set(values)];
}

function findProject(input: ResolverInput): { project: ProjectRecord | undefined; ambiguous: boolean; unknownHint: boolean } {
  const projects = input.catalog.projects;
  if (input.projectHint) {
    const hint = normalize(input.projectHint);
    const exact = projects.find((p) => normalize(p.id) === hint || p.aliases.some((a) => normalize(a) === hint));
    return { project: exact, ambiguous: false, unknownHint: !exact };
  }

  const prompt = normalize(input.prompt);
  const matches = projects.filter((project) =>
    [project.id, ...project.aliases].some((alias) => prompt.includes(normalize(alias))),
  );
  if (matches.length === 1) return { project: matches[0], ambiguous: false, unknownHint: false };
  return { project: undefined, ambiguous: matches.length > 1, unknownHint: false };
}

function classifyRoute(input: ResolverInput, project?: ProjectRecord): Route {
  const text = normalize(`${input.prompt} ${input.continuityHint ?? ''}`);
  if (
    input.continuityHint ||
    hasAny(text, ['continuemos', 'retomemos', 'quedo pendiente', 'protocolo de continuidad', 'continue from continuity'])
  ) {
    return 'CONTINUITY_RESUME';
  }
  if (hasAny(text, ['estado', 'autorizacion', 'autoridad', 'permiso vigente', 'status', 'authority'])) {
    return 'STATUS_OR_AUTHORITY';
  }
  if (
    hasAny(text, [
      'audita',
      'auditoria',
      'reassessment',
      'reevalua',
      'revisa por que fallo',
      'por que fallo',
      'failure analysis',
      'fallo el despliegue',
    ])
  ) {
    return 'AUDIT_OR_REASSESSMENT';
  }
  if (hasAny(text, ['nuevo diseno', 'crea un hero', 'disena', 'crea una landing', 'new design', 'landing page'])) {
    return 'NEW_DESIGN';
  }
  if (hasAny(text, ['corrige', 'implementa', 'modifica', 'codigo', 'code change', 'despliega', 'deploy'])) {
    return 'CODE_CHANGE';
  }
  if (project) return 'PROJECT_CONTINUATION';
  return 'UNKNOWN_ESCALATION';
}

function classifyRisk(route: Route, input: ResolverInput, project?: ProjectRecord): RiskClass {
  const text = normalize(input.prompt);
  if (route === 'AUDIT_OR_REASSESSMENT') {
    return hasAny(text, ['despliegue', 'deploy', 'credencial', 'security', 'iam', 'produccion']) ? 'CRITICAL' : 'UNCERTAIN';
  }
  if (route === 'STATUS_OR_AUTHORITY') return 'MEDIUM';
  if (route === 'CODE_CHANGE') {
    if (hasAny(text, ['despliega', 'deploy', 'credencial', 'secret', 'runtime', 'produccion'])) return 'CRITICAL';
    if ((input.explicitPaths?.length ?? 0) <= 2 && hasAny(text, ['corrige', 'fix', 'ajusta'])) return 'SMALL_CLEAR';
    return 'MEDIUM';
  }
  if (route === 'NEW_DESIGN') return project ? 'MEDIUM' : 'SMALL_CLEAR';
  if (route === 'CONTINUITY_RESUME' || route === 'PROJECT_CONTINUATION') return 'MEDIUM';
  return 'UNCERTAIN';
}

function actionFromPrompt(prompt: string): string {
  const text = normalize(prompt);
  if (hasAny(text, ['despliega', 'deploy'])) return 'DEPLOY';
  if (hasAny(text, ['implementa'])) return 'IMPLEMENT';
  if (hasAny(text, ['corrige', 'modifica', 'ajusta', 'fix'])) return 'MODIFY';
  return 'WRITE';
}

function pathAllowed(path: string, allowedPaths: string[]): boolean {
  return allowedPaths.some((allowed) => {
    if (allowed === '*') return true;
    if (allowed.endsWith('/**')) return path.startsWith(allowed.slice(0, -3));
    return path === allowed;
  });
}

function activeAuthorization(
  input: ResolverInput,
  project: ProjectRecord | undefined,
  requiredAction: string,
): AuthorizationRecord | undefined {
  if (!project) return undefined;
  const verifiedHead = input.verifiedHeads?.[project.repository];
  return input.catalog.authorizations.find(
    (authorization) =>
      authorization.status === 'GRANTED' &&
      authorization.repository === project.repository &&
      authorization.branch === project.branch &&
      authorization.headSha === verifiedHead &&
      (authorization.allowedActions.includes(requiredAction) || authorization.allowedActions.includes('*')) &&
      (input.explicitPaths ?? []).every((path) => pathAllowed(path, authorization.allowedPaths)),
  );
}

function sourceMatchesProject(source: SourceRecord, project?: ProjectRecord): boolean {
  if (!project) return source.projectId === undefined;
  return source.projectId === project.id || source.projectId === undefined;
}

function extractSurface(prompt: string): string[] {
  const text = normalize(prompt);
  const surfaces: string[] = [];
  for (const surface of ['hero', 'motion', 'counter', 'icon', 'deployment', 'footer', 'responsive', 'authorization', 'security']) {
    if (text.includes(surface)) surfaces.push(surface);
  }
  if (text.includes('anim')) surfaces.push('motion');
  if (text.includes('despliegue') || text.includes('deploy')) surfaces.push('deployment');
  return unique(surfaces);
}

function resolveSource(source: SourceRecord, reason: string[]): ResolvedSource {
  return {
    path: source.path,
    repository: source.repository,
    commitSha: source.headSha,
    namespace: source.namespace,
    reason,
    bytes: source.bytes,
    digest: source.digest,
  };
}

export function resolveContext(input: ResolverInput): ContextManifest {
  const projectResolution = findProject(input);
  const project = projectResolution.project;
  const route = classifyRoute(input, project);
  const riskClass = classifyRisk(route, input, project);
  const prompt = normalize(input.prompt);
  const surfaceTags = extractSurface(input.prompt);
  const selection = new Map<string, { bucket: SourceBucket; source: SourceRecord; reasons: string[] }>();

  const add = (source: SourceRecord | undefined, bucket: SourceBucket, reason: string): void => {
    if (!source) return;
    const existing = selection.get(source.path);
    if (existing) {
      existing.reasons.push(reason);
      const currentIndex = BUCKETS.indexOf(existing.bucket);
      const requestedIndex = BUCKETS.indexOf(bucket);
      if (requestedIndex < currentIndex) existing.bucket = bucket;
      return;
    }
    selection.set(source.path, { bucket, source, reasons: [reason] });
  };

  const sources = input.catalog.sources;
  const kinds = (kind: string): SourceRecord[] => sources.filter((source) => source.kind === kind);
  const projectKinds = (kind: string): SourceRecord[] =>
    kinds(kind).filter((source) => sourceMatchesProject(source, project));

  for (const source of kinds('OPERATING_RULES')) add(source, 'always', 'stable operating rules');

  if (route === 'STATUS_OR_AUTHORITY' || route === 'AUDIT_OR_REASSESSMENT') {
    for (const kind of ['START_HERE', 'LAB_CONTRACT', 'METHODOLOGY']) {
      for (const source of kinds(kind)) add(source, 'required', `governance required for ${route}`);
    }
  }

  if (route === 'STATUS_OR_AUTHORITY') {
    for (const kind of ['CURRENT_STATE', 'REGISTRY_INDEX', 'PROJECT_REGISTRY']) {
      for (const source of kinds(kind)) add(source, 'required', 'canonical status resolution');
    }
    for (const source of projectKinds('PROJECT_STATE')) add(source, 'required', 'target project state');
    for (const source of kinds('AUTHORIZATION')) {
      const idMatch = source.tags.some((tag) => prompt.includes(normalize(tag)));
      const activeForTarget =
        source.status === 'GRANTED' &&
        Boolean(project && (source.projectId === project.id || (project.id === 'lab' && source.projectId === undefined)));
      if (idMatch || activeForTarget) {
        add(source, 'required', idMatch ? 'explicit authorization reference' : 'active authorization for target');
      }
    }
  }

  if (route === 'CONTINUITY_RESUME') {
    for (const source of projectKinds('PROJECT_STATE')) add(source, 'required', 'target project state');
    const continuitySources = projectKinds('CONTINUITY');
    for (const source of continuitySources) {
      add(source, 'required', 'continuity resume pointer');
      for (const reference of source.references ?? []) {
        add(sources.find((candidate) => candidate.path === reference), 'required', `referenced by ${source.path}`);
      }
    }
  }

  if (route === 'PROJECT_CONTINUATION') {
    for (const source of projectKinds('PROJECT_STATE')) add(source, 'required', 'target project state');
    for (const source of projectKinds('CONTINUITY').filter((item) => item.current !== false)) {
      add(source, 'filtered', 'current continuity available');
    }
  }

  if (route === 'NEW_DESIGN') {
    for (const source of kinds('CRITERION_SELECTOR')) add(source, 'required', 'design criterion selector');
    for (const source of kinds('VISUAL_FOUNDATION')) add(source, 'required', 'minimum visual foundation');
    for (const source of projectKinds('PROJECT_STATE')) add(source, 'required', 'known project state');
    for (const source of projectKinds('BRAND_ASSETS')) add(source, 'required', 'project brand assets');
    for (const source of projectKinds('ERROR')) {
      if (source.surfaces.some((surface) => surfaceTags.includes(surface))) {
        add(source, 'onTrigger', 'surface-specific prior error');
      }
    }
  }

  if (route === 'CODE_CHANGE') {
    for (const source of projectKinds('PROJECT_STATE')) add(source, 'required', 'target project state');
    for (const path of input.explicitPaths ?? []) {
      add(sources.find((source) => source.path === path), 'required', 'explicit path');
    }
    const explicitTags = new Set(
      (input.explicitPaths ?? [])
        .flatMap((path) => path.split(/[\/._-]/))
        .map(normalize)
        .filter((tag) => tag.length > 2),
    );
    for (const source of projectKinds('TEST_FILE')) {
      if (source.tags.some((tag) => explicitTags.has(normalize(tag)))) add(source, 'required', 'test coupled to explicit path');
    }
    for (const source of projectKinds('INCIDENT')) {
      if (source.tags.some((tag) => prompt.includes(normalize(tag))) || source.surfaces.some((s) => surfaceTags.includes(s))) {
        add(source, 'onTrigger', 'applicable confirmed incident');
      }
    }
  }

  if (route === 'AUDIT_OR_REASSESSMENT') {
    for (const source of projectKinds('PROJECT_STATE')) add(source, 'required', 'target project state');
    for (const kind of ['LOG', 'ERROR', 'EVIDENCE', 'AUTHORIZATION', 'CONTINUITY']) {
      for (const source of projectKinds(kind)) {
        const relevant =
          (kind === 'AUTHORIZATION' && Boolean(project && source.projectId === project.id)) ||
          surfaceTags.length === 0 ||
          source.surfaces.some((surface) => surfaceTags.includes(surface)) ||
          source.tags.some((tag) => prompt.includes(normalize(tag)));
        if (relevant) add(source, 'auditOnly', `audit evidence kind=${kind}`);
      }
    }
  }

  if (route === 'UNKNOWN_ESCALATION') {
    for (const kind of ['START_HERE', 'LAB_CONTRACT', 'METHODOLOGY', 'PROJECT_REGISTRY']) {
      for (const source of kinds(kind)) add(source, 'required', 'minimal escalation context');
    }
  }

  if (hasAny(prompt, ['motion', 'anim', 'counter'])) {
    for (const source of kinds('MOTION_SYSTEM')) add(source, 'onTrigger', 'motion trigger');
  }

  const requiredAction = actionFromPrompt(input.prompt);
  const authorization = route === 'CODE_CHANGE' ? activeAuthorization(input, project, requiredAction) : undefined;
  if (authorization) {
    const authSource = sources.find((source) => source.kind === 'AUTHORIZATION' && source.tags.includes(authorization.id));
    add(authSource, 'required', 'active bounded authorization');
  }

  const selectedPaths = new Set(selection.keys());
  const selectedSources = [...selection.values()].map((item) => item.source);
  const conflictGroups = new Map<string, SourceRecord[]>();
  for (const source of selectedSources) {
    if (!source.canonicalKey || source.canonicalValue === undefined) continue;
    const group = conflictGroups.get(source.canonicalKey) ?? [];
    group.push(source);
    conflictGroups.set(source.canonicalKey, group);
  }
  const conflicts: ConflictRecord[] = [];
  for (const [key, group] of conflictGroups) {
    const values = unique(group.map((source) => source.canonicalValue ?? ''));
    if (values.length > 1) conflicts.push({ key, paths: group.map((source) => source.path), values });
  }

  const staleContinuity = selectedSources.some((source) => source.kind === 'CONTINUITY' && source.current === false);
  const targetRepo = project?.repository ?? input.repositoryHint;
  const targetHead = targetRepo ? input.verifiedHeads?.[targetRepo] : undefined;
  const knownRepo = targetRepo
    ? input.catalog.projects.some((candidate) => candidate.repository === targetRepo) || sources.some((source) => source.repository === targetRepo)
    : true;
  const expectedHead = project?.headSha;
  const headMismatch = Boolean(expectedHead && targetHead && expectedHead !== targetHead);
  const missingSelectedPath = [...selectedPaths].some((path) => !sources.some((source) => source.path === path));
  const missingContinuity = route === 'CONTINUITY_RESUME' && projectKinds('CONTINUITY').length === 0;
  const missingDesignInputs =
    route === 'NEW_DESIGN' &&
    (kinds('CRITERION_SELECTOR').length === 0 ||
      kinds('VISUAL_FOUNDATION').length === 0 ||
      Boolean(project && projectKinds('BRAND_ASSETS').length === 0));

  let terminalState: TerminalState;
  if (projectResolution.unknownHint || projectResolution.ambiguous || !knownRepo) terminalState = 'BLOCKED_UNKNOWN_OWNER';
  else if (headMismatch) terminalState = 'BLOCKED_HEAD_MISMATCH';
  else if (missingSelectedPath) terminalState = 'BLOCKED_INVALID_MANIFEST';
  else if (conflicts.length > 0 || staleContinuity) terminalState = 'RESOLUTION_REQUIRED';
  else if (route === 'UNKNOWN_ESCALATION' || missingContinuity || missingDesignInputs) terminalState = 'INSUFFICIENT_CONTEXT';
  else if (route === 'CODE_CHANGE' && !authorization) terminalState = 'AWAITING_AUTHORIZATION';
  else if (route === 'CODE_CHANGE') terminalState = 'READY';
  else terminalState = 'READ_ONLY_READY';

  const sourceBuckets: Record<SourceBucket, ResolvedSource[]> = {
    always: [],
    required: [],
    filtered: [],
    onTrigger: [],
    auditOnly: [],
    historicalReference: [],
  };
  const selectionReasonByPath: Record<string, string[]> = {};
  for (const item of selection.values()) {
    const reasons = unique(item.reasons);
    sourceBuckets[item.bucket].push(resolveSource(item.source, reasons));
    selectionReasonByPath[item.source.path] = reasons;
  }
  for (const bucket of BUCKETS) sourceBuckets[bucket].sort((a, b) => a.path.localeCompare(b.path));

  const selectedBytes = selectedSources.reduce((sum, source) => sum + source.bytes, 0);
  const fullCorpusBytes = sources.reduce((sum, source) => sum + source.bytes, 0);
  const reductionPercent = fullCorpusBytes === 0 ? 0 : Number((((fullCorpusBytes - selectedBytes) / fullCorpusBytes) * 100).toFixed(3));
  const omitted = sources.filter((source) => !selectedPaths.has(source.path));
  const targetNamespaces = new Set(selectedSources.map((source) => source.namespace));
  const targetRepositories = new Set(selectedSources.map((source) => source.repository));

  return {
    schemaVersion: '1.0.0',
    resolverVersion: RESOLVER_VERSION,
    route,
    riskClass,
    target: {
      ...(project ? { projectId: project.id, repository: project.repository, branch: project.branch, headSha: targetHead ?? project.headSha, namespace: project.namespace } : {}),
      ...(!project && input.repositoryHint ? { repository: input.repositoryHint } : {}),
    },
    authority: authorization
      ? {
          effect: 'BOUNDED_EXECUTION',
          authorizationId: authorization.id,
          lifecycleStatus: authorization.status,
          allowedActions: authorization.allowedActions,
          allowedPaths: authorization.allowedPaths,
          forbiddenActions: authorization.forbiddenActions,
        }
      : {
          effect: route === 'CODE_CHANGE' ? 'NONE' : 'READ_ONLY',
          allowedActions: route === 'CODE_CHANGE' ? [] : ['READ', 'RESOLVE_CONTEXT'],
          allowedPaths: selectedSources.map((source) => source.path),
          forbiddenActions: route === 'CODE_CHANGE' ? ['WRITE_WITHOUT_ACTIVE_AUTHORIZATION'] : ['CANONICAL_WRITE'],
        },
    sources: sourceBuckets,
    exclusions: {
      namespaces: unique(omitted.map((source) => source.namespace).filter((namespace) => !targetNamespaces.has(namespace))).sort(),
      repositories: unique(omitted.map((source) => source.repository).filter((repository) => !targetRepositories.has(repository))).sort(),
      paths: omitted.map((source) => source.path).sort(),
      reasons: ['DEFAULT_DENY', 'NOT_JUSTIFIED_BY_ROUTE_OR_TRIGGER'],
    },
    conflicts: {
      state: conflicts.length > 0 || staleContinuity ? 'RESOLUTION_REQUIRED' : 'NONE',
      items: conflicts,
    },
    budget: {
      selectedSources: selectedSources.length,
      selectedBytes,
      fullCorpusBytes,
      reductionPercent,
      estimatedTokens: Math.ceil(selectedBytes / 4),
    },
    escalationTriggers: [
      'HEAD_MISMATCH',
      'UNKNOWN_OWNER',
      'STALE_CONTINUITY',
      'AUTHORIZATION_CONFLICT',
      'CANONICAL_CONFLICT',
      'PATH_OUTSIDE_ALLOWLIST',
      'MATERIAL_SCOPE_EXPANSION',
    ],
    trace: {
      selectionReasonByPath,
      omittedCandidatePaths: omitted.map((source) => source.path).sort(),
      canonicalParentDigests: Object.fromEntries(selectedSources.map((source) => [source.path, source.digest])),
    },
    terminalState,
  };
}
