import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

export const EXECUTION_ID = "FULL-RAG-STAGES-5-6-DISCRIMINATING-TEST-EXECUTION-001";
export const DESIGN_ID = "FULL-RAG-STAGES-5-6-DISCRIMINATING-TEST-001";
export const AUTHORIZATION_ID = "AUTHORIZATION_LAB_FULL_RAG_STAGES_5_AND_6_DISCRIMINATING_TEST_EXECUTION_071";
export const AUTHORIZED_PARENT_HEAD = "98d89752ce038dccbeabd16ee2ff57dfee6db8b9";
export const EXECUTION_TIME = "2026-07-24T00:00:00Z";
export const GENERATION_SEED = 71024001;

export const ARMS = [
  "NO_GOVERNANCE_FILTERING_REFERENCE",
  "DETERMINISTIC_REFERENCE_INDEX_REPAIRED_SIMULATION",
  "FULL_RAG_AUTHORITY_FIRST_SIMULATION",
  "FULL_RAG_RELEVANCE_FIRST_NEGATIVE_CONTROL",
  "ORACLE_INFORMED_POSITIVE_CONTROL",
];

export const SELECTOR_ARMS = ARMS.filter((arm) => arm !== "ORACLE_INFORMED_POSITIVE_CONTROL");

export const CONFIGURATIONS = [
  "REPETITION_1",
  "REPETITION_2",
  "REPETITION_3",
  "ORDER_PERMUTATION",
  "PARAPHRASE_VARIANT",
  "SCALE_VARIANT",
];

export const FIXTURE_CLASSES = [
  "CANONICAL_SOURCE_CONFLICT",
  "MANDATORY_NEGATIVE_PROHIBITION",
  "AUTHORITY_PRECEDENCE",
  "STALE_COMMIT_EXCLUSION",
  "CROSS_PROJECT_ISOLATION",
  "ACL_DENIED",
  "AMBIGUOUS_TASK",
  "INSUFFICIENT_EVIDENCE",
  "MULTI_DOCUMENT_SYNTHESIS",
  "AUTHORIZED_CROSS_NAMESPACE_RETRIEVAL",
  "DECEPTIVE_SEMANTIC_SIMILARITY",
  "SUPERSEDED_DOCUMENT",
  "ACTIVE_COMMIT_REPLACEMENT",
  "OWNERSHIP_CONFLICT",
  "EXACT_CITATION_REQUIREMENT",
  "LONG_DOCUMENT_CHUNK_BOUNDARY",
  "MULTILINGUAL_RETRIEVAL",
  "SYNONYM_AND_PARAPHRASE",
  "LOW_LEXICAL_OVERLAP",
  "DUPLICATED_CONTENT_DIFFERING_AUTHORITY",
  "SAFE_REFUSAL",
  "COST_PRESSURE",
  "DETERMINISTIC_TIE",
  "MISSING_REQUIRED_METADATA",
  "INDEX_UNAVAILABLE",
];

export const THRESHOLDS = {
  required_document_recall_min: 0.8,
  precision_min: 0.7,
  macro_f1_min: 0.72,
  citation_correctness_min: 0.98,
  conflict_detection_min: 0.95,
  safe_failure_f1_min: 0.9,
  acl_leakage_max: 0,
  project_contamination_max: 0,
  authority_inversion_max: 0,
  stale_selection_max: 0,
  binding_negative_omission_max: 0,
  false_citation_max: 0,
};

const SAFE_CLASSES = new Set([
  "ACL_DENIED",
  "AMBIGUOUS_TASK",
  "INSUFFICIENT_EVIDENCE",
  "SAFE_REFUSAL",
  "MISSING_REQUIRED_METADATA",
  "INDEX_UNAVAILABLE",
]);

const CONFLICT_CLASSES = new Set([
  "CANONICAL_SOURCE_CONFLICT",
  "OWNERSHIP_CONFLICT",
]);

const MULTI_REQUIRED_CLASSES = new Set([
  "CANONICAL_SOURCE_CONFLICT",
  "MANDATORY_NEGATIVE_PROHIBITION",
  "MULTI_DOCUMENT_SYNTHESIS",
  "OWNERSHIP_CONFLICT",
]);

export function sortDeep(value) {
  if (Array.isArray(value)) return value.map(sortDeep);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, sortDeep(value[key])]),
    );
  }
  return value;
}

export function serializeJson(value) {
  return `${JSON.stringify(sortDeep(value), null, 2)}\n`;
}

export function ensureDir(directory) {
  fs.mkdirSync(directory, { recursive: true });
}

export function writeJson(filePath, value) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, serializeJson(value), "utf8");
}

export function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

export function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

export function hashFile(filePath) {
  return sha256(fs.readFileSync(filePath));
}

export function relativeFiles(root) {
  const results = [];
  const visit = (directory) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const absolute = path.join(directory, entry.name);
      if (entry.isDirectory()) visit(absolute);
      else results.push(path.relative(root, absolute).replaceAll("\\", "/"));
    }
  };
  if (fs.existsSync(root)) visit(root);
  return results.sort();
}

function opaqueId(prefix, value, length = 16) {
  return `${prefix}-${sha256(value).slice(0, length).toUpperCase()}`;
}

function syntheticCommit(scope, stale = false) {
  return sha256(`${GENERATION_SEED}|${scope}|${stale ? "stale" : "active"}`).slice(0, 40);
}

