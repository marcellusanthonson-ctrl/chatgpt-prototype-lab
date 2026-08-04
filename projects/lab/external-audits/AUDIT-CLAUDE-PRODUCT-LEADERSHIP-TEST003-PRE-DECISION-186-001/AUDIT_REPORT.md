# AUDIT-CLAUDE-PRODUCT-LEADERSHIP-TEST003-PRE-DECISION-186-001

Auditoría externa independiente, adversarial, estrictamente de solo lectura, previa a la decisión.
Auditor: CLAUDE. Autorización: `..._INDEPENDENT_EXTERNAL_READ_ONLY_DECISION_AUDIT_186`.

---

## 1. HEAD auditado

| Campo | Valor |
|---|---|
| Repositorio | `marcellusanthonson-ctrl/chatgpt-prototype-lab` |
| Rama | `main` |
| HEAD remoto vivo verificado | `b00904cb46f5ef9ff3bd6b44e6a293ddd42281b0` |
| Método | `VERIFY_LIVE_AT_USE` — `git ls-remote`; `HEAD` y `refs/heads/main` coinciden |
| `expected_parent_head` declarado por la autorización 186 | `0845757639d601e785ab76605343ef9ef09e6cb0` |
| Relación verificada | el HEAD auditado es hijo directo del padre esperado (commit `b00904c`, "authorize Claude Product Leadership pre-decision audit 186") |
| Autorización 186 en la ancestría | **SÍ** — publicada en el propio commit auditado |
| Artefactos obligatorios | 21 de 21 `source_refs` presentes y legibles; 0 faltantes |
| Condiciones de parada | ninguna disparada |

Integridad de calibration-v2 verificada de forma **independiente**: recalculé los cinco SHA-256 y coinciden con el `MANIFEST` — 5 de 5. No dependo del reporte del ejecutor.

---

## 2. Resultado global

`RECOMMEND_REPLAY_AS_IS`

El estado probatorio real es más simple que el estado documental. **Cero de los 112 outputs mínimos de Test 003 existen.** Ninguna afirmación sobre el valor de Product Leadership —a favor o en contra— está sostenida por nada en el HEAD auditado. Lo único que se ha probado es el instrumento, y se ha probado que funciona: el intento 002 superó preflight de red, autenticación, procedencia de runner, modelo exacto y smoke, y llegó a ejecutar dos invocaciones reales de scorer antes de detenerse en la compuerta de calibración.

Lo que la narrativa documental vigente sugiere —"bloqueos repetidos de entorno"— **no resiste la desagregación causal**:

| Intento | Causa exacta | Clase |
|---|---|---|
| 182 etapa 3 / intento 001 | acceso a modelo o herramienta no reproducible | RUNNER |
| 183 / intento 001 | instalación efímera sin red; autenticación preexistente no disponible | ENTORNO + RUNNER |
| 184 / intento 002 | **preflight completo en PASS**; se detuvo en calibración v1 | CONTRATO PROBATORIO |
| 185 / intento 001 | lanzado en `CHATGPT_CONTAINER_NON_CODEX_LINUX`: sin DNS, sin HTTPS, sin binario codex | **DESPACHO A SUPERFICIE NO ELEGIBLE** |

El bloqueo 185 no es un obstáculo técnico nuevo. Es un despacho a un entorno que jamás fue candidato, cuando el brief 185 ya exigía como precondición `NETWORKED_CODEX_NATIVE_EXECUTION_SURFACE_AVAILABLE`. Se quemó una autorización por no verificar una precondición ya escrita.

---

## 3. Recomendación única

**A — `AUTHORIZE_ONE_USER_OPENED_CODEX_REPLAY_AS_CURRENTLY_DESIGNED`**
Confianza: **MEDIA-ALTA**.

Con una condición que **no** altera el diseño del test, ni el contrato calibration-v2, ni el `runner_contract`: la próxima autorización debe tratar la verificación de superficie, autenticación preexistente, procedencia del runner y modelo exacto como una etapa cuyo **fracaso no consume la autorización**. Es un cambio al criterio de consumo, no al diseño. Por eso sigue siendo A y no B.

