# Foundation Library del LAB

Esta biblioteca define bases documentales reutilizables para producir interfaces y servicios consistentes sin comenzar desde una página en blanco. No contiene código, dependencias, credenciales, datos reales ni autorización de implementación.

## Autoridad y fuente de verdad

- Repositorio canónico: `marcellusanthonson-ctrl/chatgpt-prototype-lab`.
- Aprobador único: Jonathan Martínez.
- Índice canónico: `registry/foundation-library.json`.
- Schemas canónicos: `schemas/design-archetype.schema.json` y `schemas/backend-pattern.schema.json`.
- El repositorio es la fuente de verdad. Un índice RAG futuro, si se autoriza, solo podrá ser un derivado de lectura.

## Uso de los arquetipos

Cada proyecto selecciona un arquetipo y expresa únicamente un delta. El orden obligatorio es: preservar invariantes, seleccionar tokens, aplicar cambios de marca, comprobar contraste y responsividad, y registrar excepciones. El delta nunca puede eliminar accesibilidad, estados de interacción, límites de contenido ni reglas responsivas.

Los cuatro modos responsivos son rangos de contenido verificables, no nombres de dispositivos. Las pruebas deben cubrir los límites inferior y superior de cada rango, zoom al 200 %, reflujo, teclado, contenido largo y localización.

## Uso de los patrones backend

Los patrones describen contratos, estados, invariantes, fallos y pruebas. Son neutrales al proveedor y no son implementaciones copiables. La configuración sustituible por cliente se mantiene separada de valores administrados por entorno. Los secretos solo se representan mediante referencias opacas y nunca se almacenan en esta biblioteca.

En pagos, la aplicación nunca captura ni persiste datos de tarjeta. Un proveedor compatible debe alojar la captura regulada. Cambiar datos del cliente significa sustituir configuración no secreta validada; no significa reutilizar llaves, cuentas, webhooks o identificadores sensibles.

## Estado

Los artefactos están `DOCUMENTED_AND_VALIDATED`. Esto acredita consistencia documental, no funcionamiento en producción. Runtime, integración, producto, despliegue y release permanecen sin autorización.
