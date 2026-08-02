# Protocolo reutilizable de motion

## Fases obligatorias

1. **Motion intent contract:** definir objetivo perceptual, dato dinámico, contenido estático, inicio, final, trigger, repetición, reduced motion, geometría máxima y propietario de cada propiedad visual.
2. **Clasificación:** registrar taxonomía, cálculo, riesgo, coste y personalización.
3. **Reconstrucción fiel a fuente:** antes de abstraer, inventariar todas las fuentes y preservar una implementación de referencia, contrato de fidelidad, anatomía visual, invariantes geométricos y baseline renderizado.
4. **Comparación fuente-candidato:** medir DOM, contenido, geometría horizontal y vertical, estilos computados, comportamiento, capturas, diff y SSIM en el mismo navegador.
5. **Revisión humana antes de abstraer:** publicar una comparación humana y mantener `HUMAN_REVIEW_PENDING` hasta aprobación explícita.
6. **Prototipo mínimo aislado:** HTML monolítico, sin dependencias ni red; puede conservar el contexto fuente necesario para reproducir geometría y scroll.
7. **Congelación del baseline:** hash, inventario y evidencia inmediatamente después de la aprobación.
8. **Extracción genérica:** retirar identidad de producto sin cambiar invariantes.
9. **Contrato de fórmula:** obligatorio cuando la identidad depende de cálculos.
10. **Contrato de personalización:** separar invariantes, tokens, coreografía, adaptación visual y derivación signature.
11. **Validación perceptual:** primer frame, 25 %, 50 %, 75 %, final y 500 ms posteriores.
12. **Validación técnica:** cinco reproducciones, tres viewports, reentrada, reduced motion, consola, red, geometría y DOM.
13. **Cierre documental atómico:** manifiesto, integridad, validación y registro en la misma ejecución.
14. **Integración separada:** cada producto requiere baseline, autorización, diff, rollback y revisión humana.

## Reglas técnicas

- Animar la variable, no su sintaxis.
- Mantener sufijos, unidades y etiquetas en nodos estáticos.
- Usar `textContent` para valores dinámicos; no `innerHTML` por frame.
- Limitar progreso y valores al dominio permitido.
- Reservar geometría máxima antes del movimiento.
- Esperar `document.fonts.ready` cuando las fuentes cambien medidas.
- No combinar dos motores sobre la misma propiedad.
- El DOM final debe existir desde el inicio.
- Una fórmula correcta no prueba fidelidad visual ni anatómica.
- Ninguna adaptación neutral puede presentarse como implementación de referencia.
- La comparación automatizada no sustituye la revisión humana ni autoriza reemplazo canónico.
