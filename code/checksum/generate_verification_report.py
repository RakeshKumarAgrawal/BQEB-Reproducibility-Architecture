#!/usr/bin/env python3
"""
generate_verification_report.py

MISSING COMPONENT, now implemented: a formatted, human-readable report,
distinct from verify_manifest.py's existing console output and raw
--json-out dump. Takes verify_manifest.py's JSON output (unchanged,
existing format) and renders it as a Markdown report suitable for
inclusion as supplementary evidence -- does not re-implement any
verification logic, purely a reporting layer on top of already-tested code.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def render_report(results: dict, manifest_name: str) -> str:
    total = len(results["MATCH"]) + len(results["MISMATCH"]) + len(results["MISSING"])
    status = "PASS" if not results["MISMATCH"] and not results["MISSING"] else "FAIL"

    lines = [
        f"# Artifact Verification Report",
        "",
        f"**Manifest:** {manifest_name}",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"**Overall status:** {status}",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|---|---|",
        f"| Total files checked | {total} |",
        f"| Matched | {len(results['MATCH'])} |",
        f"| Mismatched (corrupted) | {len(results['MISMATCH'])} |",
        f"| Missing | {len(results['MISSING'])} |",
        "",
    ]

    if results["MISMATCH"]:
        lines += ["## Mismatched Files", ""]
        for m in results["MISMATCH"]:
            lines += [
                f"- `{m['path']}`",
                f"  - expected: `{m['expected']}`",
                f"  - actual: `{m['actual']}`",
            ]
        lines.append("")

    if results["MISSING"]:
        lines += ["## Missing Files", ""]
        for m in results["MISSING"]:
            lines.append(f"- `{m}`")
        lines.append("")

    if status == "PASS":
        lines += ["## Result", "", "All artifacts verified against the manifest. No corruption or missing files detected."]
    else:
        lines += ["## Result", "", "**Verification FAILED.** See mismatched/missing files above. Per the established failure-behavior standard, any dependent process consuming these artifacts should halt, not proceed with a warning."]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verification-json", required=True, type=Path,
                         help="Output of verify_manifest.py --json-out")
    parser.add_argument("--manifest-name", required=True,
                         help="Label for the manifest being reported on")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    if not args.verification_json.exists():
        print(f"ERROR: {args.verification_json} not found. Run verify_manifest.py "
              f"with --json-out first -- this script formats existing results, "
              f"it does not run verification itself.")
        raise SystemExit(2)

    results = json.loads(args.verification_json.read_text())
    report = render_report(results, args.manifest_name)
    args.out.write_text(report)
    print(f"Report written to {args.out}")


if __name__ == "__main__":
    main()
