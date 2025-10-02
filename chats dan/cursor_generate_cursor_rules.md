# Generate cursor rules
_Exported on 10/1/2025 at 21:51:44 GMT+1 from Cursor (1.7.28)_

---

**User**

/Generate Cursor Rules

@g:\My Drive\REFACTOR_AFTERLABMEET\REFACTOR_GUIDE.md 


create a cursor rules based on this file

---

**Cursor**

I'll create a `.cursorrules` file at the workspace root that encodes enforceable guidelines distilled from `REFACTOR_GUIDE.md`, so Cursor consistently applies your project's conventions across edits.

```plaintext
*** Begin Patch
*** Add File: g:\My Drive\REFACTOR_AFTERLABMEET\Codes_New\Codes\.cursorrules
## Cursor Rules for this Repository (derived from REFACTOR_GUIDE.md)

These rules are the authoritative editing guidelines for this repo. They codify the style, structure, and architectural policies across `Config` and `BehaviorClassifier` packages. All automated edits must comply.

### Core Principles
- **Single Source of Truth (SSOT)**: All config values must come from `Config` modules. Never duplicate or hardcode experiment paths, schema, thresholds, or colors elsewhere.
- **Fail fast, fail clear**: Raise descriptive errors for invalid/missing config or inputs. No silent defaults.
- **Readable before clever**: Prefer clarity and maintainability over brevity or over-optimization.
- **Tabs-only indentation**: Use tabs for indentation across all files. Do not mix with spaces.
- **No side-effects in Config**: Config defines values and helpers only; it never touches the filesystem.

### File Organization with Cells
- Modules are organized notebook-style using `#%%` cell markers.
- Mandatory cells:
  - `CELL 00 — HEADER & OVERVIEW`: single module docstring with file path, repo/commit/timestamp, overview, and canonical tree if relevant.
  - `CELL 01 — IMPORTS`: consolidated imports.
  - `CELL 04 — PUBLIC API`: single immutable public bundle (second-to-last cell).
  - `CELL 05 — REPORT` (optional): must be the final cell and only consume the public bundle.
- Flexible cells:
  - `CELL 02 — CONSTANTS / POLICIES`
  - `CELL 03 — HELPERS / CORE LOGIC`
- Rules:
  - Only Cell 00 contains the module docstring.
  - Every later cell starts with a short banner docstring (triple-quoted) describing the section.
  - `from __future__ import annotations` must appear immediately after the module docstring and before any other imports (in Cell 01).
  - If a REPORT exists, it is always the final cell.

### Imports
- Consolidate imports in Cell 01.
- Order: standard library → typing → third-party → local.
- Remove unused imports. Lint must be clean.

### Titles, Spacing, Comments
- Section titles are ALL CAPS using `# TITLE` (no ASCII art, no `===`).
- Spacing:
  - 2 blank lines between cells.
  - 2 blank lines before/after titles.
  - 1 blank line inside sections.
- Inline comments must add domain intent; never restate code.

### Constants & Policies
- Constants are ALL_CAPS with descriptive inline comments stating domain role (not vague purpose).
- Group related constants under titled sections.
- Never duplicate values from `Config`.
- Validate policies at import time; raise on invalid states (e.g., duplicate suffixes).

### Helpers
- Private helpers are prefixed with `_`.
- Stateless and policy-light; raise on invalid inputs (no silent fallbacks).
- Place cross-cell helpers in the HELPERS cell; otherwise define locally where used.

### Functions & Docstrings
- Type hints are required.
- Use Google-style docstrings with `Args`, `Returns`, `Raises`, and `Notes` where rationale matters (e.g., half-open intervals, NaNs).

### Public API Contract
- Each module must expose exactly one immutable bundle, wrapped with `MappingProxyType`.
- `__all__` lists only that bundle.
- No stray globals and no legacy aliases.
- Do not mutate public bundles after definition.

### Report Cells
- Optional, always the final cell.
- Only consume the module’s public bundle; print human-readable summaries.
- No computation, QC checks, or writes in REPORT cells.

### Error Handling
- Default: raise descriptive errors.
- Allowed suppression: non-critical I/O only; must include the comment:
	```python
	except Exception:
		# best-effort; never break session
		pass
	```
- Never suppress in `Config` or core helpers.