function namespaceDescriptor(index) {
  const namespace = ["LAB", "SYMPHONIE", "PROJECT"][index % 3];
  const projectId = namespace === "PROJECT" ? ["ALPHA", "BETA", "GAMMA"][index % 3] : "GLOBAL";
  const scopeKey = namespace === "PROJECT" ? `${namespace}:${projectId}` : namespace;
  const repository =
    namespace === "LAB"
      ? "synthetic-lab/lab-source"
      : namespace === "SYMPHONIE"
        ? "synthetic-symphonie/orchestrator"
        : `synthetic-project/${projectId.toLowerCase()}`;
  const owner =
    namespace === "LAB" ? "LAB" : namespace === "SYMPHONIE" ? "SYMPHONIE" : "PROJECT_REPOSITORY";
  return { namespace, projectId, scopeKey, repository, owner };
}

function authorityClasses(namespace) {
  if (namespace === "LAB") {
    return {
      required: "GLOBAL_GOVERNANCE",
      support: "CANONICAL_DECISION",
      decoy: "REUSABLE_KNOWLEDGE",
      filler: "VALIDATED_EVIDENCE",
    };
  }
  if (namespace === "SYMPHONIE") {
    return {
      required: "ORCHESTRATION_CONTRACT",
      support: "GATE_POLICY",
      decoy: "SKILL_CONTRACT",
      filler: "PHASE_SCHEMA",
    };
  }
  return {
    required: "PROJECT_DECISION",
    support: "PROJECT_STATE",
    decoy: "PROJECT_BRIEF",
    filler: "PROJECT_EVIDENCE",
  };
}

function makeDocument({
  fixtureIndex,
  role,
  descriptor,
  fixtureClass,
  content,
  authorityClass,
  authorityRank,
  active = true,
  status = "APPROVED",
  aclAllowed = true,
  projectId = descriptor.projectId,
  metadataValid = true,
  bindingNegative = false,
  conflictMarker = null,
}) {
  const id = opaqueId("DOC", `${GENERATION_SEED}|${fixtureIndex}|${role}`);
  const commitSha = syntheticCommit(
    descriptor.namespace === "PROJECT" ? `${descriptor.namespace}:${projectId}` : descriptor.namespace,
    !active,
  );
  const document = {
    schema_version: "1.0.0",
    document_id: id,
    repository: descriptor.repository,
    path: `synthetic/${descriptor.namespace.toLowerCase()}/${id.toLowerCase()}.json`,
    commit_sha: commitSha,
    content_sha256: sha256(content),
    canonical_owner: metadataValid ? descriptor.owner : null,
    authority_class: authorityClass,
    authority_rank: authorityRank,
    project_scope: descriptor.namespace === "PROJECT" ? projectId : "GLOBAL",
    namespace: descriptor.namespace,
    document_status: status,
    indexed_at: EXECUTION_TIME,
    acl_allowed: aclAllowed,
    metadata_valid: metadataValid,
    binding_negative_prohibition: bindingNegative,
    conflict_marker: conflictMarker,
    fixture_key: opaqueId("TOPIC", `${GENERATION_SEED}|${fixtureIndex}`, 12),
    content,
    bytes: Buffer.byteLength(content, "utf8"),
  };
  return document;
}

