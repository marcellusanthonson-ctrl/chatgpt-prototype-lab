# ChatGPT Prototype LAB

`README_ROLE = ECOSYSTEM_CONCEPTUAL_AND_OPERATIONAL_ENTRYPOINT`

`README_ALIGNMENT = CANONICAL_MODEL_V2_AND_APPROVED_FOUNDATION_BASELINE`

El LAB es un ecosistema federado de gobierno, conocimiento reutilizable, fundaciones, patrones, evidencia, capacidades y protocolos de validación. Conecta proyectos sin absorber su identidad: cada proyecto conserva su arquitectura, estado, decisiones, roadmap, riesgos, autorizaciones e implementación en su repositorio propietario.

Este README es un mapa de entrada. No es una fuente paralela de estado, una autorización de ejecución ni un contrato de runtime.

## Mapa del ecosistema

| Capa | Responsabilidad |
|---|---|
| LAB | Gobierno, autoridad, decisiones transversales, patrones, fundaciones, evidencia, continuidad, referencias cruzadas y validación. |
| Fundaciones | Mínimos técnicos y de calidad reutilizables. La referencia visual vigente es [`MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001@1.1.1`](foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001/), con estado referenciado `HUMAN_BASELINE_APPROVED`. |
| Patrones | Métodos reutilizables validados mediante evidencia. Incluyen [`PAT-LAB-008`](patterns/PAT-LAB-008.json), `ASSET_FIRST_BRAND_ASSOCIATED_VISUAL_SELECTION_AND_INTEGRATION`. |
| Bibliotecas de assets | Activos locales versionados con procedencia, licencia, hash, restricciones, selección y aprobación contextual. La biblioteca correspondiente se consulta por su [`MANIFEST`](foundation-library/brand-icons/LOCAL-ICON-ASSET-CANDIDATE-LIBRARY-001/MANIFEST.json), sin duplicar aquí su inventario. |
| Skills y capacidades | Ejecutores especializados y delimitados que consumen fundaciones, patrones y assets. No poseen el estado de los proyectos ni autoridad autónoma. |
| Repositorios de proyecto | Propietarios operativos del estado, arquitectura, fases, contratos, roadmap, decisiones del proyecto, implementación y runtime. |
| Autoridad humana | Jonathan Martínez es el único aprobador de decisiones normativas y autorizaciones de ejecución. |

## Decisiones contextualizadas

El LAB comparte conocimiento, no resultados visuales uniformes. Las fundaciones comparten mínimos y no identidades; una estrategia validada puede aplicarse de forma distinta según el contexto del proyecto. Los proyectos no tienen que verse iguales.

```text
CONOCIMIENTO TRANSVERSAL
→ CONTEXTO DEL PROYECTO
→ ANÁLISIS
→ PROPUESTA O DECISIÓN TÉCNICA
→ APROBACIÓN HUMANA CUANDO CORRESPONDA
→ EJECUCIÓN DELIMITADA
→ EVIDENCIA
→ APRENDIZAJE REUTILIZABLE
```

Las decisiones normativas y las autorizaciones pertenecen a la autoridad humana. El análisis técnico puede producir propuestas, pero no sustituye esa autoridad.

### Qué se comparte y qué pertenece al proyecto

| Transversalmente compartido | Contextual y propio de cada proyecto |
|---|---|
| Calidad mínima, accesibilidad estructural, responsive, seguridad y trazabilidad | Marca, dirección visual, paleta, tipografía y composición |
| Protocolos, patrones validados y validaciones | Densidad, contenido, narrativa y movimiento |
| Criterios de evidencia y aprendizaje reutilizable | Funcionalidades, arquitectura y riesgo |

## Fundación visual mínima aprobada

[`MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001@1.1.1`](foundation-library/visual-foundations/MINIMUM-IMPECCABLE-VISUAL-FOUNDATION-001/) es un baseline adaptable de integridad estructural, comportamiento responsive, terminación e interacción. No es una plantilla visual universal ni una identidad que deba copiarse entre proyectos.

```text
HUMAN_BASELINE_APPROVED
STATIC_VALIDATION = PASS
WCAG_CONFORMANCE = NOT_ESTABLISHED
```

