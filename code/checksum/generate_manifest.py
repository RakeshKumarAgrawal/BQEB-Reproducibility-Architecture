#!/usr/bin/env python3
"""
generate_manifest.py

Hashing workflow: computes SHA-256 for every artifact in a specified scope
and writes a manifest file. Extends the manuscript's currently-documented
6-file coverage (Appendix B) to the full artifact inventory identified in
the artifact-integrity review.

Usage:
    python generate_manifest.py --scope software-outputs --root artifacts/ \
        --out manifests/v1.0.0_software_outputs.sha256
    python generate_manifest.py --scope dataset --root data/ \
        --out manifests/v1_dataset.sha256
    python generate_manifest.py --scope registry-entry --root registry/secbench/ \
        --out manifests/secbench_registry_entry.sha256
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CHUNK_SIZE = 1024 * 1024  # 1 MB, avoids loading large files fully into memory

# Scopes map directly to the artifact-integrity review's inventory rows.
# Each scope's file pattern is explicit -- nothing here silently expands to
# "everything in the directory," to avoid accidentally hashing files that
# were never part of the manuscript's integrity claims.
SCOPES = {
    "software-outputs": ["predictions.csv", "metrics.csv", "model_comparison.csv",
                          "experiment_manifest.json", "*.split.csv"],
    "dataset": ["*.csv"],
    "release-tarball": ["*.tar.gz", "*.zip"],
    "registry-entry": ["*.yaml", "*.yml", "*.json"],
    "benchmark-card": ["*.json", "*.yaml"],
    # Added during real BL-04 execution: none of the 5 original scopes match
    # anything in the actual Paper 1 repository (confirmed empirically --
    # all 5 hashed 0 files against it). Those scopes target ForecastBench's
    # experimental data outputs, which don't exist because no real
    # ForecastBench run has occurred. This scope covers what the Paper 1
    # repository actually, currently contains: engineering source and docs.
    "engineering-artifacts": ["*.py", "*.md"],
}


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()


def collect_files(root: Path, patterns: list[str]) -> list[Path]:
    files = []
    for pattern in patterns:
        files.extend(sorted(root.rglob(pattern)))
    # De-duplicate while preserving order (a file could match >1 pattern)
    seen = set()
    unique = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def generate_manifest(scope: str, root: Path, out: Path) -> dict:
    if scope not in SCOPES:
        raise ValueError(f"Unknown scope '{scope}'. Valid scopes: {list(SCOPES)}")

    files = collect_files(root, SCOPES[scope])
    entries = []
    for f in files:
        entries.append({
            "path": str(f.relative_to(root)),
            "sha256": sha256_of_file(f),
            "size_bytes": f.stat().st_size,
        })

    manifest = {
        "scope": scope,
        "root": str(root),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(entries),
        "entries": entries,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2))

    # Also emit a plain sha256sum-compatible file alongside the JSON, so
    # `sha256sum -c` works directly without requiring this script.
    plain_path = out.with_suffix(".sha256")
    with open(plain_path, "w") as f:
        for entry in entries:
            f.write(f"{entry['sha256']}  {entry['path']}\n")

    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True, choices=list(SCOPES))
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    if not args.root.exists():
        print(f"ERROR: root path {args.root} does not exist.", file=sys.stderr)
        sys.exit(1)

    manifest = generate_manifest(args.scope, args.root, args.out)
    print(f"Hashed {manifest['file_count']} file(s) under scope '{args.scope}'")
    print(f"Manifest written to {args.out}")
    print(f"Plain checksums written to {args.out.with_suffix('.sha256')}")


if __name__ == "__main__":
    main()
