#!/usr/bin/env python3
"""
statistical_comparison.py

Implements the paired statistical comparison protocol Section 15 of the
manuscript commits to but does not name a specific test for. Test choice
(paired t-test vs. Wilcoxon signed-rank) is decided per-comparison via a
normality check on the residual differences, not fixed in advance -- the
manuscript's own residuals may or may not be normally distributed, and this
should not be assumed either way.

This script does NOT contain ForecastBench's actual residuals. It operates
on whatever two paired residual arrays it is given; the demonstration run
at the bottom of this file uses clearly-synthetic data for validation only.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
from scipy import stats


ALPHA = 0.05


@dataclass
class PairwiseTestResult:
    model_a: str
    model_b: str
    task: str
    n_paired_observations: int
    normality_p_value: float
    test_used: str
    test_statistic: float
    p_value_raw: float
    p_value_corrected: float | None
    effect_size_name: str
    effect_size_value: float
    ci_lower: float | None = None  # MISSING COMPONENT, now added
    ci_upper: float | None = None  # MISSING COMPONENT, now added
    ci_method: str | None = None   # MISSING COMPONENT, now added
    significant_at_alpha: bool | None = None  # set after correction is applied


def check_normality(differences: np.ndarray) -> float:
    """Shapiro-Wilk on the paired differences (not the raw residuals) --
    this is what the paired t-test's assumption actually requires."""
    if len(differences) < 3:
        raise ValueError("Shapiro-Wilk requires at least 3 observations")
    _, p_value = stats.shapiro(differences)
    return p_value


def rank_biserial_correlation(differences: np.ndarray) -> float:
    """Effect size for Wilcoxon signed-rank: r = Z / sqrt(N)."""
    n = len(differences)
    _, p = stats.wilcoxon(differences)
    # Recover Z from the p-value's implied standard normal quantile,
    # consistent with how scipy's wilcoxon does not directly expose Z.
    z = stats.norm.isf(p / 2) * np.sign(np.sum(differences))
    return float(z / np.sqrt(n))


def cohens_d_paired(differences: np.ndarray) -> float:
    return float(np.mean(differences) / np.std(differences, ddof=1))


def bootstrap_ci_mean_difference(differences: np.ndarray, confidence: float = 0.95) -> tuple[float, float]:
    """MISSING COMPONENT, now implemented: bootstrap CI on the mean paired
    difference. Chosen over a parametric CI formula specifically because it
    works identically regardless of whether the t-test or Wilcoxon path was
    taken -- one CI method, not two different derivations to keep in sync."""
    res = stats.bootstrap(
        (differences,), np.mean, confidence_level=confidence,
        n_resamples=10000, method="BCa", random_state=42,
    )
    return float(res.confidence_interval.low), float(res.confidence_interval.high)


def compare_pair(
    model_a: str,
    model_b: str,
    task: str,
    residuals_a: np.ndarray,
    residuals_b: np.ndarray,
) -> PairwiseTestResult:
    if len(residuals_a) != len(residuals_b):
        raise ValueError(
            f"Paired comparison requires equal-length arrays: "
            f"{len(residuals_a)} vs {len(residuals_b)}"
        )

    differences = np.abs(residuals_a) - np.abs(residuals_b)
    normality_p = check_normality(differences)
    ci_lower, ci_upper = bootstrap_ci_mean_difference(differences)

    if normality_p > ALPHA:
        # Differences are consistent with normality -- use the parametric test.
        stat, p_raw = stats.ttest_rel(np.abs(residuals_a), np.abs(residuals_b))
        test_used = "paired_t_test"
        effect_name = "cohens_d"
        effect_value = cohens_d_paired(differences)
    else:
        # Differences deviate from normality -- use the non-parametric test.
        stat, p_raw = stats.wilcoxon(differences)
        test_used = "wilcoxon_signed_rank"
        effect_name = "rank_biserial_r"
        effect_value = rank_biserial_correlation(differences)

    return PairwiseTestResult(
        model_a=model_a,
        model_b=model_b,
        task=task,
        n_paired_observations=len(differences),
        normality_p_value=float(normality_p),
        test_used=test_used,
        test_statistic=float(stat),
        p_value_raw=float(p_raw),
        p_value_corrected=None,  # filled in by apply_correction()
        effect_size_name=effect_name,
        effect_size_value=effect_value,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        ci_method="bootstrap_BCa_95pct_n10000",
        significant_at_alpha=None,
    )


