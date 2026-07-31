# M2 — Shadow integration registry

This directory contains a deterministic, non-active representation of the four current criterion modules.

- `SHADOW_INTEGRATION_REGISTRY.json` indexes four `SHADOW_ONLY` adapters.
- `module-adapters/*/ADAPTER.json` reference the active selector and M1A packages without copying their full package contents.
- `STATIC_SHADOW_EQUIVALENCE_REPORT.json` records catalog equivalence.
- `VALIDATION_RESULTS.json` records two equivalent validation runs.
- The active selector remains authoritative and unchanged.
- No resolver, runtime behavior, module activation, integration or M3 execution is included.

M2 result: `M2_PASS`.

The M0 count of 27 signals comprises 23 distinct module activation-rule signals plus 4 exclusion signals.
