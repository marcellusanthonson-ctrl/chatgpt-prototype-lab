# Protocolos de evidencia de Foundation Library

Estos documentos definen pruebas y oráculos; no registran ejecuciones. Todos permanecen en estado `EVIDENCE_PROTOCOL_DEFINED_NOT_EXECUTED`.

## Evidencia de diseño

Cada arquetipo cubre los límites 320, 639, 640, 1023, 1024, 1439, 1440 y 1920 px; contenido extremo; zoom y reflujo; teclado y foco; semántica para lectores de pantalla; contraste calculado; movimiento reducido; estados de interacción; y estados vacío, carga, error y éxito.

Los anchos son puntos de comprobación del contrato, no modelos de dispositivos. Un resultado futuro solo podrá marcarse como aprobado si conserva contenido, acciones y orden semántico en cada frontera.

## Evidencia backend

Cada patrón cubre camino correcto, validación, autorización, duplicados, agotamiento de reintentos, concurrencia, redacción, aislamiento cliente-entorno, frontera de secretos y recuperación. Los casos describen entradas sintéticas deterministas y resultados esperados.

Pagos añade doce comprobaciones específicas. La captura de datos regulados debe permanecer alojada fuera de la aplicación; el navegador no puede declarar un pago exitoso; importes y monedas se validan en servidor; y eventos duplicados o desordenados no pueden duplicar efectos.

## Límites epistemológicos

Un protocolo definido no demuestra que un sistema funcione. `runtime_validated`, `integration_validated` y `production_validated` permanecen `false` hasta autorizaciones y evidencia posteriores. Ninguna fixture contiene personas, tarjetas, credenciales, secretos o transacciones reales.
