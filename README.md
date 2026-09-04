# BQEB: A Reproducibility-First Architecture for Modular Energy AI Benchmarking

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22291930.svg)](https://doi.org/10.5281/zenodo.22291930)

A reproducibility-first architecture for modular energy AI benchmarking with deterministic execution, artifact integrity validation, evidence traceability, and governance mechanisms.

## Scope

This package accompanies the BQEB Architecture manuscript and its supplementary materials. It provides engineering tools and evidence records for the architecture's reproducibility mechanisms. The package validates deterministic execution paths, confirms checksum integrity, and supplies statistical-analysis and coverage-analysis tooling.

## Layout

- `manuscript/` contains the preserved final manuscript candidates.
- `supplementary/` contains the associated supplementary materials.
- `code/` contains reproducibility, validation, checksum, statistical-analysis, and coverage-analysis tools.
- `evidence/` records evidence status and traceability.
- `docs/` contains release, evidence, and migration guidance.

## Reproducibility boundaries

The deterministic example and checksum tests are runnable engineering artifacts. ForecastBench reconciliation, real-data statistical validation, and cross-environment reproducibility remain unexecuted pending complete migration. See `docs/REPRODUCIBILITY_SCOPE.md` for detailed boundary definitions.

## Citation

See `CITATION.cff`. For this Zenodo release, cite using DOI: https://doi.org/10.5281/zenodo.22291930
