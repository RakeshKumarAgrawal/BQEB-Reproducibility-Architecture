#!/usr/bin/env python3
"""
classify_coverage.py

Parses coverage.py's JSON report (`coverage json`) and produces a
per-function breakdown split by the classification scheme in
classification_rules.py. This is the core tool -- it operates on any
coverage.json file, real or synthetic, and contains no ForecastBench-
specific data itself.

Usage:
    coverage run -m pytest
    coverage json -o coverage.json
    python classify_coverage.py --coverage-json coverage.json --out classified.json
"""

import argparse
import ast
import json
from pathlib import Path

from classification_rules import classify_function


def extract_function_line_ranges(source_path: Path) -> dict:
    """
    Parses a Python source file's AST to get each function's line range,
    so per-line coverage data can be attributed to a specific function
    rather than only to a file.
    """
    tree = ast.parse(source_path.read_text())
    ranges = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_line = getattr(node, "end_lineno", node.lineno)
            ranges[node.name] = (node.lineno, end_line)
    return ranges


def compute_function_coverage(
    file_path: str, executed_lines: set, missing_lines: set, source_root: Path
) -> list[dict]:
    full_path = source_root / file_path
    if not full_path.exists():
        return []

    func_ranges = extract_function_line_ranges(full_path)
    results = []
    for func_name, (start, end) in func_ranges.items():
        func_lines = set(range(start, end + 1))
        covered = func_lines & executed_lines
        total_statements = func_lines & (executed_lines | missing_lines)
        if not total_statements:
            continue

        coverage_pct = len(covered) / len(total_statements) * 100
        qualified_name = f"{Path(file_path).stem}.{func_name}"
        category = classify_function(qualified_name)

        results.append({
            "qualified_name": qualified_name,
            "file": file_path,
            "reproducibility_critical": category is not None,
            "category": category,
            "statements_total": len(total_statements),
            "statements_covered": len(covered),
            "coverage_pct": round(coverage_pct, 2),
        })
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage-json", required=True, type=Path)
    parser.add_argument("--source-root", type=Path, default=Path("."))
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    coverage_data = json.loads(args.coverage_json.read_text())
    all_functions = []

    for file_path, file_data in coverage_data["files"].items():
        executed = set(file_data["executed_lines"])
        missing = set(file_data["missing_lines"])
        all_functions.extend(
            compute_function_coverage(file_path, executed, missing, args.source_root)
        )

    critical = [f for f in all_functions if f["reproducibility_critical"]]
    general = [f for f in all_functions if not f["reproducibility_critical"]]

    def aggregate(funcs):
        total = sum(f["statements_total"] for f in funcs)
        covered = sum(f["statements_covered"] for f in funcs)
        return {
            "function_count": len(funcs),
            "statements_total": total,
            "statements_covered": covered,
            "coverage_pct": round(covered / total * 100, 2) if total else None,
        }

    report = {
        "aggregate_coverage_pct": coverage_data["totals"]["percent_covered"],
        "reproducibility_critical": aggregate(critical),
        "general": aggregate(general),
        "functions": all_functions,
    }

    args.out.write_text(json.dumps(report, indent=2))
    print(f"Aggregate coverage (whole suite): {report['aggregate_coverage_pct']}%")
    print(f"Reproducibility-critical coverage: {report['reproducibility_critical']['coverage_pct']}% "
          f"({report['reproducibility_critical']['function_count']} functions)")
    print(f"General-purpose coverage: {report['general']['coverage_pct']}% "
          f"({report['general']['function_count']} functions)")
    print(f"Written to {args.out}")


if __name__ == "__main__":
    main()
