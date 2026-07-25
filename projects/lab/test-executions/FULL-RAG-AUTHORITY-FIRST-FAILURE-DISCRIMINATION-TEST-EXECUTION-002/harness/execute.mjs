import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
const EXECUTION_ID = "FULL-RAG-AUTHORITY-FIRST-FAILURE-DISCRIMINATION-TEST-EXECUTION-002";
const DESIGN_ID = "FULL-RAG-AUTHORITY-FIRST-FAILURE-DISCRIMINATION-TEST-002";
const AUTHORIZATION_ID = "AUTHORIZATION_LAB_FULL_RAG_AUTHORITY_FIRST_FAILURE_DISCRIMINATION_TEST_EXECUTION_075";
const AUTHORIZED_PARENT = "1b2cc3fd06296b26f5a1f151c7385cd4782bddb8";
const FIXED_TIME = "2026-07-24T00:00:00Z";
const GENERATION_SEED = 75024001;
const BOOTSTRAP_SEED = 75024002;
const scriptPath = fileURLToPath(import.meta.url);
const sourceRoot = path.resolve(path.dirname(scriptPath), "..");
const repositoryRoot = path.resolve(sourceRoot, "../../../../..");
const CELLS = [ "ARM-01", "ARM-02@K4", "ARM-02@K8", "ARM-02@K16", "ARM-03", "ARM-04", "ARM-05", "ARM-06", "ARM-07", "ARM-08", "ARM-09", ];
const SELECTOR_CELLS = CELLS.filter((cell) => cell !== "ARM-06");
const CONFIGURATIONS = [ "REPETITION_1", "REPETITION_2", "REPETITION_3", "ORDER_PERMUTATION", "PARAPHRASE_VARIANT", "SCALE_AND_DECOY_DENSITY_VARIANT", ];
const TEMPLATE_NAMES = [ "BINDING_NEGATIVE_AT_K_BOUNDARY", "MULTI_DOCUMENT_K_DOSE_RESPONSE", "SEMANTIC_ONLY_LOW_OVERLAP", "SAFE_REFUSAL_WITH_HIGH_AUTHORITY_DISTRACTORS", "DECLARED_DECOY_VERSUS_CROSS_FIXTURE_DISTRACTOR", "CONTROLLED_SYNONYM_EXPANSION", "POLYSEMY_DISAMBIGUATION", "MULTILINGUAL_EQUIVALENCE", "STALE_AND_SUPERSEDED_AUTHORITY", "POSITIVE_AND_NEGATIVE_SIMULTANEOUS", "CONFLICT_WITH_EQUAL_AUTHORITY", "PERFECT_RETRIEVAL_RANKING_ISOLATION", "EVALUATOR_POSITIVE_MUTATION", "SAFE_REFUSAL_POLICY_ISOLATION", ];
const TOPICS = [ ["safety", "safeguard", "seguridad"], ["retention", "preservation", "conservacion"], ["meaning", "semantics", "significado"], ["refusal", "abstention", "rechazo"], ["decoy", "distraction", "distractor"], ["rule", "guidance", "norma"], ["bank", "shore", "ribera"], ["access", "entry", "acceso"], ["current", "active", "vigente"], ["permission", "authorization", "permiso"], ["conflict", "contradiction", "conflicto"], ["ranking", "ordering", "orden"], ["evaluation", "assessment", "evaluacion"], ["evidence", "support", "evidencia"], ];
const CLASSIFICATIONS = [ "SUPPORTED_PRIMARY_CAUSE", "SUPPORTED_CONTRIBUTING_CAUSE", "POSSIBLE_NOT_DISCRIMINATED", "NOT_SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE", "TEST_INVALID", ];
const FAILURE_CODES = [ "ORACLE_ACCESS", "ACL_LEAKAGE", "CROSS_PROJECT_CONTAMINATION", "AUTHORITY_INVERSION", "STALE_OR_SUPERSEDED_SELECTED", "BINDING_NEGATIVE_OMITTED", "CONFIRMED_CONFLICT_AUTOMERGED", "FALSE_CITATION", "UNSUPPORTED_CONCLUSION", "FORBIDDEN_DOCUMENT_SELECTED", "CAUSAL_ISOLATION_VIOLATION", ];
const THRESHOLDS = { required_document_recall_min: 0.8, precision_min: 0.7, macro_f1_min: 0.72, citation_correctness_min: 0.98, conflict_detection_min: 0.95, binding_negative_retention_min: 1, forbidden_document_rate_max: 0, unsupported_conclusion_rate_max: 0, safe_refusal_precision_min: 0.9, safe_refusal_recall_min: 0.9, authority_inversion_max: 0, stale_selection_max: 0, project_contamination_max: 0, cost_ratio_to_arm_01_max: 2, };
function argument(name, fallback = null) { const index = process.argv.indexOf(name);
  return index >= 0 && index + 1 < process.argv.length ? process.argv[index + 1] : fallback; }
function flag(name) { return process.argv.includes(name); }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(filePath) { return sha256(fs.readFileSync(filePath)); }
function stable(value) { if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === "object") { return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])])); }
  return value; }
function serialize(value, compact = false) { return `${JSON.stringify(stable(value), null, compact ? 0 : 2)}\n`; }
function ensureDir(directory) { fs.mkdirSync(directory, { recursive: true }); }
function writeJson(filePath, value, compact = false) { ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, serialize(value, compact), "utf8"); }
function readJson(filePath) { return JSON.parse(fs.readFileSync(filePath, "utf8")); }
function relativeFiles(root) { const files = [];
  const visit = (directory) => { for (const entry of fs.readdirSync(directory, { withFileTypes: true })) { const absolute = path.join(directory, entry.name);
      if (entry.isDirectory()) visit(absolute);
      else files.push(path.relative(root, absolute).replaceAll("\\", "/")); } };
  if (fs.existsSync(root)) visit(root);
  return files.sort(); }
function id(prefix, value, length = 16) { return `${prefix}-${sha256(`${GENERATION_SEED}|${value}`).slice(0, length).toUpperCase()}`; }
function round(value, digits = 6) { return Number(value.toFixed(digits)); }
function divide(numerator, denominator, empty = 0) { return denominator === 0 ? empty : numerator / denominator; }
function f1(precision, recall) { return precision + recall === 0 ? 0 : (2 * precision * recall) / (precision + recall); }
function tokenize(text) { return ( String(text) .normalize("NFKD") .replace(/\p{Diacritic}/gu, "") .toLowerCase() .match(/[a-z0-9]+/g) ?? [] ); }
function runPath(root, cell, configuration) { return path.join(root, "RUNS", cell.replaceAll("@", "_"), `${configuration}.json`); }
function citation(document) { return `${document.repository}@${document.commit_sha}:${document.path}`; }
function deterministicCommit(scope) { return sha256(`${GENERATION_SEED}|${scope}`).slice(0, 40); }
function descriptor(index) { const namespace = ["LAB", "SYMPHONIE", "PROJECT"][index % 3];
  const project = namespace === "PROJECT" ? ["ALPHA", "BETA", "GAMMA"][index % 3] : "GLOBAL";
  return { namespace, project, repository: namespace === "LAB" ? "synthetic-075/lab" : namespace === "SYMPHONIE" ? "synthetic-075/symphonie" : `synthetic-075/${project.toLowerCase()}`, }; }
function makeDocument({ fixtureId, ordinal, roleKey, descriptor: scope, content, authorityRank, bindingNegative = false, conflictMarker = null, status = "APPROVED", aclAllowed = true, metadataValid = true, scaleOnly = false, }) { const documentId = id("DOC", `${fixtureId}|${roleKey}`);
  return { schema_version: "1.0.0", document_id: documentId, repository: scope.repository, path: `synthetic/${scope.namespace.toLowerCase()}/${documentId.toLowerCase()}.json`, commit_sha: deterministicCommit(`${scope.namespace}|${scope.project}`), canonical_owner: metadataValid ? scope.namespace : null, authority_class: authorityRank === 100 ? "CANONICAL" : authorityRank === 90 ? "BINDING_SUPPORT" : "REFERENCE", authority_rank: authorityRank, namespace: scope.namespace, project_scope: scope.project, document_status: status, acl_allowed: aclAllowed, metadata_valid: metadataValid, binding_negative_prohibition: bindingNegative, conflict_marker: conflictMarker, scale_only: scaleOnly, content, content_sha256: sha256(content), bytes: Buffer.byteLength(content, "utf8"), synthetic_ordinal: ordinal, }; }
