# LAB — vista de estado

La fuente estructurada es PROJECT_STATE.json. El estado global vigente pertenece a CURRENT_STATE.json.

## Identidad

- Project-ID: lab.
- Estado: active.
- Contrato: LAB_CONTRACT.md v2.1.
- Autoridad autónoma del modelo: no.

## Función

Gobernar autoridad, decisiones, reevaluaciones, errores, patrones, briefs y continuidad. El LAB no es runtime de producto.

## Política de HEAD propio

El LAB no almacena su propio HEAD como estado vigente, porque cada commit volvería obsoleto el valor.

- head_policy: VERIFY_LIVE_AT_USE.
- verified_parent_head: baseline anterior a la transición.
- self_head_is_canonical_state: false.

El HEAD vigente se resuelve desde main al iniciar cada conversación.

## Fuentes de ChatGPT

El punto de entrada canónico es `project-sources/chatgpt/START_HERE.md`. Las siete fuentes operativas se versionan en el LAB; las copias adjuntas no son fuente de verdad y solo pueden señalar este entrypoint.

## Test de instrucciones

LAB-CHATGPT-INSTRUCTIONS-TEST-001 se ejecutó con Terra 5.6 y razonamiento ligero.

Resultado: PASS_WITH_FINDINGS.

- Verificó GitHub, separó autoridad y evidencia y respetó solo lectura.
- La afirmación falsa sobre integración debía clasificarse REVERSED, no MODIFIED.
- Detectó el HEAD autorreferencial obsoleto del LAB.

## Autorización

No existe autorización activa reutilizable. Runtime, integración y producto permanecen no autorizados.
