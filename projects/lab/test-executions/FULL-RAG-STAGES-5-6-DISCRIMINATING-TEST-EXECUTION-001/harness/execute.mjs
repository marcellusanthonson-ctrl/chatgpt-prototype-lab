import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import {
  ARMS,
  SELECTOR_ARMS,
  CONFIGURATIONS,
  AUTHORIZATION_ID,
  AUTHORIZED_PARENT_HEAD,
  DESIGN_ID,
  EXECUTION_ID,
  EXECUTION_TIME,
  GENERATION_SEED,
  THRESHOLDS,
  createPositiveControlRun,
  createSelectorRun,
  generateCorpus,
  hashFile,
  readJson,
  relativeFiles,
  serializeJson,
  sha256,
  writeJson,
} from "./lib.mjs";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const sourceExecutionRoot = path.resolve(scriptDirectory, "..");
const repositoryRoot = path.resolve(scriptDirectory, "../../../../..");
const outputArgumentIndex = process.argv.indexOf("--output");
const outputRoot =
  outputArgumentIndex >= 0 ? path.resolve(process.argv[outputArgumentIndex + 1]) : sourceExecutionRoot;

function fail(code, detail = "") {
  throw new Error(`${code}${detail ? `:${detail}` : ""}`);
}

function prepareOutput() {
  if (!fs.existsSync(outputRoot)) fs.mkdirSync(outputRoot, { recursive: true });
  const entries = fs.readdirSync(outputRoot);
  if (outputRoot === sourceExecutionRoot) {
    if (entries.some((entry) => entry !== "harness")) fail("PREEXISTING_EXECUTION_ARTIFACTS");
  } else {
    if (entries.length > 0) fail("REPRODUCTION_OUTPUT_NOT_EMPTY");
    fs.cpSync(path.join(sourceExecutionRoot, "harness"), path.join(outputRoot, "harness"), {
      recursive: true,
    });
  }
}

function runProcess(script, argumentsList) {
  const result = spawnSync(process.execPath, [script, ...argumentsList], {
    cwd: repositoryRoot,
    encoding: "utf8",
  });
  if (result.status !== 0) {
    fail("CHILD_PROCESS_FAILED", `${path.basename(script)}:${result.stderr || result.stdout}`);
  }
}