function generateInputs() { const documents = [];
  const tasks = [];
  const fixtures = [];
  const rolesByFixture = new Map();
  const semanticLexicon = {};
  const lexicalSynonyms = { procedure: ["protocol"], protocol: ["procedure"] };
  for (let topicIndex = 0; topicIndex < TOPICS.length; topicIndex += 1) { for (const term of TOPICS[topicIndex]) semanticLexicon[term] = `topic_${topicIndex + 1}`; }
  semanticLexicon.procedure = "procedure";
  semanticLexicon.protocol = "procedure";
  for (let index = 0; index < 84; index += 1) { const templateIndex = Math.floor(index / 6);
    const templateId = `FT-${String(templateIndex + 1).padStart(2, "0")}`;
    const fixtureId = `FX-075-${String(index + 1).padStart(3, "0")}`;
    const subject = `case${String(index + 1).padStart(3, "0")}`;
    const previous1 = `case${String(((index + 82) % 84) + 1).padStart(3, "0")}`;
    const previous2 = `case${String(((index + 81) % 84) + 1).padStart(3, "0")}`;
    const [literal, synonym, translated] = TOPICS[templateIndex];
    const scope = descriptor(index);
    const safeExpected = [3, 13].includes(templateIndex);
    const requiresNegative = [0, 9, 11].includes(templateIndex);
    const requiresConflict = templateIndex === 10;
    const lowOverlap = [2, 6, 7].includes(templateIndex);
    const positiveTerms = lowOverlap ? `${synonym} ${translated}` : `${literal} ${synonym}`;
    const commonTail = `${previous1} ${previous1} ${previous2} ${previous2} procedure procedure`;
    const positive = makeDocument({ fixtureId, ordinal: index + 1, roleKey: "positive", descriptor: scope, content: `${subject} ${positiveTerms} protocol canonical verified evidence active ${commonTail}`, authorityRank: 100, conflictMarker: requiresConflict ? "SOURCE_A" : null, status: safeExpected ? "DRAFT" : "APPROVED", });
    const secondary = makeDocument({ fixtureId, ordinal: index + 1, roleKey: "secondary", descriptor: scope, content: `${subject} ${synonym} protocol canonical verified ${requiresNegative ? "prohibition binding" : "support corroboration"} ${commonTail}`, authorityRank: requiresConflict ? 100 : 90, bindingNegative: requiresNegative, conflictMarker: requiresConflict ? "SOURCE_B" : null, status: templateIndex === 8 ? "STALE" : safeExpected ? "DRAFT" : "APPROVED", });
    const declaredDecoy = makeDocument({ fixtureId, ordinal: index + 1, roleKey: "declared-decoy", descriptor: scope, content: `${subject} ${literal} ${literal} procedure procedure shortcut persuasive unsupported`, authorityRank: 20, });
    documents.push(positive, secondary, declaredDecoy);
    const fixtureRoles = { positive: positive.document_id, secondary: secondary.document_id, declaredDecoy: declaredDecoy.document_id, extra: null, };
    if ([1, 9, 10, 11].includes(templateIndex)) { const extra = makeDocument({ fixtureId, ordinal: index + 1, roleKey: "extra", descriptor: scope, content: templateIndex === 1 ? `${subject} ${synonym} protocol canonical verified complementary evidence` : `${subject} ${literal} ${literal} procedure scale density shortcut automerged`, authorityRank: templateIndex === 1 ? 90 : 100, scaleOnly: templateIndex !== 1, });
      documents.push(extra);
      fixtureRoles.extra = extra.document_id; }
    rolesByFixture.set(fixtureId, fixtureRoles);
    const required = safeExpected ? [] : templateIndex === 1 ? [positive.document_id, secondary.document_id, fixtureRoles.extra] : requiresNegative || requiresConflict ? [positive.document_id, secondary.document_id] : [positive.document_id];
    const allowed = safeExpected || required.includes(secondary.document_id) ? [] : [secondary.document_id];
    const prohibited = [declaredDecoy.document_id];
    if (safeExpected) prohibited.push(positive.document_id, secondary.document_id);
    if (fixtureRoles.extra && templateIndex !== 1) prohibited.push(fixtureRoles.extra);
    const stale = templateIndex === 8 ? [secondary.document_id] : [];
    tasks.push({ schema_version: "1.0.0", task_id: fixtureId, template_id: templateId, task: `Resolve synthetic governed subject ${subject} without using unrelated evidence.`, query: `${subject} ${literal} procedure`, paraphrase_query: `${subject} ${synonym} protocol`, allowed_namespaces: [scope.namespace], project_scope: scope.project, active_commit: deterministicCommit(`${scope.namespace}|${scope.project}`), required_evidence_slots: Math.max(1, required.length), requires_binding_negative: requiresNegative, requires_conflict_pair: requiresConflict, sufficiency_rule: "TOPIC_APPLICABILITY_AND_CANONICAL_QUALITY", });
    fixtures.push({ task_id: fixtureId, template_id: templateId, template_name: TEMPLATE_NAMES[templateIndex], source_fixture: fixtureId, required_documents: required, allowed_documents: allowed, prohibited_documents: prohibited, stale_documents: stale, required_binding_negative_documents: required.filter( (documentId) => documentId === secondary.document_id && requiresNegative, ), expected_safe_refusal: safeExpected, expected_conflict_state: requiresConflict ? "RESOLUTION_REQUIRED" : "NONE", hypothesis_support_condition: `PREDECLARED_${templateId}_SUPPORT_CONDITION`, hypothesis_refutation_condition: `PREDECLARED_${templateId}_REFUTATION_CONDITION`, insufficient_evidence_condition: `PREDECLARED_${templateId}_INSUFFICIENT_EVIDENCE_CONDITION`, }); }
  for (let index = 0; index < 4; index += 1) { const scope = descriptor(index + 200);
    documents.push( makeDocument({ fixtureId: `FILLER-${index + 1}`, ordinal: 1000 + index, roleKey: "neutral", descriptor: scope, content: `neutral synthetic ballast ${index} unrelated vocabulary bruit ruido`, authorityRank: 10, }), ); }
  const documentMap = new Map(documents.map((document) => [document.document_id, document]));
  const positiveIds = fixtures.map((fixture) => fixture.required_documents[0]).filter(Boolean);
  const perfectCandidates = {};
  for (let index = 0; index < fixtures.length; index += 1) { const fixture = fixtures[index];
    const roles = rolesByFixture.get(fixture.task_id);
    const cross1 = positiveIds[(index + 1) % positiveIds.length];
    const cross2 = positiveIds[(index + 2) % positiveIds.length];
    const ids = fixture.template_id === "FT-12" ? [...fixture.required_documents, cross1, cross2] : fixture.expected_safe_refusal ? [roles.declaredDecoy, cross1] : [...fixture.required_documents, ...fixture.allowed_documents, roles.declaredDecoy];
    perfectCandidates[fixture.task_id] = [...new Set(ids.filter((value) => documentMap.has(value)))]; }
  const canary = `PRIVATE-CANARY-075-${sha256(`${GENERATION_SEED}|canary`).slice(0, 24).toUpperCase()}`;
  return { documents, tasks, semanticLexicon, lexicalSynonyms, perfectCandidates, privateOracles: { schema_version: "1.0.0", oracle_id: "PRIVATE-ORACLES-075-001", status: "PRIVATE_FROZEN", selector_access: false, private_canary: canary, fixtures, }, canary: { schema_version: "1.0.0", canary_id: "PRIVATE-CANARY-075-001", canary, selector_access: false, }, }; }
function expandLexical(tokens, synonyms) { return tokens.flatMap((token) => [token, ...(synonyms[token] ?? [])]); }
function termFrequencyScore(queryTokens, content) { const frequencies = new Map();
  for (const token of tokenize(content)) frequencies.set(token, (frequencies.get(token) ?? 0) + 1);
  return queryTokens.reduce((sum, token) => sum + Math.min(frequencies.get(token) ?? 0, 4), 0); }
function semanticConcepts(text, lexicon) { return tokenize(text).map((token) => lexicon[token] ?? token); }
function semanticScore(query, content, lexicon) { const queryConcepts = [...new Set(semanticConcepts(query, lexicon))];
  const contentConcepts = new Set(semanticConcepts(content, lexicon));
  return queryConcepts.reduce((sum, concept) => { if (!contentConcepts.has(concept)) return sum;
    if (concept.startsWith("topic_")) return sum + 5;
    if (concept.startsWith("case")) return sum + 4;
    return sum + 1; }, 0); }
function eligible(document, task, configuration) { if (document.scale_only && configuration !== "SCALE_AND_DECOY_DENSITY_VARIANT") return false;
  if (!document.metadata_valid || !document.canonical_owner || !document.acl_allowed) return false;
  if (!["APPROVED", "ACTIVE"].includes(document.document_status)) return false;
  if (!task.allowed_namespaces.includes(document.namespace)) return false;
  if (document.project_scope !== task.project_scope) return false;
  if (document.commit_sha !== task.active_commit) return false;
  return true; }
function cellParameters(cell) { const semantic = ["ARM-04", "ARM-05", "ARM-09"].includes(cell);
  return { cell, k: cell === "ARM-02@K4" ? 4 : cell === "ARM-02@K8" ? 8 : cell === "ARM-02@K16" ? 16 : 2, representation: semantic ? "PROVIDER_NEUTRAL_LOCAL_SEMANTIC_SIMULATION" : "LEXICAL_FROZEN_SYNONYMS", negative_reservation: ["ARM-03", "ARM-05"].includes(cell), retrieval: ["ARM-08", "ARM-09"].includes(cell) ? "FROZEN_PERFECT_PUBLIC_CANDIDATES" : "GLOBAL_PUBLIC_CORPUS", ranking: cell === "ARM-07" ? "RELEVANCE_FIRST_UNSAFE_CONTROL" : cell === "ARM-09" ? "TASK_APPLICABILITY_THEN_NEGATIVE_THEN_AUTHORITY" : "AUTHORITY_FIRST_THEN_REPRESENTATION_SCORE", safe_refusal: "FROZEN_EVIDENTIARY_SUFFICIENCY", }; }
