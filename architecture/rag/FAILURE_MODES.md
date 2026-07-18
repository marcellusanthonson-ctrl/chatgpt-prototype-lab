# RAG-FAILURE-MODES-001

Estado: `DOCUMENTED_NOT_IMPLEMENTED`.

- HEAD o commit incorrecto: excluir el namespace y solicitar reconstrucción.
- Metadatos incompletos: rechazar el chunk.
- Propietario desconocido: detener la propuesta sin seleccionar destino.
- Conflicto canónico: detener la conclusión y devolver las fuentes.
- ACL denegada: excluir el contenido sin revelar datos del ámbito.
- Validación fallida: conservar el repositorio intacto y devolver errores tipados.
- Autorización ausente: impedir commit y push.
- Índice indisponible: fallar explícitamente o leer una fuente canónica permitida.
- Proyecto incorrecto: denegar recuperación y registrar solo metadatos no sensibles.
- Secreto detectado: excluir antes de fragmentar o indexar.

Los estados seguros siempre preservan los repositorios y evitan respuestas no citadas. Ningún fallback puede mezclar proyectos, reutilizar credenciales ni convertir una propuesta en autorización.