Y una regla de detención declarada **antes** de ejecutar, no después:

- si vuelve a bloquearse por superficie o autenticación **habiendo verificado** las precondiciones → la evidencia pasa a sostener B;
- si calibration-v2 falla con desajustes concentrados en CAL2-003 / CAL2-004 → revisión acotada de la regla de frontera del rubro, **no** rechazo del candidato;
- si falla con desajustes dispersos entre las 8 anclas críticas → reevaluar la medibilidad del constructo.

---

## 4. Veredictos de los claims predeclarados

| Claim | Dominio | Veredicto | Confianza |
|---|---|---|---|
| 186-01 — el bloqueo 185 es de entorno y no dice nada sobre calibration-v2 | FACTUAL | **CONFIRMED** | ALTA |
| 186-02 — calibration-v2 basta para un intento más sin rediseño | MIXED | **MODIFIED** | MEDIA |
| 186-03 — superficie Codex + gpt-5.6-sol exacto es proporcionado | MIXED | **MODIFIED** | MEDIA-ALTA |
| 186-04 — la repetición en Codex abierto por el usuario es la acción de mayor valor y menor arrepentimiento | NORMATIVE | **CONFIRMED** (con precondición) | MEDIA-ALTA |
| 186-05 — la evidencia es insuficiente para concluir valor o transferencia negativa | FACTUAL | **CONFIRMED** | ALTA |
| 186-06 — los bloqueos repetidos justifican revisar la estrategia de ejecución | MIXED | **MODIFIED** | MEDIA-ALTA |
| 186-07 — una auditoría de solo lectura mejora la decisión aunque no satisfaga la Fase 3 | MIXED | **CONFIRMED** | ALTA |

**186-01 → CONFIRMED, y más fuerte que como está escrito.** `smoke_requests=0`, `calibration_scorer_requests=0`, `test003_model_requests=0`, EXECUTION-004 nunca creada. No existe ningún resultado parcial de calibración v2 en ninguna parte. Es más preciso llamarlo bloqueo de *elegibilidad de superficie*: el entorno observado no tenía siquiera DNS.

**186-02 → MODIFIED.** El fallo de v1 se explica por subespecificación del contrato, no por inestabilidad del scorer: el prompt v1 no contenía **ninguna** definición de etiqueta, ninguna precedencia, ninguna regla de frontera y ningún `gold_rationale`; y ambos scorers convergieron en la *misma* etiqueta no-gold para CAL-003. Convergencia, no ruido — firma de rubro malo. v2 corrige exactamente eso: definiciones, tests positivos y negativos, precedencia de 6 niveles, 4 reglas de frontera, casos 6→12, 8 anclas críticas, esquema de salida estricto.

Pero la afirmación "suficientemente discriminante y reproducible" no está establecida, por dos razones concretas:

1. **Riesgo residual en CAL2-003, que es ancla crítica.** La precedencia sitúa `CORRECT_ABSTENTION` *por encima* de `AMBIGUOUS`, y la regla 2 del prompt ordena aplicar precedencia antes de bajar de nivel. El `candidate_response` de CAL2-003 conserva la formulación "…before ranking the signals", que es precisamente lo que llevó a ambos scorers v1 a `CORRECT_ABSTENTION`. Lo único que lo impide ahora son los tests negativos. Un desajuste ahí es FAIL inmediato.
2. **Ajuste al modo de falla.** Las definiciones, las reglas de frontera y el texto del propio ítem CAL2-003 fueron redactados después de observar el error exacto, y los dos casos disputados se conservaron como anclas. La compuerta quedó parcialmente ajustada a la falla que debe detectar, lo que reduce su independencia como prueba de fiabilidad del scorer. Formalmente todo es pre-freeze y por tanto permitido — pero el `MANIFEST` de v2 contiene un bloque `adjudications` sobre CAL2-003 y CAL2-004 mientras la autorización 185 declara `post_hoc_adjudication_allowed=false`. Es consistente y se lee ambiguo.

