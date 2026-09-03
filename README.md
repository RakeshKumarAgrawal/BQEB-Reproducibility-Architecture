# BQEB: A Reproducibility-First Architecture for Modular Energy AI Benchmarking

A reproducibility-first architecture for modular energy AI benchmarking with deterministic execution, artifact integrity validation, evidence traceability, and governance mechanisms.

## Scope

This package accompanies the BQEB Architecture manuscript and its supplementary materials. It provides engineering tools and evidence records for the architecture’s reproducibility mechanisms. The included tools do not turn pending experiments into completed findings.

## Layout

- `manuscript/` contains the preserved final manuscript candidates.
- `supplementary/` contains the associated supplementary materials.
- `code/` contains reproducibility, validation, checksum, statistical-analysis, and coverage-analysis tools.
- `evidence/` records evidence status and traceability.
- `docs/` contains release, evidence, and migration guidance.

## Reproducibility boundaries

The deterministic example and checksum tests are runnable engineering artifacts. ForecastBench reconciliation, real-data statistical validation, and cross-environment reproducibility remain unexecuted or pending as recorded in `docs/EVIDENCE_STATUS.md`.

## Citation

See `CITATION.cff`. No publication DOI is assigned by this migration package.
