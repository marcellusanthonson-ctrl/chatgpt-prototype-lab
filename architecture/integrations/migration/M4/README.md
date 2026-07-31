# M4 human cutover decision preparation

This package prepares the human M4 gate after the remediated M3 exact-equivalence result.

It does not select, recommend, infer, or execute a cutover option. The static selector remains authoritative, the shadow registry remains inactive, and authorization 160 remains only a proposal.

The rollback claim is bounded to documentary and source readiness. No operational or production rollback was executed. Any later M5 activation must begin with the separately authorized pre-activation rollback drill described in `ROLLBACK_READINESS.json`.

`ERR-LAB-008` records the contained general-validator array-delta crash. The bounded validator for this package is `scripts/validate_integration_factory_m4_preparation_159.py`; it does not repair the general validator.