### Formatting & Lint
- Tabs-only indentation; max line length ≤ 100 characters.
- Double quotes for all strings.
- Descriptive identifiers; avoid unexplained abbreviations.
- Use half-open intervals `[start, end)` for frame ranges.
- Prefer NumPy/Pandas vectorization; allow loops only if vectorization harms readability and document rationale.
- Ruff and mypy must pass clean; remove unused code paths.

### Anti-Patterns (Strict NOs)
- Duplicating config values outside `Config`.
- Silent fallback defaults in helpers.
- Legacy aliases or multiple public bundles.
- Imports scattered outside Cell 01 or left unused.
- Printing outside the REPORT cell.
- Creating/resolving directories in `Config` (no `mkdir`, `touch`, `.resolve()`).
- Mixing tabs and spaces; lines > 100 chars; inconsistent quotes.
- One-letter variable names outside trivial loops.
- Second docstring before the `__future__` import.
- Swallowing exceptions without the allowed best-effort justification.
- Stripping file suffixes with fallbacks instead of fail-fast logic.
- Complex public API logic hidden in lambdas.

### Module Archetypes (reference)
- Config module skeleton:
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
- Helper module skeleton (`BehaviorClassifier/_utils.py`):
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

### PR Checklist (enforced expectations)
- Cell 00 docstring with metadata and overview present; no second docstring elsewhere.
- `from __future__ import annotations` immediately after docstring.
- Imports consolidated and ordered; no unused imports.
- Every later cell begins with a banner docstring.
- Section titles in ALL CAPS with required spacing.
- Constants ALL_CAPS with domain-role comments; logically grouped.
- Functions type-hinted with Google-style docstrings.
- Exactly one immutable public bundle per module; `__all__` lists only that bundle.
- REPORT cell (if any) only prints summaries from the public bundle.
- Config never performs filesystem actions.
- Fail fast for invalid policies/config (e.g., duplicate suffixes, collisions).
- Tabs-only, ≤ 100 chars/line, double quotes consistent.
- No stray globals; lint and mypy must pass.
- Sanity checks present where policy could drift.

### Editing Behavior for Cursor
- When creating or modifying files, maintain the cell structure and spacing rules.
- Do not introduce spaces for indentation; preserve existing tabs.
- When adding functions, include full type hints and Google-style docstrings.
- When exposing helpers/constants, update the single public bundle and `__all__` accordingly.
- Avoid adding computation or I/O in Config and REPORT cells.
- Prefer vectorized NumPy/Pandas implementations and document when loops are chosen.

### Decision Table (routing code changes)
- Experiment-wide constants or schema → `Config` package.
- General data transforms (no policy) → `BehaviorClassifier/_utils.py`.
- Classification thresholds, smoothing, tie-breaks → `BehaviorClassifier/_classifier`.
- QC checks and error/flag reporting → `BehaviorClassifier/_qc_error_flag`.
- Orchestration/sequencing → `BehaviorClassifier/_main`.
- Colab/Drive path handling → `BehaviorClassifier/_colab`.
- Entry scripts with side-effects → `*_run.py`.

*** End Patch
```

I'll check the workspace root to verify the correct path and then create the `.cursorrules` file with the distilled rules.

```plaintext
*** Begin Patch
*** Add File: g:\My Drive\REFACTOR_AFTERLABMEET\Codes_New\Codes\.cursorrules
## Cursor Rules for this Repository (derived from REFACTOR_GUIDE.md)

These rules are the authoritative editing guidelines for this repo. They codify the style, structure, and architectural policies across `Config` and `BehaviorClassifier` packages. All automated edits must comply.

### Core Principles
- **Single Source of Truth (SSOT)**: All config values must come from `Config` modules. Never duplicate or hardcode experiment paths, schema, thresholds, or colors elsewhere.
- **Fail fast, fail clear**: Raise descriptive errors for invalid/missing config or inputs. No silent defaults.
- **Readable before clever**: Prefer clarity and maintainability over brevity or over-optimization.
- **Tabs-only indentation**: Use tabs for indentation across all files. Do not mix with spaces.
- **No side-effects in Config**: Config defines values and helpers only; it never touches the filesystem.

### File Organization with Cells
- Modules are organized notebook-style using `#%%` cell markers.
- Mandatory cells:
  - `CELL 00 — HEADER & OVERVIEW`: single module docstring with file path, repo/commit/timestamp, overview, and canonical tree if relevant.
  - `CELL 01 — IMPORTS`: consolidated imports.
  - `CELL 04 — PUBLIC API`: single immutable public bundle (second-to-last cell).
  - `CELL 05 — REPORT` (optional): must be the final cell and only consume the public bundle.
