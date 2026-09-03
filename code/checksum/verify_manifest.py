#!/usr/bin/env python3
"""
verify_manifest.py

Verification workflow: recomputes SHA-256 for every file listed in a
manifest and reports MATCH / MISMATCH / MISSING per file. Exit code is
non-zero if any file fails, so this composes directly into CI or the
experimental protocol's automated test cases.

Usage:
    python verify_manifest.py --manifest manifests/v1.0.0_software_outputs.json --root artifacts/
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

CHUNK_SIZE = 1024 * 1024


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()


def verify(manifest_path: Path, root: Path) -> dict:
    manifest = json.loads(manifest_path.read_text())
    results = {"MATCH": [], "MISMATCH": [], "MISSING": []}

    for entry in manifest["entries"]:
        file_path = root / entry["path"]
        if not file_path.exists():
            results["MISSING"].append(entry["path"])
            continue

        actual_hash = sha256_of_file(file_path)
        if actual_hash == entry["sha256"]:
            results["MATCH"].append(entry["path"])
        else:
            results["MISMATCH"].append({
                "path": entry["path"],
                "expected": entry["sha256"],
                "actual": actual_hash,
            })

    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json-out", type=Path, default=None,
                         help="Optional path to write machine-readable results")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"ERROR: manifest {args.manifest} not found.", file=sys.stderr)
        sys.exit(2)

    results = verify(args.manifest, args.root)

    print(f"MATCH:    {len(results['MATCH'])}")
    print(f"MISMATCH: {len(results['MISMATCH'])}")
    print(f"MISSING:  {len(results['MISSING'])}")

    if results["MISMATCH"]:
        print("\nMismatched files (expected failure behavior: HALT dependent process):")
        for m in results["MISMATCH"]:
            print(f"  {m['path']}")
            print(f"    expected: {m['expected']}")
            print(f"    actual:   {m['actual']}")

    if results["MISSING"]:
        print("\nMissing files:")
        for m in results["MISSING"]:
            print(f"  {m}")

    if args.json_out:
        args.json_out.write_text(json.dumps(results, indent=2))

    # Non-zero exit on ANY mismatch or missing file -- verification failure
    # halts the dependent process rather than warning and continuing,
    # consistent with the "expected failure behavior" specified in the
    # artifact-integrity review.
    sys.exit(1 if (results["MISMATCH"] or results["MISSING"]) else 0)


if __name__ == "__main__":
    main()
