# Continuidad entre conversaciones

Document-Role: STABLE_PROJECT_SOURCE
Canonical-Sources: docs/CONTINUITY_PROTOCOL.md; architecture/governance/PROGRESSIVE_CONVERSATION_CONTINUITY_001/CONTRACT.json; architecture/governance/FOCUS_AND_ROADMAP_PRESERVATION_001/CONTRACT.json
Authority-Effect: NONE

## Función

La continuidad preserva memoria **y posición de trabajo**. Se usa al cambiar de conversación y progresivamente cuando un trabajo material abre ramas laterales o acumula contexto que todavía no pertenece a un owner-artifact.

## Paquete CURRENT

- `CURRENT_CONTINUITY.json`: fuente estructurada.
- `CURRENT_CONTINUITY.md`: vista humana.
- `ATTACHMENT_MANIFEST.json`: archivos y orden.
- `START_PROMPT.md`: primer mensaje.
- `archive/`: paquetes reemplazados.

## Sesión progresiva

La sesión activa indicada por CURRENT contiene `SESSION.json`, `CONTEXT_LEDGER.json`, `OPEN_CONTEXT.json`, `WORK_POSITION_GRAPH.json`, `PROMOTION_MAP.json` y `SESSION_SUMMARY.md`.

Campos de posición obligatorios: main track, main objective, anchor node, last completed node, active node, next required node, return node, current branch, branch effect e integration target.

## Regla de ramas

Una discusión lateral crea una rama; no mueve silenciosamente la posición principal. Toda rama abierta conserva un punto de retorno. Cambiar main objective requiere cambio explícito de foco por Jonathan Martínez.

## Generación

1. Verificar HEAD.
2. Leer estado, registros, owner-artifacts y reglas operativas.
3. Leer la sesión activa y su grafo de posición.
4. Detectar información material no incorporada y clasificarla.
5. Preservar main track, ramas y return nodes.
6. Construir manifiesto y START_PROMPT.
7. Validar referencias.
8. Archivar el CURRENT anterior cuando corresponda.

El nuevo modelo entrega HEAD, estado, decisiones, autorizaciones, pendientes, divergencias, posición de trabajo y una siguiente acción antes de ejecutar.

## Reporte posterior a cada prueba

Después de cada prueba o intento terminal ejecutado directamente por ChatGPT o Codex, entregar a Jonathan un reporte antes de iniciar otra prueba. Debe identificar resultado, estado, logros, evidencia, defectos/bloqueos, pruebas pendientes y `NOT_RUN`, gates, autorización y una sola siguiente acción. El reporte no crea autoridad.
