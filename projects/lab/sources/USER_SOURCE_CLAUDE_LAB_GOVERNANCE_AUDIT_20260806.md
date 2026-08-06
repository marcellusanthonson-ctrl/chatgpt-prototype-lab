# Informe de auditoría — Gobernanza del LAB y propuesta de remediación

**Preparado para:** equipo de desarrollo
**Preparado por:** Claude, auditor independiente de solo lectura
**Repositorio:** `marcellusanthonson-ctrl/chatgpt-prototype-lab`, rama `main`
**HEAD remoto verificado en vivo:** `37ba39e9dcc630fd4569d2f50a80967cb52f2341`
**Fecha de cierre del informe:** 2026-08-06

**Naturaleza del informe:** todo hallazgo fue verificado por lectura directa del repositorio (clon local en modo solo lectura) y de la API pública de GitHub. Ningún archivo del repositorio fue modificado, ninguna rama fue creada, ningún commit fue publicado. Este documento no constituye autorización de ejecución ni aprobación de implementación — es evidencia y recomendación para decisión humana.

---

## 1. Resumen ejecutivo

| Área | Estado encontrado |
|---|---|
| Resultado de la ejecución 004 de Product Leadership Test 003 | El `FAIL` publicado no se sostiene tal como está declarado. Dictamen: **MODIFIED** — el resultado correcto según el propio contrato del test es `INSUFFICIENT_EVIDENCE`. |
| Enforcement de publicación en GitHub | **Inexistente.** `main` no tiene protección de rama, ni required checks, ni rulesets. Cualquier actor con acceso de escritura puede empujar directo. |
| Identificadores de decisiones | **3 colisiones confirmadas** (no 1): `DEC-LAB-023`, `DEC-LAB-024`, `DEC-LAB-025` existen duplicados con contenido distinto en dos directorios paralelos. |
| Roadmap y visibilidad de portafolio | `ROADMAP.json` desactualizado desde el 3 de agosto; `ROADMAP.md` desde el 22 de julio. El paquete de continuidad vigente **no menciona** Product Leadership, Software Solution Engineering ni Contextual Bootstrap Resolver — verificado en el archivo real, ahora mismo. |
| Mecanismos de autocorrección ya existentes | Existen y en un caso funcionaron correctamente, pero se dejaron de usar: el ciclo de aprendizaje de errores (autorización 193) se aplicó dos veces y luego se abandonó durante nueve autorizaciones consecutivas. |
| Reglas operativas del modelo | `docs/MODEL_OPERATING_RULES.md` no aparece en ninguna ruta de lectura obligatoria — ni en el arranque canónico, ni en el paquete de continuidad activo. |

**Conclusión general:** el repositorio tiene disciplina documental fuerte a nivel de intención (contratos, schemas, protocolos) y disciplina de enforcement casi nula a nivel de ejecución. El patrón se repite en cada área auditada: la regla existe por escrito y nada obliga a cumplirla. Se diseñó, a lo largo de esta auditoría, una arquitectura de remediación que invierte ese orden — exigibilidad antes que más estructura — y quedó aprobada en principio, pendiente de dos ajustes menores antes de convertirse en autorización.

---

## 2. Alcance y método

La auditoría cubrió dos objetos distintos:

1. **Auditoría técnica puntual:** el resultado publicado de `PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-EXECUTION-004`, intento `ATTEMPT-003`, bajo la autorización 188.
2. **Auditoría de infraestructura de gobernanza:** el estado real de enforcement de publicación, integridad de identificadores, vigencia del roadmap, y continuidad entre conversaciones — motivada por bloqueos observados en autorizaciones posteriores (194 a 203).

Método: verificación del HEAD remoto en vivo en cada paso (`git ls-remote`), clonado de solo lectura, verificación de hashes SHA-256 contra los manifiestos de congelamiento declarados, reproducción independiente de las métricas cuantitativas mediante reimplementación del pipeline de análisis, y consultas de solo lectura a la API pública de GitHub (`repos/.../branches/main`, `repos/.../actions/workflows`, `repos/.../actions/permissions`) para verificar el estado real de protección de rama y workflows, contrastado contra el árbol de archivos versionado.

---

## 3. Hallazgo A — Auditoría técnica: Test 003 de Product Leadership, ejecución 004

