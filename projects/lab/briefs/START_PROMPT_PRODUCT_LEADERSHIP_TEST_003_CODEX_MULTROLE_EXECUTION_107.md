Continúa ChatGPT Prototype LAB desde `marcellusanthonson-ctrl/chatgpt-prototype-lab`, rama `main`.

Antes de cualquier acción:

1. Verifica el HEAD remoto vigente de `main`.
2. Confirma que `c45738b8159db8e20f96d5446ed0420d5dac06d3` es el `expected_parent_head` de la autorización 107 y que los commits posteriores solo incorporan autorización, brief y este prompt.
3. Lee `project-sources/chatgpt/START_HERE.md` y sigue exactamente su orden.
4. Lee:
   - `projects/lab/authorizations/AUTHORIZATION_LAB_PRODUCT_LEADERSHIP_TEST_003_CODEX_MULTROLE_EXECUTION_107.json`
   - `projects/lab/briefs/BRIEF_PRODUCT_LEADERSHIP_TEST_003_CODEX_MULTROLE_EXECUTION_107.json`
   - `projects/lab/test-designs/PRODUCT-LEADERSHIP-PROSPECTIVE-VALUE-TEST-003/PROPOSAL.json`
   - `projects/lab/test-designs/PRODUCT-LEADERSHIP-PROSPECTIVE-VALUE-TEST-003/EXECUTION_CONTRACT.json`
   - `projects/lab/test-executions/PRODUCT-LEADERSHIP-PROSPECTIVE-VALUE-TEST-003/PREFLIGHT_STOP_106.json`

MODO: `MULTROLE_SYNTHETIC_EXECUTION_FAIL_CLOSED`.

Tu primera tarea no es generar fixtures. Primero debes demostrar y documentar separación operacional real entre:

- PACKAGE generator;
- BASELINE generator;
- independent normalization operator;
- randomization custodian;
- evaluator 1;
- evaluator 2;
- evaluator 3;
- independent auditor.

Usa workspaces, procesos o sesiones separadas y registra sus identidades, permisos, accesos, herramientas y timestamps. El operador de normalización no puede acceder a oráculos ni mappings. Los evaluadores no pueden conocer los brazos. El custodio de randomización es el único que conserva el mapping antes del unblinding. El auditor opera en lectura independiente.

Antes de generar contenido publica y congela:

- `ROLE_ASSIGNMENT_MANIFEST.json`;
- `ACCESS_MATRIX.json`;
- `SESSION_AND_TOOL_LOG_MANIFEST.json`;
- `ORACLE_MAPPING_CUSTODY_LOG.json`;
- `PRE_UNBLIND_CHECKPOINT_MANIFEST.json`;
- `HASH_AND_LINE_ENDING_VALIDATION.json`;
- `PREFLIGHT_RESULT.json`.

El checkpoint previo al unblinding debe ser externo, inmutable y verificable. Todos los archivos deben usar UTF-8, LF, sin BOM, y SHA-256 sobre bytes canónicos.

FAIL CLOSED: si cualquier separación de rol, log, custodia, checkpoint, hash o condición contractual no puede probarse, detente antes de generar fixtures, outputs, scores u oráculos. Publica un stop package completo y consume la autorización 107 por stop documentado.

Solo si `PREFLIGHT_RESULT = PASS`, ejecuta exactamente las dos repeticiones y los 320 IDs congelados por el contrato. No cambies umbrales después de ver resultados. Publica el paquete reproducible completo, verifica el remoto y consume la autorización 107.

No actives ni integres Product Leadership. No modifiques Symphonie ni productos. No uses datos reales, runtime, RAG, embeddings, vector database, deployment o release.