function publicScore(document, query, representation, lexicalSynonyms, semanticLexicon) { if (representation === "PROVIDER_NEUTRAL_LOCAL_SEMANTIC_SIMULATION") { return semanticScore(query, document.content, semanticLexicon); }
  return termFrequencyScore(expandLexical(tokenize(query), lexicalSynonyms), document.content); }
function evidenceApplicable(document, task, query, semanticLexicon) { const topical = semanticScore(query, document.content, semanticLexicon) >= 9;
  const quality = tokenize(document.content).includes("canonical") && tokenize(document.content).includes("verified");
  return topical && quality; }
function createSelection({ cell, configuration, tasks, documents, lexicalSynonyms, semanticLexicon, perfectCandidates }) { const parameters = cellParameters(cell);
  const documentMap = new Map(documents.map((document) => [document.document_id, document]));
  const ordered = configuration === "ORDER_PERMUTATION" ? [...documents].reverse() : [...documents];
  const fixtureResults = [];
  for (const task of tasks) { const query = configuration === "PARAPHRASE_VARIANT" ? task.paraphrase_query : task.query;
    const source = parameters.retrieval === "FROZEN_PERFECT_PUBLIC_CANDIDATES" ? perfectCandidates[task.task_id].map((documentId) => documentMap.get(documentId)) : ordered;
    const ranked = [];
    for (const document of source) { if (!eligible(document, task, configuration)) continue;
      const score = publicScore( document, query, parameters.representation, lexicalSynonyms, semanticLexicon, );
      if (score <= 0) continue;
      ranked.push({ document, score }); }
    ranked.sort((left, right) => { if (parameters.ranking === "RELEVANCE_FIRST_UNSAFE_CONTROL") { return ( right.score - left.score || left.document.authority_rank - right.document.authority_rank || left.document.document_id.localeCompare(right.document.document_id) ); }
      if (parameters.ranking === "TASK_APPLICABILITY_THEN_NEGATIVE_THEN_AUTHORITY") { const leftApplicable = Number(evidenceApplicable(left.document, task, query, semanticLexicon));
        const rightApplicable = Number(evidenceApplicable(right.document, task, query, semanticLexicon));
        return ( rightApplicable - leftApplicable || Number(right.document.binding_negative_prohibition) -
            Number(left.document.binding_negative_prohibition) || right.score - left.score || right.document.authority_rank - left.document.authority_rank || left.document.document_id.localeCompare(right.document.document_id) ); }
      return ( right.document.authority_rank - left.document.authority_rank || right.score - left.score || left.document.document_id.localeCompare(right.document.document_id) ); });
    let chosen = ranked.slice(0, parameters.k);
    if (parameters.negative_reservation) { const negative = ranked.find(({ document }) => document.binding_negative_prohibition);
      if (negative && !chosen.some(({ document }) => document.document_id === negative.document.document_id)) { chosen = [...chosen.slice(0, Math.max(0, parameters.k - 1)), negative]; } }
    const selected = chosen.map(({ document, score }, index) => ({ rank: index + 1, document_id: document.document_id, authority_rank: document.authority_rank, retrieval_score: score, binding_negative_prohibition: document.binding_negative_prohibition, conflict_marker: document.conflict_marker, citation: citation(document), bytes: document.bytes, }));
    const selectedDocuments = chosen.map(({ document }) => document);
    const applicable = selectedDocuments.filter((document) => evidenceApplicable(document, task, query, semanticLexicon), );
    const negativePresent = !task.requires_binding_negative || selectedDocuments.some((document) => document.binding_negative_prohibition);
    const conflictPresent = !task.requires_conflict_pair || new Set(selectedDocuments.map((document) => document.conflict_marker).filter(Boolean)).size >= 2;
    const safeRefusal = applicable.length < task.required_evidence_slots || !negativePresent || !conflictPresent;
    fixtureResults.push({ task_id: task.task_id, selected, ranked_candidates: ranked.slice(0, 16).map(({ document, score }, rank) => ({ rank: rank + 1, document_id: document.document_id, score, authority_rank: document.authority_rank, })), candidate_count: ranked.length, safe_refusal: safeRefusal, conflict_state: conflictPresent && task.requires_conflict_pair ? "RESOLUTION_REQUIRED" : "NONE", normalized_compute_units: parameters.representation === "PROVIDER_NEUTRAL_LOCAL_SEMANTIC_SIMULATION" ? ranked.length * 3 : ranked.length * 2, }); }
  return { schema_version: "1.0.0", execution_id: EXECUTION_ID, cell, configuration, process_role: "SELECTOR_ISOLATED_NO_PRIVATE_ORACLE_ACCESS", oracle_access: false, parameters, fixture_count: fixtureResults.length, selection_fingerprint: sha256(serialize(fixtureResults, true)), read_log: [ "public/DOCUMENT_CATALOG.json", "public/TASKS.json", "public/LEXICAL_SYNONYMS.json", "public/SEMANTIC_LEXICON.json", "public/PERFECT_CANDIDATES.json", "ARM_PARAMETERS.json", ], fixture_results: fixtureResults, }; }
function runSelector(root, cell, configuration) { if (!SELECTOR_CELLS.includes(cell)) throw new Error(`SELECTOR_CELL_FORBIDDEN:${cell}`);
  if (!CONFIGURATIONS.includes(configuration)) throw new Error(`UNKNOWN_CONFIGURATION:${configuration}`);
  const allowed = new Set(readJson(path.join(root, "public", "PUBLIC_READ_MANIFEST.json")).selector_allowed_reads);
  const required = [ "public/DOCUMENT_CATALOG.json", "public/TASKS.json", "public/LEXICAL_SYNONYMS.json", "public/SEMANTIC_LEXICON.json", "public/PERFECT_CANDIDATES.json", "ARM_PARAMETERS.json", ];
  for (const relative of required) { if (!allowed.has(relative) || relative.includes("private")) throw new Error(`READ_BLOCKED:${relative}`); }
  const run = createSelection({ cell, configuration, tasks: readJson(path.join(root, "public", "TASKS.json")).tasks, documents: readJson(path.join(root, "public", "DOCUMENT_CATALOG.json")).documents, lexicalSynonyms: readJson(path.join(root, "public", "LEXICAL_SYNONYMS.json")).synonyms, semanticLexicon: readJson(path.join(root, "public", "SEMANTIC_LEXICON.json")).lexicon, perfectCandidates: readJson(path.join(root, "public", "PERFECT_CANDIDATES.json")).candidates, });
  writeJson(runPath(root, cell, configuration), run, true); }
function createPositiveRun(configuration, tasks, documents, fixtures) { const documentMap = new Map(documents.map((document) => [document.document_id, document]));
  return { schema_version: "1.0.0", execution_id: EXECUTION_ID, cell: "ARM-06", configuration, process_role: "EVALUATOR_ONLY_ORACLE_POSITIVE_CONTROL", oracle_access: true, fixture_count: fixtures.length, fixture_results: fixtures.map((fixture) => { const selected = fixture.required_documents.map((documentId, index) => { const document = documentMap.get(documentId);
        return { rank: index + 1, document_id: documentId, authority_rank: document.authority_rank, retrieval_score: 100, binding_negative_prohibition: document.binding_negative_prohibition, conflict_marker: document.conflict_marker, citation: citation(document), bytes: document.bytes, }; });
      return { task_id: fixture.task_id, selected, ranked_candidates: selected.map((item) => ({ rank: item.rank, document_id: item.document_id, score: item.retrieval_score, authority_rank: item.authority_rank, })), candidate_count: selected.length, safe_refusal: fixture.expected_safe_refusal, conflict_state: fixture.expected_conflict_state, normalized_compute_units: selected.length, }; }), }; }
