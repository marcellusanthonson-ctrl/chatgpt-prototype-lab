# RAG-INDEX-LIFECYCLE-001

Estado: `DOCUMENTED_NOT_IMPLEMENTED`.

El índice es un caché derivado de solo lectura. El repositorio es la única fuente de verdad.

Una reconstrucción futura solo podrá iniciarse por un push canónico verificado. Debe fijar el commit exacto, producir IDs deterministas, reconstruir únicamente el namespace afectado y comparar el manifiesto nuevo con el anterior. Todo chunk ausente del nuevo manifiesto se elimina como obsoleto.

Una publicación de índice solo es válida si todos sus chunks pertenecen al mismo commit declarado para el namespace. Un índice con HEAD incorrecto, metadatos incompletos o mezcla de commits queda fuera de recuperación.

El fallo del caché no autoriza inferencias sin citas. El sistema debe fallar explícitamente o recurrir a una lectura canónica permitida. Este documento no selecciona base vectorial ni modelo de embeddings.
