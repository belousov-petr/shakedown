"""
README/SKILL.md parity check.

Catches drift between the marketing surface (README.md) and the agent
spec (SKILL.md). Flags features promised in one but absent in the
other.

Why this exists: the v1.0.0 review found that README promised a
"fix them all" interactive flow that SKILL.md did not implement.
This script catches that class of drift before it ships again.

Usage:
    python scripts/parity-check.py
    python scripts/parity-check.py --strict  # exit non-zero on any drift

Exits:
    0 - parity OK (no drift)
    1 - drift detected (in --strict mode)
    2 - input error (missing file)

Stdlib only. Python 3.8+.
"""

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"
SKILL_PATH = REPO_ROOT / "SKILL.md"

# Tokens that name a user-visible feature, follow-up handler, phase, or
# named output section. Matched case-insensitively as a whole phrase.
# Add a token here when you ship a new handler / section / mode.
FEATURE_TOKENS = [
    # Delivery modes (Phase 1f)
    "Inline mode",
    "File mode",
    # Phase 7 follow-up handlers
    "Fix them all",
    "Fix selected",
    "Re-run Phase 5",
    "Compare with",
    "Create GitHub issues",
    # Major report sections
    "Production Readiness",
    "Top 10 Ranked Recommendations",
    "Uncomfortable Question",
    "Value Assessment",
    "Skill Standards",
    "Storage Efficiency",
    "Goal Fulfillment",
    "Blind Spots",
    "Objective Clarity",
    "Resilience Testing",
    "Data Store Diagnostics",
    "Architecture & Code Quality",
    "Error Handling",
    "Performance & Bottleneck",
    "Logging & Observability",
    "Documentation Quality",
    # Phases (the agent must know the phase exists)
    "Phase 1",
    "Phase 2",
    "Phase 3",
    "Phase 4",
    "Phase 5",
    "Phase 6",
    "Phase 7",
]


def normalize(text: str) -> str:
    """Lowercase, collapse whitespace - tolerant matching."""
    return re.sub(r"\s+", " ", text.lower())


def find_token(text_norm: str, token: str) -> bool:
    """Whole-phrase match, case-insensitive, whitespace-tolerant."""
    needle = normalize(token)
    return needle in text_norm


def check_parity(readme_text: str, skill_text: str) -> tuple[list, list, list]:
    """
    Returns (in_both, in_readme_only, in_skill_only).

    in_readme_only = promised in README, missing from SKILL.md
        -> drift hazard: agent doesn't know about a marketed feature
    in_skill_only = present in SKILL.md, missing from README
        -> documentation gap: users won't know the feature exists
    """
    readme_norm = normalize(readme_text)
    skill_norm = normalize(skill_text)

    in_both = []
    in_readme_only = []
    in_skill_only = []

    for token in FEATURE_TOKENS:
        in_readme = find_token(readme_norm, token)
        in_skill = find_token(skill_norm, token)
        if in_readme and in_skill:
            in_both.append(token)
        elif in_readme:
            in_readme_only.append(token)
        elif in_skill:
            in_skill_only.append(token)

    return in_both, in_readme_only, in_skill_only


def report(in_both: list, in_readme_only: list, in_skill_only: list) -> None:
    total = len(in_both) + len(in_readme_only) + len(in_skill_only)

    print(f"Parity check: {len(in_both)}/{total} tokens present in both files\n")

    if in_readme_only:
        print(
            f"[FAIL] {len(in_readme_only)} feature(s) in README.md but NOT in SKILL.md"
            " - agent does not know they exist:"
        )
        for t in in_readme_only:
            print(f"  - {t}")
        print()

    if in_skill_only:
        print(
            f"[WARN] {len(in_skill_only)} feature(s) in SKILL.md but NOT in README.md"
            " - users will not know they exist:"
        )
        for t in in_skill_only:
            print(f"  - {t}")
        print()

    if not in_readme_only and not in_skill_only:
        print("[PASS] No drift detected.")


def main() -> int:
    strict = "--strict" in sys.argv

    if not README_PATH.exists():
        print(f"[ERROR] {README_PATH} not found", file=sys.stderr)
        return 2
    if not SKILL_PATH.exists():
        print(f"[ERROR] {SKILL_PATH} not found", file=sys.stderr)
        return 2

    readme_text = README_PATH.read_text(encoding="utf-8")
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    in_both, in_readme_only, in_skill_only = check_parity(readme_text, skill_text)
    report(in_both, in_readme_only, in_skill_only)

    if strict and (in_readme_only or in_skill_only):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
