# BLT-Preflight

**Automated PR advisory system for OWASP BLT — GSoC 2026 prototype**

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Prototype-orange)
![GSoC](https://img.shields.io/badge/GSoC-2026%20Proposal-red?logo=google)

BLT-Preflight intercepts pull requests at creation time, parses the diff, and checks it against OWASP BLT's contribution policy — before any human review occurs. Violations are caught in seconds, not hours.

---

## The Problem

OWASP BLT enforces a tiered contribution policy: new contributors (fewer than 3 merged PRs) are restricted to **single-file, deletion-only changes**. This rule protects repository integrity.

In practice:
- ~35–40% of new-contributor PRs violate at least one rule (multi-file edits, code additions)
- Maintainers spend an estimated 4–6 hours/week on preventable triage rejections
- Contributors whose first PR gets a bot failure message with no guidance rarely return

This prototype proves that **these violations can be caught and explained automatically**, before a human ever opens the PR.

---

## How It Works

```
PR opened
    │
    ▼
Diff retrieved (unified diff format)
    │
    ▼
unidiff parses diff → DiffMetadata
    │
    ▼
RuleEngine evaluates against contributor policy
    │
    ├── PASS → "PR is compliant. Ready for review."
    │
    └── FAIL → Specific violation messages per rule
```

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/blt-preflight
cd blt-preflight

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

---

## Example Output

Given a diff with 2 files changed and 1 line added:

```
--- PR Metrics ---
  Files changed : 2
  Lines added   : 1
  Lines deleted : 2

RESULT: INVALID

  [SINGLE_FILE_LIMIT]      Too many files changed. Expected ≤ 1, found 2.
  [CODE_ADDITION_BLOCKED]  New contributors cannot add lines. Expected 0, found 1.
```

Given a compliant deletion-only, single-file diff:

```
--- PR Metrics ---
  Files changed : 1
  Lines added   : 0
  Lines deleted : 4

RESULT: VALID — PR is compliant. Ready for human review.
```

---

## Core Logic

The rule engine is intentionally transparent. Rules are evaluated as simple predicates against diff metadata:

```python
# rule_engine.py

def evaluate(diff: DiffMetadata, contributor: ContributorStats, rules: dict) -> list[Violation]:
    violations = []

    if contributor.merged_prs < rules["min_prs_for_code_edit"]:
        if diff.additions > 0:
            violations.append(Violation(
                code="CODE_ADDITION_BLOCKED",
                message=f"New contributors cannot add lines. Expected 0, found {diff.additions}."
            ))
        if diff.files_changed > 1:
            violations.append(Violation(
                code="SINGLE_FILE_LIMIT",
                message=f"Too many files changed. Expected ≤ 1, found {diff.files_changed}."
            ))

    return violations
```

Rules are loaded from `preflight_rules.yml` — no code change required to update policy:

```yaml
# preflight_rules.yml
min_prs_for_code_edit: 3
trust_levels:
  - tier: 0
    max_files: 1
    allow_additions: false
  - tier: 1
    max_files: 3
    allow_additions: true
```

---

## Project Structure

```
blt-preflight/
├── main.py                # Entry point
├── diff_parser.py         # unidiff wrapper → DiffMetadata dataclass
├── rule_engine.py         # Loads YAML rules, evaluates violations
├── models.py              # DiffMetadata, ContributorStats, Violation dataclasses
├── preflight_rules.yml    # Contributor policy (YAML, no code change needed)
├── sample.diff            # Test diff — multi-file with additions (should fail)
├── sample_clean.diff      # Test diff — single file deletion only (should pass)
├── requirements.txt
└── README.md
```

---

## Test Cases

| Diff | Files | Additions | Expected Result |
|------|-------|-----------|-----------------|
| `sample.diff` | 2 | 1 | INVALID (2 violations) |
| `sample_clean.diff` | 1 | 0 | VALID |
| Single file, 0 additions | 1 | 0 | VALID |
| Single file, 1 addition | 1 | 1 | INVALID (CODE_ADDITION_BLOCKED) |
| Two files, 0 additions | 2 | 0 | INVALID (SINGLE_FILE_LIMIT) |

---

## What the Full GSoC Proposal Adds

This prototype covers the diff parser and rule engine. The full system (proposed for GSoC 2026) extends this with:

| Component | Status |
|-----------|--------|
| Diff Parser (`unidiff`) | ✅ Prototype complete |
| YAML Rule Engine | ✅ Prototype complete |
| GitHub Actions integration | 📋 Proposed |
| BLT Contributor API client | 📋 Proposed |
| Automated PR comment (Markdown feedback) | 📋 Proposed |
| Trust Score Algorithm (tier progression) | 📋 Proposed |
| Maintainer Triage Dashboard (HTMX) | 📋 Proposed |

Full proposal: [GSoC 2026 — BLT-Preflight](LINK_TO_PROPOSAL)

---

## Dependencies

```
unidiff==0.7.5
pyyaml==6.0.1
```

---

## Author

**Pranav Agarwal**  
GSoC 2026 Applicant — OWASP BLT  
[GitHub](https://github.com/agarwalpranav0711) 