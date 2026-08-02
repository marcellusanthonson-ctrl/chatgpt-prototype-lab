# Checklist

## Antes de construir
- [ ] Intención y resultado perceptual definidos.
- [ ] Inventario completo de fuente con blobs, hashes, roles, imports y selectores.
- [ ] Implementación de referencia y contratos de fidelidad, anatomía y geometría creados.
- [ ] Elementos dinámicos y estáticos separados.
- [ ] Trigger, repetición y reduced motion definidos.
- [ ] Geometría máxima y fórmula identificadas.

## Implementación
- [ ] Un propietario por propiedad visual.
- [ ] Progreso limitado a `[0,1]`.
- [ ] Sin overlays que sustituyan el DOM canónico.
- [ ] Sin `innerHTML` por frame.
- [ ] Fuentes y medidas estabilizadas.

## Prueba
- [ ] Cinco reproducciones completas.
- [ ] 390×844, 768×1024 y 1440×1000.
- [ ] Primer frame y estado final válidos.
- [ ] Cero frames vacíos, NaN o valores fuera de rango.
- [ ] Reduced motion preserva información y layout.
- [ ] Cero recursos externos y errores de consola.
- [ ] Baseline fuente y comparación fuente-candidato en el mismo navegador.
- [ ] Eje horizontal, concentricidad, geometría vertical, estilos computados, diff y SSIM validados.

## Cierre
- [ ] Hashes, inventario, diff y procedencia.
- [ ] Resultado humano separado del técnico.
- [ ] Estado no supera la autoridad concedida.
- [ ] Comparación humana publicada antes de cualquier abstracción, reemplazo o promoción.
