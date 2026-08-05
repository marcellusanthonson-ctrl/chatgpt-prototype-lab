# Continuidad LAB — Product Leadership pendiente de rediseño del instrumento

## Estado verificado

El HEAD remoto de `main` verificado al crear este paquete fue:

`c21af774f3bf3248867bda365b36eb62e15f1a01`

No debe asumirse vigente en la próxima conversación. Se aplica `VERIFY_LIVE_AT_USE`.

El paquete de continuidad fue publicado mediante PR #40 en:

`57579e007c537db5875fa57c262a721300608e0f`

La autorización 191 quedó consumida después de verificar esa publicación y no deja autoridad residual.

Product Leadership (`INT-LAB-004`) continúa como:

`CANDIDATE_NOT_ACTIVE_NOT_INTEGRATED`

La fábrica contractual está completa y validada, pero la integración no ha sido promovida, activada ni adoptada por Symphonie.

## Ejecución 004 y auditoría Phase 3

`PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-004 / ATTEMPT-003` produjo 52 fixtures, cuatro brazos, 112 outputs y 112 scores.

El runner emitió históricamente:

`FAIL_REVISE_OR_REJECT_EVIDENCE_READY_FOR_SEPARATE_EXTERNAL_AUDIT_DECISION`

Ese resultado se conserva como salida histórica inmutable. La auditoría independiente de Claude y la reconciliación canónica bajo la autorización 190 determinaron:

- dictamen de auditoría: `MODIFIED`;
- interpretación válida de la ejecución: `INSUFFICIENT_EVIDENCE`;
- adjudicación del paquete: `NONE`;
- recomendación: `RETEST_DUE_TO_MATERIAL_EXECUTION_OR_DESIGN_DEFECT`.

La evidencia no permite afirmar que el paquete Product Leadership esté bien o mal diseñado. Sí confirma que el instrumento utilizado para evaluarlo presentaba defectos materiales.

## Defectos confirmados del instrumento

1. Los controles negativos no ejercitaron el comportamiento inseguro esperado.
2. El runner no podía emitir el estado canónico `INSUFFICIENT_EVIDENCE`.
3. El scorer penalizó información verdadera del paquete por no recibir contexto suficiente.
4. Los fixtures no satisfacían el contrato mínimo de entrada del paquete.
5. Los prompts baseline y package no eran simétricos salvo por la presencia del paquete.
6. Las stop conditions canónicas no fueron aplicadas.

## Pendiente crítico

`PEND-LAB-048` está abierto con estado:

`OPEN_AWAITING_SEPARATE_INSTRUMENT_REDESIGN_AND_RETEST_AUTHORIZATION`

La siguiente etapa debe corregir el instrumento antes de cualquier retest. Requiere una autorización separada para:

- simetría de brazos;
- contexto válido del scorer o redacción del estado del paquete;
- controles negativos fijos o no rechazables;
- fixtures y oráculos alineados con `INPUT_CONTRACT`;
- rama `INSUFFICIENT_EVIDENCE` y stop conditions;
- calibración de la rúbrica real;
- cadena de custodia del runner;
- gates y límites de claims del futuro test.

No existe autoridad para ejecutar ese rediseño, repetir la prueba, modificar el paquete, promoverlo, activarlo o integrarlo.

## Uso resolutivo de Codex

Se conserva como principio operativo solicitado por Jonathan Martínez:

**Codex es el ejecutor técnico delimitado y resolutivo; ChatGPT gobierna, valida y reconcilia.**

Para cada ejecución futura:

- ChatGPT prepara un brief JSON completo con repositorio, rama, HEAD vivo, fuentes, alcance, paths, acciones permitidas y prohibidas, entregables, validaciones, stop conditions y permisos de publicación.
- Una vez concedida una autorización explícita, Codex continúa sin confirmaciones repetidas hasta completar el alcance o encontrar una condición material de detención.
- Codex resuelve dentro del alcance los problemas técnicos, documentales y de validación menores; ejecuta validaciones determinísticas y devuelve evidencia exacta.
- Codex no se limita a entregar un plan cuando la ejecución está autorizada y es factible.
- Codex no infiere autoridad, no toma decisiones normativas y no promueve ni integra candidatos por iniciativa propia.
- Commit, push, PR y merge requieren permisos explícitos en la autorización aplicable.

Codex solo debe detenerse por autoridad ausente o consumida, mismatch del parent HEAD, riesgo de credenciales o identidad, acción destructiva no autorizada, expansión material de alcance, sustitución de modelo o tooling, contradicción canónica irresoluble o gate obligatorio fallido.

## Divergencias conocidas

`CURRENT_STATE.json`, `projects/lab/PROJECT_STATE.json`, `registry/index.json`, `projects/lab/integrations/index.json`, `INT-LAB-004.json` y el roadmap del programa contienen vistas históricas anteriores a la reconciliación 190.

Para el estado actual de Product Leadership prevalecen los registros específicos:

- `EVD-LAB-AUD-008`;
- `REA-LAB-010`;
- `REC-LAB-PL003-EXEC004-AUDIT190-001`;
- `PEND-LAB-048`;
- lifecycle y autorización 190.

No se autorizó corregir las vistas agregadas dentro de este paquete de continuidad.

## Autoridad

- Autorización 190: consumida, sin autoridad residual.
- Autorización 191: consumida después de la publicación verificada, sin autoridad residual.
- Rediseño del instrumento: no autorizado.
- Retest o nuevas llamadas al modelo: no autorizados.
- Modificación del paquete Product Leadership: no autorizada.
- Promoción, activación, integración, runtime o producto: no autorizados.

## Siguiente acción única

Preparar una autorización explícita y un brief resolutivo para Codex que cubran exclusivamente el rediseño del instrumento exigido por `PEND-LAB-048`, sin ejecutar todavía el retest.