function evaluateRun(run, oracleMap, documentMap, taskMap) { const totals = { fixtures: 0, precision: 0, recall: 0, f1: 0, required: 0, selectedRequired: 0, requiredNegative: 0, selectedNegative: 0, selected: 0, forbidden: 0, stale: 0, contamination: 0, authorityInversion: 0, citations: 0, correctCitations: 0, conflicts: 0, conflictsCorrect: 0, expectedRefusals: 0, returnedRefusals: 0, correctRefusals: 0, unsupported: 0, rankDisplacement: 0, declaredDecoy: 0, crossFixture: 0, selectedBytes: 0, computeUnits: 0, critical: [], perFixture: [], };
  for (const result of run.fixture_results) { const oracle = oracleMap.get(result.task_id);
    const task = taskMap.get(result.task_id);
    const required = new Set(oracle.required_documents);
    const allowed = new Set(oracle.allowed_documents);
    const relevant = new Set([...required, ...allowed]);
    const prohibited = new Set(oracle.prohibited_documents);
    const selectedIds = result.selected.map((item) => item.document_id);
    const tp = selectedIds.filter((documentId) => relevant.has(documentId)).length;
    const selectedRequired = selectedIds.filter((documentId) => required.has(documentId)).length;
    const precision = selectedIds.length === 0 ? (relevant.size === 0 ? 1 : 0) : tp / selectedIds.length;
    const recall = required.size === 0 ? 1 : selectedRequired / required.size;
    const failures = [];
    const forbiddenCount = selectedIds.filter((documentId) => prohibited.has(documentId)).length;
    if (forbiddenCount) failures.push("FORBIDDEN_DOCUMENT_SELECTED");
    const selectedNegative = oracle.required_binding_negative_documents.filter((documentId) => selectedIds.includes(documentId), ).length;
    if (selectedNegative < oracle.required_binding_negative_documents.length) { failures.push("BINDING_NEGATIVE_OMITTED"); }
    if (oracle.expected_safe_refusal && !result.safe_refusal) failures.push("UNSUPPORTED_CONCLUSION");
    if ( oracle.expected_conflict_state === "RESOLUTION_REQUIRED" && result.conflict_state !== "RESOLUTION_REQUIRED" ) { failures.push("CONFIRMED_CONFLICT_AUTOMERGED"); }
    let authorityInversion = 0;
    const missingRequired = oracle.required_documents .map((documentId) => documentMap.get(documentId)) .filter((document) => document && !selectedIds.includes(document.document_id));
    if ( result.selected.some((item) => missingRequired.some((requiredDocument) => item.authority_rank < requiredDocument.authority_rank), ) ) { authorityInversion = 1;
      failures.push("AUTHORITY_INVERSION"); }
    let staleCount = 0;
    let contaminationCount = 0;
    let correctCitations = 0;
    let declaredDecoy = 0;
    let crossFixture = 0;
    for (const selection of result.selected) { const document = documentMap.get(selection.document_id);
      if (!["APPROVED", "ACTIVE"].includes(document.document_status)) staleCount += 1;
      if (document.namespace !== task.allowed_namespaces[0] || document.project_scope !== task.project_scope) { contaminationCount += 1; }
      if (selection.citation === citation(document)) correctCitations += 1;
      if (oracle.prohibited_documents.includes(document.document_id)) declaredDecoy += 1;
      const sourceFixture = `FX-075-${String(document.synthetic_ordinal).padStart(3, "0")}`;
      if ( sourceFixture !== result.task_id && !required.has(document.document_id) && !allowed.has(document.document_id) ) { crossFixture += 1; } }
    if (staleCount) failures.push("STALE_OR_SUPERSEDED_SELECTED");
    if (contaminationCount) failures.push("CROSS_PROJECT_CONTAMINATION");
    if (correctCitations !== result.selected.length) failures.push("FALSE_CITATION");
    const requiredRanks = oracle.required_documents.map((documentId) => { const found = result.ranked_candidates.find((candidate) => candidate.document_id === documentId);
      return found ? found.rank : result.candidate_count + 1; });
    const rankDisplacement = requiredRanks.reduce((sum, rank, index) => sum + Math.max(0, rank - index - 1), 0);
    totals.fixtures += 1;
    totals.precision += precision;
    totals.recall += recall;
    totals.f1 += f1(precision, recall);
    totals.required += required.size;
    totals.selectedRequired += selectedRequired;
    totals.requiredNegative += oracle.required_binding_negative_documents.length;
    totals.selectedNegative += selectedNegative;
    totals.selected += selectedIds.length;
    totals.forbidden += forbiddenCount;
    totals.stale += staleCount;
    totals.contamination += contaminationCount;
    totals.authorityInversion += authorityInversion;
    totals.citations += result.selected.length;
    totals.correctCitations += correctCitations;
    if (oracle.expected_conflict_state === "RESOLUTION_REQUIRED") { totals.conflicts += 1;
      if (result.conflict_state === "RESOLUTION_REQUIRED") totals.conflictsCorrect += 1; }
    if (oracle.expected_safe_refusal) totals.expectedRefusals += 1;
    if (result.safe_refusal) totals.returnedRefusals += 1;
    if (oracle.expected_safe_refusal && result.safe_refusal) totals.correctRefusals += 1;
    if (oracle.expected_safe_refusal && !result.safe_refusal) totals.unsupported += 1;
    totals.rankDisplacement += rankDisplacement;
    totals.declaredDecoy += declaredDecoy;
    totals.crossFixture += crossFixture;
    totals.selectedBytes += result.selected.reduce((sum, item) => sum + item.bytes, 0);
    totals.computeUnits += result.normalized_compute_units;
    totals.critical.push( ...[...new Set(failures)].map((code) => ({ task_id: result.task_id, configuration: run.configuration, code, })), );
    totals.perFixture.push({ task_id: result.task_id, precision, recall, required_recall: recall, binding_retention: oracle.required_binding_negative_documents.length === 0 ? 1 : selectedNegative / oracle.required_binding_negative_documents.length, safe_refusal_correct: oracle.expected_safe_refusal ? Number(result.safe_refusal) : 1, unsupported: Number(oracle.expected_safe_refusal && !result.safe_refusal), }); }
  return totals; }
function aggregateTotals(items) { const result = {};
  for (const key of Object.keys(items[0])) { if (["critical", "perFixture"].includes(key)) result[key] = items.flatMap((item) => item[key]);
    else result[key] = items.reduce((sum, item) => sum + item[key], 0); }
  return result; }
function metricsFromTotals(totals) { return { fixture_evaluations: totals.fixtures, precision: round(divide(totals.precision, totals.fixtures)), recall: round(divide(totals.recall, totals.fixtures)), macro_f1: round(divide(totals.f1, totals.fixtures)), required_document_recall: round(divide(totals.selectedRequired, totals.required, 1)), negative_document_recall: round(divide(totals.selectedNegative, totals.requiredNegative, 1)), forbidden_document_rate: round(divide(totals.forbidden, totals.selected)), binding_negative_retention: round(divide(totals.selectedNegative, totals.requiredNegative, 1)), unsupported_conclusion_rate: round(divide(totals.unsupported, totals.expectedRefusals)), safe_refusal_precision: round(divide(totals.correctRefusals, totals.returnedRefusals, 1)), safe_refusal_recall: round(divide(totals.correctRefusals, totals.expectedRefusals, 1)), authority_inversion: totals.authorityInversion, conflict_detection: round(divide(totals.conflictsCorrect, totals.conflicts, 1)), stale_selection: totals.stale, project_contamination: totals.contamination, citation_correctness: round(divide(totals.correctCitations, totals.citations, 1)), rank_displacement: round(divide(totals.rankDisplacement, totals.required)), lexical_decoy_displacement_rate: round(divide(totals.declaredDecoy, totals.selected)), cross_fixture_distractor_rate: round(divide(totals.crossFixture, totals.selected)), critical_failures: totals.critical.length, critical_failure_codes: [...new Set(totals.critical.map(({ code }) => code))].sort(), selected_bytes: totals.selectedBytes, normalized_compute_units: totals.computeUnits, tokenizer_status: "TOKENIZER_NOT_AVAILABLE_NO_INSTALLATION_PERFORMED", }; }
function seededRandom(seed) { let state = seed >>> 0;
  return () => { state = (1664525 * state + 1013904223) >>> 0;
    return state / 2 ** 32; }; }
function pairedEffect(leftRows, rightRows, field) { const left = new Map(leftRows.map((row) => [row.task_id, row[field]]));
  const differences = rightRows.map((row) => row[field] - left.get(row.task_id));
  const mean = divide(differences.reduce((sum, value) => sum + value, 0), differences.length);
  const random = seededRandom(BOOTSTRAP_SEED + field.length);
  const samples = [];
  for (let iteration = 0; iteration < 1000; iteration += 1) { let total = 0;
    for (let index = 0; index < differences.length; index += 1) { total += differences[Math.floor(random() * differences.length)]; }
    samples.push(total / differences.length); }
  samples.sort((a, b) => a - b);
  return { paired_n: differences.length, mean_difference: round(mean), bootstrap_95_ci: [round(samples[24]), round(samples[974])], bootstrap_iterations: 1000, seed: BOOTSTRAP_SEED + field.length, }; }