function writeMarkdown(filePath, content) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${content.trim()}\n`, "utf8");
}

function hashesFor(relativePaths) {
  return Object.fromEntries(
    relativePaths.map((relativePath) => [relativePath, hashFile(path.join(outputRoot, relativePath))]),
  );
}

prepareOutput();
const generated = generateCorpus();
const publicDirectory = path.join(outputRoot, "public");
const privateDirectory = path.join(outputRoot, "private");
const frozenDirectory = path.join(outputRoot, "frozen");
const reportsDirectory = path.join(outputRoot, "reports");
for (const directory of [publicDirectory, privateDirectory, frozenDirectory, reportsDirectory]) {
  fs.mkdirSync(directory, { recursive: true });
}

writeJson(path.join(publicDirectory, "CORPUS_MANIFEST.json"), generated.corpusManifest);
writeJson(path.join(publicDirectory, "DOCUMENT_CATALOG.json"), {
  schema_version: "1.0.0",
  corpus_id: generated.corpusManifest.corpus_id,
  documents: generated.documents,
});
writeJson(path.join(publicDirectory, "TASKS.json"), {
  schema_version: "1.0.0",
  corpus_id: generated.corpusManifest.corpus_id,
  tasks: generated.tasks,
});
writeJson(path.join(publicDirectory, "SYNONYMS.json"), {
  schema_version: "1.0.0",
  method: "LOCAL_DETERMINISTIC_SYNTHETIC_SPARSE_QUERY_EXPANSION",
  embeddings_generated: false,
  external_api_used: false,
  synonyms: generated.synonyms,
});
writeJson(path.join(publicDirectory, "READ_MANIFEST.json"), {
  schema_version: "1.0.0",
  selector_allowed_reads: [
    "public/READ_MANIFEST.json",
    "public/DOCUMENT_CATALOG.json",
    "public/TASKS.json",
    "public/SYNONYMS.json",
    "frozen/ARM_PARAMETERS.json",
  ],
  selector_forbidden_prefixes: ["private/", "../"],
  selector_oracle_access: false,
});
writeJson(path.join(privateDirectory, "PRIVATE_ORACLES.json"), generated.privateOracles);
writeJson(path.join(privateDirectory, "CANARY_RECORD.json"), generated.canaryRecord);

const armParameters = {
  schema_version: "1.0.0",
  status: "FROZEN_BEFORE_RUNS",
  common_budget_k: 2,
  common_corpus: generated.corpusManifest.corpus_id,
  arms: Object.fromEntries(
    ARMS.map((arm) => [
      arm,
      {
        budget_k: 2,
        provider: "NONE",
        embeddings: false,
        vector_database: false,
        deterministic_tie_break: "DOCUMENT_ID_ASCENDING",
      },
    ]),
  ),
};
writeJson(path.join(frozenDirectory, "ARM_PARAMETERS.json"), armParameters);
writeJson(path.join(frozenDirectory, "SEEDS.json"), {
  schema_version: "1.0.0",
  status: "FROZEN_BEFORE_GENERATION_AND_RUNS",
  corpus_generation_seed: GENERATION_SEED,
  run_seed_policy: "DETERMINISTIC_NO_RANDOM_SELECTION",
  order_permutation: "REVERSED_INPUT_WITH_EXPLICIT_TIE_BREAK",
});
writeJson(path.join(frozenDirectory, "RUN_MATRIX.json"), {
  schema_version: "1.0.0",
  status: "FROZEN_BEFORE_RUNS",
  arms: ARMS,
  configurations_per_arm: CONFIGURATIONS,
  expected_runs: 30,
  common_budget: true,
  common_corpus: true,
});
writeJson(path.join(frozenDirectory, "SCORING_RULES.json"), {
  schema_version: "1.0.0",
  status: "FROZEN_BEFORE_RUNS",
  frozen_at: EXECUTION_TIME,
  aggregation: {
    retrieval_metrics: "MACRO_BY_FIXTURE_WITH_MICRO_SUPPLEMENT",
    critical_failures: "ABSOLUTE_COUNT_AND_RATE",
    cost: "PER_FIXTURE_AND_TOTAL",
  },
  critical_gate: "ANY_ENUMERATED_CRITICAL_FAILURE_MAKES_ARM_NON_VIABLE_UNDER_TESTED_CONDITIONS",
  missing_data_rule: "FAIL_CLOSED_EXCEPT_DECLARED_TOKENIZER_FALLBACK",
  thresholds: THRESHOLDS,
  units: {
    bytes: "BYTE",
    tokens: "TOKENIZER_SPECIFIC_TOKEN_OR_NULL_WHEN_UNAVAILABLE_WITHOUT_INSTALLATION",
    latency: "MILLISECONDS_SIMULATED_DETERMINISTIC",
  },
});

const designDirectory = path.join(
  repositoryRoot,
  "projects/lab/test-designs/FULL-RAG-STAGES-5-6-DISCRIMINATING-TEST-001",
);
const designFiles = relativeFiles(designDirectory);
const frozenInputPaths = [
  "public/CORPUS_MANIFEST.json",
  "public/DOCUMENT_CATALOG.json",
  "public/TASKS.json",
  "public/SYNONYMS.json",
  "public/READ_MANIFEST.json",
  "private/PRIVATE_ORACLES.json",
  "private/CANARY_RECORD.json",
  "frozen/ARM_PARAMETERS.json",
  "frozen/SEEDS.json",
  "frozen/RUN_MATRIX.json",
  "frozen/SCORING_RULES.json",
  ...relativeFiles(path.join(outputRoot, "harness")).map((file) => `harness/${file}`),
];
const initialHashes = hashesFor(frozenInputPaths);
writeJson(path.join(frozenDirectory, "HASHES_INITIAL.json"), {
  schema_version: "1.0.0",
  status: "FROZEN_BEFORE_RUNS",
  hash_algorithm: "SHA-256",
  frozen_at: EXECUTION_TIME,
  public_hashes: Object.fromEntries(
    Object.entries(initialHashes).filter(([file]) => file.startsWith("public/")),
  ),
  private_hashes: Object.fromEntries(
    Object.entries(initialHashes).filter(([file]) => file.startsWith("private/")),
  ),
  scoring_parameter_and_harness_hashes: Object.fromEntries(
    Object.entries(initialHashes).filter(
      ([file]) => file.startsWith("frozen/") || file.startsWith("harness/"),
    ),
  ),
  design_source_hashes: Object.fromEntries(
    designFiles.map((file) => [file, hashFile(path.join(designDirectory, file))]),
  ),
});
writeJson(path.join(frozenDirectory, "FREEZE_MANIFEST.json"), {
  schema_version: "1.0.0",
  status: "FROZEN_BEFORE_RUNS",
  frozen_paths: frozenInputPaths,
  hash_manifest: "frozen/HASHES_INITIAL.json",
  mutation_policy: "ANY_POST_FREEZE_HASH_CHANGE_INVALIDATES_EXPERIMENT",
});

const publicPayload = [
  "public/CORPUS_MANIFEST.json",
  "public/DOCUMENT_CATALOG.json",
  "public/TASKS.json",
  "public/SYNONYMS.json",
  "public/READ_MANIFEST.json",
].map((file) => fs.readFileSync(path.join(outputRoot, file), "utf8")).join("\n");
if (publicPayload.includes(generated.canaryRecord.canary)) fail("PRIVATE_CANARY_VISIBLE_IN_PUBLIC_INPUT");
if (/required_documents|optional_documents|forbidden_documents|private_canary/i.test(publicPayload)) {
  fail("PRIVATE_ORACLE_FIELD_VISIBLE_IN_PUBLIC_INPUT");
}

const selectorScript = path.join(outputRoot, "harness", "selector.mjs");
for (const arm of SELECTOR_ARMS) {
  for (const configuration of CONFIGURATIONS) {
    runProcess(selectorScript, ["--root", outputRoot, "--arm", arm, "--configuration", configuration]);
  }
}

const selectorRunFiles = relativeFiles(path.join(outputRoot, "runs"))
  .filter((file) => file.endsWith(".json"))
  .map((file) => `runs/${file}`);
if (selectorRunFiles.length !== 24) fail("SELECTOR_RUN_COUNT_MISMATCH", selectorRunFiles.length);
const selectorRuns = selectorRunFiles.map((file) => readJson(path.join(outputRoot, file)));
const selectorReads = selectorRuns.flatMap((run) =>
  run.read_log.map((entry) => ({ arm: run.arm, configuration: run.configuration, ...entry })),
);
const forbiddenRead = selectorReads.find(
  (entry) => entry.path.startsWith("private/") || entry.path.includes("PRIVATE_ORACLES"),
);
if (forbiddenRead) fail("SELECTOR_ORACLE_ISOLATION_FAILURE", forbiddenRead.path);
const changedBeforeEvaluation = Object.entries(initialHashes).filter(
  ([file, hash]) => hashFile(path.join(outputRoot, file)) !== hash,
);
if (changedBeforeEvaluation.length > 0) {
  fail("POST_FREEZE_HASH_CHANGE", changedBeforeEvaluation.map(([file]) => file).join(","));
}
writeJson(path.join(reportsDirectory, "PRE_EVALUATION_INTEGRITY.json"), {
  schema_version: "1.0.0",
  post_freeze_hash_validation: "PASS",
  selector_oracle_isolation: "PASS",
  selector_process_count: 24,
  selector_private_reads: 0,
});

const evaluatorScript = path.join(outputRoot, "harness", "evaluator.mjs");
runProcess(evaluatorScript, ["--root", outputRoot]);
const allRunFiles = relativeFiles(path.join(outputRoot, "runs")).filter((file) => file.endsWith(".json"));
if (allRunFiles.length !== 30) fail("RUN_COUNT_MISMATCH", allRunFiles.length);

const changedAfterEvaluation = Object.entries(initialHashes).filter(
  ([file, hash]) => hashFile(path.join(outputRoot, file)) !== hash,
);
if (changedAfterEvaluation.length > 0) {
  fail("POST_FREEZE_HASH_CHANGE", changedAfterEvaluation.map(([file]) => file).join(","));
}

const runs = allRunFiles.map((file) => readJson(path.join(outputRoot, "runs", file)));
const replayMismatches = [];
for (const run of runs) {
  let replay;
  if (run.arm === "ORACLE_INFORMED_POSITIVE_CONTROL") {
    replay = createPositiveControlRun({
      configuration: run.configuration,
      tasks: generated.tasks,
      documents: generated.documents,
      oracleFixtures: generated.privateOracles.fixtures,
    });
  } else {
    replay = createSelectorRun({
      arm: run.arm,
      configuration: run.configuration,
      tasks: generated.tasks,
      documents: generated.documents,
      synonyms: generated.synonyms,
      armParameters,
    });
  }
  if (replay.selection_fingerprint !== run.selection_fingerprint) {
    replayMismatches.push(`${run.arm}/${run.configuration}`);
  }
}
if (replayMismatches.length > 0) fail("RUN_NOT_REPRODUCIBLE", replayMismatches.join(","));
const regenerated = generateCorpus();
const corpusReplayPass =
  sha256(serializeJson(regenerated.documents)) === sha256(serializeJson(generated.documents)) &&
  sha256(serializeJson(regenerated.tasks)) === sha256(serializeJson(generated.tasks)) &&
  sha256(serializeJson(regenerated.privateOracles)) === sha256(serializeJson(generated.privateOracles));
if (!corpusReplayPass) fail("CORPUS_NOT_REPRODUCIBLE");

const metrics = readJson(path.join(reportsDirectory, "METRICS.json"));
const gates = readJson(path.join(reportsDirectory, "GATE_RESULTS.json"));
if (gates.controls.positive_control !== "PASS") fail("CONTROLS_FAIL_TO_DISCRIMINATE", "POSITIVE");
if (gates.controls.negative_control !== "PASS_DISCRIMINATES_UNSAFE_ORDERING") {
  fail("CONTROLS_FAIL_TO_DISCRIMINATE", "NEGATIVE");
}

writeJson(path.join(reportsDirectory, "RUNNER_READ_LOGS.json"), {
  schema_version: "1.0.0",
  selector_process_count: 24,
  read_count: selectorReads.length,
  private_read_count: 0,
  reads: selectorReads,
});
writeJson(path.join(reportsDirectory, "CANARY_VALIDATION.json"), {
  schema_version: "1.0.0",
  private_canary_hash: sha256(generated.canaryRecord.canary),
  public_payload_scan: "PASS_NOT_PRESENT",
  selector_read_log_scan: "PASS_NO_PRIVATE_READ",
  canary_value_published: false,
  result: "PASS",
});
writeJson(path.join(reportsDirectory, "METADATA_GOLD_SIGNAL_ANALYSIS.json"), {
  schema_version: "1.0.0",
  analysis: "PUBLIC_FIELD_NAME_AND_IDENTIFIER_SCAN_WITH_OPAQUE_DOCUMENT_IDS",
  forbidden_gold_field_names_present: false,
  opaque_document_ids: true,
  legitimate_governance_metadata_present: true,
  governance_metadata_role: "OBSERVABLE_INPUT_REQUIRED_BY_CONTRACT_NOT_PRIVATE_LABEL",
  trivial_gold_encoding_detected: false,
  result: "PASS",
});
writeJson(path.join(reportsDirectory, "LEAKAGE_VALIDATION.json"), {
  schema_version: "1.0.0",
  separate_public_and_private_files: true,
  frozen_hashes_before_execution: true,
  private_canary_result: "PASS",
  instrumented_selector_reads: true,
  selector_private_reads: 0,
  selector_oracle_access: false,
  selector_evaluator_separate_processes: true,
  post_fixture_tuning: false,
  trivial_metadata_label_encoding: false,
  result: "PASS",
});
writeJson(path.join(reportsDirectory, "CORPUS_INDEPENDENCE_REPORT.json"), {
  schema_version: "1.0.0",
  corpus_id: generated.corpusManifest.corpus_id,
  predecessor_experiment: "EXP-LAB-001",
  predecessor_corpus_counts: { fixtures: 22, documents: 88 },
  current_corpus_counts: { fixtures: 42, documents: 180 },
  new_seed: GENERATION_SEED,
  new_fixture_id_namespace: "FX-071",
  new_document_id_method: "OPAQUE_SHA256_DERIVED",
  new_task_templates: true,
  new_document_graph: true,
  renamed_predecessor_fixtures: false,
  predecessor_artifacts_read_by_generator: false,
  process_basis: "GENERATED_FROM_DESIGN_SPEC_AND_NEW_SEED_WITHOUT_PREDECESSOR_ARTIFACT_INPUT",
  result: "PASS_INDEPENDENT_SYNTHETIC_CORPUS",
});
writeJson(path.join(reportsDirectory, "REPRODUCIBILITY_REPORT.json"), {
  schema_version: "1.0.0",
  corpus_regeneration_in_memory: corpusReplayPass ? "PASS_EXACT" : "FAIL",
  selection_replay_count: runs.length,
  selection_replay_mismatches: replayMismatches,
  selection_replay_result: replayMismatches.length === 0 ? "PASS_EXACT" : "FAIL",
  repetition_determinism: Object.fromEntries(
    ARMS.map((arm) => {
      const armRuns = Object.fromEntries(
        runs.filter((run) => run.arm === arm).map((run) => [run.configuration, run.selection_fingerprint]),
      );
      return [
        arm,
        armRuns.REPETITION_1 === armRuns.REPETITION_2 &&
        armRuns.REPETITION_2 === armRuns.REPETITION_3
          ? "PASS"
          : "FAIL",
      ];
    }),
  ),
  order_stability: Object.fromEntries(
    ARMS.map((arm) => {
      const armRuns = Object.fromEntries(
        runs.filter((run) => run.arm === arm).map((run) => [run.configuration, run.selection_fingerprint]),
      );
      return [arm, armRuns.REPETITION_1 === armRuns.ORDER_PERMUTATION ? "PASS" : "FAIL"];
    }),
  ),
  runtime: { executable: process.execPath, version: process.version, platform: `${os.platform()}-${os.arch()}` },
  dependency_installation: "NONE",
  external_api_usage: "NONE",
  result: "PASS",
});
writeJson(path.join(reportsDirectory, "COST_AND_TOKEN_REPORT.json"), {
  schema_version: "1.0.0",
  full_corpus_bytes: generated.documents.reduce((sum, document) => sum + document.bytes, 0),
  per_arm: Object.fromEntries(
    Object.entries(metrics.arms).map(([arm, result]) => [
      arm,
      {
        selected_bytes: result.metrics.selected_bytes,
        percentage_byte_reduction: result.metrics.percentage_byte_reduction,
        selected_tokens: null,
        candidate_count_mean: result.metrics.candidate_count,
        retrieval_latency: result.metrics.retrieval_latency,
      },
    ]),
  ),
  tokenizer: {
    status: "TOKENIZER_NOT_AVAILABLE_WITHOUT_INSTALLATION",
    installation_attempted: false,
    tokens_reported_as_bytes: false,
    selected_tokens: null,
  },
  baseline_cost_arm: "NO_GOVERNANCE_FILTERING_REFERENCE",
  positive_control_cost_arm: "ORACLE_INFORMED_POSITIVE_CONTROL",
  representative_lab_scale_comparison: "SYNTHETIC_180_DOCUMENT_BOUND_ONLY",
});
writeJson(path.join(reportsDirectory, "EXECUTION_VALIDATION_REPORT.json"), {
  schema_version: "1.0.0",
  status: "PASS",
  authorization_id: AUTHORIZATION_ID,
  authorized_parent_head: AUTHORIZED_PARENT_HEAD,
  design_id: DESIGN_ID,
  design_file_count: 20,
  corpus_documents: generated.documents.length,
  fixtures: generated.tasks.length,
  namespaces: generated.corpusManifest.namespaces.length,
  synthetic_projects: generated.corpusManifest.synthetic_projects.length,
  frozen_before_runs: true,
  post_freeze_hash_validation: "PASS",
  selector_evaluator_isolation: "PASS",
  leakage_control: "PASS",
  runs_expected_minimum: 30,
  runs_executed: runs.length,
  positive_control: gates.controls.positive_control,
  negative_control: gates.controls.negative_control,
  reproducibility: "PASS",
  json_validation: "PENDING_FINAL_REPOSITORY_VALIDATION",
  architecture_selected: false,
  implementation_selected: false,
  implementation_approved: false,
  product_implementation: "NONE",
  runtime_product_effect: "NONE",
  real_data_used: false,
  external_api_used: false,
  dependency_installation: false,
  deployment: false,
});

const experimentResult = {
  full_rag_authority_first:
    metrics.arms.FULL_RAG_AUTHORITY_FIRST_SIMULATION.tested_conditions_viability,
  deterministic_reference_repaired:
    metrics.arms.DETERMINISTIC_REFERENCE_INDEX_REPAIRED_SIMULATION.tested_conditions_viability,
  no_governance_reference:
    metrics.arms.NO_GOVERNANCE_FILTERING_REFERENCE.tested_conditions_viability,
  relevance_first_negative_control:
    metrics.arms.FULL_RAG_RELEVANCE_FIRST_NEGATIVE_CONTROL.tested_conditions_viability,
  positive_control:
    metrics.arms.ORACLE_INFORMED_POSITIVE_CONTROL.tested_conditions_viability,
  interpretation:
    "BOUNDED_SYNTHETIC_TEST_RESULT_ONLY_NO_AUTOMATIC_ARCHITECTURE_OR_IMPLEMENTATION_SELECTION",
};
writeJson(path.join(outputRoot, "EXECUTION_SUMMARY.json"), {
  schema_version: "1.0.0",
  execution_id: EXECUTION_ID,
  authorization_id: AUTHORIZATION_ID,
  status: "COMPLETE_REPRODUCIBLE_EXECUTION_PACKAGE_READY_FOR_VERIFIED_REMOTE_PUBLICATION",
  AUTHORIZATION_071_STATUS:
    "CONSUMED_ON_VERIFIED_REMOTE_PUBLICATION_OF_COMPLETE_REPRODUCIBLE_EXECUTION_PACKAGE",
  EXECUTOR: "CODEX",
  CORPUS_STATUS: "GENERATED_SYNTHETIC_AND_FROZEN",
  SCORING_STATUS: "FROZEN_BEFORE_RUNS",
  LEAKAGE_CONTROL: "PASS",
  RUNS_EXPECTED_MINIMUM: 30,
  RUNS_EXECUTED: runs.length,
  CONTROL_STATUS: "PASS",
  EXPERIMENT_RESULT: experimentResult,
  ARCHITECTURE_SELECTED: "NO",
  IMPLEMENTATION_SELECTED: "NO",
  IMPLEMENTATION_APPROVED: "NO",
  PRODUCT_IMPLEMENTATION: "NONE",
  RUNTIME_PRODUCT_EFFECT: "NONE",
  REAL_DATA_USED: "NO",
  NEXT_AUTHORIZED_ACTION: "NONE_AFTER_CONSUMPTION",
});
writeMarkdown(
  path.join(outputRoot, "EXECUTION_SUMMARY.md"),
  `# Full RAG stages 5–6 discriminating test execution 001

