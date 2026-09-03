# Reproducibility Guide

## Available local checks

```powershell
python code/reproducibility/deterministic_computation.py --seed 42 --out results/output.json
python -m pytest code/checksum/test_verify_manifest.py
```

The deterministic command runs a representative, seeded computation. The checksum test verifies manifest behavior. These checks validate the included engineering tools and do not constitute a completed cross-environment experiment or a real-data benchmark study.

## Status boundaries

See `EVIDENCE_STATUS.md` before interpreting any generated output. In particular, reconciliation and statistical-validation tools require inputs not included in this migration package.