**Dictamen:** `MODIFIED`
**Recomendación:** `RETEST_DUE_TO_MATERIAL_EXECUTION_OR_DESIGN_DEFECT`

### 3.1 Lo que se verificó como correcto

Las 15 cifras cuantitativas declaradas (línea base 22.8654, paquete 21.4327, incremento −1.4327, IC95% [−1.9712, −0.9327], negative transfer 38/52 = 73.08%, net decision value −8.019, 1/8 gates aprobados) se reproducen **exactamente** desde los artefactos congelados. Integridad de hashes: 112/112 outputs verificados, 4/4 digests maestros correctos. La ejecución técnica (runner, modelo, calibración de dos scorers independientes) fue disciplinada y bien documentada.

### 3.2 Por qué el resultado `FAIL` no se sostiene

- **Los controles negativos nunca fallaron.** El brazo diseñado para producir respuestas inseguras (autoridad falsa, evidencia inventada) recibió 4 respuestas correctas y de alta calidad — el modelo se negó a producir el defecto que el control necesitaba para validar al evaluador. `PL-GATE-CONTROLS` falla por esto, y el propio contrato del test (`SCORING_AND_GATES.json`) define que cuando los controles fallan, el resultado correcto es `INSUFFICIENT_EVIDENCE`, no `FAIL`. El código del runner (`RUN_TEST003.mjs`) no tiene esa rama de salida implementada — solo puede emitir PASS o FAIL.
- **El blinding fue derrotado por longitud de output.** Un solo umbral de 1250 caracteres clasifica el brazo (baseline vs. paquete) con 99.0% de exactitud. El evaluador ciego penalizó como "evidencia fabricada" o "confusión de autoridad" afirmaciones que eran verdaderas y venían dadas por el propio prompt del brazo paquete.
- **Los prompts de generación no son simétricos entre brazos.** El baseline instruye explícitamente brevedad y enumera las tres etiquetas de clasificación; el paquete no. Dos dimensiones de puntuación explican el 74.5% del decremento de valor reportado, y ambas están confundidas por esta asimetría.
- **El colapso de activación mide a los fixtures, no al paquete.** El `INPUT_CONTRACT` del paquete exige 7 campos de contexto y ordena clasificar como `LIMITED_OR_AMBIGUOUS` si faltan; los fixtures solo entregan una frase de escenario. 0 de 52 outputs del paquete clasificaron `ACTIVE`, exactamente como predice esa regla.

### 3.3 Antes de un nuevo intento, se requiere corregir

1. Simetría de prompts entre brazos.
2. Dar al evaluador ciego contexto sobre la existencia del paquete, o redactar sin autorreferencias.
3. Construir controles negativos como artefactos fijos, no generados por modelo.
4. Resolver la discrepancia entre fixtures e `INPUT_CONTRACT`.
5. Implementar la rama `INSUFFICIENT_EVIDENCE` y las stop conditions ya definidas en el diseño pero ausentes del código.
6. Calibrar la rúbrica de 12 dimensiones realmente usada (la calibración v2 existente valida una tarea de 6 etiquetas distinta a la de scoring real).

---

## 4. Hallazgo B — Infraestructura de gobernanza del repositorio

### 4.1 Enforcement de publicación: inexistente

Verificado vía API de GitHub en vivo:

```
GET /repos/.../branches/main
"protected": false
"required_status_checks": { "enforcement_level": "off", "contexts": [] }
```

No existe `.github/workflows/` en el árbol vigente. Sin embargo, la API de GitHub Actions todavía enumera **8 workflows con estado `"active"`**, todos asociados a autorizaciones puntuales ya cerradas (177, 178, 179, 180, 167), cuyos archivos fueron borrados tras cumplir su propósito.

Reconstruí el historial de borrado. **Tres identidades distintas** han eliminado archivos de `.github/workflows/` como parte de rutina de cierre:

| Commit | Autor (email de commit) | Acción |
|---|---|---|
| `48f2eba4` | `github-actions[bot]` | borra workflow al publicar la autorización 180 |
| `a74bd8b4` | `Jonathan Fabián <marcellus.anthonson@gmail.com>` | borra workflow, "replace stale identity" |
| `cc5ae428` | `github-actions[bot]` | borra workflow al reconciliar autorización 179 |
| `02c5605d`, `2822fc39`, `a7b3ff0c` | `ChatGPT Prototype LAB <actions@users.noreply.github.com>` | borra 4 workflows, "remove temporary tooling" |

