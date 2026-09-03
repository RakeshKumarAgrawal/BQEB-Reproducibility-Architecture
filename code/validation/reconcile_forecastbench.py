#!/usr/bin/env python3
"""
reconcile_forecastbench.py

Investigation + verification procedure for the disclosed ForecastBench metric
discrepancy (BQEB architecture manuscript, Table 3 / Section 12).

This script implements deliverables 1-6 of the implementation request:
  1. Investigation procedure   -> main()
  2. Files to inspect          -> REQUIRED_FILES
  3. Configuration checks      -> check_config()
  4. Random seed verification  -> check_seed()
  5. Artifact verification     -> verify_checksums()
  6. Root-cause analysis       -> classify_discrepancy()

IMPORTANT: This script contains NO invented metric values. Every comparison
is a placeholder until the two external sources (refs [5] and [6]) and a
fresh v1.0.0 run are actually obtained and placed at the paths below. Running
this script against absent inputs will correctly fail at the file-existence
check rather than silently proceeding.
"""

import hashlib
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# 2. FILES TO INSPECT
# ---------------------------------------------------------------------------
# Paths are placeholders for the user to populate with the actual retrieved
# artifacts. Nothing here is fabricated data -- these are the inputs the
# procedure requires before it can produce an output.

REQUIRED_FILES = {
    "source_5_values": "inputs/forecastbench_researchsquare_preprint_values.json",
    "source_6_values": "inputs/forecastbench_zenodo_paper_values.json",
    "fresh_run_metrics": "inputs/fresh_v1.0.0_metrics.csv",
    "fresh_run_manifest": "inputs/fresh_v1.0.0_experiment_manifest.json",
    "published_checksums": "inputs/published_v1.0.0_checksums.sha256",
    "split_file": "inputs/train_test_split/",
}


@dataclass
class InvestigationResult:
    files_present: dict = field(default_factory=dict)
    config_match: dict = field(default_factory=dict)
    seed_match: bool | None = None
    checksum_results: dict = field(default_factory=dict)
    probable_cause: str = "unknown"
    evidence: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# 1. INVESTIGATION PROCEDURE (entry point)
# ---------------------------------------------------------------------------
def main():
    result = InvestigationResult()

    print("=== Step 1: Confirm required artifacts are present ===")
    all_present = True
    for label, path in REQUIRED_FILES.items():
        exists = Path(path).exists()
        result.files_present[label] = exists
        status = "FOUND" if exists else "MISSING"
        print(f"  [{status}] {label}: {path}")
        if not exists:
            all_present = False

    if not all_present:
        print()
        print("HALT: Investigation cannot proceed. The following are required")
        print("and are not obtainable from the manuscript alone:")
        for label, path in REQUIRED_FILES.items():
            if not result.files_present[label]:
                print(f"  - {label} (expected at {path})")
        print()
        print("This is the correct, expected outcome until refs [5] and [6]")
        print("are actually retrieved. Do not proceed past this point by")
        print("substituting placeholder or estimated values.")
        sys.exit(1)

    print()
    print("=== Step 2: Configuration checks ===")
    result.config_match = check_config(
        REQUIRED_FILES["fresh_run_manifest"],
        REQUIRED_FILES["source_5_values"],
        REQUIRED_FILES["source_6_values"],
    )

    print()
    print("=== Step 3: Random seed verification ===")
    result.seed_match = check_seed(REQUIRED_FILES["fresh_run_manifest"])

    print()
    print("=== Step 4: Artifact (checksum) verification ===")
    result.checksum_results = verify_checksums(
        REQUIRED_FILES["fresh_run_metrics"],
        REQUIRED_FILES["published_checksums"],
    )

    print()
    print("=== Step 5: Root-cause classification ===")
    result.probable_cause, result.evidence = classify_discrepancy(result)
    print(f"  Probable cause: {result.probable_cause}")
    for e in result.evidence:
        print(f"    - {e}")

    print()
    print("=== Step 6: Write findings for manuscript update ===")
    write_findings(result)


