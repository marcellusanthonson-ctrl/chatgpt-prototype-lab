import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import {
  SELECTOR_ARMS,
  CONFIGURATIONS,
  createSelectorRun,
  readJson,
  writeJson,
} from "./lib.mjs";

function argument(name) {
  const index = process.argv.indexOf(name);
  if (index < 0 || index + 1 >= process.argv.length) throw new Error(`MISSING_ARGUMENT:${name}`);
  return process.argv[index + 1];
}

const root = path.resolve(argument("--root"));
const arm = argument("--arm");
const configuration = argument("--configuration");
if (!SELECTOR_ARMS.includes(arm)) throw new Error(`SELECTOR_ARM_FORBIDDEN:${arm}`);
if (!CONFIGURATIONS.includes(configuration)) throw new Error(`UNKNOWN_CONFIGURATION:${configuration}`);

const readLog = [];
function trackedRead(relativePath) {
  const normalized = relativePath.replaceAll("\\", "/");
  if (normalized.includes("/private/") || normalized.startsWith("private/")) {
    throw new Error(`PRIVATE_READ_BLOCKED:${normalized}`);
  }
  const absolute = path.resolve(root, normalized);
  if (!absolute.startsWith(root + path.sep)) throw new Error(`READ_OUTSIDE_ROOT_BLOCKED:${normalized}`);
  readLog.push({ path: normalized, access: "READ", process_role: "SELECTOR" });
  return readJson(absolute);
}

const readManifest = trackedRead("public/READ_MANIFEST.json");
const allowed = new Set(readManifest.selector_allowed_reads);
const requiredReads = [
  "public/DOCUMENT_CATALOG.json",
  "public/TASKS.json",
  "public/SYNONYMS.json",
  "frozen/ARM_PARAMETERS.json",
];
for (const relativePath of requiredReads) {
  if (!allowed.has(relativePath)) throw new Error(`READ_NOT_ALLOWLISTED:${relativePath}`);
}

const documents = trackedRead("public/DOCUMENT_CATALOG.json").documents;
const tasks = trackedRead("public/TASKS.json").tasks;
const synonyms = trackedRead("public/SYNONYMS.json").synonyms;
const armParameters = trackedRead("frozen/ARM_PARAMETERS.json");
const run = createSelectorRun({
  arm,
  configuration,
  tasks,
  documents,
  synonyms,
  armParameters,
  readLog,
});
const output = path.join(root, "runs", arm, `${configuration}.json`);
writeJson(output, run);
fs.writeFileSync(
  path.join(root, "runs", arm, `${configuration}.complete`),
  `${run.selection_fingerprint}\n`,
  "utf8",
);