El patrón "workflow se crea por autorización, corre, se borra al cerrar" está establecido y demostrado, no es hipotético. Cualquier gate permanente que se instale sin excluir explícitamente a estas identidades de esa práctica es candidato a correr la misma suerte.

### 4.2 Duplicación de namespace de decisiones

Existen dos directorios canónicos paralelos para decisiones del LAB:

- `decisions/` (raíz del repo): **31 archivos**, actividad hasta el 2 de agosto — es el directorio realmente vigente.
- `projects/lab/decisions/`: **3 archivos** (más un índice), los tres del mismo lote del 27 de julio (asignación de auditor, estrategia híbrida Codex, proveedor AWS) — nunca reconciliado con el directorio raíz.

Escaneo de unicidad por clase documental (decisiones, autorizaciones, errores, evidencia, pendientes, integraciones):

| Clase | IDs únicos | Colisiones |
|---|---|---|
| Decisiones | 32 | **3** — `DEC-LAB-023`, `DEC-LAB-024`, `DEC-LAB-025`, contenido distinto en cada directorio |
| Autorizaciones | 158 | 1, verificada como enmienda legítima, no defecto |
| Errores | 12 | 0 |
| Evidencia | 104 | 0 |
| Pendientes | 33 | 0 |
| Integraciones | 4 | 0 |

`registry/decisions.json` declara 27 decisiones y no indexa correctamente ninguno de los dos directorios completos. El defecto está contenido a la clase "decisiones" — no es un problema sistémico de todo el repositorio.

### 4.3 Roadmap desactualizado y portafolio invisible en continuidad

`projects/lab/ROADMAP.json`: última modificación 3 de agosto — anterior a las autorizaciones 194 a 203. `ROADMAP.md` (raíz): última modificación 22 de julio, todavía indica como siguiente paso observar Criterion Layer con Terra 5.6, que ya no es la línea vigente.

`INT-LAB-004` (Product Leadership) declara `lifecycle_stage` anclado a la autorización 187, mientras `INTEGRATION_READINESS.json` del mismo objeto ya refleja la autorización 193 — un ciclo completo de desfase entre dos archivos que describen la misma integración.

**Verificación empírica, en vivo, del riesgo de pérdida de portafolio:** el paquete de continuidad activo (`projects/lab/continuity/CURRENT_CONTINUITY.json`), el que se entregaría a una conversación nueva hoy mismo, contiene **cero menciones** de Product Leadership, Software Solution Engineering, Contextual Bootstrap Resolver, `INT-LAB-004` o `INT-LAB-005`. Está construido enteramente alrededor de la autorización 203. Una conversación nueva que parta de este paquete no tendría ninguna indicación de que esas tres líneas de trabajo existen y están activas.

### 4.4 Mecanismos de autocorrección: existen, uno funcionó, se abandonaron

Existe `EXECUTION-LEARNING-FEEDBACK-LOOP-001` (creado por la autorización 193), que obliga a consultar errores registrados antes de ejecutar y producir un `LEARNING_APPLICATION_REPORT.json`. Solo existen dos reportes de este tipo en todo el repositorio: el de la autorización 193 y el de la 194. El de la 194 funcionó exactamente como se diseñó — detectó y aplicó controles preventivos para dos errores confirmados. **Después de eso, nueve autorizaciones consecutivas (195 a 203) no produjeron el reporte**, y el brief de Codex A para la 203 ni siquiera tiene el campo `learning_context` que el contrato exige como obligatorio.

Del mismo modo, la política de `execution_envelope` y `context_manifest` (autorización 194) nunca se retroalimentó a los ocho briefs despachados después de su adopción, hasta que Codex A la aplicó por su cuenta y bloqueó la autorización 203 por esa ausencia.

### 4.5 `docs/MODEL_OPERATING_RULES.md` no está en ninguna ruta de lectura obligatoria

Verificado contra el `required_reading_order` real (18 entradas) del paquete de continuidad activo: no aparece. Tampoco aparece en el orden canónico de `START_HERE.md` ni en la especificación de `CONTINUITY_PROTOCOL.md`. El documento que contiene las reglas de independencia analítica, el protocolo de aprendizaje de errores y el formato de reporte de cierre no es lectura forzada para ninguna conversación nueva.

