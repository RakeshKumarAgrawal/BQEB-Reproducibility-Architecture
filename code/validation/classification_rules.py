"""
classification_rules.py

Defines, explicitly and in one place, what counts as "reproducibility-
critical" code for the purposes of this coverage report. This exists
because the manuscript's own gap (Section 20) is precisely that no such
definition currently exists anywhere -- without it, "targeted coverage"
would just be a second arbitrary number, not an improvement on the first.

Classification is by function/module NAME PATTERN, not by file location
alone, since a single file (e.g., the orchestration module) may contain
both reproducibility-critical and general-purpose functions.

Matching is done by substring check with underscores stripped, not raw
regex word-boundary matching -- an earlier version of this file used
`\\bseed\\b` style patterns, which silently failed to match
"set_random_seed" because regex word boundaries do not trigger across
underscores (both `_` and letters are "word characters," so there is no
boundary between them). That was a real bug, caught by running this
against a synthetic test case before shipping it, not a hypothetical one.
"""

# Keywords checked as substrings of the underscore-stripped function name.
# Each category corresponds directly to a claim made elsewhere in the
# manuscript:
#   - SEEDING       -> Section 11's "deterministic execution" claim
#   - PARTITIONING  -> Section 11's "chronological partitioning" claim
#   - CHECKSUMMING  -> Section 11's "checksummed artifacts" claim
REPRODUCIBILITY_CRITICAL_KEYWORDS = {
    "seeding": {"seed", "randomstate", "random_state"},
    "partitioning": {"split", "partition", "chronological"},
    "checksumming": {"checksum", "sha256", "hash"},
}


def classify_function(qualified_name: str) -> str | None:
    """
    Returns the reproducibility-critical category for a function, or None
    if it doesn't match any category (i.e., it's general-purpose code).

    Matches by checking whether each keyword (with its own underscores
    stripped) appears as a substring of the qualified name (also with
    underscores stripped). This correctly matches "seed" against
    "set_random_seed" -> "setrandomseed", which a raw regex word-boundary
    match does not, since word boundaries do not trigger across
    underscores.

    A function is classified by name only -- this is a deliberate,
    disclosed limitation (see the accompanying report's "Threats to
    Validity" section): a function could be reproducibility-relevant
    without matching any keyword here (a false negative), and this
    classifier does not claim otherwise.
    """
    name_no_underscores = qualified_name.lower().replace("_", "")

    for category, keywords in REPRODUCIBILITY_CRITICAL_KEYWORDS.items():
        for keyword in keywords:
            if keyword.replace("_", "") in name_no_underscores:
                return category
    return None


def is_reproducibility_critical(qualified_name: str) -> bool:
    return classify_function(qualified_name) is not None