- Flexible cells:
  - `CELL 02 — CONSTANTS / POLICIES`
  - `CELL 03 — HELPERS / CORE LOGIC`
- Rules:
  - Only Cell 00 contains the module docstring.
  - Every later cell starts with a short banner docstring (triple-quoted) describing the section.
  - `from __future__ import annotations` must appear immediately after the module docstring and before any other imports (in Cell 01).
  - If a REPORT exists, it is always the final cell.

### Imports
- Consolidate imports in Cell 01.
- Order: standard library → typing → third-party → local.
- Remove unused imports. Lint must be clean.

### Titles, Spacing, Comments
- Section titles are ALL CAPS using `# TITLE` (no ASCII art, no `===`).
- Spacing:
  - 2 blank lines between cells.
  - 2 blank lines before/after titles.
  - 1 blank line inside sections.
- Inline comments must add domain intent; never restate code.

### Constants & Policies
- Constants are ALL_CAPS with descriptive inline comments stating domain role (not vague purpose).
- Group related constants under titled sections.
- Never duplicate values from `Config`.
- Validate policies at import time; raise on invalid states (e.g., duplicate suffixes).

### Helpers
- Private helpers are prefixed with `_`.
- Stateless and policy-light; raise on invalid inputs (no silent fallbacks).
- Place cross-cell helpers in the HELPERS cell; otherwise define locally where used.

### Functions & Docstrings
- Type hints are required.
- Use Google-style docstrings with `Args`, `Returns`, `Raises`, and `Notes` where rationale matters (e.g., half-open intervals, NaNs).

### Public API Contract
- Each module must expose exactly one immutable bundle, wrapped with `MappingProxyType`.
- `__all__` lists only that bundle.
- No stray globals and no legacy aliases.
- Do not mutate public bundles after definition.

### Report Cells
- Optional, always the final cell.
- Only consume the module’s public bundle; print human-readable summaries.
- No computation, QC checks, or writes in REPORT cells.

### Error Handling
- Default: raise descriptive errors.
- Allowed suppression: non-critical I/O only; must include the comment:
	```python
	except Exception:
		# best-effort; never break session
		pass
	```
- Never suppress in `Config` or core helpers.

### Formatting & Lint
- Tabs-only indentation; max line length ≤ 100 characters.
- Double quotes for all strings.
- Descriptive identifiers; avoid unexplained abbreviations.
- Use half-open intervals `[start, end)` for frame ranges.
- Prefer NumPy/Pandas vectorization; allow loops only if vectorization harms readability and document rationale.
- Ruff and mypy must pass clean; remove unused code paths.

### Anti-Patterns (Strict NOs)
- Duplicating config values outside `Config`.
- Silent fallback defaults in helpers.
- Legacy aliases or multiple public bundles.
- Imports scattered outside Cell 01 or left unused.
- Printing outside the REPORT cell.
- Creating/resolving directories in `Config` (no `mkdir`, `touch`, `.resolve()`).
- Mixing tabs and spaces; lines > 100 chars; inconsistent quotes.
- One-letter variable names outside trivial loops.
- Second docstring before the `__future__` import.
- Swallowing exceptions without the allowed best-effort justification.
- Stripping file suffixes with fallbacks instead of fail-fast logic.
- Complex public API logic hidden in lambdas.

### Module Archetypes (reference)
- Config module skeleton:
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
- Helper module skeleton (`BehaviorClassifier/_utils.py`):
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

### PR Checklist (enforced expectations)
- Cell 00 docstring with metadata and overview present; no second docstring elsewhere.
- `from __future__ import annotations` immediately after docstring.
- Imports consolidated and ordered; no unused imports.
- Every later cell begins with a banner docstring.
- Section titles in ALL CAPS with required spacing.
- Constants ALL_CAPS with domain-role comments; logically grouped.
- Functions type-hinted with Google-style docstrings.
- Exactly one immutable public bundle per module; `__all__` lists only that bundle.
- REPORT cell (if any) only prints summaries from the public bundle.
- Config never performs filesystem actions.
- Fail fast for invalid policies/config (e.g., duplicate suffixes, collisions).
- Tabs-only, ≤ 100 chars/line, double quotes consistent.
- No stray globals; lint and mypy must pass.
- Sanity checks present where policy could drift.