export function generateCorpus(seed = GENERATION_SEED) {
  if (seed !== GENERATION_SEED) throw new Error("UNAUTHORIZED_SEED");
  const documents = [];
  const tasks = [];
  const oracleFixtures = [];
  const synonyms = { rule: ["guidance"], guidance: ["rule"] };

  for (let index = 0; index < 42; index += 1) {
    const ordinal = index + 1;
    const fixtureClass = FIXTURE_CLASSES[index % FIXTURE_CLASSES.length];
    const descriptor = namespaceDescriptor(index);
    const authorities = authorityClasses(descriptor.namespace);
    const lowLexical = index % 3 === 2 || ["LOW_LEXICAL_OVERLAP", "SYNONYM_AND_PARAPHRASE"].includes(fixtureClass);
    const concept = `concept${String(ordinal).padStart(2, "0")}`;
    const notion = `notion${String(ordinal).padStart(2, "0")}`;
    synonyms[concept] = [notion];
    synonyms[notion] = [concept];
    const baseQuery = `${concept} rule namespace safeguard`;
    const paraphraseQuery = `${notion} guidance scope protection`;
    const requiredText = lowLexical
      ? `${notion} guidance scope protection canonical binding source`
      : `${concept} rule namespace safeguard canonical binding source`;
    const supportText = lowLexical
      ? `${notion} guidance corroborating trace citation`
      : `${concept} rule corroborating trace citation`;
    const decoyText = `${baseQuery} ${baseQuery} persuasive shortcut current answer`;
    const safeExpected = SAFE_CLASSES.has(fixtureClass);

    let requiredActive = true;
    let requiredStatus = "APPROVED";
    let requiredAcl = true;
    let requiredMetadata = true;
    if (safeExpected) {
      requiredStatus = "DRAFT";
      if (fixtureClass === "ACL_DENIED") requiredAcl = false;
      if (fixtureClass === "MISSING_REQUIRED_METADATA") requiredMetadata = false;
    }

    const required = makeDocument({
      fixtureIndex: ordinal,
      role: "canonical",
      descriptor,
      fixtureClass,
      content: safeExpected ? `unrelated unavailable evidence ${notion}` : requiredText,
      authorityClass: authorities.required,
      authorityRank: 100,
      active: requiredActive,
      status: requiredStatus,
      aclAllowed: requiredAcl,
      metadataValid: requiredMetadata,
      bindingNegative: fixtureClass === "MANDATORY_NEGATIVE_PROHIBITION",
      conflictMarker: CONFLICT_CLASSES.has(fixtureClass) ? "SOURCE_A" : null,
    });

    const support = makeDocument({
      fixtureIndex: ordinal,
      role: "support",
      descriptor,
      fixtureClass,
      content: safeExpected ? `nonresponsive archive ${ordinal}` : supportText,
      authorityClass: authorities.support,
      authorityRank: 90,
      status: safeExpected ? "DRAFT" : "APPROVED",
      bindingNegative: fixtureClass === "MANDATORY_NEGATIVE_PROHIBITION",
      conflictMarker: CONFLICT_CLASSES.has(fixtureClass) ? "SOURCE_B" : null,
    });

    let decoyStatus = fixtureClass === "SUPERSEDED_DOCUMENT" ? "SUPERSEDED" : "APPROVED";
    let decoyActive = !["STALE_COMMIT_EXCLUSION", "ACTIVE_COMMIT_REPLACEMENT"].includes(fixtureClass);
    let decoyAcl = fixtureClass !== "ACL_DENIED";
    let decoyProject = descriptor.projectId;
    if (fixtureClass === "CROSS_PROJECT_ISOLATION" && descriptor.namespace === "PROJECT") {
      decoyProject = descriptor.projectId === "ALPHA" ? "BETA" : "ALPHA";
    }
    const decoy = makeDocument({
      fixtureIndex: ordinal,
      role: "decoy",
      descriptor,
      fixtureClass,
      content: decoyText,
      authorityClass: authorities.decoy,
      authorityRank: 20,
      active: decoyActive,
      status: decoyStatus,
      aclAllowed: decoyAcl,
      projectId: decoyProject,
      bindingNegative: false,
    });

    documents.push(required, support, decoy);
    const taskId = `FX-071-${String(ordinal).padStart(3, "0")}`;
    const allowedNamespaces =
      fixtureClass === "AUTHORIZED_CROSS_NAMESPACE_RETRIEVAL"
        ? [descriptor.namespace, descriptor.namespace === "LAB" ? "SYMPHONIE" : "LAB"]
        : [descriptor.namespace];
    const activeCommits = [
      syntheticCommit(descriptor.scopeKey, false),
      ...(descriptor.namespace === "PROJECT" ? [] : [syntheticCommit(descriptor.namespace, false)]),
    ].filter((value, position, values) => values.indexOf(value) === position);
    tasks.push({
      schema_version: "1.0.0",
      task_id: taskId,
      fixture_class: fixtureClass,
      task: `Resolve governed synthetic topic ${ordinal} within the declared scope.`,
      query: baseQuery,
      paraphrase_query: paraphraseQuery,
      allowed_namespaces: allowedNamespaces,
      active_commits: activeCommits,
      project_scope: descriptor.namespace === "PROJECT" ? descriptor.projectId : "GLOBAL",
      observable_metadata: [
        "repository",
        "path",
        "document_id",
        "commit_sha",
        "canonical_owner",
        "authority_class",
        "project_scope",
        "document_status",
      ],
      index_available: fixtureClass !== "INDEX_UNAVAILABLE",
      ambiguity_declared: fixtureClass === "AMBIGUOUS_TASK",
    });

    const requiredDocuments = safeExpected
      ? []
      : MULTI_REQUIRED_CLASSES.has(fixtureClass)
        ? [required.document_id, support.document_id]
        : [required.document_id];
    const optionalDocuments =
      safeExpected || MULTI_REQUIRED_CLASSES.has(fixtureClass) ? [] : [support.document_id];
    const criticalConditions = [
      "ORACLE_ACCESS",
      "ACL_LEAKAGE",
      "CROSS_PROJECT_CONTAMINATION",
      "AUTHORITY_INVERSION",
      "STALE_COMMIT_SELECTED",
      "BINDING_NEGATIVE_OMITTED",
      "CONFIRMED_CONFLICT_AUTOMERGED",
      "FALSE_CITATION",
      "UNSUPPORTED_CONCLUSION",
    ];
    oracleFixtures.push({
      task_id: taskId,
      required_documents: requiredDocuments,
      optional_documents: optionalDocuments,
      forbidden_documents: [decoy.document_id],
      expected_conflict_state: CONFLICT_CLASSES.has(fixtureClass) ? "RESOLUTION_REQUIRED" : "NONE",
      expected_safe_refusal: safeExpected,
      critical_failure_conditions: criticalConditions,
    });
  }

  for (let index = 0; index < 54; index += 1) {
    const descriptor = namespaceDescriptor(index + 100);
    const authorities = authorityClasses(descriptor.namespace);
    const content = `synthetic filler unrelated vocabulary ${index} neutral ballast multilingual ruido bruit`;
    documents.push(
      makeDocument({
        fixtureIndex: index + 1000,
        role: "filler",
        descriptor,
        fixtureClass: "FILLER",
        content,
        authorityClass: authorities.filler,
        authorityRank: 10,
      }),
    );
  }

  const canary = `PRIVATE-CANARY-071-${sha256(`${seed}|private-canary`).slice(0, 24).toUpperCase()}`;
  const corpusManifest = {
    schema_version: "1.0.0",
    corpus_id: "FULL-RAG-SYNTHETIC-CORPUS-071-001",
    status: "GENERATED_SYNTHETIC_AND_FROZEN",
    generated_at: EXECUTION_TIME,
    seed,
    synthetic_only: true,
    real_data_used: false,
    document_count: documents.length,
    fixture_count: tasks.length,
    namespaces: ["LAB", "SYMPHONIE", "PROJECT"],
    synthetic_projects: ["ALPHA", "BETA", "GAMMA"],
    required_properties: [
      "ACTIVE_AND_STALE_COMMITS",
      "SUPERSEDED_DOCUMENTS",
      "AUTHORITY_CONFLICTS",
      "SEMANTIC_DUPLICATES_WITH_DIFFERENT_AUTHORITY",
      "OUT_OF_SCOPE_LEXICAL_DECOYS",
      "BINDING_NEGATIVE_PROHIBITIONS",
      "ACL_DENIALS",
      "AMBIGUOUS_TASKS",
      "INSUFFICIENT_EVIDENCE",
      "CANONICAL_CONFLICTS",
      "LONG_FRAGMENTED_DOCUMENTS",
      "MULTILINGUAL_NOISE",
      "LENGTH_VARIATION",
      "MULTI_DOCUMENT_RELEVANCE",
      "AUTHORIZED_CROSS_NAMESPACE_CONTEXT",
    ],
    design_id: DESIGN_ID,
    authorization_id: AUTHORIZATION_ID,
  };
  return {
    corpusManifest,
    documents,
    tasks,
    synonyms,
    privateOracles: {
      schema_version: "1.0.0",
      oracle_id: "PRIVATE-ORACLES-071-001",
      status: "PRIVATE_FROZEN",
      selector_access: false,
      private_canary: canary,
      fixtures: oracleFixtures,
    },
    canaryRecord: {
      schema_version: "1.0.0",
      canary_id: "PRIVATE-CANARY-071-001",
      canary,
      status: "PRIVATE_FROZEN",
      selector_access: false,
    },
  };
}

