# LAB code maintainability policy

Manually maintained code is limited to 280 physical lines per file for `.js`, `.jsx`, `.ts`, `.tsx`, `.py`, `.html`, `.css`, `.scss`, `.vue`, `.svelte`, `.sh`, `.ps1`, and `.sql`. New or modified code above the limit causes `STOP` and must be modularized. Minification, line concatenation, or compression performed to appear compliant is prohibited.

An over-limit path must be registered with one class and a concrete reason: `GENERATED`, `VENDORED`, `HISTORICAL_IMMUTABLE`, `EXTERNAL_FORMAT_CONSTRAINT`, `LOCKFILE`, `SNAPSHOT`, or `DATASET`. Historical evidence is classified, not rewritten solely for line length.

## Preliminary monolithic visual HTML

A controlled preliminary visual-validation HTML may exceed 280 lines only when registered as `EXTERNAL_FORMAT_CONSTRAINT` and beginning exactly with:

```html
<!-- SYMPHONIE_MONOLITHIC_PRELIMINARY_VISUAL_EXCEPTION: AUTHORIZED_FOR_PRELIMINARY_VISUAL_VALIDATION_ONLY -->
```

This exception does not authorize product code, deployment, runtime, data, or a human decision. Other historical HTML may only remain over the limit when it is genuinely immutable historical evidence and is not modified.
