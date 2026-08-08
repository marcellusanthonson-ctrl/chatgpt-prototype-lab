# Gobierno, autoridad y verdad

Document-Role: STABLE_PROJECT_SOURCE
Canonical-Sources: LAB_CONTRACT.md; docs/CANONICAL_OWNERSHIP.md; docs/AUTHORIZATION_APPROVAL_RESPONSE_PROTOCOL.md
Authority-Effect: NONE

## Función y propiedad

El LAB conserva gobierno, autoridad, decisiones transversales, errores, patrones, briefs y continuidad. No es runtime.

- LAB: gobierno y continuidad.
- Repositorio de proyecto: estado operativo, fases, contratos, schemas y roadmap.
- MammothSkills: producción, auditoría, adaptación y release de skills.
- Evidencia histórica: resultados inmutables, nunca estado vigente.

Un consumidor referencia al propietario y no copia historiales completos.

## Clases

HECHO, PROPUESTA, IDEA, DECISIÓN, AUTORIZACIÓN, RESULTADO, PENDIENTE, ERROR y EVIDENCIA son clases separadas. No convertir una en otra por inferencia.

## Autoridad

Jonathan Martínez es el único aprobador normativo y ejecutivo. ChatGPT coordina y valida; Claude participa cuando se le asigna descubrimiento o definición; Codex ejecuta técnicamente sin autoridad autónoma.

Una conversación, plan, commit, prueba o resultado no crea autorización. Las autorizaciones consumidas, expiradas o revocadas no se reutilizan.

## Solicitud obligatoria de autorización

Toda vez que ChatGPT solicite autoridad de ejecución debe terminar su respuesta con el script textual completo y copiable definido en `docs/AUTHORIZATION_APPROVAL_RESPONSE_PROTOCOL.md`.

La autorización falla cerrada si el script falta, es ambiguo, está incompleto, identifica otro ID o scope, o su parent/baseline dejó de estar vigente. No inferir `GRANTED` desde “ok”, “continúa”, una propuesta, un commit o un resultado técnico. Preservar la respuesta textual de Jonathan como fuente humana y registrar `grant_inferred: false`.

## Verdad

Jonathan puede decidir preferencias y trade-offs. La verdad factual se determina por evidencia y la ejecución por autorización. Ninguna autoridad sustituye a otra.