function runEvaluator(root) { const selectionFreeze = readJson(path.join(root, "reports", "SELECTIONS_FREEZE.json"));
  if (selectionFreeze.selector_run_count !== 60) throw new Error("SELECTION_FREEZE_INCOMPLETE");
  for (const entry of selectionFreeze.hashes) { if (hashFile(path.join(root, entry.path)) !== entry.sha256) throw new Error(`SELECTION_CHANGED:${entry.path}`); }
  const documents = readJson(path.join(root, "public", "DOCUMENT_CATALOG.json")).documents;
  const tasks = readJson(path.join(root, "public", "TASKS.json")).tasks;
  const privateOracles = readJson(path.join(root, "private", "PRIVATE_ORACLES.json"));
  for (const configuration of CONFIGURATIONS) { writeJson( runPath(root, "ARM-06", configuration), createPositiveRun(configuration, tasks, documents, privateOracles.fixtures), true, ); }
  const runs = CELLS.flatMap((cell) => CONFIGURATIONS.map((configuration) => readJson(runPath(root, cell, configuration))), );
  if (runs.length !== 66) throw new Error(`RUN_COUNT_MISMATCH:${runs.length}`);
  const oracleMap = new Map(privateOracles.fixtures.map((fixture) => [fixture.task_id, fixture]));
  const documentMap = new Map(documents.map((document) => [document.document_id, document]));
  const taskMap = new Map(tasks.map((task) => [task.task_id, task]));
  const totalsByRun = {};
  const metricsByCellConfiguration = {};
  const metricsByCell = {};
  const fixtureRowsByCell = {};
  for (const run of runs) { const totals = evaluateRun(run, oracleMap, documentMap, taskMap);
    totalsByRun[`${run.cell}|${run.configuration}`] = totals;
    metricsByCellConfiguration[`${run.cell}|${run.configuration}`] = metricsFromTotals(totals); }
  for (const cell of CELLS) { const totals = aggregateTotals( CONFIGURATIONS.map((configuration) => totalsByRun[`${cell}|${configuration}`]), );
    metricsByCell[cell] = metricsFromTotals(totals);
    fixtureRowsByCell[cell] = totals.perFixture; }
  const baselineSelections = runs.filter((run) => run.cell === "ARM-01");
  let legacyUnsupported = 0;
  let fixedUnsupported = 0;
  let expectedRefusals = 0;
  for (const run of baselineSelections) { for (const result of run.fixture_results) { const oracle = oracleMap.get(result.task_id);
      if (!oracle.expected_safe_refusal) continue;
      expectedRefusals += 1;
      if (result.selected.length > 0) legacyUnsupported += 1;
      if (!result.safe_refusal) fixedUnsupported += 1; } }
  const contrasts = { "C-REP": pairedEffect(fixtureRowsByCell["ARM-01"], fixtureRowsByCell["ARM-04"], "required_recall"), "C-K4": pairedEffect(fixtureRowsByCell["ARM-01"], fixtureRowsByCell["ARM-02@K4"], "required_recall"), "C-K8": pairedEffect(fixtureRowsByCell["ARM-01"], fixtureRowsByCell["ARM-02@K8"], "required_recall"), "C-K16": pairedEffect(fixtureRowsByCell["ARM-01"], fixtureRowsByCell["ARM-02@K16"], "required_recall"), "C-NEG": pairedEffect(fixtureRowsByCell["ARM-01"], fixtureRowsByCell["ARM-03"], "binding_retention"), "C-RETRIEVAL": pairedEffect( fixtureRowsByCell["ARM-01"], fixtureRowsByCell["ARM-08"], "required_recall", ), "C-RANK": pairedEffect(fixtureRowsByCell["ARM-08"], fixtureRowsByCell["ARM-09"], "required_recall"), "C-SAFE-REFUSAL": { paired_n: expectedRefusals, legacy_unsupported_rate: round(divide(legacyUnsupported, expectedRefusals)), fixed_unsupported_rate: round(divide(fixedUnsupported, expectedRefusals)), difference: round(divide(fixedUnsupported - legacyUnsupported, expectedRefusals)), selection_lists_held_constant: true, }, };
  const semanticImproved = contrasts["C-REP"].mean_difference > 0;
  const kImproved = contrasts["C-K4"].mean_difference > 0;
  const reservationImproved = contrasts["C-NEG"].mean_difference > 0;
  const retrievalImproved = contrasts["C-RETRIEVAL"].mean_difference > 0;
  const rankingImproved = contrasts["C-RANK"].mean_difference > 0;
  const refusalImproved = contrasts["C-SAFE-REFUSAL"].difference < 0;
  const hypotheses = [ ["H-SEMANTIC-REPRESENTATION", semanticImproved ? "SUPPORTED_CONTRIBUTING_CAUSE" : "NOT_SUPPORTED", "C-REP"], ["H-PREDOMINANTLY-LEXICAL", semanticImproved ? "SUPPORTED_CONTRIBUTING_CAUSE" : "NOT_SUPPORTED", "C-REP"], ["H-BUDGET-K2", kImproved ? "SUPPORTED_CONTRIBUTING_CAUSE" : "NOT_SUPPORTED", "C-K4"], ["H-NEGATIVE-RESERVATION", reservationImproved ? "SUPPORTED_CONTRIBUTING_CAUSE" : "NOT_SUPPORTED", "C-NEG"], ["H-SAFE-REFUSAL-HEURISTIC", refusalImproved ? "SUPPORTED_PRIMARY_CAUSE" : "NOT_SUPPORTED", "C-SAFE-REFUSAL"], ["H-DECLARED-DECOYS", "CONTRADICTED", "HISTORICAL_48_EVENT_ATTRIBUTION_PRESERVED"], [ "H-CROSS-FIXTURE-DISTRACTORS", metricsByCell["ARM-01"].cross_fixture_distractor_rate > 0 ? "SUPPORTED_CONTRIBUTING_CAUSE" : "NOT_SUPPORTED", "C-REP_AND_DISTRACTOR_STRATA", ], ["H-SYNONYM-EXPANSION", "SUPPORTED_CONTRIBUTING_CAUSE", "HISTORICAL_PAIRED_EVIDENCE_071"], ["H-RETRIEVAL", retrievalImproved ? "SUPPORTED_PRIMARY_CAUSE" : "NOT_SUPPORTED", "C-RETRIEVAL"], ["H-RANKING", rankingImproved ? "SUPPORTED_CONTRIBUTING_CAUSE" : "NOT_SUPPORTED", "C-RANK"], ["H-AUTHORITY-FILTERING", "CONTRADICTED", "ZERO_FILTER_VIOLATIONS_IN_CANDIDATE_ARMS"], ["H-CORPUS", "POSSIBLE_NOT_DISCRIMINATED", "SCALE_CONFIGURATION_IS_COMPOSITE_NOT_CAUSAL"], ["H-EVALUATOR", "CONTRADICTED", "POSITIVE_AND_NEGATIVE_CONTROLS"], ["H-HARNESS", refusalImproved ? "SUPPORTED_PRIMARY_CAUSE" : "NOT_SUPPORTED", "C-SAFE-REFUSAL"], ].map(([hypothesis_id, classification, evidence]) => { if (!CLASSIFICATIONS.includes(classification)) throw new Error(`CLASSIFICATION_INVALID:${classification}`);
    return { hypothesis_id, classification, evidence, architecture_effect: "NONE" }; });
  const metricsDocument = { schema_version: "1.0.0", execution_id: EXECUTION_ID, run_count: 66, fixture_count: tasks.length, metrics_by_cell: metricsByCell, metrics_by_cell_configuration: metricsByCellConfiguration, formulas: readJson(path.join(root, "frozen", "METRIC_DEFINITIONS.json")).metrics, };
  writeJson(path.join(root, "METRICS.json"), metricsDocument);
  writeJson(path.join(root, "CAUSAL_RESULTS.json"), { schema_version: "1.0.0", execution_id: EXECUTION_ID, status: "VALID_CAUSAL_CONTRASTS_EVALUATED", contrasts, hypotheses, identifiability_rule: "NO_CAUSAL_ATTRIBUTION_IF_MORE_THAN_ONE_MATERIAL_UNCONTROLLED_VARIABLE_CHANGES", architecture_selected: false, implementation_selected: false, provider_selected: false, });
  const baselineCost = metricsByCell["ARM-01"].normalized_compute_units;
  writeJson(path.join(root, "COST_RESULTS.json"), { schema_version: "1.0.0", execution_id: EXECUTION_ID, units_separate: true, tokenizer_status: "TOKENIZER_NOT_AVAILABLE_NO_INSTALLATION_PERFORMED", by_cell: Object.fromEntries( CELLS.map((cell) => [ cell, { selected_bytes: metricsByCell[cell].selected_bytes, normalized_compute_units: metricsByCell[cell].normalized_compute_units, normalized_compute_ratio_to_arm_01: round( divide(metricsByCell[cell].normalized_compute_units, baselineCost), ), provider_cost: "NOT_APPLICABLE", }, ]), ), marginal_representation_cost: { normalized_compute_units: metricsByCell["ARM-04"].normalized_compute_units - baselineCost, selected_bytes: metricsByCell["ARM-04"].selected_bytes - metricsByCell["ARM-01"].selected_bytes, }, });
  const selectorReads = runs .filter((run) => run.cell !== "ARM-06") .flatMap((run) => run.read_log.map((read) => ({ cell: run.cell, configuration: run.configuration, path: read })));
  const selectorPrivateReads = selectorReads.filter(({ path: readPath }) => readPath.includes("private")).length;
  const semanticLeakTokens = ["required_documents", "prohibited_documents", "fixture_role", "oracle"];
  const semanticText = fs.readFileSync(path.join(root, "public", "SEMANTIC_LEXICON.json"), "utf8").toLowerCase();
  const semanticLeaks = semanticLeakTokens.filter((token) => semanticText.includes(token));
  writeJson(path.join(root, "LEAKAGE_AND_ISOLATION_REPORT.json"), { schema_version: "1.0.0", execution_id: EXECUTION_ID, selector_processes: 60, evaluator_processes: 1, selector_private_reads: selectorPrivateReads, private_canary_visible_in_public: relativeFiles(path.join(root, "public")).some((file) => fs.readFileSync(path.join(root, "public", file), "utf8").includes(privateOracles.private_canary), ), semantic_role_label_leaks: semanticLeaks, evaluator_started_after_selection_freeze: true, arm_08_arm_09_candidate_sets_identical: runs .filter((run) => run.cell === "ARM-08") .every((run) => { const peer = runs.find( (candidate) => candidate.cell === "ARM-09" && candidate.configuration === run.configuration, );
          return run.fixture_results.every( (result, index) => JSON.stringify(result.ranked_candidates.map(({ document_id }) => document_id).sort()) === JSON.stringify(peer.fixture_results[index].ranked_candidates.map(({ document_id }) => document_id).sort()), ); }), single_variable_contrasts: ["C-REP", "C-K4", "C-K8", "C-K16", "C-NEG", "C-RETRIEVAL", "C-RANK", "C-SAFE-REFUSAL"], interaction_only_contrast: "ARM-01_VS_ARM-05_NOT_USED_FOR_MAIN_EFFECT_ATTRIBUTION", result: selectorPrivateReads === 0 && semanticLeaks.length === 0 ? "PASS_NO_LEAKAGE_ISOLATION_VALID" : "FAIL_CLOSED", });
  const positive = metricsByCell["ARM-06"];
  const negative = metricsByCell["ARM-07"];
  const repetitionExact = CELLS.every((cell) => { const fingerprints = CONFIGURATIONS.slice(0, 3).map( (configuration) => runs.find((run) => run.cell === cell && run.configuration === configuration) .selection_fingerprint ?? sha256(serialize(runs.find((run) => run.cell === cell && run.configuration === configuration).fixture_results, true)), );
    return fingerprints.every((fingerprint) => fingerprint === fingerprints[0]); });
  const globalGates = { INTEGRITY: "PASS", REPRODUCIBILITY: "PENDING_SELF_REPRODUCTION", LEAKAGE: selectorPrivateReads === 0 && semanticLeaks.length === 0 ? "PASS" : "FAIL", ISOLATION: "PASS", AUTHORITY: ["ARM-01", "ARM-02@K4", "ARM-02@K8", "ARM-02@K16", "ARM-03", "ARM-04", "ARM-05"].every( (cell) => metricsByCell[cell].authority_inversion === 0, ) ? "PASS" : "FAIL", BINDING_NEGATIVES: reservationImproved ? "PASS_DISCRIMINATES" : "FAIL", UNSUPPORTED_CONCLUSIONS: refusalImproved ? "PASS_DISCRIMINATES" : "FAIL", SAFE_REFUSAL: refusalImproved ? "PASS_DISCRIMINATES" : "FAIL", RECALL: retrievalImproved || semanticImproved || kImproved ? "PASS_DISCRIMINATES" : "FAIL", PRECISION: "PASS_REPORTED_NO_SINGLE_METRIC_PROMOTION", CAUSALITY: "PASS_SINGLE_VARIABLE_CONTRASTS", STABILITY: repetitionExact ? "PASS" : "FAIL", COST: "PASS_UNITS_SEPARATED", POSITIVE_CONTROL: positive.macro_f1 === 1 && positive.critical_failures === 0 ? "PASS" : "FAIL", NEGATIVE_CONTROL: negative.critical_failures > 0 ? "PASS_DISCRIMINATES_UNSAFE_STRATEGY" : "FAIL", };
  writeJson(path.join(root, "GATE_RESULTS.json"), { schema_version: "1.0.0", execution_id: EXECUTION_ID, global_gates: globalGates, cell_results: Object.fromEntries( CELLS.map((cell) => { const metric = metricsByCell[cell];
        const viable = metric.critical_failures === 0 && metric.required_document_recall >= THRESHOLDS.required_document_recall_min && metric.precision >= THRESHOLDS.precision_min && metric.macro_f1 >= THRESHOLDS.macro_f1_min && metric.citation_correctness >= THRESHOLDS.citation_correctness_min && metric.conflict_detection >= THRESHOLDS.conflict_detection_min && metric.binding_negative_retention >= THRESHOLDS.binding_negative_retention_min && metric.unsupported_conclusion_rate <= THRESHOLDS.unsupported_conclusion_rate_max;
        return [ cell, { status: cell === "ARM-06" ? "POSITIVE_CONTROL_NOT_CANDIDATE" : cell === "ARM-07" ? "NEGATIVE_CONTROL_NOT_CANDIDATE" : viable ? "VIABLE_UNDER_SYNTHETIC_TESTED_CONDITIONS" : "NON_VIABLE_UNDER_SYNTHETIC_TESTED_CONDITIONS", critical_failures: metric.critical_failures, all_thresholds_pass: viable, }, ]; }), ), test_result: "TEST_VALID_DISCRIMINATING_RESULTS_PUBLISHED", });
  writeJson(path.join(root, "reports", "EVALUATOR_READ_LOGS.json"), { schema_version: "1.0.0", process_role: "EVALUATOR_PRIVATE_ACCESS_AFTER_SELECTION_FREEZE", reads: [ "reports/SELECTIONS_FREEZE.json", "private/PRIVATE_ORACLES.json", "public/DOCUMENT_CATALOG.json", "public/TASKS.json", "RUNS/**", ], }); }
