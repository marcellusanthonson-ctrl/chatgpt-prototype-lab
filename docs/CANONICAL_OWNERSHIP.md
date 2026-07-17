# Propiedad canónica

| Información | Propietario | Consumidores |
|---|---|---|
| Autoridad y decisiones transversales | LAB | Todos los proyectos |
| Estado, fases, contratos y roadmap de Symphonie | symphonie | LAB y ejecutores |
| Skills reutilizables y releases | MammothSkills | Symphonie y otros consumidores |
| Resultados históricos | Repositorio donde se produjo la evidencia | Registros por referencia |
| Brief y continuidad | Proyecto consumidor bajo contrato LAB | Claude, Codex y ChatGPT |

Reglas:

- Un consumidor guarda referencia, digest y estado observado; no copia historiales completos.
- Los snapshots declaran fecha, HEAD y estado CURRENT, STALE o ARCHIVED.
- La evidencia conserva procedencia y limitaciones.
- Las discrepancias se registran; no se resuelven por inferencia.

- Un repositorio no registra su propio HEAD como estado vigente dentro del mismo commit. Usa head_policy = VERIFY_LIVE_AT_USE y, cuando sea útil, verified_parent_head como evidencia histórica.
- MODIFIED se usa solo cuando el núcleo del claim conserva una parte sustentada. Si el núcleo es falso, el dictamen es REVERSED aunque exista un hecho periférico relacionado.
