
---

# Developer’s Guide for Config & BehaviorClassifier (v3)

## Context

This project is a standardized pipeline for **behavioral classification of Drosophila videos**.
It has two core packages:

* **Config** — the single source of truth for paths, experiment design, schema, thresholds, and colors.
* **BehaviorClassifier** — the classification engine: classifiers, QC, orchestrator, Colab adapters, and runners.

The code already works. This guide ensures all modules look **consistent, professional, and easy to maintain**.
Every contributor must follow it. PRs not conforming will not be merged.

---

## 1) Core Philosophy

* **SSOT (Single Source of Truth)**
  All config values come directly from `Config`. Never redefine or hardcode.
  *Why:* avoids drift between modules, keeps one authoritative source.

* **Fail fast, fail clear**
  Raise descriptive errors if config values are missing or invalid. No silent defaults.
  *Why:* prevents subtle bugs later in analysis.

* **Best-effort only where justified**
  Suppression allowed only for non-critical I/O (e.g., Colab background sync).
  *Why:* background failures shouldn’t kill long runs, but config errors must.

* **Readable before clever**
  Prioritize clarity, maintainability, and documentation over brevity.
  *Why:* this is scientific software; long-lived clarity beats short-term speed.

* **Indentation = tabs**
  One indent = one tab. No spaces.
  *Why:* avoids mismatches between Colab, editors, and git diffs.

---

## 2) Cell Structure

Modules are organized notebook-style with **cells** (`#%%`).

### Mandatory cells

* **Cell 00 — HEADER & OVERVIEW**
  Module docstring only: file path, commit metadata, overview, and canonical tree if relevant.
* **Cell 01 — IMPORTS**
  Consolidated, ordered imports.
* **Cell 04 — PUBLIC API**
  Single immutable bundle, second-to-last cell.
* **Cell 05 — REPORT**
  Optional, last cell. Only consumes the bundle.

### Flexible cells

* **Cell 02 — CONSTANTS / POLICIES**
* **Cell 03 — HELPERS / CORE LOGIC**

### Rules

* Only Cell 00 is the module docstring.
* Later cells start with a **banner docstring** (triple-quoted string) describing the section.
* `from __future__ import annotations` must appear immediately after the module docstring, before any other imports.
* If a REPORT exists, it must always be the final cell.

---

## 3) Titles, Spacing, Comments

* **Section titles:** `# TITLE` (ALL CAPS). Never use `===` or ASCII art.
* **Spacing:**

  * 2 blank lines between cells.
  * 2 blank lines before/after titles.
  * 1 blank line inside sections.
* **Inline comments:** Always inline with code. Never restate code.
* **Descriptive comments only:** Must explain intent or domain role.

---

## 4) Constants & Policies

* All constants **ALL\_CAPS**.
* Comments must describe **domain role**, not vague purpose.
  Example: `SLEAP_SUFFIX = "_sleap.csv"  # sleap body-parts data`
* Group related constants under titled sections.
* Never duplicate values from Config.
* Fail fast on invalid policies (e.g., duplicate suffixes).

---

## 5) Helpers

* Private helpers prefixed with `_`.
* If reused across cells, place in **HELPERS** cell.
* If local to one logic block, define inline.
* Helpers must be **stateless** and **policy-light**.
* **Strictness required:** No silent fallbacks. Raise on invalid input.

---

## 6) Functions & Docstrings

* **Type hints required**.
* **Google style docstrings only.**
* Include rationale in `Notes` if behavior may surprise (e.g., half-open intervals, NaNs).
* Include `Raises:` when a function fails fast.

---

## 7) Public API

* Each module exports **exactly one immutable bundle**.
* Bundle wrapped in `MappingProxyType`.
* `__all__` must list only that bundle.
* No stray globals.
* No legacy aliases. Only one canonical public name per helper or constant.

---

## 8) Reports

* Optional, final cell.
* Must use only the exported bundle (`PATH`, `EXPERIMENT`, `UTILS`, etc.).
* No computation, no QC checks, no writes. Print summaries only.
* Intended for humans (console output).

---

## 9) Error Handling

* **Default:** raise descriptive errors.
* **Allowed suppression:** non-critical I/O only. Must include comment:

```python
except Exception:
	# best-effort; never break session
	pass
```

* Never swallow errors in Config or helpers.

---

## 10) Formatting Rules

* Tabs only.
* Line length ≤ 100 characters.
* Double quotes for strings.
* Descriptive variable names; no unexplained abbreviations.
* Half-open intervals `[start, end)` for all frame ranges.
* Lint must pass clean (Ruff, mypy).

---

## 11) Module Archetypes

### Config module skeleton