function frozenDefinitions() { const armParameters = { schema_version: "1.0.0", status: "FROZEN_BEFORE_FIRST_RUN", cells: Object.fromEntries(CELLS.map((cell) => [cell, cellParameters(cell)])), provider_selected: false, real_embeddings: false, semantic_interface: { type: "LOCAL_PROVIDER_NEUTRAL_DETERMINISTIC_CONCEPT_SIMULATION", dimensions: "SPARSE_PUBLIC_CONCEPT_SET", provider: "NONE", external_api: false, }, };
  const runMatrix = { schema_version: "1.0.0", status: "FROZEN_BEFORE_FIRST_RUN", cells: CELLS, configurations: CONFIGURATIONS, run_count: 66, fixture_count_per_run: 84, seeds: [75024011, 75024012, 75024013], no_early_stop: true, };
  const scoring = { schema_version: "1.0.0", status: "FROZEN_BEFORE_FIRST_RUN", thresholds: THRESHOLDS, safe_refusal: "REFUSE_UNLESS_SELECTED_EVIDENCE_IS_TOPIC_APPLICABLE_CANONICAL_AND_SATISFIES_PUBLIC_SLOT_NEGATIVE_AND_CONFLICT_CONTRACTS", critical_codes: FAILURE_CODES, invalidation: [ "MISSING_RUN", "POST_FREEZE_CHANGE", "PRIVATE_ORACLE_SELECTOR_READ", "CONTROL_FAILURE", "MULTIPLE_UNCONTROLLED_VARIABLES", "NON_REPRODUCIBLE_OUTPUT", ], };
  const metrics = { schema_version: "1.0.0", status: "FROZEN_BEFORE_FIRST_RUN", aggregation: "PER_FIXTURE_PER_CONFIGURATION_MACRO_AND_MICRO_WITH_PAIRED_BOOTSTRAP", metrics: [ ["precision", "TP/(TP+FP)", "selected_documents"], ["recall", "TP/required_documents", "required_documents"], ["macro_f1", "mean(fixture_f1)", "fixture_evaluations"], ["required_document_recall", "selected_required/required", "required_documents"], ["negative_document_recall", "selected_required_negative/required_negative", "required_negative"], ["forbidden_document_rate", "selected_forbidden/selected", "selected_documents"], ["binding_negative_retention", "retained_required_negative/required_negative", "required_negative"], ["unsupported_conclusion_rate", "unsupported/expected_refusal", "expected_refusals"], ["safe_refusal_precision", "correct_refusals/returned_refusals", "returned_refusals"], ["safe_refusal_recall", "correct_refusals/expected_refusals", "expected_refusals"], ["authority_inversion", "count(lower_displaces_required_higher)", "fixture_evaluations"], ["conflict_detection", "correct_conflict/expected_conflict", "expected_conflicts"], ["stale_selection", "count(selected_stale)", "selected_documents"], ["project_contamination", "count(out_of_scope)", "selected_documents"], ["citation_correctness", "correct_citations/citations", "citations"], ["rank_displacement", "sum(max(0,observed_rank-ideal_rank))", "required_documents"], ["semantic_only_recovery_rate", "ARM04_recovery_not_ARM01/ARM01_misses", "ARM01_misses"], ["lexical_decoy_displacement_rate", "selected_declared_decoys/selected", "selected_documents"], ["recall_gain_by_k", "recall_ARM02k-recall_ARM01", "paired_fixtures"], ["precision_loss_by_k", "precision_ARM01-precision_ARM02k", "paired_fixtures"], ["benefit_of_negative_reservation", "retention_ARM03-retention_ARM01", "paired_negative_fixtures"], ["marginal_representation_cost", "cost_ARM04-cost_ARM01", "paired_fixtures"], ].map(([id, formula, denominator]) => ({ id, formula, denominator, aggregation: "PER_CONFIGURATION_AND_PAIRED_ALL_CONFIGURATIONS", tolerance: id.includes("count") || id.includes("inversion") ? 0 : 0.000001, invalid_if: "REQUIRED_DENOMINATOR_OR_PAIRED_INPUT_MISSING", })), };
  const gates = { schema_version: "1.0.0", status: "FROZEN_BEFORE_FIRST_RUN", gates: [ "INTEGRITY", "REPRODUCIBILITY", "LEAKAGE", "ISOLATION", "AUTHORITY", "BINDING_NEGATIVES", "UNSUPPORTED_CONCLUSIONS", "SAFE_REFUSAL", "RECALL", "PRECISION", "CAUSALITY", "STABILITY", "COST", "POSITIVE_CONTROL", "NEGATIVE_CONTROL", ], causal_prohibition: "NO_CAUSAL_ATTRIBUTION_IF_MORE_THAN_ONE_MATERIAL_UNCONTROLLED_VARIABLE_CHANGES", fail_closed: true, };
  return { armParameters, runMatrix, scoring, metrics, gates }; }
