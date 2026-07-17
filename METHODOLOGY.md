# Metodología del LAB — v2.0

## 1. Objetivo

Mantener conocimiento verificable, autoridad explícita y ejecución productiva sin duplicación ni derivaciones no autorizadas.

## 2. Reconstrucción

Leer en este orden:

1. LAB_CONTRACT.md.
2. METHODOLOGY.md.
3. CURRENT_STATE.json.
4. registry/index.json.
5. registry/projects.json.
6. PROJECT_STATE.json del proyecto.
7. decisiones vigentes.
8. autorizaciones.
9. errores abiertos.
10. evidencia y patrones aplicables.
11. paquete CURRENT de continuidad, si existe.

Verificar repositorios, ramas y HEAD antes de afirmar estado.

## 3. Ciclo de información

1. Capturar la afirmación material.
2. Clasificarla como hecho, propuesta, idea, decisión, autorización, resultado, pendiente, error o evidencia.
3. Asignar proyecto y propietario canónico.
4. Registrar source_refs.
5. Vincular relaciones sin duplicar el contenido.
6. Validar estados y referencias.
7. Cerrar la sesión con control de omisiones.

## 4. Ciclo de decisión

Estados: DRAFT, PROPOSED, UNDER_REVIEW, APPROVED, REJECTED, SUPERSEDED o WITHDRAWN.

Solo Jonathan Martínez aprueba. Una decisión incorrecta no se elimina: otra decisión la reemplaza explícitamente. Toda decisión debe indicar alcance, consecuencias, no-autorizaciones y archivos afectados.

## 5. Ciclo de autorización

Estados: PROPOSED, GRANTED, CONSUMED, EXPIRED, REVOKED o REJECTED.

Una autorización contiene alcance, repositorio, rama, acciones permitidas, prohibiciones y criterio de consumo. Al publicar y verificar el resultado se marca CONSUMED. No quedan permisos implícitos.

## 6. Ideas e integraciones

Las ideas se registran sin convertirlas en roadmap. Las integraciones usan estados separados: IDEA, CANDIDATE, EVALUATED, PROPOSED, AUTHORIZED, INTEGRATED, REMOVED o REJECTED.

Una evaluación técnica o experimento no puede superar PROPOSED sin autorización explícita. Cada integración debe identificar productor, consumidor, versión, evidencia y rollback.

## 7. Brief de ejecución

Toda ejecución compleja debe recibir un brief JSON conforme a schemas/brief.schema.json. El brief limita contexto, paths, autoridad, entregables, validaciones y stop conditions. El modelo no debe reenviar historia que no contribuya al objetivo.

## 8. Continuidad

El protocolo estándar está en docs/CONTINUITY_PROTOCOL.md. CURRENT_CONTINUITY.json es canónico; Markdown y START_PROMPT.md son vistas operativas. El manifiesto enumera attachments obligatorios, opcionales y faltantes.

## 9. Auditoría

1. Fijar repositorio, rama, HEAD, alcance y autoridad.
2. Inventariar sin modificar.
3. Separar observación, hipótesis, finding, corrección y aprobación.
4. Aplicar correcciones solo si están autorizadas.
5. Validar cambio exacto, schemas, referencias, estados y efectos.
6. Verificar publicación y registrar autorizaciones consumidas.

## 10. Productividad

- Agrupar operaciones independientes.
- Preguntar solo por bloqueos materiales.
- No repetir contexto ya presente en el brief.
- No generar resúmenes genéricos.
- Resolver correcciones menores dentro del alcance sin pausar.
- Entregar resultado, cambios, validación, divergencias y siguiente acción.
- Recomendar una sola acción.
- No usar lenguaje de certeza mayor que la evidencia.

## 11. Fail closed

Detenerse ante autoridad ausente, repositorio ambiguo, datos sensibles no autorizados, destino irreversible, contradicción canónica o expansión material del alcance. Una pregunta no bloqueante no detiene la ejecución.
