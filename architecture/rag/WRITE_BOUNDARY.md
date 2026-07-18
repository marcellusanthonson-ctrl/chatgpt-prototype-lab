# RAG-WRITE-BOUNDARY-001

Estado: `DOCUMENTED_NOT_IMPLEMENTED`.

El modelo puede emitir una propuesta estructurada, no un cambio autoritativo. La frontera obligatoria es:

1. Emitir payload conforme al schema de la herramienta.
2. Resolver un único repositorio propietario.
3. Materializar el cambio fuera del estado canónico.
4. Ejecutar el validador del repositorio.
5. Devolver errores de validación al modelo para una propuesta corregida.
6. Comprobar autorización activa: aprobador, HEAD, rama, rutas y acciones.
7. Permitir commit solo a un ejecutor delimitado.
8. Reconstruir el namespace después del commit verificado.

La corrección automática de formato no concede autoridad. Sin autorización, el estado seguro es `AWAITING_EXPLICIT_APPROVAL`. El modelo no puede hacer commit, push, mutar el índice ni elegir por sí mismo el repositorio de destino.