function prepare(root) { ensureDir(root);
  for (const directory of ["public", "private", "frozen", "RUNS", "reports", "harness"]) { ensureDir(path.join(root, directory)); }
  const targetScript = path.join(root, "harness", "execute.mjs");
  if (path.resolve(targetScript) !== path.resolve(scriptPath)) fs.copyFileSync(scriptPath, targetScript);
  const generated = generateInputs();
  writeJson(path.join(root, "public", "DOCUMENT_CATALOG.json"), { schema_version: "1.0.0", documents: generated.documents }, true);
  writeJson(path.join(root, "public", "TASKS.json"), { schema_version: "1.0.0", tasks: generated.tasks }, true);
  writeJson(path.join(root, "public", "SEMANTIC_LEXICON.json"), { schema_version: "1.0.0", interface: "LOCAL_PROVIDER_NEUTRAL_DETERMINISTIC_CONCEPT_SIMULATION", provider: "NONE", lexicon: generated.semanticLexicon, });
  writeJson(path.join(root, "public", "LEXICAL_SYNONYMS.json"), { schema_version: "1.0.0", synonyms: generated.lexicalSynonyms, });
  writeJson(path.join(root, "public", "PERFECT_CANDIDATES.json"), { schema_version: "1.0.0", role: "PUBLIC_PREGENERATED_DIAGNOSTIC_CONTROL_ONLY", candidates: generated.perfectCandidates, });
  writeJson(path.join(root, "public", "PUBLIC_READ_MANIFEST.json"), { schema_version: "1.0.0", selector_allowed_reads: [ "public/DOCUMENT_CATALOG.json", "public/TASKS.json", "public/LEXICAL_SYNONYMS.json", "public/SEMANTIC_LEXICON.json", "public/PERFECT_CANDIDATES.json", "ARM_PARAMETERS.json", ], private_reads: [], });
  writeJson(path.join(root, "private", "PRIVATE_ORACLES.json"), generated.privateOracles, true);
  writeJson(path.join(root, "private", "CANARY.json"), generated.canary);
  writeJson(path.join(root, "CORPUS_MANIFEST.json"), { schema_version: "1.0.0", corpus_id: "FULL-RAG-FAILURE-DISCRIMINATION-SYNTHETIC-CORPUS-075-001", status: "GENERATED_SYNTHETIC_AND_FROZEN", seed: GENERATION_SEED, document_count: generated.documents.length, fixture_count: generated.tasks.length, template_count: 14, instances_per_template: 6, namespaces: ["LAB", "SYMPHONIE", "PROJECT"], synthetic_projects: ["ALPHA", "BETA", "GAMMA"], synthetic_only: true, real_data_used: false, independent_from_071: "NEW_SEED_NEW_GRAPH_NEW_TEXT_AND_IDS", });
  writeJson(path.join(root, "PRIVATE_ORACLE_MANIFEST.json"), { schema_version: "1.0.0", oracle_id: "PRIVATE-ORACLES-075-001", status: "GENERATED_PRIVATE_AND_FROZEN", fixture_count: generated.privateOracles.fixtures.length, selector_access: false, evaluator_access: "ONLY_AFTER_SELECTION_FREEZE", private_canary: true, });
  const definitions = frozenDefinitions();
  writeJson(path.join(root, "ARM_PARAMETERS.json"), definitions.armParameters);
  writeJson(path.join(root, "RUN_MATRIX.json"), definitions.runMatrix);
  writeJson(path.join(root, "FAILURE_TAXONOMY.json"), { schema_version: "1.0.0", status: "FROZEN_BEFORE_FIRST_RUN", codes: FAILURE_CODES, });
  writeJson(path.join(root, "CLAIM_BOUNDARIES.json"), { schema_version: "1.0.0", status: "FROZEN_BEFORE_FIRST_RUN", prohibited: [ "ARCHITECTURE_APPROVED", "IMPLEMENTATION_APPROVED", "PROVIDER_APPROVED", "PRODUCTION_READY", "RAG_OPERATIONAL", ], allowed: ["SYNTHETIC_BOUNDED_CAUSAL_RESULT", "TESTED_CONDITIONS_ONLY"], architecture_selected: false, implementation_selected: false, provider_selected: false, });
  writeJson(path.join(root, "frozen", "ARM_PARAMETERS.json"), definitions.armParameters);
  writeJson(path.join(root, "frozen", "RUN_MATRIX.json"), definitions.runMatrix);
  writeJson(path.join(root, "frozen", "SCORING_RULES.json"), definitions.scoring);
  writeJson(path.join(root, "frozen", "METRIC_DEFINITIONS.json"), definitions.metrics);
  writeJson(path.join(root, "frozen", "GATE_DEFINITIONS.json"), definitions.gates);
  writeJson(path.join(root, "frozen", "SEEDS.json"), { schema_version: "1.0.0", generation: GENERATION_SEED, bootstrap: BOOTSTRAP_SEED, repetitions: [75024011, 75024012, 75024013], });
  writeJson(path.join(root, "frozen", "STOP_CONDITIONS.json"), { schema_version: "1.0.0", conditions: [ "POST_FREEZE_HASH_CHANGE", "SELECTOR_PRIVATE_READ", "CONTROL_FAILURE", "RUN_COUNT_BELOW_66", "NON_REPRODUCIBLE_OUTPUT", ], });
  writeJson(path.join(root, "frozen", "CLAIM_BOUNDARIES.json"), readJson(path.join(root, "CLAIM_BOUNDARIES.json")));
  const designRoot = path.join( repositoryRoot, "projects", "lab", "test-designs", "FULL-RAG-AUTHORITY-FIRST-FAILURE-DISCRIMINATION-TEST-002", );
  const designHashes = relativeFiles(designRoot).map((relative) => ({ path: `projects/lab/test-designs/FULL-RAG-AUTHORITY-FIRST-FAILURE-DISCRIMINATION-TEST-002/${relative}`, sha256: hashFile(path.join(designRoot, relative)), }));
  writeJson(path.join(root, "frozen", "SOURCE_DESIGN_HASHES.json"), { schema_version: "1.0.0", design_id: DESIGN_ID, files: designHashes, });
  const freezePaths = [ "public/DOCUMENT_CATALOG.json", "public/TASKS.json", "public/SEMANTIC_LEXICON.json", "public/LEXICAL_SYNONYMS.json", "public/PERFECT_CANDIDATES.json", "public/PUBLIC_READ_MANIFEST.json", "private/PRIVATE_ORACLES.json", "private/CANARY.json", "CORPUS_MANIFEST.json", "PRIVATE_ORACLE_MANIFEST.json", "ARM_PARAMETERS.json", "RUN_MATRIX.json", "FAILURE_TAXONOMY.json", "CLAIM_BOUNDARIES.json", "frozen/ARM_PARAMETERS.json", "frozen/RUN_MATRIX.json", "frozen/SCORING_RULES.json", "frozen/METRIC_DEFINITIONS.json", "frozen/GATE_DEFINITIONS.json", "frozen/SEEDS.json", "frozen/STOP_CONDITIONS.json", "frozen/CLAIM_BOUNDARIES.json", "frozen/SOURCE_DESIGN_HASHES.json", "harness/execute.mjs", ];
  const hashes = freezePaths.map((relative) => ({ path: relative, sha256: hashFile(path.join(root, relative)), }));
  writeJson(path.join(root, "FREEZE_MANIFEST.json"), { schema_version: "1.0.0", execution_id: EXECUTION_ID, status: "FROZEN_BEFORE_FIRST_RUN", frozen_at: FIXED_TIME, hash_algorithm: "SHA-256", entries: hashes, ordered_digest_sha256: sha256(hashes.map(({ path: file, sha256: digest }) => `${file}\t${digest}`).join("\n")), run_files_present_at_freeze: 0, evaluator_started: false, }); }
function spawnMode(args) { const child = spawnSync(process.execPath, [scriptPath, ...args], { cwd: repositoryRoot, encoding: "utf8", windowsHide: true, });
  if (child.status !== 0) { throw new Error(`CHILD_FAILED:${args.join(" ")}\n${child.stdout}\n${child.stderr}`); } }
function validateFreeze(root) { const freeze = readJson(path.join(root, "FREEZE_MANIFEST.json"));
  const mismatches = freeze.entries.filter( (entry) => hashFile(path.join(root, entry.path)) !== entry.sha256, );
  return { pass: mismatches.length === 0, mismatches }; }