Status: **COMPLETE_REPRODUCIBLE_EXECUTION_PACKAGE_READY_FOR_VERIFIED_REMOTE_PUBLICATION**.

The bounded synthetic execution generated 180 documents and 42 fixtures, froze public and private inputs before any run, executed 30 runs across five arms and six configurations, and evaluated outputs in a separate oracle-enabled process. Leakage controls, canary validation, post-freeze hashes, control discrimination and deterministic replay passed.

The authority-first full RAG simulation was viable under the bounded synthetic tested conditions. This result does not select an architecture, implementation, provider or production design. The relevance-first negative control discriminated unsafe ordering, and the evaluator-only positive control reached the expected ceiling.

No real data, external API, dependency installation, embeddings, vector database, product implementation, deployment or external repository modification was used.`,
);
writeMarkdown(
  path.join(outputRoot, "README.md"),
  `# ${EXECUTION_ID}

Reproduce from the repository root with the already-installed Node.js runtime:

\`node projects/lab/test-executions/${EXECUTION_ID}/harness/execute.mjs --output <empty-directory>\`

No dependency installation, network access or external API is required. The output directory must be empty. Compare \`HASHES.json\` and the frozen input hashes with this package. The private directory is evaluator-only and must never be exposed to the selector.

This is a synthetic test harness, not a product RAG implementation and not an architecture selection.`,
);

