# Inicio canónico para ChatGPT

Document-Role: CANONICAL_ENTRYPOINT
Canonical-Repository: marcellusanthonson-ctrl/chatgpt-prototype-lab
Canonical-Branch: main
Head-Policy: VERIFY_LIVE_AT_USE
Authority-Effect: NONE

## Inicio obligatorio

Antes de responder sobre estado, decisiones, autorizaciones, errores, pendientes o próxima acción:

1. Verificar el HEAD remoto vigente de `main`; nunca tomar un HEAD almacenado dentro del propio LAB como estado actual.
2. Leer `LAB_CONTRACT.md`.
3. Leer `METHODOLOGY.md`.
4. Leer `docs/MODEL_OPERATING_RULES.md`.
5. Leer `CURRENT_STATE.json`.
6. Leer `registry/index.json` y `registry/projects.json`.
7. Identificar el proyecto activo y leer su `PROJECT_STATE.json`.
8. Leer decisiones, autorizaciones, errores, pendientes, roadmap y evidencia aplicables desde sus owner-artifacts.
9. Leer `projects/lab/continuity/CURRENT_CONTINUITY.json` y la sesión activa indicada allí para reconstruir posición de trabajo, ramas y retorno.
10. Leer las fuentes de esta carpeta en el orden de `01_SOURCE_MANIFEST.md`.

JSON es la fuente estructurada; Markdown es vista humana. Los agregados son proyecciones de navegación y no reemplazan al owner-artifact de una decisión, autorización, error, pendiente o evidencia.

## GOV-007

Antes de una instrucción material que pueda cambiar estado, prioridad, foco, autoridad, owner-artifacts o posición de trabajo, aplicar el filtro `GOV-007` conforme a `schemas/impact-preview.schema.json`. La vista previa no crea autoridad.

## Continuidad de foco

Aplicar `FOCUS_AND_ROADMAP_PRESERVATION_001` y `PROGRESSIVE_CONVERSATION_CONTINUITY_001`: una rama lateral no mueve el main track; cambiar el objetivo principal exige decisión humana explícita.

Si GitHub no puede consultarse, declararlo y no inventar estado, HEAD, decisiones ni autorizaciones. Estas fuentes no crean autorización. Una modificación requiere aprobación explícita, vigente y delimitada de Jonathan Martínez.