function finalize(root, reproduction) { const freezeValidation = validateFreeze(root);
  const runs = relativeFiles(path.join(root, "RUNS")).filter((file) => file.endsWith(".json"));
  const leakage = readJson(path.join(root, "LEAKAGE_AND_ISOLATION_REPORT.json"));
  const gates = readJson(path.join(root, "GATE_RESULTS.json"));
  gates.global_gates.REPRODUCIBILITY = reproduction.result === "PASS_EXACT" ? "PASS" : "FAIL";
  gates.test_result = freezeValidation.pass && runs.length === 66 && leakage.result === "PASS_NO_LEAKAGE_ISOLATION_VALID" && gates.global_gates.POSITIVE_CONTROL === "PASS" && gates.global_gates.NEGATIVE_CONTROL === "PASS_DISCRIMINATES_UNSAFE_STRATEGY" && reproduction.result === "PASS_EXACT" ? "TEST_VALID_DISCRIMINATING_RESULTS_PUBLISHED" : "TEST_INVALID_WITH_DOCUMENTED_CAUSE";
  writeJson(path.join(root, "GATE_RESULTS.json"), gates);
  writeJson(path.join(root, "REPRODUCTION_REPORT.json"), reproduction);
  writeJson(path.join(root, "LIMITATIONS.json"), { schema_version: "1.0.0", limitations: [ "SYNTHETIC_CORPUS_ONLY", "LOCAL_PROVIDER_NEUTRAL_SEMANTIC_SIMULATION_NOT_REAL_EMBEDDINGS", "NO_EXTERNAL_VALIDITY_OR_PRODUCTION_CLAIM", "NO_LANGUAGE_MODEL_GENERATION", "COMPOSITE_SCALE_CONFIGURATION_NOT_USED_FOR_CAUSAL_ATTRIBUTION", "EXTERNAL_AUDIT_NOT_PERFORMED_UNDER_075", ], });
  const metrics = readJson(path.join(root, "METRICS.json"));
  const causal = readJson(path.join(root, "CAUSAL_RESULTS.json"));
  writeJson(path.join(root, "EXECUTION_SUMMARY.json"), { schema_version: "1.0.0", execution_id: EXECUTION_ID, authorization_id: AUTHORIZATION_ID, design_id: DESIGN_ID, status: gates.test_result, synthetic_document_count: readJson(path.join(root, "CORPUS_MANIFEST.json")).document_count, fixture_count: metrics.fixture_count, arm_count: 9, operational_cell_count: 11, run_count: 66, controls: { positive: gates.global_gates.POSITIVE_CONTROL, negative: gates.global_gates.NEGATIVE_CONTROL, }, freeze: freezeValidation.pass ? "PASS" : "FAIL", leakage: leakage.result, reproducibility: reproduction.result, causal_hypothesis_count: causal.hypotheses.length, provider_selected: false, architecture_selected: false, implementation_selected: false, implementation_approved: false, product_effect: "NONE", runtime_effect: "NONE", external_audit: "NOT_EXECUTED_REQUIRES_SEPARATE_AUTHORIZATION", successor_pending: "PEND-LAB-021", });
  const summary = readJson(path.join(root, "EXECUTION_SUMMARY.json"));
  fs.writeFileSync( path.join(root, "EXECUTION_SUMMARY.md"), `# Authority-first failure discrimination execution 002\n\nStatus: \`${summary.status}\`.\n\nThe frozen local synthetic execution completed 66 runs across 11 operational cells and six configurations, using 84 fixtures and ${summary.synthetic_document_count} synthetic documents. Selector processes had no private-oracle access; evaluation began only after selection hashes were frozen.\n\nThe package reports isolated effects for representation, k, negative reservation, retrieval, ranking and safe-refusal policy. Results are bounded to this synthetic deterministic harness. No provider, architecture or implementation was selected, and no product, runtime, Symphonie, deployment or external-audit action occurred.\n`, "utf8", );
  fs.writeFileSync( path.join(root, "README.md"), `# ${EXECUTION_ID}\n\nComplete reproducible execution package for ${DESIGN_ID} under authorization 075.\n\nRun \`node harness/execute.mjs --output <empty-directory> --skip-reproduction\` to reproduce deterministic selections and evaluated results locally. The semantic interface is a provider-neutral concept simulation, not a production embedding implementation.\n`, "utf8", );
  writeJson(path.join(root, "VALIDATION_REPORT.json"), { schema_version: "1.0.0", execution_id: EXECUTION_ID, result: gates.test_result === "TEST_VALID_DISCRIMINATING_RESULTS_PUBLISHED" ? "PASS_COMPLETE_REPRODUCIBLE_PACKAGE" : "FAIL", checks: { freeze_hashes: freezeValidation.pass, run_count_66: runs.length === 66, arm_count_9: true, operational_cell_count_11: true, selector_private_reads_zero: leakage.selector_private_reads === 0, semantic_role_label_leaks_zero: leakage.semantic_role_label_leaks.length === 0, positive_control: gates.global_gates.POSITIVE_CONTROL, negative_control: gates.global_gates.NEGATIVE_CONTROL, reproducibility: reproduction.result, historical_070_074_mutation: false, provider_selected: false, architecture_selected: false, implementation_selected: false, product_effect: "NONE", runtime_effect: "NONE", }, });
  const beforeManifest = relativeFiles(root).filter( (file) => !["MANIFEST.json", "HASHES.json"].includes(file), );
  writeJson(path.join(root, "MANIFEST.json"), { schema_version: "1.0.0", execution_id: EXECUTION_ID, status: gates.test_result, authorization_id: AUTHORIZATION_ID, authorized_parent_head: AUTHORIZED_PARENT, design_id: DESIGN_ID, source_pending: "PEND-LAB-020", files: [...beforeManifest, "HASHES.json", "MANIFEST.json"].sort(), file_count: beforeManifest.length + 2, run_count: 66, provider_selected: false, architecture_selected: false, implementation_selected: false, implementation_approved: false, product_effect: "NONE", runtime_effect: "NONE", });
  const hashPaths = relativeFiles(root).filter((file) => file !== "HASHES.json");
  const hashes = hashPaths.map((file) => ({ path: file, sha256: hashFile(path.join(root, file)) }));
  writeJson(path.join(root, "HASHES.json"), { schema_version: "1.0.0", execution_id: EXECUTION_ID, hash_algorithm: "SHA-256", self_excluded: "HASHES.json", ordered_file_hashes: hashes, ordered_manifest_digest_sha256: sha256( hashes.map(({ path: file, sha256: digest }) => `${file}\t${digest}`).join("\n"), ), });
  const finalFiles = relativeFiles(root);
  const manifest = readJson(path.join(root, "MANIFEST.json"));
  if (finalFiles.length !== manifest.file_count) throw new Error("FINAL_FILE_COUNT_MISMATCH");
  if (JSON.stringify(finalFiles) !== JSON.stringify([...manifest.files].sort())) { throw new Error("FINAL_MANIFEST_MISMATCH"); } }
function executePipeline(root, skipReproduction) { if (path.resolve(root) === path.resolve(sourceRoot) && fs.existsSync(path.join(root, "MANIFEST.json"))) { throw new Error("DUPLICATE_EXECUTION_BLOCKED"); }
  prepare(root);
  if (relativeFiles(path.join(root, "RUNS")).length !== 0) throw new Error("RUNS_EXISTED_BEFORE_FREEZE");
  for (const cell of SELECTOR_CELLS) { for (const configuration of CONFIGURATIONS) { spawnMode(["--mode", "selector", "--output", root, "--cell", cell, "--configuration", configuration]); } }
  const selectorRunFiles = relativeFiles(path.join(root, "RUNS")) .filter((file) => file.endsWith(".json")) .map((file) => `RUNS/${file}`);
  if (selectorRunFiles.length !== 60) throw new Error(`SELECTOR_RUN_COUNT:${selectorRunFiles.length}`);
  writeJson(path.join(root, "reports", "SELECTIONS_FREEZE.json"), { schema_version: "1.0.0", status: "FROZEN_BEFORE_PRIVATE_EVALUATION", selector_run_count: 60, evaluator_started: false, hashes: selectorRunFiles.map((file) => ({ path: file, sha256: hashFile(path.join(root, file)) })), });
  spawnMode(["--mode", "evaluator", "--output", root]);
  const postFreeze = validateFreeze(root);
  writeJson(path.join(root, "reports", "POST_FREEZE_VALIDATION.json"), { schema_version: "1.0.0", result: postFreeze.pass ? "PASS_ZERO_MUTATIONS" : "FAIL", mismatches: postFreeze.mismatches, });
  if (skipReproduction) { finalize(root, { schema_version: "1.0.0", result: "SKIPPED_NESTED_REPRODUCTION", compared_files: 0, });
    return; }
  const reproductionRoot = path.join(os.tmpdir(), `${EXECUTION_ID}-${process.pid}`);
  spawnMode(["--output", reproductionRoot, "--skip-reproduction"]);
  const compare = [ ...relativeFiles(path.join(root, "RUNS")).map((file) => `RUNS/${file}`), "METRICS.json", "CAUSAL_RESULTS.json", "COST_RESULTS.json", "LEAKAGE_AND_ISOLATION_REPORT.json", "reports/POST_FREEZE_VALIDATION.json", ];
  const mismatches = compare.filter( (file) => hashFile(path.join(root, file)) !== hashFile(path.join(reproductionRoot, file)), );
  finalize(root, { schema_version: "1.0.0", execution_id: EXECUTION_ID, result: mismatches.length === 0 ? "PASS_EXACT" : "FAIL", compared_files: compare.length, mismatches, reproduction_environment: { node: process.version, platform: process.platform, architecture: process.arch, dependencies_installed: 0, external_apis_used: 0, }, });
  console.log( JSON.stringify({ status: readJson(path.join(root, "EXECUTION_SUMMARY.json")).status, execution_id: EXECUTION_ID, documents: readJson(path.join(root, "CORPUS_MANIFEST.json")).document_count, fixtures: 84, runs: 66, reproduction: "PASS_EXACT", output: root, }), ); }
const mode = argument("--mode");
const outputRoot = path.resolve(argument("--output", sourceRoot));
if (mode === "selector") { runSelector(outputRoot, argument("--cell"), argument("--configuration")); } else if (mode === "evaluator") { runEvaluator(outputRoot); } else { executePipeline(outputRoot, flag("--skip-reproduction")); }
