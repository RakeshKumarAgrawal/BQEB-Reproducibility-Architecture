#!/usr/bin/env python3
"""
deterministic_computation.py

A representative deterministic computation, seeded exactly per the
manuscript's Section 11 pattern ("all stochastic components... are seeded,
with the value used documented alongside each release"). This script exists
to be run repeatedly (same environment, then across environments) so that
its output hash becomes the object of comparison for the reproducibility
experiment.

This is NOT a reproduction of ForecastBench's actual model code (I don't
have access to it) -- it's new, illustrative infrastructure that exercises
the same class of stochastic operations (random split, model fit, seeded
prediction) that a real forecasting pipeline would.
"""

import argparse
import hashlib
import json
import os
import platform
import random
import sys
from datetime import datetime, timezone

import numpy as np


def run_deterministic_pipeline(seed: int) -> dict:
    random.seed(seed)
    np.random.seed(seed)

    # Representative stochastic operations: synthetic feature generation,
    # a random split, and a small computation -- standing in for the class
    # of operations a real forecasting benchmark performs, without claiming
    # to be that benchmark's actual code.
    n_samples = 1000
    X = np.random.rand(n_samples, 5)
    y = X @ np.array([1.5, -2.0, 0.5, 3.0, -1.0]) + np.random.normal(0, 0.1, n_samples)

    indices = list(range(n_samples))
    random.shuffle(indices)
    split_point = int(n_samples * 0.7)
    train_idx, test_idx = indices[:split_point], indices[split_point:]

    coeffs = np.linalg.lstsq(X[train_idx], y[train_idx], rcond=None)[0]
    predictions = X[test_idx] @ coeffs
    mae = float(np.mean(np.abs(predictions - y[test_idx])))

    output = {
        "seed": seed,
        "coefficients": coeffs.tolist(),
        "mae": mae,
        "train_indices_first_10": train_idx[:10],
        "test_indices_first_10": test_idx[:10],
    }
    return output


def environment_fingerprint() -> dict:
    """Records what actually varies across environments, so a future
    cross-machine comparison can distinguish 'output differs' from
    'here is what was different about the environment that produced it'."""
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "numpy_version": np.__version__,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED", "NOT_SET"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="results/output.json")
    args = parser.parse_args()

    output = run_deterministic_pipeline(args.seed)
    output["environment"] = environment_fingerprint()
    output["generated_at_utc"] = datetime.now(timezone.utc).isoformat()

    # The output hash excludes the timestamp and environment fingerprint --
    # those are expected to vary (or at least the timestamp always will);
    # what must NOT vary is the computed result itself.
    result_only = {k: v for k, v in output.items()
                    if k not in ("environment", "generated_at_utc")}
    output["result_hash_sha256"] = hashlib.sha256(
        json.dumps(result_only, sort_keys=True).encode()
    ).hexdigest()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(output, f, indent=2)

    print(f"seed={args.seed} result_hash={output['result_hash_sha256']}")
    print(f"Written to {args.out}")


if __name__ == "__main__":
    main()
