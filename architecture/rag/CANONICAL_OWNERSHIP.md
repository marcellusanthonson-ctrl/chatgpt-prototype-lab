# RAG-CANONICAL-OWNERSHIP-001

Estado: `DOCUMENTED_NOT_IMPLEMENTED`.

| Namespace | Propietario canónico | Contenido autoritativo | No puede reemplazar |
|---|---|---|---|
| LAB | chatgpt-prototype-lab | Gobernanza, metodología, decisiones, patrones, Foundation Library y evidencia | Estado de producto o contratos de fase de Symphonie |
| SYMPHONIE | symphonie | Fases, schemas, gates y contratos de orquestación | Gobernanza global del LAB o estado de un producto |
| PROJECT | Repositorio explícito del proyecto | Brief, estado, decisiones, evidencia y delta aprobados | Gobernanza del LAB, orquestación de Symphonie u otro proyecto |

La propiedad se resuelve antes de la similitud semántica. Una alta similitud nunca eleva la autoridad. Un proyecto puede especializar una base mediante un delta aprobado, pero no reescribir sus invariantes globales.

Cada namespace mantiene una clave de aislamiento. PROJECT añade `project_id` y repositorio; la recuperación entre proyectos se deniega por defecto. Un cambio propuesto siempre se dirige al propietario canónico del conocimiento afectado.
