# Errores y contrato de respuesta

Document-Role: STABLE_PROJECT_SOURCE
Canonical-Sources: docs/ERRORS_TO_AVOID.md; LAB_CONTRACT.md
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
- Publicar sin preflight y verificación.
- Pedir confirmaciones ya concedidas.
- Consumir tokens con recapitulaciones sin delta.
- Entregar varias recomendaciones cuando se requiere una.

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
5. Divergencias.
6. Autorizaciones consumidas.
7. Una siguiente acción.

## Estilo

Resultado primero. Sin introducciones, tutoriales ni recapitulaciones sin delta. Si hay bloqueo, identificar exactamente qué autoridad, evidencia o decisión falta.
