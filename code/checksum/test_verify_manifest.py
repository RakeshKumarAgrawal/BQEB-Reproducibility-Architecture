"""
test_verify_manifest.py

Formal pytest suite for verify_manifest.py, chosen as the representative
first test file because its pass/fail contract is the clearest of the six
tools. Exercises the exact scenarios already manually verified in prior
work (clean pass, corruption detection, missing-file detection) as real,
repeatable, CI-discoverable tests instead of one-off bash_tool runs.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from verify_manifest import verify, sha256_of_file


@pytest.fixture
def artifact_dir(tmp_path):
    d = tmp_path / "artifacts"
    d.mkdir()
    (d / "predictions.csv").write_text("real content A")
    (d / "metrics.csv").write_text("real content B")
    return d


@pytest.fixture
def manifest(tmp_path, artifact_dir):
    entries = []
    for f in sorted(artifact_dir.iterdir()):
        entries.append({"path": f.name, "sha256": sha256_of_file(f)})
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"entries": entries}))
    return manifest_path


def test_clean_verification_passes(manifest, artifact_dir):
    results = verify(manifest, artifact_dir)
    assert len(results["MATCH"]) == 2
    assert len(results["MISMATCH"]) == 0
    assert len(results["MISSING"]) == 0


def test_corrupted_file_detected(manifest, artifact_dir):
    (artifact_dir / "predictions.csv").write_text("TAMPERED")
    results = verify(manifest, artifact_dir)
    assert len(results["MATCH"]) == 1
    assert len(results["MISMATCH"]) == 1
    assert results["MISMATCH"][0]["path"] == "predictions.csv"


def test_missing_file_detected(manifest, artifact_dir):
    (artifact_dir / "metrics.csv").unlink()
    results = verify(manifest, artifact_dir)
    assert len(results["MATCH"]) == 1
    assert len(results["MISSING"]) == 1
    assert results["MISSING"][0] == "metrics.csv"


def test_both_corruption_and_missing_detected_together(manifest, artifact_dir):
    (artifact_dir / "predictions.csv").write_text("TAMPERED")
    (artifact_dir / "metrics.csv").unlink()
    results = verify(manifest, artifact_dir)
    assert len(results["MATCH"]) == 0
    assert len(results["MISMATCH"]) == 1
    assert len(results["MISSING"]) == 1
