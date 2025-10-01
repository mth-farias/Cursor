## Schema Design and Maintenance Guide

This guide inventories current schemas and proposes improvements to make them easier to evolve, validate, and consume across the project.

### Current Schema Inventory (as implemented)
- **Config.param.PARAM**: Canonical column registry for all CSVs/DataFrames.
  - Sections: BASE, SHARED, TRACKED, SCORED, SLEAP, POSE.
  - Each entry uses `ParamSpec` with fields: `label`, `tags`, `type`, `unit`, `role`, `domain`, `description`.
  - Strong validation: allowed sets for type/role/unit/tags; domain rules (binary, numeric range, categorical).
- **Config.experiment.EXPERIMENT**: Experiment paradigm and derived structures.
  - TypedDict schemas: `StimSpec`, `PeriodSpec` for declarative inputs.
  - Derived: seconds↔frames, period ordering/ranges, `STIMULI_DERIVED` checks, helpers.
- **Config.path.PATH**: Canonical folder tree, file suffix policy, pure path helpers.
- **Config.color.COLOR**: Color anchors, policies, colormaps, and resolvers.
- Data consumers
  - `BehaviorClassifier/utils/*`: policy-light helpers that should rely on Config for SSOT.

### Problems to Avoid
- Fragmented or duplicated definitions of the same field/meaning across modules.
- Silent fallbacks; unclear failure modes on malformed inputs.
- Inconsistent naming between files (e.g., tokens vs. labels vs. CSV columns).
- Weak typing of declarative config; unchecked dictionaries.

### Proposal: Standardize and Strengthen Schemas
1) Single source of truth (SSOT)
   - Keep schema and enumerations centralized in `Config.param` and experiment inputs/types in `Config.experiment`.
   - Prohibit duplicating column semantics elsewhere; consumers must reference `PARAM` and `EXPERIMENT`.

2) Typed, explicit declaratives
   - Retain `TypedDict` for `StimSpec`/`PeriodSpec`. Add `total=True` variants where appropriate to make required keys explicit.
   - For complex nested config (future), introduce additional `TypedDict`s rather than free-form dicts.

3) Naming conventions
   - CSV header names live under `PARAM.*` keys and their `label` fields; code should reference those names.
   - Keep roles/units consistent with consumer logic: e.g., all binary signals use role "binary" and domain `[0, 1]`.
   - Ensure `Config.experiment.STIMULI[...]['name']` values match `PARAM.SHARED` stimulus column keys.

4) Versioning and change control
   - Add an optional `SCHEMA_VERSION: str` in `Config.param` and bump on breaking changes.
   - Maintain a short CHANGELOG block in this guide documenting schema-impacting changes.

5) Validation posture
   - Keep fail-fast validations in `Config.param` and `Config.experiment` (already present).
   - Add cross-bundle checks during app startup (optional small validator) to verify alignment:
     - Every `STIMULI[name]` appears in `PARAM.SHARED` with role `binary` and domain `[0, 1]`.
     - Timebase constraints (`FRAME_RATE > 0`), period contiguity, and derived totals are already checked.

6) DataFrame-level schema checks (consumers)
   - Consumers should use `PARAM` to validate input tables:
     - Columns present, types parsable, and domains respected (binary/categorical/numeric ranges).
   - Provide light validators in `BehaviorClassifier/utils/validate.py` that accept `PARAM` entries to assert domains and uniqueness.

7) Structured access helpers
   - Provide small helpers that map `PARAM` to runtime constraints:
     - Example: lists of expected columns per file (`tracked`, `sleap`, `scored`, `pose`) derived from `tags`.
   - Add a function in `Config.param` report cell or a separate helper module that prints per-table minimal schemas for quick QA.

8) Consistent time and geometry conversions
   - Enforce consumption of `EXPERIMENT['FRAME_RATE']`, `ARENA_WIDTH_MM`, `ARENA_HEIGHT_MM` by geometry/kinematics helpers.
   - Keep all seconds↔frames conversions centralized in `Config.experiment` (already present).

9) Backwards compatibility and deprecation
   - When renaming columns or tags, keep a temporary alias map in `Config.param` REPORT section for user-facing notice only (no runtime aliasing).
   - Provide a migration checklist (below) when removing or changing semantics.

### Actionable Checklist for Adding/Changing Schemas
- Define or update entries in `Config.param`:
  - Add a `ParamSpec` in the correct section with `label`, `tags`, `type`, `unit`, `role`, `domain`, `description`.
  - Ensure `domain` is compliant with the role.
- If the change involves stimuli or timing, update `Config.experiment`:
  - Add/modify `STIMULI` settings; validate with detection pairs and trials semantics.
  - Keep `ALIGNMENT_STIM` consistent with registry and not ignored.
- Confirm column alignment across modules:
  - `STIMULI[name]` entries exist in `PARAM.SHARED` with binary, `[0, 1]`.
  - New scored columns have coherent units and roles.
- Update consumers:
  - Use `PARAM` to validate DataFrame inputs and `EXPERIMENT` for time/arena settings.
  - Keep helpers stateless and policy-light; avoid duplicating config values.
- Update docs:
  - Amend this guide and, if necessary, the quick-start notes in module REPORT cells.

### Example: Validating a tracked DataFrame with PARAM
```python
import pandas as pd
from Config.param import PARAM
from BehaviorClassifier.utils.validate import check_domain

def validate_tracked(df: pd.DataFrame) -> None:
	cols = ["FrameIndex", "NormalizedCentroidX", "NormalizedCentroidY", "PixelChange"]
	missing = [c for c in cols if c not in df]
	if missing:
		raise KeyError(f"Missing tracked columns: {missing}")

	# Apply domain checks from PARAM (examples)
	check_domain(df["NormalizedCentroidX"], min_value=0.0, max_value=1.0)
	check_domain(df["NormalizedCentroidY"], min_value=0.0, max_value=1.0)
```

### Future Enhancements
- Generate markdown schema docs from `PARAM` automatically (sectioned tables per file/tag).
- Optional strict runtime schema validator that maps `PARAM` to `pandas.api.types` checks.
- Add small `schema_diffs()` utility to compare current `PARAM` to a saved snapshot for PR reviews.

---
Ownership: Config is authoritative for schemas and policies; consumers must reference it rather than re-declaring values.


