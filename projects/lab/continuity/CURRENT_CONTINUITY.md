# LAB continuity — autorización 196 y probe zero-model

Canonical repository: `marcellusanthonson-ctrl/chatgpt-prototype-lab`  
Branch: `main`  
Entrypoint: `project-sources/chatgpt/START_HERE.md`  
HEAD policy: `VERIFY_LIVE_AT_USE`

## Estado alcanzado

La autorización 195 publicó en `README.md` la sección **“Ejecución optimizada con Codex Desktop”**. Su lifecycle registra `CONSUMED_VERIFIED_REMOTE_PUBLICATION`, con PR de publicación 52, merge `ad3b5ff55eb811662410bfc888b65ff73d8bc24c`, PR de cierre 53 y HEAD de cierre `9e095a25c367e980cd4a69d224c26b3c73b7d0f4`. No conserva autoridad residual.

La autorización 196 fue aprobada por Jonathan Martínez para reconciliar esta continuidad y ejecutar un probe local zero-model bajo límites fail-closed.

## Resultado del probe 196

Resultado terminal:

`INSUFFICIENT_EVIDENCE`

El entorno observable fue Linux `6.18.35` `x86_64`, no Windows. `codex` no está instalado en esta superficie, por lo que no fue posible:

- crear el fresh Windows worktree exigido;
- demostrar 13/13 coincidencias raw-byte;
- ejecutar `codex login status` sobre una sesión ChatGPT preexistente;
- verificar Codex CLI `0.146.0` y su SHA-256;
- verificar localmente `gpt-5.6-sol`, reasoning `medium` y sandbox read-only;
- ejecutar los validadores desde el worktree requerido.

La regla `.gitattributes` para fijar LF en `INSTRUMENT_REDESIGN_191/**` sí está presente.

Este resultado **no** determina que el equipo Windows de Jonathan esté listo o no listo. Solo determina que esta superficie no ofrece evidencia suficiente. No se realizó ninguna solicitud a modelos, login, retest, auditoría, adjudicación, promoción, activación o integración.

## Product Leadership

`INT-LAB-004` permanece:

`CANDIDATE_NOT_ACTIVE_NOT_INTEGRATED`

Readiness permanece:

`NOT_READY_FOR_FRESH_RETEST_REISSUE`

Execution 005 / ATTEMPT-004 continúa como `BLOCKED_BEFORE_MODEL_REQUESTS`, con cero solicitudes y cero retries. No existe autorización de fresh retest.

## Autorización 196

Estado durante esta publicación:

`EXECUTED_AWAITING_VERIFIED_REMOTE_PUBLICATION`

Resultado:

`INSUFFICIENT_EVIDENCE`

Después de verificar la publicación remota debe quedar `CONSUMED` y sin autoridad residual.

## Divergencias preservadas

`CURRENT_STATE.json`, `projects/lab/PROJECT_STATE.json` y `registry/index.json` siguen siendo proyecciones agregadas desactualizadas.

`PEND-LAB-048.json` e `INTEGRATION_READINESS.json` todavía describen el probe como no autorizado. La autorización 196 no incluyó esos paths, por lo que esta ejecución los identifica como divergencia pero no los modifica.

## Prohibiciones vigentes

No hay autoridad para solicitudes a modelos, login, fresh retest, replay, regeneración, rescoring, auditoría, adjudicación, cambio de `INT-LAB-004`, promoción, activación, integración, runtime, producto, Skills, SDK, credenciales o repositorios externos.

## Siguiente acción única

Publicar y verificar remotamente el resultado documental de la autorización 196 y consumirla sin autoridad residual.

Después del consumo, cualquier nueva comprobación deberá ejecutarse mediante una autorización separada desde el entorno Windows real de Codex Desktop o reconciliar evidencia generada por esa máquina.
