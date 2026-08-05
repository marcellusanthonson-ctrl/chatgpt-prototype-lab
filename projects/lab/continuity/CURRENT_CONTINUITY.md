# LAB continuity — autorización 196 consumida y probe zero-model

Canonical repository: `marcellusanthonson-ctrl/chatgpt-prototype-lab`  
Branch: `main`  
Entrypoint: `project-sources/chatgpt/START_HERE.md`  
HEAD policy: `VERIFY_LIVE_AT_USE`

## Estado alcanzado

La autorización 195 publicó en `README.md` la sección **“Ejecución optimizada con Codex Desktop”** y quedó `CONSUMED_VERIFIED_REMOTE_PUBLICATION`, sin autoridad residual.

La autorización 196 fue aprobada, ejecutada, publicada y consumida. La publicación principal corresponde al PR 54 y al merge:

`ea069609bbac26ccb20d025f79758d96ff42df3f`

Estado:

`CONSUMED_VERIFIED_REMOTE_PUBLICATION`

Autoridad residual:

`NONE`

## Resultado del probe 196

Resultado terminal:

`INSUFFICIENT_EVIDENCE`

El entorno observable fue Linux `6.18.35` `x86_64`, no Windows. `codex` no estaba instalado en esta superficie. Por ello no fue posible:

- crear el fresh Windows worktree exigido;
- demostrar 13/13 coincidencias raw-byte;
- ejecutar `codex login status` sobre una sesión ChatGPT preexistente;
- verificar Codex CLI `0.146.0` y su SHA-256;
- verificar localmente `gpt-5.6-sol`, reasoning `medium` y sandbox read-only;
- ejecutar los validadores desde el worktree requerido.

La regla `.gitattributes` para fijar LF en `INSTRUMENT_REDESIGN_191/**` sí está presente.

Este resultado no determina que el equipo Windows de Jonathan Martínez esté listo o no listo. Solo establece que esta superficie no aportó evidencia suficiente. Hubo cero solicitudes a modelos, cero acciones de login y ningún retest, auditoría, adjudicación, promoción, activación o integración.

## Product Leadership

`INT-LAB-004` permanece:

`CANDIDATE_NOT_ACTIVE_NOT_INTEGRATED`

Readiness permanece:

`NOT_READY_FOR_FRESH_RETEST_REISSUE`

Execution 005 / ATTEMPT-004 continúa como `BLOCKED_BEFORE_MODEL_REQUESTS`, con cero solicitudes y cero retries. No existe autorización de fresh retest ni autoridad ejecutiva activa.

## Divergencias preservadas

`CURRENT_STATE.json`, `projects/lab/PROJECT_STATE.json` y `registry/index.json` siguen siendo proyecciones agregadas desactualizadas.

`PEND-LAB-048.json` e `INTEGRATION_READINESS.json` todavía describen el probe como no autorizado. La autorización 196 no incluyó esos paths, por lo que quedaron identificados como divergencia y no fueron modificados.

## Prohibiciones vigentes

No hay autoridad para solicitudes a modelos, login, probe adicional, fresh retest, replay, regeneración, rescoring, auditoría, adjudicación, cambio de `INT-LAB-004`, promoción, activación, integración, runtime, producto, Skills, SDK, credenciales o repositorios externos.

## Siguiente acción única

Preparar una autorización separada para ejecutar el probe zero-model desde el entorno Windows real de Codex Desktop o para reconciliar evidencia generada por esa máquina.
