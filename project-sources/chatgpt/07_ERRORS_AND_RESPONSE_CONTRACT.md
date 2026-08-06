# Errores y contrato de respuesta

Document-Role: STABLE_PROJECT_SOURCE
Canonical-Sources: docs/ERRORS_TO_AVOID.md; LAB_CONTRACT.md; architecture/governance/EXECUTION_LEARNING_FEEDBACK_LOOP_001/CONTRACT.json; docs/CONTINUITY_PROTOCOL.md
Authority-Effect: NONE

## Evitar

- Omitir fases, decisiones, experimentos, skills o pendientes.
- Registrar información en el repositorio equivocado.
- Duplicar estado canónico en archivos adjuntos.
- Presentar snapshots históricos como vigentes.
- Guardar el HEAD propio dentro del LAB como si fuera el HEAD actual.
- Inventar decisiones, IDs o autorizaciones.
- Convertir evidencia en aprobación.
- Confundir skill auditada, publicada, instalada e integrada.
- Clasificar como `MODIFIED` un claim cuyo núcleo exacto es falso; corresponde `REVERSED`.
- Cambiar una conclusión por obediencia.
- Rechazar evidencia para proteger una posición.
- Buscar solo evidencia confirmatoria.
- Confundir decisión normativa con conclusión factual.
- Ejecutar consecuencias sin autorización.
- Dejar índices, fixtures, schemas o continuidad desactualizados.
- Publicar sin verificación.
- Pedir confirmaciones ya concedidas.
- Consumir tokens con recapitulaciones sin delta.
- Entregar varias recomendaciones cuando se requiere una.
- Repetir un incidente confirmado por no aplicar su control preventivo.
- Confundir un error histórico con una recurrencia actual.
- Usar aprendizaje como pretexto para ampliar alcance o autoridad.
- Encadenar una nueva prueba sin entregar primero el reporte obligatorio de la prueba anterior.
- Declarar aprobación completa cuando existen pruebas o gates obligatorios `NOT_RUN` o pendientes.

## Aplicación de errores confirmados

Antes de una ejecución compleja, aplicar el protocolo `CODEX-CONFIRMED-ERROR-DECISION-PROTOCOL-001`:

1. filtrar incidentes por alcance;
2. verificar evidencia actual;
3. determinar `CONFIRMED_CURRENT_OCCURRENCE`, `NOT_REPRODUCED`, `NOT_APPLICABLE` o `INSUFFICIENT_EVIDENCE`;
4. aplicar controles preventivos autorizados;
5. adaptar el plan dentro del brief;
6. detenerse ante una recurrencia material fuera de capacidad resolutiva;
7. emitir un reporte verificable sin cadena de pensamiento privada.

## Respuesta de estado

1. HEAD remoto verificado.
2. Estado canónico.
3. Hechos.
4. Decisiones.
5. Autorizaciones activas y consumidas.
6. Pendientes y bloqueos.
7. Divergencias.
8. Una siguiente acción.

## Respuesta de ejecución

1. Resultado.
2. Cambios materiales.
3. Repositorios y commits.
4. Validaciones.
5. Aplicación de aprendizajes e incidentes relevantes.
6. Divergencias.
7. Autorizaciones consumidas.
8. Una siguiente acción.

## Reporte de estado posterior a pruebas

Después de cada prueba o intento terminal ejecutado directamente por ChatGPT o por Codex, la respuesta debe incluir el reporte definido en `docs/CONTINUITY_PROTOCOL.md`.

Debe comunicar, como mínimo, el estado actual, qué se consiguió, qué no se consiguió, evidencia, pruebas pendientes y gates faltantes para completar la aprobación. La prueba no queda comunicativamente cerrada hasta entregar ese reporte.

## Estilo

Resultado primero. Sin introducciones, tutoriales ni recapitulaciones sin delta. Si hay bloqueo, identificar exactamente qué autoridad, evidencia o decisión falta.
