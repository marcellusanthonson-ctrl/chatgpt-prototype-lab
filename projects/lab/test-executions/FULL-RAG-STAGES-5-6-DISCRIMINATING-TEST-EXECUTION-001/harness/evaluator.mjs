import path from "node:path";
import process from "node:process";
import {
  ARMS,
  CONFIGURATIONS,
  createPositiveControlRun,
  evaluateAll,
  readJson,
  relativeFiles,
  writeJson,
} from "./lib.mjs";

function argument(name) {
  const index = process.argv.indexOf(name);
  if (index < 0 || index + 1 >= process.argv.length) throw new Error(`MISSING_ARGUMENT:${name}`);
  return process.argv[index + 1];
}

const root = path.resolve(argument("--root"));
const evaluatorReads = [];
function trackedRead(relativePath) {
  evaluatorReads.push({ path: relativePath.replaceAll("\\", "/"), access: "READ", process_role: "EVALUATOR" });
  return readJson(path.join(root, relativePath));
}

const documents = trackedRead("public/DOCUMENT_CATALOG.json").documents;
const tasks = trackedRead("public/TASKS.json").tasks;
const privateOracles = trackedRead("private/PRIVATE_ORACLES.json");
for (const configuration of CONFIGURATIONS) {
  const run = createPositiveControlRun({
    configuration,
    tasks,
    documents,
    oracleFixtures: privateOracles.fixtures,
    readLog: evaluatorReads,
  });
  writeJson(
    path.join(root, "runs", "ORACLE_INFORMED_POSITIVE_CONTROL", `${configuration}.json`),
    run,
  );
}

const runFiles = relativeFiles(path.join(root, "runs")).filter((file) => file.endsWith(".json"));
const runs = runFiles.map((file) => trackedRead(path.join("runs", file).replaceAll("\\", "/")));
if (runs.length !== 30) throw new Error(`RUN_COUNT_MISMATCH:${runs.length}`);
for (const arm of ARMS) {
  const count = runs.filter((run) => run.arm === arm).length;
  if (count !== 6) throw new Error(`ARM_RUN_COUNT_MISMATCH:${arm}:${count}`);
}
const freezeValidation = trackedRead("reports/PRE_EVALUATION_INTEGRITY.json");
const evaluation = evaluateAll({
  runs,
  tasks,
  documents,
  oracleFixtures: privateOracles.fixtures,
  initialHashPass: freezeValidation.post_freeze_hash_validation === "PASS",
  leakagePass: freezeValidation.selector_oracle_isolation === "PASS",
});
writeJson(path.join(root, "reports", "METRICS.json"), evaluation);
writeJson(path.join(root, "reports", "GATE_RESULTS.json"), {
  schema_version: "1.0.0",
  execution_id: evaluation.execution_id,
  gates_by_arm: Object.fromEntries(
    Object.entries(evaluation.arms).map(([arm, result]) => [
      arm,
      {
        role: result.role,
        gates: result.gates,
        tested_conditions_viability: result.tested_conditions_viability,
      },
    ]),
  ),
  controls: {
    positive_control:
      evaluation.arms.ORACLE_INFORMED_POSITIVE_CONTROL.tested_conditions_viability ===
        "VIABLE_UNDER_SYNTHETIC_TESTED_CONDITIONS" &&
      evaluation.arms.ORACLE_INFORMED_POSITIVE_CONTROL.metrics.macro_f1 === 1 &&
      evaluation.arms.ORACLE_INFORMED_POSITIVE_CONTROL.metrics.critical_failures === 0
        ? "PASS"
        : "FAIL",
    negative_control:
      evaluation.arms.FULL_RAG_RELEVANCE_FIRST_NEGATIVE_CONTROL.metrics.critical_failures > 0
        ? "PASS_DISCRIMINATES_UNSAFE_ORDERING"
        : "FAIL",
  },
  architecture_selected: false,
  implementation_selected: false,
  implementation_approved: false,
});
writeJson(path.join(root, "reports", "EVALUATOR_READ_LOGS.json"), {
  schema_version: "1.0.0",
  process_role: "EVALUATOR_PRIVATE_ORACLE_ACCESS",
  reads: evaluatorReads,
});
