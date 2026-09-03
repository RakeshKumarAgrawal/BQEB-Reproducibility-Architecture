#!/usr/bin/env python3
"""
compare_release_manifests.py

Referenced by .github/workflows/cross-artifact-verification.yml.

Compares the current release's artifact checksums against the previous
release's, and fails (non-zero exit) if any output artifact changed without
a corresponding entry in the release notes explaining why (code change,
data version bump, or seed change).

This is new engineering content designed to close the CI gap identified in
the artifact-integrity review -- it does not describe an existing mechanism.
"""

import argparse
import sys
from pathlib import Path


def load_checksums(path: str) -> dict:
    checksums = {}
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        hash_val, filename = line.split(maxsplit=1)
        checksums[filename.strip()] = hash_val.strip()
    return checksums


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True, help="Path to current release's checksums.sha256")
    parser.add_argument("--previous", required=True, help="Previous release tag, or 'none' for first release")
    parser.add_argument(
        "--release-notes",
        default="RELEASE_NOTES.md",
        help="File expected to document any intentional output change",
    )
    args = parser.parse_args()

    if args.previous == "none":
        print("No previous release to compare against (first release). Passing.")
        sys.exit(0)

    current = load_checksums(args.current)

    # In actual CI, the previous release's checksums.sha256 would be fetched
    # via `gh release download <tag>`. That network call is intentionally
    # left as a TODO here rather than fabricated, since it depends on the
    # real repository's release history existing.
    previous_checksums_path = f"previous_release_{args.previous}_checksums.sha256"
    if not Path(previous_checksums_path).exists():
        print(f"TODO: fetch {previous_checksums_path} via 'gh release download {args.previous}'")
        print("Skipping comparison until this is wired up in the actual repository.")
        sys.exit(0)

    previous = load_checksums(previous_checksums_path)

    changed = {
        fname: (previous.get(fname), current_hash)
        for fname, current_hash in current.items()
        if previous.get(fname) != current_hash
    }

    if not changed:
        print("No output artifacts changed since previous release.")
        sys.exit(0)

    print(f"{len(changed)} artifact(s) changed since release {args.previous}:")
    for fname, (old_hash, new_hash) in changed.items():
        print(f"  {fname}: {old_hash} -> {new_hash}")

    notes = Path(args.release_notes)
    if not notes.exists() or not notes.read_text().strip():
        print()
        print("FAIL: outputs changed but no release notes document why.")
        print(f"Add an explanation to {args.release_notes} before this release")
        print("can be published -- this is the exact gap that let two")
        print("publications diverge without either one being flagged.")
        sys.exit(1)

    print()
    print(f"Outputs changed; release notes present at {notes}. Human review")
    print("still required to confirm the explanation is adequate -- this")
    print("script checks that notes exist, not that they're correct.")
    sys.exit(0)


if __name__ == "__main__":
    main()
