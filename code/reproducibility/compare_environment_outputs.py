#!/usr/bin/env python3
"""
compare_environment_outputs.py

Verification protocol implementation: compares result hashes across any
number of output files (same-environment repeats, or genuinely different
environments once available). Reports MATCH/MISMATCH and surfaces the
environment fingerprint differences when a mismatch occurs, so a mismatch
can be attributed rather than just detected.
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("outputs", nargs="+", type=Path,
                         help="Two or more output JSON files to compare")
    args = parser.parse_args()

    if len(args.outputs) < 2:
        print("Need at least 2 output files to compare.", file=sys.stderr)
        sys.exit(2)

    records = []
    for path in args.outputs:
        data = json.loads(path.read_text())
        records.append((path, data))

    reference_hash = records[0][1]["result_hash_sha256"]
    all_match = True

    print(f"Reference: {records[0][0]} (hash={reference_hash})")
    for path, data in records[1:]:
        h = data["result_hash_sha256"]
        match = h == reference_hash
        all_match &= match
        print(f"{'MATCH' if match else 'MISMATCH'}: {path} (hash={h})")
        if not match:
            print("  Environment fingerprint comparison:")
            ref_env = records[0][1]["environment"]
            this_env = data["environment"]
            for key in ref_env:
                if ref_env[key] != this_env.get(key):
                    print(f"    {key}: reference={ref_env[key]!r} vs this={this_env.get(key)!r}")

    print()
    print("ALL MATCH" if all_match else "MISMATCH DETECTED")
    sys.exit(0 if all_match else 1)


if __name__ == "__main__":
    main()