Consecuencia práctica: un PASS de calibration-v2 será **menos informativo de lo que aparenta** y debe registrarse con esa salvedad para la Fase 3.

**186-03 → MODIFIED.** El modelo exacto sí es proporcionado: el test es un contraste intra-modelo entre 4 brazos y sustituirlo confunde la única comparación que el test existe para hacer. La *superficie* Codex es otra cosa: nada en `TEST-001 MANIFEST`, `SCORING_AND_GATES` ni `FINAL_DESIGN_REVIEW_001` la exige. Lo que el diseño exige es procedencia reproducible y no manipular credenciales. Codex es el instrumento elegido para satisfacer esa segunda restricción —razón legítima, operativa, no probatoria— y es la mayor fuente de riesgo de bloqueo de toda la línea: 2 de 4 intentos perdidos ahí, 0 perdidos por el contrato probatorio.

**186-06 → MODIFIED, casi REVERSED en su lectura fuerte.** Lo que el registro justifica es revisar el **despacho**, no la estrategia. Y hay un agravante documental: en el merge #27 se sobrescribieron en `INT-LAB-004` los campos `exact_model_verified` (true→false), `preauthorized_authentication_verified` (true→false), `networked_codex_surface_verified` (true→false) y `smoke_requests` (1→0). Esos campos describían el intento 002 y fueron reemplazados por los valores del 185. **Quien lea sólo el HEAD concluirá, razonable pero erróneamente, que el entorno nunca funcionó.** Ese artefacto documental es, probablemente, parte de por qué este claim parece verdadero.

---

## 5. Comparación de las cinco alternativas

| | A repetir | B revisar estrategia | C pausar | D rechazar | E insuficiente |
|---|---|---|---|---|---|
| Valor de información | **ALTO** | BAJO (informa sobre el instrumento, no sobre el candidato) | NULO | NULO | NULO |
| Costo | ejecución BAJO / gobierno MEDIO-ALTO | ALTO | nulo hoy, acumulativo | irreversible en conocimiento | nulo |
| Reversibilidad | **TOTAL** | alta | total | **BAJA** | total |
| Riesgo operacional | MEDIO (mitigable) | bajo | nulo | bajo | nulo |
| Riesgo epistémico | MEDIO | **ALTO** | medio | **MUY ALTO** | medio |
| Costo de oportunidad | BAJO | ALTO | ALTO | MUY ALTO | ALTO |
| Exposición a costo hundido | **MEDIO** | bajo | nulo | nulo | nulo |
| Riesgo de rechazo prematuro | nulo | bajo | bajo | **MÁXIMO** | bajo |

**Por qué las otras son inferiores bajo la evidencia vigente:**

**B** paga costo de rediseño contra una configuración que ya funcionó de extremo a extremo hasta la compuerta de calibración. La única falla de estrategia demostrada es de despacho, y un control de precondiciones la corrige a costo casi nulo. Además, reabrir el contrato invita exactamente al ajuste post hoc que ya es un riesgo del paquete v2.

**C** no produce información y no existe ninguna condición externa identificada que se espere que cambie. La superficie requerida existe hoy y funcionó hace horas. Con SSE también bloqueado tras una resolución de runner separada, pausar detiene las dos integraciones prioritarias a la vez: costo de oportunidad puro.

**D** es la definición del rechazo prematuro. Sería una decisión sobre el valor del candidato tomada con 0 outputs de evidencia de valor, en contradicción directa con el veredicto CONFIRMED del claim 186-05 y con `LAB_CONTRACT` §11 —cambiar de posición por evidencia, no por fatiga—. Se perderían además 52 fixtures, 4 brazos y 13 artefactos de fábrica ya validados.

**E** describe correctamente el estado probatorio y aun así es una decisión equivocada, porque confunde dos preguntas. La pregunta en decisión no es "¿aporta valor Product Leadership?" —eso es 186-05, y la respuesta es que no se sabe— sino "¿cuál es el paso más barato que produce evidencia discriminante?". Esa segunda pregunta **sí** tiene respuesta con la evidencia vigente, y cuesta dos llamadas al modelo.