La aprobación del baseline no declara conformidad WCAG, preparación de producto, identidad universal ni autorización automática para copiarlo o integrarlo.

## Patrón asset-first para elementos asociados a marcas

El patrón [`PAT-LAB-008`](patterns/PAT-LAB-008.json) evita reconstrucciones aproximadas de activos asociados a marcas. Usa candidatos verificables y conserva su geometría al integrar el activo seleccionado:

```text
NEED_IDENTIFICATION
→ VERIFIED_CANDIDATE_ACQUISITION
→ PROVENANCE_AND_LICENSE_REGISTRATION
→ STATIC_SECURITY_VALIDATION
→ CONTEXTUAL_COMPARISON
→ HUMAN_SELECTION
→ IMMUTABLE_GEOMETRY_INTEGRATION
→ FOCUSED_VALIDATION
→ HUMAN_CONTEXTUAL_APPROVAL
```

La procedencia, licencia, hashes, restricciones y decisiones de la biblioteca se consultan en su [`MANIFEST`](foundation-library/brand-icons/LOCAL-ICON-ASSET-CANDIDATE-LIBRARY-001/MANIFEST.json). Evidencia técnica y aprobación contextual no equivalen a una aprobación jurídica general de uso de marca.

## Entrada para un nuevo piloto

El flujo operativo es:

1. Verificar el HEAD remoto vivo de `main`.
2. Leer [`project-sources/chatgpt/START_HERE.md`](project-sources/chatgpt/START_HERE.md).
3. Reconstruir el estado canónico.
4. Identificar el proyecto propietario o crear una definición de proyecto expresamente autorizada.
5. Seleccionar las fundaciones y patrones aplicables.
6. Definir qué se reutiliza y qué se adapta al contexto.
7. Preparar un brief y una autorización delimitada.
8. Ejecutar en el repositorio propietario.
9. Validar el resultado.
10. Registrar evidencia y aprendizaje reutilizable.

Esta secuencia describe un proceso: no autoriza ninguno de sus pasos, no selecciona un piloto y no habilita cambios en proyectos.

## Orden canónico de lectura

1. Verificar el HEAD remoto vivo de `main`; no usar un SHA almacenado en este README.
2. Leer [`project-sources/chatgpt/START_HERE.md`](project-sources/chatgpt/START_HERE.md).
3. Leer [`LAB_CONTRACT.md`](LAB_CONTRACT.md).
4. Leer [`METHODOLOGY.md`](METHODOLOGY.md).
5. Leer [`CURRENT_STATE.json`](CURRENT_STATE.json).
6. Leer [`registry/index.json`](registry/index.json).
7. Leer [`registry/projects.json`](registry/projects.json).
8. Leer el `PROJECT_STATE.json` del proyecto activo.
9. Leer decisiones, autorizaciones, errores, pendientes, roadmap, evidencia y continuidad aplicables.

## Fuentes de verdad y continuidad

- JSON es la fuente estructurada canónica; Markdown es su vista humana.
- El HEAD remoto vivo se verifica al usar el repositorio y no se fija aquí.
- Este README orienta; no reemplaza contratos, estado, registros ni autorizaciones.
- La propiedad de cada dato está definida en [`docs/CANONICAL_OWNERSHIP.md`](docs/CANONICAL_OWNERSHIP.md).
- Las reglas de los modelos están en [`docs/MODEL_OPERATING_RULES.md`](docs/MODEL_OPERATING_RULES.md).
- La continuidad entre conversaciones sigue [`docs/CONTINUITY_PROTOCOL.md`](docs/CONTINUITY_PROTOCOL.md).

## Límites de autoridad

El LAB no es runtime y no autoriza despliegues, releases, integración de producto ni acceso a credenciales. La existencia de evidencia no constituye aprobación; una aprobación no constituye autorización de ejecución. Codex, las skills y las capacidades no reciben autoridad autónoma por este README. Jonathan Martínez conserva la autoridad exclusiva para aprobar decisiones normativas y conceder autorizaciones explícitas, vigentes y delimitadas.

```text
RUNTIME_EFFECT = NONE
PRODUCT_EFFECT = NONE
EXTERNAL_PROJECT_EFFECT = NONE
NEW_PILOT_AUTHORIZED = NO
```