### Editing Behavior for Cursor
- When creating or modifying files, maintain the cell structure and spacing rules.
- Do not introduce spaces for indentation; preserve existing tabs.
- When adding functions, include full type hints and Google-style docstrings.
- When exposing helpers/constants, update the single public bundle and `__all__` accordingly.
- Avoid adding computation or I/O in Config and REPORT cells.
- Prefer vectorized NumPy/Pandas implementations and document when loops are chosen.

### Decision Table (routing code changes)
- Experiment-wide constants or schema → `Config` package.
- General data transforms (no policy) → `BehaviorClassifier/_utils.py`.
- Classification thresholds, smoothing, tie-breaks → `BehaviorClassifier/_classifier`.
- QC checks and error/flag reporting → `BehaviorClassifier/_qc_error_flag`.
- Orchestration/sequencing → `BehaviorClassifier/_main`.
- Colab/Drive path handling → `BehaviorClassifier/_colab`.
- Entry scripts with side-effects → `*_run.py`.

*** End Patch
```

Creating a `.cursorrules` file at the repository root with rules distilled from `REFACTOR_GUIDE.md`.

```plaintext
*** Begin Patch
*** Add File: .cursorrules
## Cursor Rules for this Repository (derived from REFACTOR_GUIDE.md)

These rules are the authoritative editing guidelines for this repo. They codify the style, structure, and architectural policies across `Config` and `BehaviorClassifier` packages. All automated edits must comply.

### Core Principles
- **Single Source of Truth (SSOT)**: All config values must come from `Config` modules. Never duplicate or hardcode experiment paths, schema, thresholds, or colors elsewhere.
- **Fail fast, fail clear**: Raise descriptive errors for invalid/missing config or inputs. No silent defaults.
- **Readable before clever**: Prefer clarity and maintainability over brevity or over-optimization.
- **Tabs-only indentation**: Use tabs for indentation across all files. Do not mix with spaces.
- **No side-effects in Config**: Config defines values and helpers only; it never touches the filesystem.

### File Organization with Cells
- Modules are organized notebook-style using `#%%` cell markers.
- Mandatory cells:
  - `CELL 00 — HEADER & OVERVIEW`: single module docstring with file path, repo/commit/timestamp, overview, and canonical tree if relevant.
  - `CELL 01 — IMPORTS`: consolidated imports.
  - `CELL 04 — PUBLIC API`: single immutable public bundle (second-to-last cell).
  - `CELL 05 — REPORT` (optional): must be the final cell and only consume the public bundle.
- Flexible cells:
  - `CELL 02 — CONSTANTS / POLICIES`
  - `CELL 03 — HELPERS / CORE LOGIC`
- Rules:
  - Only Cell 00 contains the module docstring.
  - Every later cell starts with a short banner docstring (triple-quoted) describing the section.
  - `from __future__ import annotations` must appear immediately after the module docstring and before any other imports (in Cell 01).
  - If a REPORT exists, it is always the final cell.

### Imports
- Consolidate imports in Cell 01.
- Order: standard library → typing → third-party → local.
- Remove unused imports. Lint must be clean.

### Titles, Spacing, Comments
- Section titles are ALL CAPS using `# TITLE` (no ASCII art, no `===`).
- Spacing:
  - 2 blank lines between cells.
  - 2 blank lines before/after titles.
  - 1 blank line inside sections.
- Inline comments must add domain intent; never restate code.

### Constants & Policies
- Constants are ALL_CAPS with descriptive inline comments stating domain role (not vague purpose).
- Group related constants under titled sections.
- Never duplicate values from `Config`.
- Validate policies at import time; raise on invalid states (e.g., duplicate suffixes).

### Helpers
- Private helpers are prefixed with `_`.
- Stateless and policy-light; raise on invalid inputs (no silent fallbacks).
- Place cross-cell helpers in the HELPERS cell; otherwise define locally where used.

### Functions & Docstrings
- Type hints are required.
- Use Google-style docstrings with `Args`, `Returns`, `Raises`, and `Notes` where rationale matters (e.g., half-open intervals, NaNs).

### Public API Contract
- Each module must expose exactly one immutable bundle, wrapped with `MappingProxyType`.
- `__all__` lists only that bundle.
- No stray globals and no legacy aliases.
- Do not mutate public bundles after definition.

### Report Cells
- Optional, always the final cell.
- Only consume the module’s public bundle; print human-readable summaries.
- No computation, QC checks, or writes in REPORT cells.

