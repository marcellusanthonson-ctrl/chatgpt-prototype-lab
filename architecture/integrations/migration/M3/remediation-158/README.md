# M3 remediation 158

Authorization 158 corrected the single `CRIT-FIX-008.expected_modules` inconsistency while preserving the 1.1.0 fixture byte-for-byte and leaving selector behavior unchanged.

- Fixture set: `1.1.1`.
- Historical fixture blob: `de4793dedc9646e388bdce5ccd1807da8a711845`.
- Remediated fixture blob: `db53d11e4a45e8f98a9b6aa540a2c7459723601b`.
- Corpus: exactly 420 deterministic synthetic cases.
- Static baseline oracles: 13/13 PASS.
- Shadow baseline oracles: 13/13 PASS.
- Static-shadow equivalence: 420/420 exact.
- Behavioral digest: `9d9f48ab881ee0f604e70ae1d23887afe8c2a6bdfcf683b49e76b0a641935329`, unchanged from original M3.
- Divergences and unexplained negative transfer: zero.

Result: `M3_REMEDIATED_PASS_EXACT_DUAL_EQUIVALENCE`. This result does not authorize M4, cutover, registry activation, selector changes, runtime or integration work.
