#!/usr/bin/env python3
"""
generate_artifact_inventory.py

MISSING COMPONENT, now implemented: a general-purpose enumeration of the
actual Paper 1 artifact set, distinct from generate_manifest.py's
SCOPES dict (which is a predefined file-pattern list per category, not an
inventory of what currently exists). This script answers "what IS the
complete Paper 1 artifact set right now" -- generate_manifest.py then
hashes whatever this inventory says exists.

The Paper 1 artifact list below is not invented -- it is taken directly
from the Research Evidence Repository Catalog (prior deliverable),
filtered to entries explicitly marked Paper 1 (excluding the Future
Paper / edge-case items: AR-06, AR-08, AR-09, AR-10, AR-11, AR-14).
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

# Source of truth: the Paper 1 Artifact List from the Evidence Repository
# Catalog. Each entry's "expected_files" is a starting point derived from
# that catalog's own file listings -- NOT independently re-verified against
# a live filesystem here, since this script's job is to state what SHOULD
# be checked, and generate_manifest.py's existing, tested code is what
# actually confirms presence and correctness.
PAPER_1_ARTIFACT_GROUPS = {
    "AR-01_forecastbench_reconciliation": {
        "backlog_item": "BL-01",
        "expected_files": [
            "reconcile_forecastbench.py",
            "compare_release_manifests.py",
            "cross-artifact-verification.yml",
        ],
    },
    "AR-02_artifact_integrity": {
        "backlog_item": "BL-04",
        "expected_files": [
            "generate_manifest.py",
            "verify_manifest.py",
            "artifact-integrity.yml",
            "REPO_STRUCTURE.md",
            "synthetic_test_results.json",
        ],
    },
    "AR-03_cross_environment_repro": {
        "backlog_item": "BL-03",
        "expected_files": [
            "compare_environment_outputs.py",
            "cross-environment-reproducibility.yml",
            "deterministic_computation.py",
            "run_1.json",
        ],
        # Dockerfile/requirements.txt deliberately excluded -- superseded
        # by AR-07 per the Evidence Repository Catalog's documented finding.
    },
    "AR-04_statistical_methodology": {
        "backlog_item": "BL-02",
        "expected_files": [
            "statistical_comparison.py",
            "power_analysis.py",
            "demonstrate_on_synthetic_data.py",
            "manuscript_subsection_15_1.md",
            "RESULT_INTERPRETATION_TEMPLATE.md",
            "statistical_comparison_demo.png",
        ],
    },
    "AR-05_targeted_coverage": {
        "backlog_item": "BL-06",
        "expected_files": [
            "classification_rules.py",
            "classify_coverage.py",
            "classified_synthetic_demo.json",
            "coverage_comparison.png",
        ],
    },
    "AR-07_unified_environment": {
        "backlog_item": "BL-03 (extends)",
        "expected_files": [
            "Dockerfile", "docker-compose.yml", "environment.yml",
            "requirements.txt", "requirements-dev.lock.txt",
            "README.md", "VERSION_PINNING_STRATEGY.md",
            "environment-verification.yml",
        ],
    },
    "AR-13_determinism_experiment": {
        "backlog_item": "BL-03A",
        "expected_files": [
            "determinism_experiment_within_env.png",
        ],
    },
}


def generate_inventory(out: Path) -> dict:
    inventory = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Research Evidence Repository Catalog, Paper 1 Artifact List",
        "groups": PAPER_1_ARTIFACT_GROUPS,
        "total_expected_files": sum(
            len(g["expected_files"]) for g in PAPER_1_ARTIFACT_GROUPS.values()
        ),
    }
    out.write_text(json.dumps(inventory, indent=2))
    return inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("paper1_artifact_inventory.json"))
    args = parser.parse_args()

    inventory = generate_inventory(args.out)
    print(f"Inventory: {len(inventory['groups'])} artifact groups, "
          f"{inventory['total_expected_files']} expected files")
    print(f"Written to {args.out}")
    print()
    print("NOTE: this lists what SHOULD exist per the Evidence Repository")
    print("Catalog. It does not itself confirm presence on disk -- feed each")
    print("group's expected_files into generate_manifest.py (existing,")
    print("tested tool) against the real repository root to do that.")


if __name__ == "__main__":
    main()
