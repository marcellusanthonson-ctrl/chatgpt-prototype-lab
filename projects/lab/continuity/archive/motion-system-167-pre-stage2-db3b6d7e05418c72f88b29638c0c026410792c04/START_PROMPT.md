La autorización 166 completó Stage 2 con `M5_BOUNDED_CUTOVER_PASS_INTEGRATION_ACTIVE_STATIC_FALLBACK_PRESERVED`. Verifica primero el HEAD remoto vigente de `main` y reconstruye el estado desde `project-sources/chatgpt/START_HERE.md`.

El pointer `architecture/integrations/active/INTEGRATION_FACTORY_RESOLUTION_POINTER.json` está en `CANDIDATE_ACTIVE_CONFIRMED`. El candidate conserva el blob `a067cd9f95b98aa1599d21e3a0ff35fa56ac3a78`; el selector estático conserva `301ba432907758fc49a9b3c86a83fc762eac4607` y permanece disponible como fallback.

Las dos observaciones pasaron 420/420, 13/13 oráculos por evaluador, cero divergencias y digest exacto determinista. El lock y los temporales fueron retirados. La autorización 166 está consumida y no es reutilizable.

`PEND-LAB-042` es la siguiente decisión única: Jonathan Martínez decide si conserva el fallback estático indefinidamente o autoriza separadamente su retiro. No infieras autoridad de retiro, retry, AWS, Terraform, runtime externo o cambios en otros repositorios.