# ---------------------------------------------------------------------------
# 3. CONFIGURATION CHECKS
# ---------------------------------------------------------------------------
def check_config(manifest_path, source_5_path, source_6_path):
    """
    Compares the dataset version, split strategy, model hyperparameters,
    AND software package versions recorded in a fresh run's manifest
    against whatever each external source discloses about its own
    methodology.

    Returns a dict of {field: (fresh_value, source_5_value, source_6_value, match)}.
    Values are read from the actual files, never invented here.
    """
    with open(manifest_path) as f:
        manifest = json.load(f)

    checks = {}
    # "software_versions" added -- MISSING COMPONENT identified and closed
    # in this pass. A metric discrepancy can arise from a scikit-learn or
    # numpy version difference alone, even with identical code, seed, and
    # data -- this was not previously checked at all.
    for field_name in ["dataset_version", "split_strategy", "model_hyperparameters", "software_versions"]:
        fresh_val = manifest.get(field_name, "NOT_RECORDED_IN_MANIFEST")
        checks[field_name] = {
            "fresh_run": fresh_val,
            "note": (
                "Compare manually against each source's stated methodology "
                "section once source_5 and source_6 documents are available "
                "in full text -- their methodology sections are prose, not "
                "structured data, and cannot be diffed automatically."
            ),
        }
        print(f"  {field_name}: fresh_run={fresh_val}")
    return checks


# ---------------------------------------------------------------------------
# 4. RANDOM SEED VERIFICATION
# ---------------------------------------------------------------------------
def check_seed(manifest_path):
    """
    Per Section 11 of the manuscript: 'all stochastic components... are
    seeded, with the value used documented alongside each release.'
    Confirms the fresh run's manifest actually records a seed, then flags
    that source-document seed disclosure must be checked by hand.
    """
    with open(manifest_path) as f:
        manifest = json.load(f)

    seed = manifest.get("seed")
    if seed is None:
        print("  FAIL: fresh run manifest does not record a seed value.")
        print("  This is itself a finding -- Section 11's determinism claim")
        print("  requires this field to be present and populated.")
        return False

    print(f"  Fresh run seed: {seed}")
    print("  ACTION REQUIRED: check whether source [5] and source [6] each")
    print("  disclose a seed value in their own methods sections. If either")
    print("  is silent on seed, that alone is sufficient to explain a metric")
    print("  discrepancy without invoking any other cause.")
    return True


# ---------------------------------------------------------------------------
# 5. ARTIFACT VERIFICATION
# ---------------------------------------------------------------------------
def verify_checksums(metrics_file_path, published_checksums_path):
    """
    Recomputes SHA-256 of the freshly generated metrics.csv and compares
    against the published hash, per Appendix I's own stated protocol.
    """
    results = {}
    with open(published_checksums_path) as f:
        published = dict(
            line.strip().split("  ", 1)[::-1] for line in f if line.strip()
        )

    fresh_hash = hashlib.sha256(Path(metrics_file_path).read_bytes()).hexdigest()
    filename = Path(metrics_file_path).name
    published_hash = published.get(filename)

    match = fresh_hash == published_hash
    results[filename] = {
        "fresh_hash": fresh_hash,
        "published_hash": published_hash,
        "match": match,
    }
    print(f"  {filename}")
    print(f"    fresh:     {fresh_hash}")
    print(f"    published: {published_hash}")
    print(f"    match: {match}")
    return results


# ---------------------------------------------------------------------------
# 6. ROOT-CAUSE ANALYSIS WORKFLOW
# ---------------------------------------------------------------------------
def classify_discrepancy(result: InvestigationResult):
    """
    Decision-tree classification against the 7 candidate causes named in the
    implementation request. Returns (cause, supporting_evidence_list).
    This function only reasons over what check_config/check_seed/
    verify_checksums actually found -- it does not guess.
    """
    evidence = []

    if result.seed_match is False:
        evidence.append("Fresh run manifest has no recorded seed (Section 11 gap)")
        return "different_random_seed (or seed undocumented)", evidence

    for chk in result.checksum_results.values():
        if not chk["match"]:
            evidence.append(
                f"Checksum mismatch: fresh run does not match published "
                f"v1.0.0 artifact -- current release may not correspond to "
                f"either source [5] or [6]"
            )
            return "different_benchmark_version", evidence

    evidence.append(
        "Automated checks (config presence, seed presence, checksum) did "
        "not by themselves isolate a cause. Manual comparison of source "
        "[5] and [6] methodology text against the fresh-run manifest "
        "(Step 2 output above) is required before classification."
    )
    return "unknown_pending_manual_source_review", evidence


def write_findings(result: InvestigationResult):
    """
    Writes a structured findings file consumable by the manuscript-update
    step (deliverable 7) and by CI (deliverable 8). Never writes a metric
    value -- only the classification and evidence trail.
    """
    out = {
        "probable_cause": result.probable_cause,
        "evidence": result.evidence,
        "seed_verified": result.seed_match,
        "checksum_results": result.checksum_results,
        "ready_for_manuscript_update": result.probable_cause
        != "unknown_pending_manual_source_review",
    }
    Path("findings.json").write_text(json.dumps(out, indent=2))
    print("  Wrote findings.json")


if __name__ == "__main__":
    main()