---

## 6. Evidencia a favor y en contra

A favor de A, en orden de peso:

- `EVD-184` documenta la superficie `CODEX_DESKTOP_LOCAL_WINDOWS` build 1.2026.190 con red PASS, autenticación preexistente de OpenAI PASS, runner 0.146.0 con digest oficial exacto, gpt-5.6-sol disponible, 1 smoke con exit 0, y dos invocaciones reales de scorer con latencia y tokens registrados. La capacidad está **demostrada**, no supuesta.
- La reversibilidad es total por diseño: `generation_gate` impide crear EXECUTION-004 o cualquier output antes del PASS de calibración.
- Un FAIL de calibration-v2 es en sí mismo discriminante: separa "el rubro sigue ambiguo" de "el scorer no es fiable". Ninguna otra opción produce eso.

En contra de A, sin suavizar:

- El costo de gobierno por intento (autorización, brief, evidencia, delta de registro, rama, PR, squash merge, actualización de 6+ artefactos agregados) **excede con mucho** el costo de ejecución. Cuatro ciclos de autorización han producido 0 de 112 outputs. El recurso escaso aquí no es el cómputo: son los ciclos de gobierno.
- El claim 186-04 es falso si la superficie no se verifica antes de consumir la autorización. Eso ya ocurrió una vez.

Dos hallazgos colaterales que no cambian la recomendación pero sí deberían corregirse por separado:

**Reescritura retroactiva de autorizaciones.** Al cerrarse, las autorizaciones 183 y 185 no cambiaron de *estado*: cambiaron sus *términos de concesión*. En la 185, entre el commit de concesión `831cdb4` y el de cierre `0845757`, nueve banderas de permiso pasaron de `true` a `false` y `residual_authority_after_publication` pasó de "CALIBRATION_V2_EXECUTION_AND_CONDITIONAL_FRESH_TEST003_ATTEMPT_ONLY" a "NONE". Hoy el artefacto declara `commit_authorized: false` mientras su propia lista `allowed_actions` incluye el commit y su estado es CONSUMED tras un squash merge. La 184 conserva sus banderas en `true`: la convención no es uniforme, y por tanto **las banderas booleanas de autorización no son hoy interpretables sin consultar la historia de git**. No disparé la condición de parada por procedencia ambigua: la procedencia de los artefactos es verificable y sus digests coinciden; esto es inconsistencia semántica interna y por eso es hallazgo, no detención.

**La ruta de lectura canónica obligatoria entrega estado obsoleto.** `START_HERE.md` ordena leer `CURRENT_STATE.json` como paso 4 y `registry/index.json` como paso 5. `CURRENT_STATE.json` declara hoy `fixture_count: 40` cuando el contrato vigente es 52, `operational_preflight: BLOCKED_NO_ELIGIBLE_BOUNDED_CREATOR`, y su estado global se refiere a SSE 180. `registry/index.json` no menciona las autorizaciones 184, 185 ni 186. Quien siga el orden obligatorio no descubre que existe esta línea completa salvo que llegue a `PEND-LAB-045`, `ROADMAP` o `INT-LAB-004`. La divergencia está autodeclarada en seis artefactos con `correction_authorized: false` —es conocida y deliberada, no oculta— pero es un riesgo epistémico vivo justo cuando se está tomando esta decisión.

---

## 7. Riesgos y costo de oportunidad

El riesgo material no es que el test falle. Es doble:

1. **Escalada de compromiso disfrazada de rigor.** Cada bloqueo genera un ciclo documental cuyo costo supera al del experimento. Sin una regla de detención declarada de antemano, la línea puede consumir ciclos indefinidamente sin producir un solo output. Por eso la regla de detención de la sección 3 es parte de la recomendación, no un adorno.
2. **Un PASS sobreinterpretado.** Si calibration-v2 pasa, el resultado será menos independiente de lo que su forma sugiere, porque el rubro fue afinado contra el error que debe detectar. Debe entrar a Fase 3 con esa salvedad escrita.

