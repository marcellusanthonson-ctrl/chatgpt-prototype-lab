# Capa selectiva de criterio para ChatGPT

Document-Role: STABLE_PROJECT_SOURCE
Canonical-Contract: project-sources/chatgpt/criterion-layer/CHATGPT-CRITERION-LAYER-001/CONTRACT.json
Integration: INT-LAB-001
Decision: DEC-LAB-016
Authority-Effect: NONE

## Función

Antes de producir una respuesta aplicable, clasificar la tarea y activar solamente los módulos definidos por `MODULE_SELECTOR.json`. La capa ordena criterio y límites de claims; no modifica pesos del modelo, no es runtime y no implementa RAG.

## Módulos

1. `EVIDENCE_AND_CLAIMS`: auditorías, análisis, estado y afirmaciones factuales, legales, normativas, de accesibilidad o validación.
2. `DESIGN_CRITERION`: UI, UX, HTML, interfaces web, briefs, prototipos y componentes.
3. `WEB_ACCESSIBILITY`: interfaces, formularios, controles, responsive, motion y claims de accesibilidad.
4. `CONTEXTUAL_VISUAL_PREFERENCE`: dirección visual para Jonathan Martínez o Symphonie, sin convertir señales contextuales en identidad universal.

Una consulta no aplicable no carga módulos de diseño, accesibilidad ni preferencia.

## Aplicación

1. Clasificar tarea, output y claims.
2. Resolver módulos mediante el selector determinista.
3. Leer las fuentes canónicas referenciadas; no copiar sus contenidos.
4. Separar gobierno, estándar normativo, guía oficial, heurística, evidencia, preferencia e inferencia.
5. Aplicar restricciones y criterio.
6. Limitar el resultado conforme a `RESULT_CONTRACT.json`.

## Base visual mínima y autocorrección

Cuando `DESIGN_CRITERION` produce o revisa un artefacto de interfaz renderizado, aplicar antes de la dirección estética `MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001`.

1. Abrir y recorrer el render real; leer HTML y CSS no basta.
2. Inspeccionar, medir, interactuar y tensionar contenido y anchuras.
3. Detectar cualquier desviación observable de propietario, contenedor, grilla, jerarquía, estado, función o intención, aunque no figure en una lista cerrada.
4. Diagnosticar la causa raíz y corregir todo defecto comprendido en el alcance vigente.
5. Reconstruir el componente cuando la causa sea estructural; no ocultar síntomas con overflow, clipping, offsets, márgenes negativos o decoración.
6. Revalidar la superficie completa afectada.

Una generación exitosa no es un PASS. Queda prohibido entregar `PASS_WITH_KNOWN_VISUAL_DEFECTS`. Los únicos cierres admitidos son `TECHNICAL_FOUNDATION_PASS_AWAITING_HUMAN_BASELINE_REVIEW` o `BLOCKED_WITH_DOCUMENTED_DEFECTS`.

## Accesibilidad y validación

- `STATIC_PASS` no acredita accesibilidad.
- Una revisión manual no sustituye prueba con tecnología de asistencia.
- Un resultado AT sólo vale para el entorno registrado.
- Si no se ejecutaron las capas correspondientes, declarar `MANUAL_NOT_RUN`, `AT_NOT_RUN` y `WCAG_CONFORMANCE_NOT_ESTABLISHED`.
- No presentar APG, técnicas o heurísticas como obligaciones normativas de WCAG.
- No declarar ausencia de barreras porque no se observaron fallos.

## Preferencia contextual

Consultar el perfil visual sólo cuando el selector lo active. Las invariantes de calidad pueden limitar una solución; paleta, tipografía, materialidad, densidad, fotografía/render y movimiento siguen dependiendo del producto y la marca. Jonathan mantiene la decisión humana sobre dirección visual.

## Límites

Esta fuente no autoriza ejecución, commits, integración de Symphonie, cambios de producto, RAG, embeddings, base vectorial, instalación de skills, tecnologías de asistencia, conformidad WCAG, despliegue ni release.
