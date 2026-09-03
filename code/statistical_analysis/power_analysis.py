#!/usr/bin/env python3
"""
power_analysis.py

Added directly in response to a real finding from the synthetic
demonstration run: at n=200 paired observations with 6-way Holm-Bonferroni
correction, a medium raw effect size (d=0.5) shrinks to d~0.25 after the
|residual| transformation the comparison operates on, landing right at the
power boundary. This script lets the actual experiment be sized correctly
BEFORE running on real ForecastBench residuals, rather than discovering
inadequate power after the fact, as the demonstration run did.
"""

import argparse
from scipy.stats import norm


def required_n(effect_size_d: float, alpha: float, power: float = 0.8) -> int:
    z_alpha = norm.isf(alpha / 2)
    z_beta = norm.isf(1 - power)
    n = ((z_alpha + z_beta) / effect_size_d) ** 2
    return int(-(-n // 1))  # ceiling


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--effect-size", type=float, default=0.25,
                         help="Expected Cohen's d on the |residual| difference "
                              "(default 0.25, matching what the synthetic "
                              "demonstration actually produced from a raw d=0.5)")
    parser.add_argument("--num-comparisons", type=int, default=6,
                         help="Number of comparisons in the Holm-Bonferroni family")
    parser.add_argument("--power", type=float, default=0.8)
    args = parser.parse_args()

    alpha_worst_case = 0.05 / args.num_comparisons  # Bonferroni bound, the
    # conservative worst case within Holm's procedure -- true Holm power is
    # slightly higher, but this bound is the safe planning number.
    n = required_n(args.effect_size, alpha_worst_case, args.power)

    print(f"Target effect size (Cohen's d): {args.effect_size}")
    print(f"Comparisons in family: {args.num_comparisons}")
    print(f"Worst-case corrected alpha: {alpha_worst_case:.5f}")
    print(f"Target power: {args.power}")
    print(f"Required paired observations per comparison: {n}")
    print()
    print("Compare this against the actual test-set size the chronological")
    print("70/15/15 split produces (Section 9) before treating a")
    print("non-significant result as evidence of no difference, rather than")
    print("evidence of inadequate power.")


if __name__ == "__main__":
    main()
