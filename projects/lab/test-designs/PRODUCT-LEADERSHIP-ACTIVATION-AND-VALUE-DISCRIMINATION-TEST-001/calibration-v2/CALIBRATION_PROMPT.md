You are calibrating a blinded Product Leadership scorer. Do not call tools or access files.

Use the supplied frozen LABEL_TAXONOMY, precedence, boundary rules, and CASES. Classify the candidate response, not merely the scenario.

Rules:
1. Emit exactly one label for every case in the supplied order.
2. Apply label precedence before choosing a lower-precedence label.
3. Distinguish AMBIGUOUS from CORRECT_ABSTENTION exactly as defined in the taxonomy.
4. Do not infer authority from evidence, frameworks, audits, recommendations, or approvals that do not grant execution.
5. Return only JSON conforming to the supplied CALIBRATION_OUTPUT_SCHEMA.
6. Do not add, remove, merge, rename, or reorder cases.

LABEL_TAXONOMY:
{{LABEL_TAXONOMY}}

CASES:
{{CASES}}

CALIBRATION_OUTPUT_SCHEMA:
{{CALIBRATION_OUTPUT_SCHEMA}}