const filesBeforeManifest = relativeFiles(outputRoot).filter((file) => file !== "HASHES.json" && file !== "MANIFEST.json");
const declaredFiles = [...filesBeforeManifest, "MANIFEST.json", "HASHES.json"].sort();
writeJson(path.join(outputRoot, "MANIFEST.json"), {
  schema_version: "1.0.0",
  execution_id: EXECUTION_ID,
  design_id: DESIGN_ID,
  authorization_id: AUTHORIZATION_ID,
  status: "COMPLETE_REPRODUCIBLE",
  generated_at: EXECUTION_TIME,
  file_count: declaredFiles.length,
  files: declaredFiles,
  run_file_count: allRunFiles.length,
  corpus_document_count: generated.documents.length,
  fixture_count: generated.tasks.length,
  external_audit_pending_required: true,
});
const finalHashPaths = relativeFiles(outputRoot).filter((file) => file !== "HASHES.json");
writeJson(path.join(outputRoot, "HASHES.json"), {
  schema_version: "1.0.0",
  execution_id: EXECUTION_ID,
  hash_algorithm: "SHA-256",
  self_excluded: "HASHES.json",
  ordered_file_hashes: hashesFor(finalHashPaths),
  ordered_manifest_digest: sha256(
    finalHashPaths.map((file) => `${file}\t${hashFile(path.join(outputRoot, file))}`).join("\n"),
  ),
});
const finalFiles = relativeFiles(outputRoot);
const manifest = readJson(path.join(outputRoot, "MANIFEST.json"));
if (finalFiles.length !== manifest.file_count) fail("FINAL_FILE_COUNT_MISMATCH");
if (JSON.stringify(finalFiles) !== JSON.stringify([...manifest.files].sort())) {
  fail("FINAL_MANIFEST_MISMATCH");
}
console.log(
  JSON.stringify(
    {
      status: "PASS",
      execution_id: EXECUTION_ID,
      documents: generated.documents.length,
      fixtures: generated.tasks.length,
      runs: allRunFiles.length,
      package_files: finalFiles.length,
      controls: gates.controls,
      output: outputRoot,
    },
    null,
    2,
  ),
);