### Error Handling
- Default: raise descriptive errors.
- Allowed suppression: non-critical I/O only; must include the comment:
	```python
	except Exception:
		# best-effort; never break session
		pass
	```
- Never suppress in `Config` or core helpers.

### Formatting & Lint
- Tabs-only indentation; max line length ≤ 100 characters.
- Double quotes for all strings.
- Descriptive identifiers; avoid unexplained abbreviations.
- Use half-open intervals `[start, end)` for frame ranges.
- Prefer NumPy/Pandas vectorization; allow loops only if vectorization harms readability and document rationale.
- Ruff and mypy must pass clean; remove unused code paths.

### Anti-Patterns (Strict NOs)
- Duplicating config values outside `Config`.
- Silent fallback defaults in helpers.
- Legacy aliases or multiple public bundles.
- Imports scattered outside Cell 01 or left unused.
- Printing outside the REPORT cell.
- Creating/resolving directories in `Config` (no `mkdir`, `touch`, `.resolve()`).
- Mixing tabs and spaces; lines > 100 chars; inconsistent quotes.
- One-letter variable names outside trivial loops.
- Second docstring before the `__future__` import.
- Swallowing exceptions without the allowed best-effort justification.
- Stripping file suffixes with fallbacks instead of fail-fast logic.
- Complex public API logic hidden in lambdas.

### Module Archetypes (reference)
- Config module skeleton:
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
- Helper module skeleton (`BehaviorClassifier/_utils.py`):
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

### PR Checklist (enforced expectations)
- Cell 00 docstring with metadata and overview present; no second docstring elsewhere.
- `from __future__ import annotations` immediately after docstring.
- Imports consolidated and ordered; no unused imports.
- Every later cell begins with a banner docstring.
- Section titles in ALL CAPS with required spacing.
- Constants ALL_CAPS with domain-role comments; logically grouped.
- Functions type-hinted with Google-style docstrings.
- Exactly one immutable public bundle per module; `__all__` lists only that bundle.
- REPORT cell (if any) only prints summaries from the public bundle.
- Config never performs filesystem actions.
- Fail fast for invalid policies/config (e.g., duplicate suffixes, collisions).
- Tabs-only, ≤ 100 chars/line, double quotes consistent.
- No stray globals; lint and mypy must pass.
- Sanity checks present where policy could drift.

### Editing Behavior for Cursor
- When creating or modifying files, maintain the cell structure and spacing rules.
- Do not introduce spaces for indentation; preserve existing tabs.
- When adding functions, include full type hints and Google-style docstrings.
- When exposing helpers/constants, update the single public bundle and `__all__` accordingly.
- Avoid adding computation or I/O in Config and REPORT cells.
- Prefer vectorized NumPy/Pandas implementations and document when loops are chosen.

### Decision Table (routing code changes)
- Experiment-wide constants or schema → `Config` package.
- General data transforms (no policy) → `BehaviorClassifier/_utils.py`.
- Classification thresholds, smoothing, tie-breaks → `BehaviorClassifier/_classifier`.
- QC checks and error/flag reporting → `BehaviorClassifier/_qc_error_flag`.
- Orchestration/sequencing → `BehaviorClassifier/_main`.
- Colab/Drive path handling → `BehaviorClassifier/_colab`.
- Entry scripts with side-effects → `*_run.py`.

*** End Patch
```

```plaintext
## Cursor Rules for this Repository (derived from REFACTOR_GUIDE.md)

These rules are the authoritative editing guidelines for this repo. They codify the style, structure, and architectural policies across `Config` and `BehaviorClassifier` packages. All automated edits must comply.

### Core Principles
- **Single Source of Truth (SSOT)**: All config values must come from `Config` modules. Never duplicate or hardcode experiment paths, schema, thresholds, or colors elsewhere.
- **Fail fast, fail clear**: Raise descriptive errors for invalid/missing config or inputs. No silent defaults.
- **Readable before clever**: Prefer clarity and maintainability over brevity or over-optimization.
- **Tabs-only indentation**: Use tabs for indentation across all files. Do not mix with spaces.
- **No side-effects in Config**: Config defines values and helpers only; it never touches the filesystem.

### File Organization with Cells
- Modules are organized notebook-style using `#%%` cell markers.
- Mandatory cells:
  - `CELL 00 — HEADER & OVERVIEW`: single module docstring with file path, repo/commit/timestamp, overview, and canonical tree if relevant.
  - `CELL 01 — IMPORTS`: consolidated imports.
  - `CELL 04 — PUBLIC API`: single immutable public bundle (second-to-last cell).
  - `CELL 05 — REPORT` (optional): must be the final cell and only consume the public bundle.