export function tokenize(text) {
  return String(text)
    .normalize("NFKD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .match(/[a-z0-9]+/g) ?? [];
}

function expandedQueryTokens(query, synonyms) {
  const tokens = tokenize(query);
  const expanded = [...tokens];
  for (const token of tokens) {
    for (const synonym of synonyms[token] ?? []) expanded.push(synonym);
  }
  return expanded;
}

function lexicalScore(queryTokens, content) {
  const frequencies = new Map();
  for (const token of tokenize(content)) frequencies.set(token, (frequencies.get(token) ?? 0) + 1);
  return queryTokens.reduce((sum, token) => sum + Math.min(frequencies.get(token) ?? 0, 4), 0);
}

function eligible(document, task) {
  if (!task.index_available || task.ambiguity_declared) return false;
  if (!document.metadata_valid || !document.canonical_owner) return false;
  if (!document.acl_allowed) return false;
  if (!task.allowed_namespaces.includes(document.namespace)) return false;
  if (!["ACTIVE", "APPROVED"].includes(document.document_status)) return false;
  if (!task.active_commits.includes(document.commit_sha)) return false;
  if (
    document.namespace === "PROJECT" &&
    task.project_scope !== "GLOBAL" &&
    document.project_scope !== task.project_scope
  ) {
    return false;
  }
  return true;
}

function compareId(left, right) {
  return left.document_id.localeCompare(right.document_id);
}

export function selectForTask({ arm, configuration, task, documents, synonyms, budget }) {
  const query =
    configuration === "PARAPHRASE_VARIANT"
      ? task.paraphrase_query
      : configuration === "SCALE_VARIANT"
        ? `${task.query} governed noise stability`
        : task.query;
  const queryTokens =
    arm === "FULL_RAG_AUTHORITY_FIRST_SIMULATION" ||
    arm === "FULL_RAG_RELEVANCE_FIRST_NEGATIVE_CONTROL"
      ? expandedQueryTokens(query, synonyms)
      : tokenize(query);
  const orderedDocuments =
    configuration === "ORDER_PERMUTATION" ? [...documents].reverse() : [...documents];
  const considered = [];
  for (const document of orderedDocuments) {
    if (arm !== "NO_GOVERNANCE_FILTERING_REFERENCE" && !eligible(document, task)) continue;
    const score = lexicalScore(queryTokens, document.content);
    if (score <= 0) continue;
    considered.push({ document, score });
  }

  if (arm === "FULL_RAG_AUTHORITY_FIRST_SIMULATION") {
    considered.sort(
      (left, right) =>
        right.document.authority_rank - left.document.authority_rank ||
        Number(right.document.binding_negative_prohibition) -
          Number(left.document.binding_negative_prohibition) ||
        Number(Boolean(right.document.conflict_marker)) -
          Number(Boolean(left.document.conflict_marker)) ||
        right.score - left.score ||
        compareId(left.document, right.document),
    );
  } else if (arm === "DETERMINISTIC_REFERENCE_INDEX_REPAIRED_SIMULATION") {
    considered.sort(
      (left, right) =>
        right.document.authority_rank - left.document.authority_rank ||
        Number(right.document.binding_negative_prohibition) -
          Number(left.document.binding_negative_prohibition) ||
        Number(Boolean(right.document.conflict_marker)) -
          Number(Boolean(left.document.conflict_marker)) ||
        right.score - left.score ||
        compareId(left.document, right.document),
    );
  } else {
    considered.sort(
      (left, right) =>
        right.score - left.score ||
        (arm === "FULL_RAG_RELEVANCE_FIRST_NEGATIVE_CONTROL"
          ? right.document.authority_rank - left.document.authority_rank
          : 0) ||
        compareId(left.document, right.document),
    );
  }

  const selected = considered.slice(0, budget).map(({ document, score }, index) => ({
    rank: index + 1,
    candidate_id: document.document_id,
    repository: document.repository,
    path: document.path,
    document_id: document.document_id,
    commit_sha: document.commit_sha,
    authority_class: document.authority_class,
    authority_rank: document.authority_rank,
    project_scope: document.project_scope,
    document_status: document.document_status,
    retrieval_score: score,
    prohibition_retained: document.binding_negative_prohibition,
    conflict_marker: document.conflict_marker,
    citation: `${document.repository}@${document.commit_sha}:${document.path}`,
    bytes: document.bytes,
  }));
  const conflictState = selected.some((item) => item.conflict_marker)
    ? "RESOLUTION_REQUIRED"
    : "NONE";
  return {
    task_id: task.task_id,
    selected,
    candidate_count: considered.length,
    conflict_state: conflictState,
    safe_refusal: selected.length === 0,
    simulated_latency_ms: Number((0.25 + considered.length * 0.07 + selected.length * 0.03).toFixed(3)),
  };
}

export function createSelectorRun({
  arm,
  configuration,
  tasks,
  documents,
  synonyms,
  armParameters,
  readLog = [],
}) {
  const fixtureResults = tasks.map((task) =>
    selectForTask({
      arm,
      configuration,
      task,
      documents,
      synonyms,
      budget: armParameters.common_budget_k,
    }),
  );
  const fingerprint = sha256(serializeJson(fixtureResults));
  return {
    schema_version: "1.0.0",
    execution_id: EXECUTION_ID,
    arm,
    configuration,
    process_role: "SELECTOR_ISOLATED_NO_ORACLE_ACCESS",
    oracle_access: false,
    fixture_count: fixtureResults.length,
    selection_fingerprint: fingerprint,
    read_log: readLog,
    fixture_results: fixtureResults,
  };
}

export function createPositiveControlRun({
  configuration,
  tasks,
  documents,
  oracleFixtures,
  readLog = [],
}) {
  const byId = new Map(documents.map((document) => [document.document_id, document]));
  const taskMap = new Map(tasks.map((task) => [task.task_id, task]));
  const fixtureResults = oracleFixtures.map((oracle) => {
    const task = taskMap.get(oracle.task_id);
    const selected = oracle.required_documents.map((documentId, index) => {
      const document = byId.get(documentId);
      return {
        rank: index + 1,
        candidate_id: document.document_id,
        repository: document.repository,
        path: document.path,
        document_id: document.document_id,
        commit_sha: document.commit_sha,
        authority_class: document.authority_class,
        authority_rank: document.authority_rank,
        project_scope: document.project_scope,
        document_status: document.document_status,
        retrieval_score: 1,
        prohibition_retained: document.binding_negative_prohibition,
        conflict_marker: document.conflict_marker,
        citation: `${document.repository}@${document.commit_sha}:${document.path}`,
        bytes: document.bytes,
      };
    });
    return {
      task_id: oracle.task_id,
      selected,
      candidate_count: selected.length,
      conflict_state: oracle.expected_conflict_state,
      safe_refusal: oracle.expected_safe_refusal,
      simulated_latency_ms: Number((0.1 + selected.length * 0.01).toFixed(3)),
      task_observed: Boolean(task),
    };
  });
  return {
    schema_version: "1.0.0",
    execution_id: EXECUTION_ID,
    arm: "ORACLE_INFORMED_POSITIVE_CONTROL",
    configuration,
    process_role: "EVALUATOR_ONLY_POSITIVE_CONTROL",
    oracle_access: true,
    selector_access: false,
    fixture_count: fixtureResults.length,
    selection_fingerprint: sha256(serializeJson(fixtureResults)),
    read_log: readLog,
    fixture_results: fixtureResults,
  };
}

function divide(numerator, denominator) {
  return denominator === 0 ? 0 : numerator / denominator;
}

function f1(precision, recall) {
  return precision + recall === 0 ? 0 : (2 * precision * recall) / (precision + recall);
}

function round(value, digits = 6) {
  return Number(value.toFixed(digits));
}

function evaluateFixture(result, oracle, documentMap) {
  const selectedIds = result.selected.map((item) => item.document_id);
  const required = new Set(oracle.required_documents);
  const optional = new Set(oracle.optional_documents);
  const forbidden = new Set(oracle.forbidden_documents);
  const relevant = new Set([...required, ...optional]);
  const truePositives = selectedIds.filter((id) => relevant.has(id)).length;
  const requiredTruePositives = selectedIds.filter((id) => required.has(id)).length;
  const falsePositives = selectedIds.filter((id) => !relevant.has(id)).length;
  const falseNegatives = oracle.required_documents.filter((id) => !selectedIds.includes(id)).length;
  const precision = selectedIds.length === 0 ? (required.size === 0 ? 1 : 0) : divide(truePositives, selectedIds.length);
  const recall = required.size === 0 ? 1 : divide(requiredTruePositives, required.size);
  const failures = [];

  for (const id of selectedIds) {
    const document = documentMap.get(id);
    if (forbidden.has(id)) {
      if (!document?.acl_allowed) failures.push("ACL_LEAKAGE");
      else if (document?.document_status === "SUPERSEDED") failures.push("STALE_COMMIT_SELECTED");
      else if (document && !oracle.required_documents.includes(id)) failures.push("AUTHORITY_INVERSION");
    }
    if (document && !["ACTIVE", "APPROVED"].includes(document.document_status)) {
      failures.push("STALE_COMMIT_SELECTED");
    }
  }
  if (
    oracle.required_documents.some(
      (id) => documentMap.get(id)?.binding_negative_prohibition && !selectedIds.includes(id),
    )
  ) {
    failures.push("BINDING_NEGATIVE_OMITTED");
  }
  if (oracle.expected_conflict_state === "RESOLUTION_REQUIRED" && result.conflict_state !== "RESOLUTION_REQUIRED") {
    failures.push("CONFIRMED_CONFLICT_AUTOMERGED");
  }
  if (oracle.expected_safe_refusal && selectedIds.length > 0) failures.push("UNSUPPORTED_CONCLUSION");
  for (const selection of result.selected) {
    const document = documentMap.get(selection.document_id);
    const expectedCitation = document
      ? `${document.repository}@${document.commit_sha}:${document.path}`
      : "";
    if (selection.citation !== expectedCitation) failures.push("FALSE_CITATION");
    if (
      document?.namespace === "PROJECT" &&
      document.project_scope !== "GLOBAL" &&
      document.project_scope !== result.project_scope &&
      result.project_scope
    ) {
      failures.push("CROSS_PROJECT_CONTAMINATION");
    }
  }
  return {
    precision,
    recall,
    f1: f1(precision, recall),
    truePositives,
    falsePositives,
    falseNegatives,
    selectedIds,
    failures: [...new Set(failures)],
  };
}

export function evaluateAll({ runs, tasks, documents, oracleFixtures, initialHashPass, leakagePass }) {
  const oracleMap = new Map(oracleFixtures.map((fixture) => [fixture.task_id, fixture]));
  const documentMap = new Map(documents.map((document) => [document.document_id, document]));
  const taskMap = new Map(tasks.map((task) => [task.task_id, task]));
  const armResults = {};

  for (const arm of ARMS) {
    const armRuns = runs.filter((run) => run.arm === arm);
    let precisionSum = 0;
    let recallSum = 0;
    let f1Sum = 0;
    let fixtureEvaluations = 0;
    let falsePositives = 0;
    let falseNegatives = 0;
    let forbiddenSelections = 0;
    let selectedCount = 0;
    let selectedBytes = 0;
    let candidateCount = 0;
    let latency = 0;
    let citations = 0;
    let correctCitations = 0;
    let authorityInversions = 0;
    let aclLeakage = 0;
    let staleSelections = 0;
    let projectContamination = 0;
    let bindingNegativeExpected = 0;
    let bindingNegativeRetained = 0;
    let conflictExpected = 0;
    let conflictCorrect = 0;
    let falseConflict = 0;
    let safeExpected = 0;
    let safeReturned = 0;
    let safeReturnedTotal = 0;
    let criticalFailures = [];
    let reciprocalRankSum = 0;
    let ndcgSum = 0;

    for (const run of armRuns) {
      for (const result of run.fixture_results) {
        const oracle = oracleMap.get(result.task_id);
        const task = taskMap.get(result.task_id);
        result.project_scope = task.project_scope;
        const evaluation = evaluateFixture(result, oracle, documentMap);
        fixtureEvaluations += 1;
        precisionSum += evaluation.precision;
        recallSum += evaluation.recall;
        f1Sum += evaluation.f1;
        falsePositives += evaluation.falsePositives;
        falseNegatives += evaluation.falseNegatives;
        selectedCount += result.selected.length;
        selectedBytes += result.selected.reduce((sum, item) => sum + item.bytes, 0);
        candidateCount += result.candidate_count;
        latency += result.simulated_latency_ms;
        forbiddenSelections += evaluation.selectedIds.filter((id) =>
          oracle.forbidden_documents.includes(id),
        ).length;
        criticalFailures.push(
          ...evaluation.failures.map((code) => ({ task_id: result.task_id, configuration: run.configuration, code })),
        );
        authorityInversions += evaluation.failures.includes("AUTHORITY_INVERSION") ? 1 : 0;
        aclLeakage += evaluation.failures.includes("ACL_LEAKAGE") ? 1 : 0;
        staleSelections += evaluation.failures.includes("STALE_COMMIT_SELECTED") ? 1 : 0;
        projectContamination += evaluation.failures.includes("CROSS_PROJECT_CONTAMINATION") ? 1 : 0;
        citations += result.selected.length;
        correctCitations += result.selected.filter((selection) => {
          const document = documentMap.get(selection.document_id);
          return (
            document &&
            selection.citation === `${document.repository}@${document.commit_sha}:${document.path}`
          );
        }).length;
        const bindingIds = oracle.required_documents.filter(
          (id) => documentMap.get(id)?.binding_negative_prohibition,
        );
        bindingNegativeExpected += bindingIds.length;
        bindingNegativeRetained += bindingIds.filter((id) =>
          evaluation.selectedIds.includes(id),
        ).length;
        if (oracle.expected_conflict_state === "RESOLUTION_REQUIRED") {
          conflictExpected += 1;
          if (result.conflict_state === "RESOLUTION_REQUIRED") conflictCorrect += 1;
        } else if (result.conflict_state === "RESOLUTION_REQUIRED") {
          falseConflict += 1;
        }
        if (oracle.expected_safe_refusal) {
          safeExpected += 1;
          if (result.safe_refusal) safeReturned += 1;
        }
        if (result.safe_refusal) safeReturnedTotal += 1;
        const firstRelevant = result.selected.findIndex((item) =>
          oracle.required_documents.includes(item.document_id),
        );
        reciprocalRankSum += firstRelevant >= 0 ? 1 / (firstRelevant + 1) : oracle.required_documents.length === 0 ? 1 : 0;
        const gains = result.selected.map((item) =>
          oracle.required_documents.includes(item.document_id)
            ? 2
            : oracle.optional_documents.includes(item.document_id)
              ? 1
              : 0,
        );
        const dcg = gains.reduce((sum, gain, index) => sum + (2 ** gain - 1) / Math.log2(index + 2), 0);
        const idealGains = [
          ...oracle.required_documents.map(() => 2),
          ...oracle.optional_documents.map(() => 1),
        ].slice(0, 2);
        const idcg = idealGains.reduce(
          (sum, gain, index) => sum + (2 ** gain - 1) / Math.log2(index + 2),
          0,
        );
        ndcgSum += idcg === 0 ? 1 : dcg / idcg;
      }
    }

    const macroPrecision = divide(precisionSum, fixtureEvaluations);
    const macroRecall = divide(recallSum, fixtureEvaluations);
    const macroF1 = divide(f1Sum, fixtureEvaluations);
    const safeRefusalPrecision = divide(safeReturned, safeReturnedTotal);
    const safeRefusalRecall = divide(safeReturned, safeExpected);
    const fingerprints = Object.fromEntries(
      armRuns.map((run) => [run.configuration, run.selection_fingerprint]),
    );
    const deterministicRepetition =
      fingerprints.REPETITION_1 === fingerprints.REPETITION_2 &&
      fingerprints.REPETITION_2 === fingerprints.REPETITION_3;
    const orderStability = fingerprints.REPETITION_1 === fingerprints.ORDER_PERMUTATION;
    const fullCorpusBytes = documents.reduce((sum, document) => sum + document.bytes, 0) * armRuns.length;
    const metrics = {
      precision: round(macroPrecision),
      recall: round(macroRecall),
      macro_f1: round(macroF1),
      false_positives: falsePositives,
      false_negatives: falseNegatives,
      forbidden_selection_rate: round(divide(forbiddenSelections, Math.max(selectedCount, 1))),
      authority_preservation: round(1 - divide(authorityInversions, fixtureEvaluations)),
      ownership_preservation: round(1 - divide(projectContamination, fixtureEvaluations)),
      status_preservation: round(1 - divide(staleSelections, fixtureEvaluations)),
      traceability_preservation: round(divide(correctCitations, Math.max(citations, 1))),
      contrary_evidence_preservation: round(divide(bindingNegativeRetained, Math.max(bindingNegativeExpected, 1))),
      conflict_handling: round(divide(conflictCorrect, Math.max(conflictExpected, 1))),
      cross_project_isolation: round(1 - divide(projectContamination, fixtureEvaluations)),
      active_commit_preservation: round(1 - divide(staleSelections, fixtureEvaluations)),
      critical_failures: criticalFailures.length,
      critical_failure_rate: round(divide(criticalFailures.length, fixtureEvaluations)),
      selected_bytes: selectedBytes,
      percentage_byte_reduction: round(100 * (1 - divide(selectedBytes, fullCorpusBytes))),
      mandatory_residual_bytes: selectedBytes,
      deterministic_repetition: deterministicRepetition,
      order_stability: orderStability,
      safe_failure_behavior: round(safeRefusalRecall),
      permissive_failure_behavior: round(1 - safeRefusalRecall),
      selector_payload_measurements: {
        fixture_evaluations: fixtureEvaluations,
        selections: selectedCount,
        run_count: armRuns.length,
      },
      ndcg_at_k: round(divide(ndcgSum, fixtureEvaluations)),
      mrr: round(divide(reciprocalRankSum, fixtureEvaluations)),
      recall_at_k: round(macroRecall),
      precision_at_k: round(macroPrecision),
      required_document_recall: round(macroRecall),
      forbidden_document_rate: round(divide(forbiddenSelections, Math.max(selectedCount, 1))),
      authority_inversion_count: authorityInversions,
      negative_prohibition_retention: round(divide(bindingNegativeRetained, Math.max(bindingNegativeExpected, 1))),
      conflict_detection_accuracy: round(divide(conflictCorrect, Math.max(conflictExpected, 1))),
      conflict_resolution_false_positive_rate: round(
        divide(falseConflict, Math.max(fixtureEvaluations - conflictExpected, 1)),
      ),
      acl_leakage_rate: round(divide(aclLeakage, fixtureEvaluations)),
      stale_document_selection_rate: round(divide(staleSelections, fixtureEvaluations)),
      project_contamination_rate: round(divide(projectContamination, fixtureEvaluations)),
      citation_completeness: round(divide(citations, Math.max(selectedCount, 1))),
      citation_correctness: round(divide(correctCitations, Math.max(citations, 1))),
      commit_pin_correctness: round(divide(correctCitations, Math.max(citations, 1))),
      safe_refusal_precision: round(safeRefusalPrecision),
      safe_refusal_recall: round(safeRefusalRecall),
      safe_failure_f1: round(f1(safeRefusalPrecision, safeRefusalRecall)),
      selected_tokens: null,
      token_measurement_status: "TOKENIZER_NOT_AVAILABLE_NO_INSTALLATION_FALLBACK_USED",
      retrieval_latency: {
        value: round(divide(latency, fixtureEvaluations), 3),
        unit: "MILLISECONDS_SIMULATED_DETERMINISTIC",
      },
      candidate_count: round(divide(candidateCount, fixtureEvaluations)),
      rank_displacement_by_authority: authorityInversions,
      semantic_contribution_after_governance_filters:
        arm === "FULL_RAG_AUTHORITY_FIRST_SIMULATION"
          ? round(
              Math.max(
                0,
                macroRecall -
                  (armResults.DETERMINISTIC_REFERENCE_INDEX_REPAIRED_SIMULATION?.metrics
                    ?.required_document_recall ?? 0),
              ),
            )
          : 0,
    };
    const criticalCodes = [...new Set(criticalFailures.map((failure) => failure.code))].sort();
    const gateA =
      initialHashPass &&
      leakagePass &&
      runs.length === 30 &&
      deterministicRepetition &&
      orderStability;
    const gateB =
      criticalFailures.length === 0 &&
      metrics.acl_leakage_rate <= THRESHOLDS.acl_leakage_max &&
      metrics.project_contamination_rate <= THRESHOLDS.project_contamination_max &&
      metrics.authority_inversion_count <= THRESHOLDS.authority_inversion_max &&
      metrics.stale_document_selection_rate <= THRESHOLDS.stale_selection_max;
    const gateC =
      metrics.required_document_recall >= THRESHOLDS.required_document_recall_min &&
      metrics.precision >= THRESHOLDS.precision_min &&
      metrics.macro_f1 >= THRESHOLDS.macro_f1_min &&
      metrics.citation_correctness >= THRESHOLDS.citation_correctness_min &&
      metrics.conflict_detection_accuracy >= THRESHOLDS.conflict_detection_min &&
      metrics.safe_failure_f1 >= THRESHOLDS.safe_failure_f1_min;
    const gateD =
      Number.isFinite(metrics.selected_bytes) &&
      metrics.percentage_byte_reduction >= 0 &&
      metrics.token_measurement_status === "TOKENIZER_NOT_AVAILABLE_NO_INSTALLATION_FALLBACK_USED";
    const gateE =
      armRuns.length === 6 &&
      deterministicRepetition &&
      orderStability &&
      Boolean(fingerprints.PARAPHRASE_VARIANT) &&
      Boolean(fingerprints.SCALE_VARIANT);
    armResults[arm] = {
      arm,
      role:
        arm === "ORACLE_INFORMED_POSITIVE_CONTROL"
          ? "EVALUATOR_ONLY_POSITIVE_CONTROL_NOT_PROMOTABLE"
          : arm === "FULL_RAG_RELEVANCE_FIRST_NEGATIVE_CONTROL"
            ? "NEGATIVE_CONTROL_NOT_PROMOTABLE"
            : arm === "NO_GOVERNANCE_FILTERING_REFERENCE"
              ? "REFERENCE_NOT_CURRENT_LAB_PROCEDURE"
              : "CANDIDATE_SIMULATION_NO_SELECTION_EFFECT",
      run_count: armRuns.length,
      metrics,
      critical_failure_codes: criticalCodes,
      gates: {
        A_EXPERIMENTAL_INTEGRITY: gateA ? "PASS" : "FAIL",
        B_CRITICAL_SAFETY: gateB ? "PASS" : "FAIL",
        C_FIDELITY: gateC ? "PASS" : "FAIL",
        D_COST: gateD ? "PASS_WITH_TOKENIZER_FALLBACK_DECLARED" : "FAIL",
        E_ROBUSTNESS: gateE ? "PASS" : "FAIL",
      },
      tested_conditions_viability:
        gateA && gateB && gateC && gateD && gateE ? "VIABLE_UNDER_SYNTHETIC_TESTED_CONDITIONS" : "NON_VIABLE_UNDER_SYNTHETIC_TESTED_CONDITIONS",
      architecture_selected: false,
      implementation_selected: false,
    };
  }
  return {
    schema_version: "1.0.0",
    execution_id: EXECUTION_ID,
    generated_at: EXECUTION_TIME,
    run_count: runs.length,
    fixture_count: tasks.length,
    arms: armResults,
    architecture_selected: false,
    implementation_selected: false,
    implementation_approved: false,
  };
}