### 4.6 Validadores sin conectar

Existen **25 scripts de validación** (`scripts/validate_*.py`, `tests/validate_*.py`) acumulados a lo largo del proyecto. Ninguno está conectado a un gate de publicación — todos dependen de que alguien se acuerde de ejecutarlos manualmente.

---

## 5. Arquitectura de remediación propuesta

Diseñada en tres iteraciones dentro de esta misma auditoría; la tercera queda **aprobada en principio**, con dos ajustes pendientes (sección 8).

**Principio rector:** primero hacer exigibles las reglas existentes; después introducir la mínima estructura necesaria para preservar los objetivos. La primera iteración de esta propuesta agregaba cuatro registros nuevos, cuatro taxonomías de estado y quince validadores antes de resolver el enforcement — fue retirada por desproporcionada respecto al problema real.

**Modelo de la ruta de publicación protegida:**

```
ACTOR → BRANCH → PULL REQUEST OBLIGATORIO → REVISIÓN HUMANA DEL CONTROL PLANE
       → CANONICAL GOVERNANCE GATE → MERGE SIN BYPASS → MAIN
```

### 5.1 Componente 1 — Protección integral de `main`

- Pull request obligatorio para todo cambio; push directo bloqueado para **todos** los actores, incluida la identidad de publicación del LAB, GitHub Actions y cualquier token con permisos elevados.
- `bypass_actors: []` — sin excepción para administradores ni propietario del repositorio.
- Check obligatorio `canonical-governance-gate`, ligado al integration ID legítimo cuando GitHub lo permita.
- Force push y eliminación de `main` bloqueados.
- Paths de control plane (`​.github/workflows/canonical-governance-gate.yml`, `CODEOWNERS`, el orquestador, los contratos de gobierno) requieren revisión de code owner, sin autoaprobación, con invalidación de aprobaciones ante nuevos commits.
- El workflow permanente se declara explícitamente `"lifecycle": "PERMANENT_CONTROL_PLANE"`, `"self_deletion_allowed": false` — para que no pueda tratarse como tooling temporal, el patrón ya demostrado en la sección 4.1.
- Permisos de GitHub Actions acotados a `contents: read`; sin capacidad de escribir, fusionar o aprobar.

### 5.2 Componente 2 — Orquestador único

`scripts/validate_canonical_governance.py`: identifica archivos modificados, determina qué validadores existentes aplican, los ejecuta, y falla si algún validador aplicable no corrió — no solo si alguno falló. Resuelve la desconexión actual entre "existe el script" y "se ejecutó".

### 5.3 Componente 3 — Contrato mínimo de foco

`architecture/governance/FOCUS_AND_ROADMAP_PRESERVATION_001/CONTRACT.json`: foco no equivale a portafolio; cambiar el foco no modifica el estado de ningún otro objetivo; la continuidad no es propietaria del roadmap; toda idea material se registra sin convertirse automáticamente en prioridad.

### 5.4 Componente 4 — Extensión mínima del roadmap existente

Se reutiliza `ROADMAP.json` (no se crea un segundo roadmap), agregando `current_focus` y `objectives[]`, con solo dos dimensiones de estado (`state`, `condition`) en vez de las cuatro taxonomías de la propuesta original.

### 5.5 Invariantes del gate (GOV-001 a GOV-007)

| ID | Verifica |
|---|---|
| GOV-001 | Unicidad de ID dentro de cada clase documental |
| GOV-002 | Namespace canónico único por clase (resuelve la duplicación de `decisions/`) |
| GOV-003 | Ningún objetivo activo desaparece sin transición terminal justificada y evidenciada |
| GOV-004 | Toda continuidad nueva declara qué objetivos activos preserva del roadmap; falla si omite alguno — resuelve directamente el hallazgo 4.3 |
| GOV-005 | Todo brief posterior a la autorización 194 tiene execution envelope y context manifest |
| GOV-006 | Todo validador aplicable a un cambio efectivamente se ejecutó |
| GOV-007 | *(nuevo, ver sección 6)* Toda instrucción clasificada como cambio material produce un `IMPACT_PREVIEW` antes de convertirse en autorización |

