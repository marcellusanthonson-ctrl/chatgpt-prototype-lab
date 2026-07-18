# RAG-RETRIEVAL-RANKING-001

Estado: `DOCUMENTED_NOT_IMPLEMENTED`.

El orden obligatorio es:

1. Resolver tarea, proyecto y clases de autoridad.
2. Seleccionar namespaces permitidos por alcance y ACL.
3. Verificar commits activos.
4. Excluir estados, propietarios y proyectos no aplicables.
5. Recuperar candidatos semánticos dentro de cada namespace.
6. Ordenar preservando primero autoridad y después relevancia.
7. Detectar contradicciones entre fuentes aplicables.
8. Entregar contexto con repositorio, ruta, commit y `document_id`.

Todo chunk requiere once metadatos: `repository`, `path`, `document_id`, `commit_sha`, `content_sha256`, `schema_version`, `canonical_owner`, `authority_class`, `project_scope`, `document_status` e `indexed_at`.

Si falta un metadato, el chunk no es recuperable. Si las fuentes entran en conflicto, el orquestador no sintetiza una conclusión: devuelve las fuentes y marca `RESOLUTION_REQUIRED`.
