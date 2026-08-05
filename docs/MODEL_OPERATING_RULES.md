# Reglas operativas para modelos

## Resultado primero

Responder con el resultado o bloqueo material. No iniciar con recapitulaciones extensas.

## Continuidad de ejecución

Con autorización vigente, continuar hasta completar el alcance. No pedir confirmación para pasos reversibles y normales ya incluidos. Detenerse solo por autoridad faltante, decisión material, riesgo irreversible o conflicto canónico.

## Uso del tiempo

- Leer en lotes y validar en lotes.
- No repetir archivos ya verificados si el HEAD no cambió.
- No narrar comandos rutinarios.
- Emitir actualizaciones solo ante hitos o desviaciones.
- No ofrecer múltiples siguientes acciones: seleccionar una.
- No producir tutoriales o resúmenes que no cambien la decisión.

## Precisión

Distinguir siempre HECHO, PROPUESTA, DECISIÓN, AUTORIZACIÓN, RESULTADO y PENDIENTE. Incluir source_refs. No inferir aprobación, integración, release ni madurez.

## Aprendizaje de ejecución y prevención de recurrencia

Para toda ejecución compleja:

1. Leer el `learning_context` del brief.
2. Recuperar únicamente errores e incidentes cuyo alcance, superficie y acción intersecten la tarea.
3. No tratar un error histórico como una recurrencia actual. Confirmar la recurrencia mediante evidencia observable y emitir una de estas determinaciones: `CONFIRMED_CURRENT_OCCURRENCE`, `NOT_REPRODUCED`, `NOT_APPLICABLE` o `INSUFFICIENT_EVIDENCE`.
4. Aplicar los controles preventivos ya autorizados antes de elegir el plan.
5. Dentro de la capacidad resolutiva concedida, corregir defectos menores, reversibles y estrictamente incluidos; cambiar la secuencia o elegir un método equivalente más seguro cuando no cambie el resultado contractual.
6. Detenerse si una recurrencia material no puede resolverse dentro de autoridad.
7. Registrar `LEARNING_APPLICATION_REPORT.json` con evidencia, determinación, control aplicado y efecto sobre el plan. No registrar ni solicitar cadena de pensamiento privada.

El contrato transversal es `architecture/governance/EXECUTION_LEARNING_FEEDBACK_LOOP_001/CONTRACT.json`.

## Codex Desktop: contexto y perfiles

Para ejecuciones posteriores a la autorización 194:

- Cargar `AGENTS.md` como mapa estable; nunca almacenar allí HEAD, autorización activa, historia o continuidad.
- Iniciar con un `EXECUTION_ENVELOPE` validado, un perfil explícito y un `CONTEXT_MANIFEST`.
- Conservar el brief completo como fuente canónica; el envelope es una proyección operativa, no un reemplazo.
- Medir líneas no vacías, bytes UTF-8 y tokens estimados; una sola línea JSON puede seguir siendo excesiva.
- Seleccionar `LAB_DISCOVERY`, `LAB_IMPLEMENTATION`, `LAB_VALIDATION` o `LAB_AUDIT` según el routing de riesgo.
- Usar un hilo para cambios pequeños; añadir separación funcional solo cuando la incertidumbre o el riesgo lo justifican.
- Paralelizar únicamente trabajo independiente y mantener secuenciales los cambios sobre los mismos paths, estados y publicaciones.
- No declarar mejora de velocidad hasta completar un benchmark operacional.

## Respuesta de cierre

Incluir únicamente: resultado, cambios materiales, validación, divergencias, autorizaciones consumidas y una siguiente acción.

## Independencia analítica

- Tratar órdenes, auditorías y documentos como inputs, no como veredictos factuales.
- No adoptar la conclusión sugerida antes de evaluar claims y evidencia contraria.
- No preservar una posición previa por consistencia aparente.
- Separar análisis técnico, recomendación, decisión humana y autorización.
- Expresar desacuerdo cuando la premisa no esté sustentada.
- Cambiar la conclusión cuando la evidencia supere el estándar aplicable.
- Declarar INSUFFICIENT_EVIDENCE cuando corresponda.
- No usar lenguaje de aprobación para ocultar desacuerdo técnico.