**Límite reconocido y documentado, no oculto:** el gate puede verificar que una justificación existe y referencia evidencia; no puede verificar que sea verdadera o suficiente. La mitigación es auditoría humana o independiente periódica, no automatización adicional.

### 5.6 Bootstrap en cinco fases

0. Preflight de solo lectura — verificar capacidad real de GitHub para aplicar cada restricción antes de tocar nada.
1. Protección provisional de `main` (PR obligatorio, sin bypass) antes de que exista el gate permanente.
2. Publicación del control plane vía PR, con el workflow corriendo y en PASS antes de fusionar.
3. Protección definitiva — activar el check obligatorio, code-owner review, descarte de aprobaciones obsoletas.
4. Validación adversarial — cuatro pruebas negativas (ver abajo).
5. Cierre — evidencia, verificación remota, consumo de autorización.

**Pruebas adversariales obligatorias antes de declarar el gate operacional:**

| ID | Prueba | Resultado exigido |
|---|---|---|
| ENF-NEG-001 | La identidad de publicación intenta empujar directo a `main` | `REMOTE_REJECTED_PROTECTED_BRANCH` |
| ENF-NEG-002 | Un PR elimina el workflow del gate | Merge bloqueado por ausencia de check y de code-owner approval |
| ENF-NEG-003 | Un PR modifica el orquestador para devolver éxito incondicional | Merge bloqueado sin aprobación humana |
| ENF-NEG-004 | La identidad administrativa intenta saltarse los controles | `BYPASS_NOT_AVAILABLE` |

### 5.7 Separación en dos autorizaciones

- **Autorización A — Enforcement de publicación.** Alcance estricto: preflight, protección de `main`, workflow permanente, orquestador mínimo, CODEOWNERS, pruebas adversariales. Excluye explícitamente migración de decisiones, cambios de roadmap, y cualquier ejecución de modelo o remediación técnica.
- **Autorización B — Reconciliación documental.** Solo después de que A cierre en PASS: resolver las tres colisiones de decisiones, formalizar la excepción de directorio, extender `ROADMAP.json`, implementar preservación de objetivos, agregar `MODEL_OPERATING_RULES.md` a la ruta de lectura obligatoria, y el filtro de impacto (GOV-007).

---

## 6. Filtro de impacto para instrucciones materiales (GOV-007)

Motivado por la dificultad de Jonathan para retener, entre conversaciones, qué ya está definido y qué falta. Antes de que una instrucción se convierta en autorización o brief, si se clasifica como cambio material, debe producirse:

```json
{
  "instruction_summary": "...",
  "classification": "MATERIAL",
  "trigger_reasons": ["..."],
  "consequences": ["qué se rompe, qué depende de esto, qué objetivos/gates afecta"],
  "estimated_effort": { "band": "SMALL | MEDIUM | LARGE", "reasoning": "..." },
  "structural_impact": {
    "contracts_or_schemas_touched": [],
    "roadmap_or_objectives_touched": [],
    "authority_created_or_consumed": "..."
  },
  "files_to_modify": [],
  "reversibility": "REVERSIBLE | COSTLY | IRREVERSIBLE",
  "risks": [],
  "requires_confirmation": true,
  "confirmed_by": null,
  "confirmed_at": null
}
```

**Criterio de "cambio material"** (para que no dependa de juicio subjetivo del modelo en el momento): crea o modifica una autorización, decisión o contrato; toca paths de control (`.github/`, `scripts/validate_*`, `architecture/governance/**`); modifica `ROADMAP.json`, `CURRENT_STATE.json` o el estado terminal de un objetivo activo; afecta más de un archivo o más de un proyecto; implica ejecución de modelo o costo real; es irreversible o de reversión costosa.

**Límite honesto:** tiene una capa conversacional (regla de comportamiento en `MODEL_OPERATING_RULES.md`, no forzable técnicamente — misma naturaleza que el ciclo de aprendizaje que ya vimos abandonado) y una capa mecánica (el gate exige que el archivo `IMPACT_PREVIEW` exista con sus campos completos antes de publicar la autorización). La segunda capa es la que realmente sostiene a la primera.

---

## 7. Snapshot del portafolio, verificado en vivo al cierre de este informe

