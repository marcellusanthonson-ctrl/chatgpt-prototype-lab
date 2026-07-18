# RAG transversal federado

Estado: `DOCUMENTED_NOT_IMPLEMENTED`.

El contrato estructurado canónico es `FEDERATION_CONTRACT.json`. Esta arquitectura define un solo servicio lógico de recuperación sobre namespaces aislados para LAB, Symphonie y cada proyecto. No define una base de conocimiento nueva: los repositorios y sus commits siguen siendo la fuente de verdad; cualquier índice futuro será un caché derivado de solo lectura.

## Lectura

La autoridad se filtra antes de calcular relevancia semántica. Una tarea selecciona namespaces autorizados, verifica commits activos, filtra propietario, clase, estado y proyecto, recupera dentro de cada namespace, detecta conflictos y devuelve contexto citado.

## Escritura

El modelo no escribe al índice ni obtiene autoridad autónoma sobre Git. Puede emitir una propuesta tipada para el repositorio propietario. La propuesta debe validarse y solo puede convertirse en commit cuando existe autorización explícita, vigente y delimitada. El índice se reconstruye después del commit canónico.

## Implementación

No se crearon embeddings, almacenamiento vectorial, API, pipeline Node.js, Tool Calling operativo, credenciales ni ingestión de datos. Los documentos describen el contrato que una futura implementación deberá satisfacer.