- Flexible cells:
  - `CELL 02 — CONSTANTS / POLICIES`
  - `CELL 03 — HELPERS / CORE LOGIC`
- Rules:
  - Only Cell 00 contains the module docstring.
  - Every later cell starts with a short banner docstring (triple-quoted) describing the section.
  - `from __future__ import annotations` must appear immediately after the module docstring and before any other imports (in Cell 01).
  - If a REPORT exists, it is always the final cell.

### Imports
- Consolidate imports in Cell 01.
- Order: standard library → typing → third-party → local.
- Remove unused imports. Lint must be clean.

### Titles, Spacing, Comments
- Section titles are ALL CAPS using `# TITLE` (no ASCII art, no `===`).
- Spacing:
  - 2 blank lines between cells.
  - 2 blank lines before/after titles.
  - 1 blank line inside sections.
- Inline comments must add domain intent; never restate code.

### Constants & Policies
- Constants are ALL_CAPS with descriptive inline comments stating domain role (not vague purpose).
- Group related constants under titled sections.
- Never duplicate values from `Config`.
- Validate policies at import time; raise on invalid states (e.g., duplicate suffixes).

### Helpers
- Private helpers are prefixed with `_`.
- Stateless and policy-light; raise on invalid inputs (no silent fallbacks).
- Place cross-cell helpers in the HELPERS cell; otherwise define locally where used.

### Functions & Docstrings
- Type hints are required.
- Use Google-style docstrings with `Args`, `Returns`, `Raises`, and `Notes` where rationale matters (e.g., half-open intervals, NaNs).

### Public API Contract
- Each module must expose exactly one immutable bundle, wrapped with `MappingProxyType`.
- `__all__` lists only that bundle.
- No stray globals and no legacy aliases.
- Do not mutate public bundles after definition.

### Report Cells
- Optional, always the final cell.
- Only consume the module’s public bundle; print human-readable summaries.
- No computation, QC checks, or writes in REPORT cells.

### Error Handling
- Default: raise descriptive errors.
- Allowed suppression: non-critical I/O only; must include the comment:
	except Exception:
		# best-effort; never break session
		pass
- Never suppress in `Config` or core helpers.

### Formatting & Lint
- Tabs-only indentation; max line length ≤ 100 characters.
- Double quotes for all strings.
- Descriptive identifiers; avoid unexplained abbreviations.
- Use half-open intervals `[start, end)` for frame ranges.
- Prefer NumPy/Pandas vectorization; allow loops only if vectorization harms readability and document rationale.
- Ruff and mypy must pass clean; remove unused code paths.

### Anti-Patterns (Strict NOs)
- Duplicating config values outside `Config`.
- Silent fallback defaults in helpers.
- Legacy aliases or multiple public bundles.
- Imports scattered outside Cell 01 or left unused.
- Printing outside the REPORT cell.
- Creating/resolving directories in `Config` (no `mkdir`, `touch`, `.resolve()`).
- Mixing tabs and spaces; lines > 100 chars; inconsistent quotes.
- One-letter variable names outside trivial loops.
- Second docstring before the `__future__` import.
- Swallowing exceptions without the allowed best-effort justification.
- Stripping file suffixes with fallbacks instead of fail-fast logic.
- Complex public API logic hidden in lambdas.

### Module Archetypes (reference)
- Config module skeleton:
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
- Helper module skeleton (`BehaviorClassifier/_utils.py`):
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

### PR Checklist (enforced expectations)
- Cell 00 docstring with metadata and overview present; no second docstring elsewhere.
- `from __future__ import annotations` immediately after docstring.
- Imports consolidated and ordered; no unused imports.
- Every later cell begins with a banner docstring.
- Section titles in ALL CAPS with required spacing.
- Constants ALL_CAPS with domain-role comments; logically grouped.
- Functions type-hinted with Google-style docstrings.
- Exactly one immutable public bundle per module; `__all__` lists only that bundle.
- REPORT cell (if any) only prints summaries from the public bundle.
- Config never performs filesystem actions.
- Fail fast for invalid policies/config (e.g., duplicate suffixes, collisions).
- Tabs-only, ≤ 100 chars/line, double quotes consistent.
- No stray globals; lint and mypy must pass.
- Sanity checks present where policy could drift.

