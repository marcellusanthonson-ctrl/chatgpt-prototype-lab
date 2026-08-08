# Propiedad canónica

| Información | Propietario | Consumidores |
|---|---|---|
| Autoridad y decisiones transversales | LAB | Todos los proyectos |
| Decisiones LAB activas | `decisions/DEC-LAB-NNN.json` | Registros, estado, roadmap, continuidad y ejecutores |
| Estado, fases, contratos y roadmap de Symphonie | symphonie | LAB y ejecutores |
| Skills reutilizables y releases | MammothSkills | Symphonie y otros consumidores |
| Resultados históricos | Repositorio donde se produjo la evidencia | Registros por referencia |
| Brief y continuidad | Proyecto consumidor bajo contrato LAB | Claude, Codex y ChatGPT |
| Posición conversacional y ramas de trabajo | `sessions/` bajo `PROGRESSIVE_CONVERSATION_CONTINUITY_001` | Continuidad y modelos; nunca fuente de autoridad |

## Reglas de propiedad

- Un consumidor guarda referencia, digest y estado observado; no copia historiales completos.
- Los snapshots declaran fecha, HEAD y estado `CURRENT`, `STALE` o `ARCHIVED`.
- La evidencia conserva procedencia y limitaciones.
- Las discrepancias se registran; no se resuelven por inferencia.
- Un repositorio no registra su propio HEAD como estado vigente dentro del mismo commit. Usa `head_policy = VERIFY_LIVE_AT_USE` y, cuando sea útil, un parent o baseline histórico.
- `MODIFIED` se usa solo cuando el núcleo del claim conserva una parte sustentada. Si el núcleo es falso, corresponde `REVERSED`.

## Namespace de decisiones

`decisions/` es el único namespace activo para decisiones LAB. Cada `DEC-LAB-NNN` debe ser globalmente único dentro de ese namespace. `projects/lab/decisions/` puede contener índices o archivos históricos archivados, pero no una segunda decisión activa con un ID ya ocupado.

Cuando se descubre una colisión histórica:

1. se preserva el blob original antes de retirar el path colisionante;
2. el titular ya vigente del ID conserva su ID salvo decisión explícita en contrario;
3. la decisión histórica distinta recibe un ID global libre sin alterar su contenido normativo;
4. el nuevo artefacto conserva el ID/path/blob original y el path archivado como procedencia;
5. no se fabrica una aprobación nueva: se preserva la aprobación histórica de la decisión cuyo identificador fue reconciliado.

## Agregados y proyecciones

`CURRENT_STATE.json`, `PROJECT_STATE.json`, `ROADMAP.json`, `PENDING.json` y los registros son **proyecciones de navegación**, no propietarios de la historia que resumen. Deben preferir referencias a owner-artifacts y pueden compactar historiales cerrados siempre que no eliminen ni cambien un objetivo no terminal.

Los registros particionados pueden conservar un `historical_base` byte-identical y aplicar una capa `current_overlay`; la capa actual prevalece únicamente como proyección y nunca reescribe el owner-artifact histórico.

## Foco y portafolio

El foco actual es una propiedad de navegación. Cambiar de foco no cancela, suspende, degrada, activa, integra ni adjudica una línea del portafolio. Aplicar `FOCUS_AND_ROADMAP_PRESERVATION_001`.

## Continuidad progresiva

La continuidad conserva memoria **y posición de trabajo**. `sessions/` registra el grafo de posición, ramas laterales y retorno bajo `PROGRESSIVE_CONVERSATION_CONTINUITY_001`; esos archivos no crean decisión, autorización ni estado operativo por sí mismos.
