# Continuidad actual — remediación M3 autorizada, no iniciada

Fecha: 2026-07-31T09:23:00-04:00

Repositorio: `marcellusanthonson-ctrl/chatgpt-prototype-lab`

Rama: `main`

Política HEAD: `VERIFY_LIVE_AT_USE`

## Decisión

`DEC-LAB-024` resuelve `PEND-LAB-035` mediante una remediación acotada. El defecto raíz es una inconsistencia preexistente de `CRIT-FIX-008`: contiene `TASK_WEB_INTERFACE`, que activa `DESIGN_CRITERION`, pero su `expected_modules` omite ese módulo.

La variante de orden inverso reproduce la misma causa; no constituye una segunda causa independiente. El selector y el shadow registry permanecen equivalentes en 420/420 casos y no existe transferencia negativa estático-shadow.

## Autorización 158

La autorización 158 está `GRANTED` con Codex como único ejecutor técnico. Autoriza:

- preservar exactamente el fixture histórico 1.1.0;
- corregir únicamente `CRIT-FIX-008.expected_modules`;
- subir la versión del fixture a 1.1.1;
- reparar exclusivamente la corrupción UTF-8 introducida por el commit M3;
- ejecutar una evaluación M3 aditiva de 420 casos, dos veces;
- publicar el resultado y reconciliar estado, registros y continuidad.

No autoriza cambios del selector, shadow registry, adaptadores M2, runtime, integraciones, M4, cutover, AWS o Terraform.

## Estado de ejecución

La remediación todavía no comenzó. El fixture, los textos corruptos y los resultados M3 históricos permanecen sin modificar en esta etapa documental.

`PEND-LAB-035` está `M3_REMEDIATION_AUTHORIZED_NOT_STARTED`.

## Divergencias documentales temporales

`registry/index.json`, `projects/lab/PENDING.json` y las vistas Markdown de estado serán reconciliados durante la etapa 2 autorizada. La corrupción UTF-8 también permanece pendiente de esa ejecución.

## Siguiente acción única

Ejecutar la etapa 2 de la autorización 158 en Codex desde el HEAD remoto verificado posterior a esta publicación.