### Editing Behavior for Cursor
- When creating or modifying files, maintain the cell structure and spacing rules.
- Do not introduce spaces for indentation; preserve existing tabs.
- When adding functions, include full type hints and Google-style docstrings.
- When exposing helpers/constants, update the single public bundle and `__all__` accordingly.
- Avoid adding computation or I/O in Config and REPORT cells.
- Prefer vectorized NumPy/Pandas implementations and document when loops are chosen.

### Decision Table (routing code changes)
- Experiment-wide constants or schema → `Config` package.
- General data transforms (no policy) → `BehaviorClassifier/_utils.py`.
- Classification thresholds, smoothing, tie-breaks → `BehaviorClassifier/_classifier`.
- QC checks and error/flag reporting → `BehaviorClassifier/_qc_error_flag`.
- Orchestration/sequencing → `BehaviorClassifier/_main`.
- Colab/Drive path handling → `BehaviorClassifier/_colab`.
- Entry scripts with side-effects → `*_run.py`.
```

I created `.cursorrules` at the repo root with enforceable rules distilled from `REFACTOR_GUIDE.md`, covering SSOT, tabs-only indentation, cell structure, imports, constants, helpers, docstrings, public API bundle, report cell constraints, error handling, formatting, anti-patterns, archetypes, checklist, editing behavior, and the decision table.

- **File**: `Codes/.cursorrules`
- **Impact**: Cursor will now guide and constrain edits to match your guide across `Config` and `BehaviorClassifier`.

---

**User**

explain to me how to better implement by cursor rules accordog to cursor documentation

---

**Cursor**

### Short answer
- Put rules in `.cursor/rules/*.mdc`, not a giant single file.
- Scope each rule file with clear file globs and atomic “Must/Never/Prefer” directives.
- Add short “Good/Bad” examples, skeleton snippets, and explicit “Edits” constraints.
- Split rules by concern (repo-wide, Python, cell structure, Config, BehaviorClassifier).

### How to structure Cursor rules (best practice)
- Scope
  - Use multiple `.mdc` files inside `.cursor/rules/`.
  - Start each with a clear title and “Applies to” section using globs.
  - Keep rules atomic and imperative: “Must”, “Never”, “Prefer”.
- Enforceability
  - Add “Edits” guidance: what Cursor can/can’t change.
  - Include “Good/Bad” examples to steer completions.
  - Provide canonical skeletons as snippets.
- Organization
  - Keep repo-wide norms in `repo.mdc`.
  - Language-specific in `python.mdc`.
  - Domain modules in `config.mdc`, `behaviorclassifier.mdc`.
  - Formatting and cell structure in `formatting.mdc`, `cells.mdc`.

### Suggested rule files layout
- `.cursor/rules/repo.mdc`: global project guardrails.
- `.cursor/rules/python.mdc`: Python typing, docstrings, imports.
- `.cursor/rules/formatting.mdc`: tabs-only, quotes, line length.
- `.cursor/rules/cells.mdc`: notebook-style cells, positions, spacing.
- `.cursor/rules/config.mdc`: SSOT and no I/O for `Config/*`.
- `.cursor/rules/behaviorclassifier.mdc`: helpers, public bundle, report rules.

### Example: repo.mdc
- Applies to: `**/*`

- Goals
  - Keep `Config` as SSOT; enforce fail-fast; ensure readability.

- Directives
  - Must: Use tabs for indentation across the repo.
  - Must: Use double quotes for strings.
  - Prefer: Vectorized NumPy/Pandas over loops unless readability suffers.
  - Never: Duplicate config values outside `Config`.

- Edits
  - Must not introduce spaces for indentation.
  - Must keep lines ≤ 100 chars.

- Good
  ```python
  SLEAP_SUFFIX = "_sleap.csv"  # sleap body-parts data
  ```

- Bad
  ```python
  SLEAP_SUFFIX = '_sleap.csv'  # vague
  ```

### Example: cells.mdc
- Applies to: `Config/**/*.py`, `BehaviorClassifier/**/*.py`

- Goals
  - Enforce notebook-style cell structure and ordering.

- Directives
  - Must: Include `#%% CELL 00 — HEADER & OVERVIEW` as the only module docstring.
  - Must: Place `from __future__ import annotations` immediately after Cell 00, before any other imports.
  - Must: Keep mandatory cells present: 00, 01, 04; `05 — REPORT` if present must be last.
  - Must: Maintain spacing — 2 blank lines between cells; 2 before/after titles; 1 inside sections.
  - Never: Add a second docstring before `__future__`.

