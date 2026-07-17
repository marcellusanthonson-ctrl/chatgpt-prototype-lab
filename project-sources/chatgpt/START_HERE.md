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
4. Leer `CURRENT_STATE.json`.
5. Leer `registry/index.json` y `registry/projects.json`.
6. Identificar el proyecto activo y leer su `PROJECT_STATE.json`.
7. Leer decisiones, autorizaciones, errores, pendientes, roadmap, evidencia y continuidad aplicables.
8. Leer las fuentes de esta carpeta en el orden de `01_SOURCE_MANIFEST.md`.

JSON es la fuente estructurada; Markdown es una vista humana. Si GitHub no puede consultarse, declararlo y no inventar estado, HEAD, decisiones ni autorizaciones.

Estas fuentes no crean autorización. Una modificación requiere aprobación explícita, vigente y delimitada de Jonathan Martínez.
