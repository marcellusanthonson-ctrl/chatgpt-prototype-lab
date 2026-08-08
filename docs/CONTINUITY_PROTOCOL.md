# Protocolo estándar de continuidad

Se activa cuando Jonathan solicita continuar un proyecto en otra conversación y se mantiene progresivamente durante trabajo material para preservar también la posición exacta.

## Archivos CURRENT

- `projects/lab/continuity/CURRENT_CONTINUITY.json`: fuente estructurada de continuidad actual.
- `projects/lab/continuity/CURRENT_CONTINUITY.md`: vista humana.
- `projects/lab/continuity/ATTACHMENT_MANIFEST.json`: archivos y orden.
- `projects/lab/continuity/START_PROMPT.md`: primer mensaje listo para usar.
- `projects/lab/continuity/archive/`: paquetes CURRENT reemplazados, preservados.

## Sesión progresiva

Aplicar `architecture/governance/PROGRESSIVE_CONVERSATION_CONTINUITY_001/CONTRACT.json`. Una sesión material usa:

- `SESSION.json`
- `CONTEXT_LEDGER.json`
- `OPEN_CONTEXT.json`
- `WORK_POSITION_GRAPH.json`
- `PROMOTION_MAP.json`
- `SESSION_SUMMARY.md`

La sesión no sustituye owner-artifacts ni crea autoridad.

## Posición obligatoria

Toda continuidad material conserva: `main_track`, `main_objective`, `anchor_node`, `last_completed_node`, `active_node`, `next_required_node`, `return_node`, `current_branch`, `branch_effect` e `integration_target`.

Una discusión lateral crea una rama y mantiene el `return_node`; no cambia por inferencia la posición principal. Cambiar el objetivo principal requiere un cambio de foco explícito. El foco se rige por `FOCUS_AND_ROADMAP_PRESERVATION_001`.

## Contenido obligatorio

Proyecto; fecha; repositorios, ramas y política de HEAD; orden de lectura; hechos; propuestas; ideas; integraciones posibles; decisiones; autorizaciones activas y consumidas; resultados; pendientes; errores; riesgos; experimentos; skills; roadmap; portafolio preservado; posición de trabajo; ramas abiertas; material no incorporado; attachments; límites y una siguiente acción.

Todo elemento material incluye `source_refs`. Las transcripciones completas solo se preservan cuando son evidencia indispensable o una fuente humana de aprobación.

## Generación

1. Verificar HEAD remoto.
2. Leer `START_HERE.md` y `docs/MODEL_OPERATING_RULES.md` en el orden canónico.
3. Leer estado, registros y owner-artifacts aplicables.
4. Leer la sesión activa y resolver su posición de trabajo.
5. Extraer información material no incorporada y clasificarla.
6. Preservar main track, ramas y return nodes.
7. Construir el manifiesto de attachments.
8. Generar la primera frase y una única siguiente acción.
9. Validar referencias y archivar el paquete CURRENT anterior byte-preserving cuando sea requerido.
10. Si cambia un HEAD externo observado, marcar la observación `STALE`; para el HEAD propio del LAB usar siempre `VERIFY_LIVE_AT_USE`.

## Primera respuesta del nuevo modelo

Debe presentar contexto reconstruido, HEAD verificado, estado, decisiones, autorizaciones, pendientes, divergencias, posición de trabajo y una siguiente acción. No debe ejecutar hasta identificar autoridad vigente para la acción concreta.

## Material no incorporado

Un contexto material discutido pero aún no promovido se registra como `MATERIAL_CONVERSATION_CONTEXT_NOT_YET_INCORPORATED` con owner objetivo o disposición pendiente. No se omite silenciosamente y tampoco se convierte en estado canónico sin autoridad.

## Reporte obligatorio posterior a cada prueba

Después de cada prueba o intento terminal ejecutado directamente por ChatGPT o por Codex, entregar a Jonathan un reporte antes de iniciar otra prueba. Aplica a `PASS`, `FAIL`, `BLOCKED`, `INSUFFICIENT_EVIDENCE`, cancelaciones y detenciones preventivas.

El reporte incluye como mínimo: ID e intento; ejecutor y entorno; objetivo y alcance; resultado exacto y límites; estado antes/después; logros; no-logros, defectos y bloqueos; evidencia; pruebas ejecutadas y `NOT_RUN`; gates pendientes; estado de aprobación; estado y consumo de autorización; y una única siguiente acción.

Un reporte no crea aprobación ni autorización. No puede declararse aprobación completa mientras existan pruebas o gates obligatorios pendientes.

## Proyecto ChatGPT

La introducción del proyecto ChatGPT referencia `project-sources/chatgpt/START_HERE.md`. `docs/MODEL_OPERATING_RULES.md` es lectura obligatoria. Las reglas operativas se leen desde el repositorio; un adjunto de bootstrap solo puede apuntar al repositorio, rama y entrypoint.