| Línea | Estado |
|---|---|
| **Foco actual** | Cerrar el enforcement de publicación (Autorización A) antes de tocar cualquier otra línea |
| Protección de publicación (Autorización A) | Diseño aprobado en principio; 2 ajustes pendientes (sección 8); sin autorizar |
| Reconciliación documental (Autorización B) | Diseñada; depende de que A cierre primero |
| Contextual Bootstrap Resolver (benchmark 203) | `CONSUMED_BLOCKED` — Codex A detenido por custodia y envelope/manifest faltantes; sin autorización de remediación activa |
| Product Leadership (`INT-LAB-004`) | `CANDIDATE`, no activa, no integrada; retest pendiente de corregir los defectos de diseño del test (sección 3) |
| Software Solution Engineering (`INT-LAB-005`) | `CANDIDATE`, no activa; autorización 180 abierta y bloqueada, reintento sin iniciar |
| Codex Desktop operating model (autorización 194) | Estándar publicado; pendiente de benchmark operacional real |

---

## 8. Puntos abiertos antes de convertir esto en autorización

1. **Verificar si `ChatGPT Prototype LAB` es un principal de GitHub autenticado distinto de la cuenta de Jonathan, o el mismo token con metadata de commit reescrita.** Si es lo segundo, la separación de revisión por CODEOWNERS (sección 5.1) no aísla realmente la aprobación y hay que rediseñar ese punto. Debe verificarse en la Fase 0 del bootstrap.
2. **Definir el procedimiento de reversión si ENF-NEG-001 falla** — si el push directo de prueba llega a tener éxito, el diseño actual no especifica revert automático ni escalamiento inmediato a Jonathan. Es la única de las cuatro pruebas adversariales cuyo modo de falla deja un efecto real en `main`.
3. **Declarar explícitamente, en el texto del contrato, la excepción de que `decisions/` (raíz) es la ubicación canónica del LAB**, mientras los proyectos gobernados por el LAB usan `projects/<id>/decisions/` — para que no vuelva a aparecer como anomalía no explicada en una futura auditoría.
4. **Agregar `docs/MODEL_OPERATING_RULES.md` a la ruta de lectura obligatoria** en `START_HERE.md`, `CONTINUITY_PROTOCOL.md` y en el `required_reading_order` de cada paquete de continuidad futuro.

---

## 9. Recomendación y próxima acción única

**Redactar y someter a aprobación la Autorización A (enforcement de publicación)**, estrictamente limitada a: preflight de capacidad de GitHub, protección de `main` sin excepciones de bypass, workflow permanente, orquestador mínimo, CODEOWNERS, y las cuatro pruebas adversariales — incorporando los dos ajustes de la sección 8 antes de redactar el brief final.

No se recomienda avanzar en paralelo con la Autorización B, la migración de decisiones, el retest de Product Leadership, ni la remediación del benchmark contextual, hasta que la Autorización A cierre en `PASS`. Mezclar la creación del mecanismo de enforcement con el trabajo que ese mecanismo debe controlar reproduce exactamente el patrón de riesgo que esta auditoría documenta.

---

## Apéndice — Cadena de autorizaciones referenciadas

| Autorización | Objetivo | Estado verificado |
|---|---|---|
| 188 | Ejecución 004 del Test 003 de Product Leadership | Consumida; resultado auditado en este informe (sección 3) |
| 193 | Ciclo de aprendizaje de errores transversal | Consumida; mecanismo activo pero subutilizado (sección 4.4) |
| 194 | Optimización de contexto y multiagente de Codex Desktop | Consumida; política nunca retroalimentada a briefs posteriores (sección 4.4) |
| 195–199 | Prototipo, benchmark shadow y remediación del Contextual Bootstrap Resolver | Consumidas |
| 200 | Recuperación forense de artefactos del benchmark 198 | Consumida; solo se recuperó el oracle, no corpus ni runner |
| 201 | Protocolo de continuidad y reporte post-prueba | Consumida |
| 202 | Diseño y construcción desde cero del benchmark operacional reproducible | Consumida; paquete publicado, no validado |
| 203 | Validación independiente del instrumento de benchmark | `CONSUMED_BLOCKED` — Codex A detenido en preflight (sección 4.1, 4.4) |

*Fin del informe.*
