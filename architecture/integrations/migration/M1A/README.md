# M1A executable artifact validation

This directory contains isolated, non-runtime `CRITERION_MODULE` candidate packages and the machine-readable result of the M1A validation.

The validation is repository-local. It does not call cloud services, use production credentials, modify the active selector, create a shadow registry, or activate any package.

## Deterministic command sequence

From the repository root:

```powershell
python -m pip install --target .validation/python --requirement scripts/requirements-integration-factory-validation.txt
$env:PYTHONPATH = ".validation/python"
python scripts/validate_integration_factory_m1a.py --check
python scripts/validate_integration_factory_m1a.py --check
python scripts/validate_repository.py
```

To reproduce all generated JSON from canonical inputs:

```powershell
$env:PYTHONPATH = ".validation/python"
python scripts/validate_integration_factory_m1a.py --materialize
python scripts/validate_integration_factory_m1a.py --check
```

The two unchanged-input `--check` runs must report the same normalized digest.