Costo de oportunidad de no actuar: ambas integraciones prioritarias de la ruta crítica quedan detenidas simultáneamente, con `PEND-LAB-045` bloqueando la Fase 2 completa.

Sobre mi propio sesgo: A es también la opción que elegiría un sesgo de costo hundido. Apliqué como control la prueba marginal prospectiva —¿recomendaría A si este fuera el primer intento, sin inversión previa?—. A un costo marginal de un smoke y dos invocaciones de scorer, con reversibilidad total y compuerta previa a la generación, la respuesta es sí. La recomendación no depende de la inversión acumulada. El control reduce el sesgo; no lo elimina. Queda declarado para que el aprobador lo pondere.

---

## 8. Limitaciones

- **PR 25 y 27 no leídos por su interfaz**: `api.github.com` devolvió HTTP 403 por límite de tasa no autenticado en todos los intentos. Se auditó en su lugar el contenido exacto mergeado vía los commits `8ef3dbd` (#25) y `0845757` (#27) y sus diffs semánticos. Falta únicamente metadato de revisión: revisores, comentarios, checks de CI.
- **No es posible verificar qué haría hoy gpt-5.6-sol**: la ejecución de modelo está prohibida por el modo. Toda afirmación sobre el resultado probable de calibration-v2 es predicción, no hecho. Ninguna conclusión de esta auditoría depende de esa predicción.
- **Los hechos de entorno son autorreportados**: internamente consistentes en cinco artefactos independientes y sin contradicción hallada, pero no verificados por un tercero.
- **No puede establecerse si 52 fixtures y 112 outputs dan potencia suficiente** para detectar transferencia negativa bajo el umbral declarado con estratificación por dominio. Diferido a Fase 3.
- **Fuera de alcance**: la vía SSE más allá del costo de oportunidad, el contenido sustantivo del paquete candidato, y la divergencia de vistas agregadas más allá de constatarla.

---

## 9. Qué evidencia cambiaría la recomendación

| Nueva evidencia | Recomendación resultante |
|---|---|
| La superficie Codex Desktop del usuario ya no está disponible, o gpt-5.6-sol no es accesible en ella | C o B |
| Segundo bloqueo de entorno o autenticación **en superficie ya verificada como elegible** | B |
| Calibration-v2 FAIL con desajustes concentrados en CAL2-003 / CAL2-004 | B acotada a la regla de frontera del rubro — **no** D |
| Calibration-v2 FAIL con desajustes dispersos y no convergentes entre las 8 anclas | B con reevaluación de medibilidad; D sólo si se repite |
| Presupuesto, plazo o regla de detención declarada que haga material el costo de otro ciclo | C o D según el presupuesto |
| Que la repetición exija creación o transferencia de credenciales, o cualquier operación prohibida | C |

Nada de lo que he leído sostendría hoy la opción D. Para llegar ahí haría falta evidencia de *valor*, y no existe ninguna.

---

## 10. No-efectos

Esta auditoría no modificó el repositorio. No hubo commit, push, pull request, merge ni comentario. No se ejecutó Codex, runner, smoke, calibración ni Test 003; cero solicitudes a modelo alguno. No hubo AWS, Terraform ni operación de cuenta. No se creó, transfirió, inspeccionó ni divulgó credencial alguna. No se reconciliaron vistas agregadas. No se hizo investigación web externa. No se satisface la compuerta de Fase 3. No hay promoción, activación, integración ni rechazo de Product Leadership.

**`AUDIT_RECOMMENDATION_IS_NOT_HUMAN_APPROVAL_OR_EXECUTION_AUTHORITY`**

La recomendación de la sección 3 es dictamen de auditor sobre una cuestión normativa. La decisión corresponde exclusivamente a Jonathan Martínez. La ejecución requiere una autorización delimitada, explícita y separada, que este paquete no crea ni sustituye. La reconciliación de estos hallazgos en el canon requiere autorización aparte.
