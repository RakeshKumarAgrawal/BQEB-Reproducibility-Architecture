#!/usr/bin/env python3
"""
generate_statistical_report.py

MISSING COMPONENT, now implemented: formatted reporting layer on top of
statistical_comparison.py's existing, unmodified test logic -- same
pattern as BL-04's generate_verification_report.py.
"""

import argparse
import json
from pathlib import Path


def render_report(results: list[dict]) -> str:
    lines = ["# Statistical Comparison Report", ""]
    lines += ["| Task | Model A | Model B | Test | n | Effect size | 95% CI | Raw p | Corrected p | Significant? |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        ci = f"[{r['ci_lower']:.3f}, {r['ci_upper']:.3f}]" if r.get("ci_lower") is not None else "N/A"
        lines.append(
            f"| {r['task']} | {r['model_a']} | {r['model_b']} | {r['test_used']} | "
            f"{r['n_paired_observations']} | {r['effect_size_value']:.3f} ({r['effect_size_name']}) | "
            f"{ci} | {r['p_value_raw']:.4f} | {r['p_value_corrected']:.4f} | "
            f"{'YES' if r['significant_at_alpha'] else 'no'} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-json", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    results = json.loads(args.results_json.read_text())
    args.out.write_text(render_report(results))
    print(f"Report written to {args.out}")


if __name__ == "__main__":
    main()