def apply_holm_bonferroni(results: list[PairwiseTestResult]) -> list[PairwiseTestResult]:
    """Holm-Bonferroni correction across the full family of comparisons
    performed in one analysis -- all 6 (3 model pairs x 2 tasks) corrected
    together, the conservative choice, since all 6 test the same underlying
    question (which model is best) rather than unrelated hypotheses."""
    raw_p = [r.p_value_raw for r in results]
    order = np.argsort(raw_p)
    m = len(raw_p)

    corrected = [None] * m
    running_max = 0.0
    for rank, idx in enumerate(order):
        adj = (m - rank) * raw_p[idx]
        running_max = max(running_max, adj)
        corrected[idx] = min(running_max, 1.0)

    for r, p_corr in zip(results, corrected):
        r.p_value_corrected = float(p_corr)
        r.significant_at_alpha = p_corr < ALPHA

    return results


def run_full_comparison(residuals: dict) -> list[PairwiseTestResult]:
    """
    residuals: {task: {model_name: np.ndarray of per-instance residuals}}
    """
    models = list(next(iter(residuals.values())).keys())
    pairs = [(models[i], models[j]) for i in range(len(models)) for j in range(i + 1, len(models))]

    results = []
    for task, model_residuals in residuals.items():
        for model_a, model_b in pairs:
            results.append(
                compare_pair(
                    model_a, model_b, task,
                    model_residuals[model_a], model_residuals[model_b],
                )
            )

    return apply_holm_bonferroni(results)


def load_residuals_from_csv(path: Path) -> dict:
    """
    MISSING COMPONENT, now implemented: real file-based input. Previously
    there was no way to feed real residual data into this tool without
    hand-writing a Python dict -- a genuine practical gap once real
    residuals actually exist.

    Expected CSV columns: task, model, residual (long format, one row per
    prediction). Returns the {task: {model: np.ndarray}} structure
    run_full_comparison() requires.
    """
    import csv
    from collections import defaultdict

    data = defaultdict(lambda: defaultdict(list))
    with open(path) as f:
        reader = csv.DictReader(f)
        required_cols = {"task", "model", "residual"}
        if not required_cols.issubset(reader.fieldnames or []):
            raise ValueError(
                f"CSV must have columns {required_cols}, got {reader.fieldnames}"
            )
        for row in reader:
            data[row["task"]][row["model"]].append(float(row["residual"]))

    return {
        task: {model: np.array(vals) for model, vals in models.items()}
        for task, models in data.items()
    }


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Run paired statistical comparison on real residual data "
                     "from a CSV file (columns: task, model, residual)."
    )
    parser.add_argument("--residuals-csv", type=Path,
                         help="Path to a real residuals CSV. If omitted, "
                              "prints usage instead of running against "
                              "invented data.")
    parser.add_argument("--out", type=Path, default=Path("results.json"))
    args = parser.parse_args()

    if args.residuals_csv is None:
        print(
            "No --residuals-csv provided. This tool requires real residual "
            "data -- see demonstrate_on_synthetic_data.py for a validation "
            "example using clearly-synthetic data, not real results.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not args.residuals_csv.exists():
        print(f"ERROR: {args.residuals_csv} not found.", file=sys.stderr)
        sys.exit(2)

    residuals = load_residuals_from_csv(args.residuals_csv)
    results = run_full_comparison(residuals)
    args.out.write_text(json.dumps([asdict(r) for r in results], indent=2))
    print(f"Wrote {len(results)} comparison results to {args.out}")