- Edits
  - Must not move REPORT logic into non-report cells.
  - Must add banner triple-quoted strings at the start of later cells.

- Good
  ```python
  #%% CELL 01 — IMPORTS
  """
  IMPORTS
  """
  from __future__ import annotations
  from types import MappingProxyType
  ```

### Example: config.mdc
- Applies to: `Config/**/*.py`

- Goals
  - Keep `Config` pure (no side-effects) and canonical.

- Directives
  - Must: Resolve values only from within `Config`; other packages import from `Config`.
  - Must: Validate policies at import time; raise on duplicate suffixes or collisions.
  - Never: Use `.resolve()`, `mkdir`, `touch`, or any filesystem writes.

- Edits
  - Must not introduce any I/O in `Config`.

- Good
  ```python
  from types import MappingProxyType

  TRACKED_SUFFIX = "_tracked.csv"  # tracked data
  PATH = MappingProxyType({"TRACKED_SUFFIX": TRACKED_SUFFIX})
  ```

### Example: behaviorclassifier.mdc
- Applies to: `BehaviorClassifier/**/*.py`

- Goals
  - Stateless helpers, single public API bundle, report-only output.

- Directives
  - Must: Prefix private helpers with `_` and keep policy-light.
  - Must: Export exactly one `MappingProxyType` bundle; `__all__` lists only that.
  - Must: Use Google-style docstrings with type hints and `Raises` where applicable.
  - Never: Silent fallbacks; use descriptive exceptions instead.
  - Report Cell: Only prints summaries; no QC checks or writes.

- Edits
  - Must not mutate public bundles after definition.
  - Must include rationale in docstrings when loops are chosen over vectorization.

- Good
  ```python
  _PUBLIC = {"compute_speed_mm_per_s": compute_speed_mm_per_s}
  UTILS = MappingProxyType(_PUBLIC)
  __all__ = ["UTILS"]
  ```

### Example: python.mdc
- Applies to: `**/*.py`

- Goals
  - Consistent Python style.

- Directives
  - Must: Full type hints on function signatures.
  - Must: Google-style docstrings (`Args`, `Returns`, `Raises`, `Notes`).
  - Must: Import order: stdlib → typing → third-party → local.
  - Never: Unused imports; lint must be clean.

- Edits
  - Must add missing type hints on new functions.
  - Should convert single quotes to double quotes in touched lines.

### Example: formatting.mdc
- Applies to: `**/*.py`

- Goals
  - Enforce formatting everywhere.

- Directives
  - Must: Tabs-only; lines ≤ 100 chars; double quotes for strings.
  - Must: Use half-open intervals `[start, end)` for frame ranges in comments/docstrings.

- Edits
  - Must convert added indentation to tabs.
  - Must not auto-wrap lines beyond 100 chars.

### Add skeletons to steer completions
Include canonical skeletons as “Good” examples in `cells.mdc` and `behaviorclassifier.mdc`—Cursor will bias completions towards them. Keep them short and authoritative.

### Make your existing REFACTOR_GUIDE.mdc more “Cursor-friendly”
- Front-load “Applies to” and “Directives” as Must/Never/Prefer bullets.
- Move narrative/context into a short “Goals”.
- Add “Edits” with explicit constraints (indentation, cell moves, report rules).
- Add short “Good/Bad” examples for each critical rule.
- Split the current long file into the suggested files above; keep each ≤ 200–300 lines.

If you want, I can split your current `REFACTOR_GUIDE.mdc` into these focused files and insert the examples and edits sections for you.

```python
  SLEAP_SUFFIX = "_sleap.csv"  # sleap body-parts data
```

```python
  SLEAP_SUFFIX = '_sleap.csv'  # vague
```

```python
  #%% CELL 01 — IMPORTS
  """
  IMPORTS
  """
  from __future__ import annotations
  from types import MappingProxyType
```

```python
  from types import MappingProxyType

  TRACKED_SUFFIX = "_tracked.csv"  # tracked data
  PATH = MappingProxyType({"TRACKED_SUFFIX": TRACKED_SUFFIX})
```

```python
  _PUBLIC = {"compute_speed_mm_per_s": compute_speed_mm_per_s}
  UTILS = MappingProxyType(_PUBLIC)
  __all__ = ["UTILS"]
```

