# Protocolo de parche visual quirúrgico

Document-Role: TRANSVERSAL_VISUAL_EXECUTION_PROTOCOL
Pattern: PAT-LAB-009
Error-Prevention: ERR-LAB-007
Authority-Effect: NONE

## Propósito

Aplicar cambios visuales localizados sobre un artefacto seleccionado por una persona sin reinterpretar, rediseñar ni mejorar superficies no solicitadas.

## Clasificación obligatoria

Antes de emitir un brief visual, clasificar la tarea como una de las siguientes:

1. `OPEN_EXPLORATION`
2. `BOUNDED_EXPLORATION`
3. `DERIVATIVE_REVISION`
4. `SURGICAL_PATCH`
5. `EXACT_REPRODUCTION`

Cuando existe un parent humano seleccionado y la petición usa expresiones como «solo», «idéntico», «mantener» o «sin cambiar lo demás», el modo predeterminado es `SURGICAL_PATCH`.

## Contrato predeterminado

```text
CREATIVE_AUTONOMY = NONE_UNLESS_EXPLICITLY_GRANTED
UNMENTIONED_ELEMENTS = LOCKED
UNREQUESTED_IMPROVEMENTS = FORBIDDEN
VISUAL_PARENT = EXACT_REFERENCED_ARTIFACT
MULTIPLE_VARIABLE_CHANGES = FORBIDDEN
```

`LOCKED` significa no modificar, refinar, refactorizar, reinterpretar ni cambiar indirectamente.

## Roles de artefactos

Cada fuente debe recibir un único rol explícito:

- `EXACT_VISUAL_PARENT`
- `ASSET_SOURCE_ONLY`
- `VISUAL_REFERENCE`
- `NEGATIVE_REFERENCE`
- `EVIDENCE_ONLY`

Un artefacto declarado `ASSET_SOURCE_ONLY` no puede aportar layout, tipografía, paleta, composición ni estilo.

## Presupuesto de cambio

Todo brief debe declarar:

- número máximo de cambios materiales;
- regiones mutables;
- selectores o propiedades mutables;
- contenido mutable;
- diferencias prohibidas;
- autonomía creativa.

Escala recomendada:

- `CHANGE_BUDGET_0`: ningún cambio visual;
- `CHANGE_BUDGET_1`: un asset o un texto;
- `CHANGE_BUDGET_2`: parche acotado de componente;
- `CHANGE_BUDGET_3`: revisión de sección;
- `CHANGE_BUDGET_4`: dirección visual completa;
- `CHANGE_BUDGET_5`: exploración abierta.

## Ejecución

1. Copiar el parent exacto.
2. Registrar hash del parent antes de trabajar.
3. Modificar solo la región y propiedad autorizadas.
4. No refactorizar código no afectado.
5. No aplicar mejoras no solicitadas.
6. Crear un único candidato salvo autorización contraria.
7. Preservar el parent intacto.

## Validación mínima

- hash del parent antes y después;
- diff de HTML o DOM;
- lista exacta de propiedades CSS modificadas;
- captura parent y sucesora en el mismo viewport;
- máscara de región mutable;
- pixel diff fuera de la máscara;
- comprobación de outputs exactos;
- estado Git;
- revisión humana de la región cambiada.

Para un parche de fidelidad estricta, el objetivo fuera de la máscara es `0` píxeles diferentes, salvo tolerancia de rasterización explícitamente documentada.

## Estados separados

```text
TECHNICAL_STATE != HUMAN_VISUAL_STATE
```

Un HTML sin errores, overflow ni clipping puede seguir siendo una regresión visual. Ningún `PASS` técnico crea aprobación estética.

Estados recomendados:

- `PATCH_FIDELITY_PASS`
- `BLOCKED_BY_UNAUTHORIZED_VISUAL_DRIFT`
- `HUMAN_VISUAL_APPROVAL_PENDING`
- `HUMAN_VISUAL_APPROVED`
- `HUMAN_VISUAL_REJECTED`

## Stop conditions

Detener y restaurar el parent cuando:

- aparece un cambio fuera de la región autorizada;
- sería necesario modificar una superficie bloqueada;
- el agente introduce una mejora no solicitada;
- el resultado usa una referencia en un rol no autorizado;
- el parent cambia;
- no puede medirse la fidelidad requerida.

## Caso de validación LivHavn

Candidate 02 confirmó que una ejecución puede pasar validaciones técnicas y ser visualmente inferior cuando el brief concede demasiadas variables. Candidate 03 confirmó, para este caso delimitado, que Codex puede ejecutar con fidelidad exacta cuando recibe parent explícito, cambio único, autonomía creativa nula y validación por región.

La inferencia correcta es acotada: Codex mostró alta fiabilidad para una transformación explícita, limitada y verificable. No se declara perfección universal.
