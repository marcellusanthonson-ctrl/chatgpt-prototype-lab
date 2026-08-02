# Protocolo reutilizable de motion

## Fases obligatorias

1. **Motion intent contract:** definir objetivo perceptual, dato dinámico, contenido estático, inicio, final, trigger, repetición, reduced motion, geometría máxima y propietario de cada propiedad visual.
2. **Clasificación:** registrar taxonomía, cálculo, riesgo, coste y personalización.
3. **Prototipo mínimo aislado:** HTML monolítico, sin landing completa, dependencias ni red.
4. **Revisión humana temprana:** validar utilidad, velocidad, continuidad, elementos quietos y movimiento innecesario.
5. **Congelación del baseline:** hash, inventario y evidencia inmediatamente después de la aprobación.
6. **Extracción genérica:** retirar identidad de producto sin cambiar invariantes.
7. **Contrato de fórmula:** obligatorio cuando la identidad depende de cálculos.
8. **Contrato de personalización:** separar invariantes, tokens, coreografía, adaptación visual y derivación signature.
9. **Validación perceptual:** primer frame, 25 %, 50 %, 75 %, final y 500 ms posteriores.
10. **Validación técnica:** cinco reproducciones, tres viewports, reentrada, reduced motion, consola, red, geometría y DOM.
11. **Cierre documental atómico:** manifiesto, integridad, validación y registro en la misma ejecución.
12. **Integración separada:** cada producto requiere baseline, autorización, diff, rollback y revisión humana.

## Reglas técnicas

- Animar la variable, no su sintaxis.
- Mantener sufijos, unidades y etiquetas en nodos estáticos.
- Usar `textContent` para valores dinámicos; no `innerHTML` por frame.
- Limitar progreso y valores al dominio permitido.
- Reservar geometría máxima antes del movimiento.
- Esperar `document.fonts.ready` cuando las fuentes cambien medidas.
- No combinar dos motores sobre la misma propiedad.
- El DOM final debe existir desde el inicio.