```python
#%% CELL 00 — HEADER & OVERVIEW
"""
Config/path.py
<repo-url> <commit-hash> <timestamp>

Overview
	Define all experiment paths and helpers.
	No filesystem I/O. Config never creates directories.
"""

#%% CELL 01 — IMPORTS
from __future__ import annotations
from pathlib import Path
from types import MappingProxyType

#%% CELL 02 — CONSTANTS / POLICIES
# FILE SUFFIXES
TRACKED_SUFFIX = "_tracked.csv"  # tracked data
SLEAP_SUFFIX = "_sleap.csv"      # sleap body-parts data

#%% CELL 03 — HELPERS / CORE LOGIC
def stem_without_suffix(path: Path) -> str:
	...

#%% CELL 04 — PUBLIC API
_PUBLIC = {"TRACKED_SUFFIX": TRACKED_SUFFIX}
PATH = MappingProxyType(_PUBLIC)
__all__ = ["PATH"]

#%% CELL 05 — REPORT
if __name__ == "__main__":
	print("=== PATH summary ===")
	for key in sorted(PATH):
		print(key)
```

### Helper module skeleton (BehaviorClassifier/\_utils.py)

```python
#%% CELL 00 — HEADER & OVERVIEW
"""
BehaviorClassifier/_utils.py
<repo-url> <commit-hash> <timestamp>

Overview
	General stateless helpers used across classification.
"""

#%% CELL 01 — IMPORTS
from __future__ import annotations
from types import MappingProxyType
import numpy as np

#%% CELL 03 — HELPERS / CORE LOGIC
def compute_speed_mm_per_s(...): ...

#%% CELL 04 — PUBLIC API
_PUBLIC = {"compute_speed_mm_per_s": compute_speed_mm_per_s}
UTILS = MappingProxyType(_PUBLIC)
__all__ = ["UTILS"]

#%% CELL 05 — REPORT
if __name__ == "__main__":
	print("=== UTILS summary ===")
	for k in sorted(UTILS):
		print(k)
```

---

## 12) Anti-Patterns (strict NOs)

❌ Duplicating config values in modules
❌ Silent fallback defaults in helpers
❌ Legacy aliases for helpers (e.g., `filename = stem_without_suffix`)
❌ Imports not consolidated in Cell 01
❌ Unused imports left in modules
❌ Comments that restate code (`x += 1  # add one`)
❌ Comments with vague words (`# stuff`, `# data`)
❌ Multiple public bundles or stray globals
❌ Logic or QC checks in the REPORT cell
❌ Creating directories in Config (`mkdir`, `touch`)
❌ Using `.resolve()` or any filesystem touch in Config
❌ Mixing tabs and spaces
❌ Lines > 100 characters
❌ Inconsistent string quotes
❌ One-letter variable names outside trivial loops
❌ Second “docstring” before `__future__` import
❌ Swallowing exceptions without justification
❌ Vague constant comments (must state domain role)
❌ Stripping file suffixes with fallback instead of fail-fast
❌ Mutating public bundles after definition
❌ Printing in non-report cells
❌ Complex logic hidden inside lambda for public API

---

## 13) Extended PR Checklist

* [ ] Cell 00 docstring present with metadata, overview, canonical tree if relevant
* [ ] `__future__` import immediately after module docstring
* [ ] Imports consolidated in Cell 01, ordered stdlib → typing → third-party → local
* [ ] No unused imports (lint clean)
* [ ] Every later cell starts with a docstring banner
* [ ] Section titles ALL CAPS, no ASCII art
* [ ] 2 blank lines between cells, 2 before/after titles, 1 inside
* [ ] Constants ALL\_CAPS with descriptive inline comments (domain role)
* [ ] Constants grouped under titled sections
* [ ] Functions type-hinted, with Google-style docstrings (Args/Returns/Notes/Raises)
* [ ] Helpers stateless, policy-light, no silent fallback
* [ ] Exactly one immutable bundle per module, wrapped in MappingProxyType
* [ ] `__all__` lists only the bundle
* [ ] No legacy aliases in public API
* [ ] Report cell only consumes bundle, prints summaries, no logic/QC/writes
* [ ] Config never creates directories or resolves paths
* [ ] Fail fast for invalid config (e.g., duplicate suffixes, collisions)
* [ ] Tabs only, ≤ 100 chars/line, double quotes consistent
* [ ] No stray globals or unused code paths
* [ ] Lint + mypy pass clean
* [ ] Sanity checks present where policy could drift (duplicate suffixes, folder collisions, rebase coverage)

---

## 14) Validation & Vectorization Rules

* Derived structures must **validate inputs at import time** (raise on error).
* Time helpers (`seconds_to_frames`, `frames_to_seconds`) must handle scalars and arrays.
* Period ranges must always use half-open `[start, end)` intervals.
* Prefer NumPy/Pandas vectorization; loops allowed only if vectorization hurts readability.
* Document rationale in docstring if loop is chosen.

---

## 15) Decision Table

**Where should code go?**

* Experiment-wide constants or schema → **Config**
* General data transforms (no policy) → **BehaviorClassifier/\_utils**
* Classification thresholds, smoothing, tie-breaks → **BehaviorClassifier/\_classifier**
* QC checks and error/flag reporting → **BehaviorClassifier/\_qc\_error\_flag**
* Orchestration/sequencing → **BehaviorClassifier/\_main**
* Colab/Drive path handling → **BehaviorClassifier/\_colab**
* Entry scripts with side-effects → `*_run.py`

---