# Protocolo estándar de continuidad

Se activa cuando Jonathan solicita continuar un proyecto en otra conversación.

## Archivos

- continuity/CURRENT_CONTINUITY.json: fuente estructurada.
- continuity/CURRENT_CONTINUITY.md: vista humana.
- continuity/ATTACHMENT_MANIFEST.json: archivos y orden.
- continuity/START_PROMPT.md: primer mensaje listo para usar.
- continuity/archive/: paquetes reemplazados.

## Contenido obligatorio

Proyecto; fecha; repositorios, ramas y HEAD; orden de lectura; hechos; propuestas; ideas; integraciones posibles; decisiones; autorizaciones activas y consumidas; resultados; pendientes; errores; riesgos; experimentos; skills; roadmap; attachments; límites y una siguiente acción.

Todo elemento material debe incluir source_refs. Las transcripciones completas solo se adjuntan cuando son evidencia indispensable.

## Generación

1. Verificar HEAD.
2. Leer estado y registros canónicos.
3. Extraer información material no incorporada.
4. Clasificar cada elemento.
5. Construir manifiesto de attachments.
6. Generar la primera frase.
7. Validar referencias y marcar el paquete anterior ARCHIVED.
8. Si cambia un HEAD, marcar el paquete STALE.

## Primera respuesta del nuevo modelo

Debe presentar contexto reconstruido, HEAD verificados, estado, decisiones, autorizaciones, pendientes, divergencias y una siguiente acción. No debe ejecutar hasta identificar una autorización vigente.
