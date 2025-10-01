## BehaviorClassifier Utils Segmentation Guide

This guide explains how to segment `BehaviorClassifier/_utils.py` into a `BehaviorClassifier/utils/` package with one module per cell, and how to expose a single immutable `BC_UTILS` bundle for backwards compatibility.

### Objectives
- **Parity**: Preserve the exact function behavior and public API keys seen in `_utils.py`.
- **Modularity**: Create one module per cell to improve discoverability and maintain SRP.
- **Back-compat**: Export `BC_UTILS` that mirrors the original nested keys.
- **Compliance**: Follow the repo's rules in `.cursor/rules/REFACTOR_GUIDE.mdc`.

### Target Layout
```
BehaviorClassifier/
  _utils.py                  # legacy (will be retired after migration)
  utils/
    __init__.py              # assembles BC_UTILS from segmented modules
    stimulus.py              # Cell 02 — STIMULUS
    labels.py                # Cell 03 — LABELS
    motion.py                # Cell 04 — MOTION
    geometry.py              # Cell 05 — GEOMETRY
    pose.py                  # Cell 06 — POSE
    alignment.py             # Cell 07 — ALIGNMENT
    validate.py              # Cell 08 — VALIDATE
    io.py                    # Cell 09 — IO
    format.py                # Cell 10 — FORMAT
docs/
  UTILS_SEGMENTATION_GUIDE.md
```

### Rules Recap (from REFACTOR_GUIDE)
- Tabs-only indentation; ≤ 100 chars/line; double quotes.
- One module docstring in Cell 00; `from __future__ import annotations` at top of Cell 01.
- Consolidate imports in Cell 01; standard → typing → third-party → local.
- Exactly one immutable public bundle per module (`MappingProxyType`).
- `__all__` lists only the bundle symbol for that module.

### Step-by-step
1) Create `BehaviorClassifier/utils/` and the modules listed above.
2) For each module:
   - Start with `#%% CELL 00 — HEADER & OVERVIEW` docstring summarizing scope and origin cell.
   - Add `#%% CELL 01 — IMPORTS` with consolidated imports.
   - Put the moved functions under `#%% CELL 03 — HELPERS / CORE LOGIC` with original docstrings and types.
   - End with `#%% CELL 04 — PUBLIC API`, e.g., `STIMULUS = MappingProxyType({...})` and `__all__ = ["STIMULUS"]`.
3) In `BehaviorClassifier/utils/__init__.py`, assemble:
   - Import each module’s bundle (e.g., `from .stimulus import STIMULUS`).
   - Build `_PUBLIC = {"stimulus": STIMULUS, ...}`.
   - Expose `BC_UTILS = MappingProxyType(_PUBLIC)` and `__all__ = ["BC_UTILS"]`.

### Migration Guidance
- New imports should prefer:
  ```python
  from BehaviorClassifier.utils import BC_UTILS
  speed = BC_UTILS["geometry"]["compute_speed_mm_per_s"](...)
  ```
- Alternatively, import per-domain bundle for clarity:
  ```python
  from BehaviorClassifier.utils.geometry import GEOMETRY
  speed = GEOMETRY["compute_speed_mm_per_s"](...)
  ```

### Backwards Compatibility
- Keep `BC_UTILS` keys identical to the original `_PUBLIC` structure:
  - `stimulus`, `labels`, `motion`, `geometry`, `pose`, `alignment`, `validate`, `io`, `format`.
- The function names within each sub-bundle must match legacy keys.

### Decommission Plan for `_utils.py`
- Phase 1: Introduce segmented modules and `utils/__init__.py` (done).
- Phase 2: Update imports across the codebase to use `BehaviorClassifier.utils`.
- Phase 3: Replace `BehaviorClassifier/_utils.py` references; leave a thin shim or removal:
  - Option A (shim): re-export `BC_UTILS` from `BehaviorClassifier.utils` to avoid breakage.
  - Option B (remove): delete `_utils.py` once all usages are migrated.

### QA Checklist
- Lint passes (tabs-only; imports used; types complete).
- Public bundles are immutable and single-export per module.
- Functional parity validated on representative datasets (stimulus onsets, speed, orientation, IO atomicity).

### Examples
```python
from BehaviorClassifier.utils import BC_UTILS

stim = BC_UTILS["stimulus"]["resolve_stim_detection"](df, "Stim").astype("Int64")
onset_idx = BC_UTILS["stimulus"]["onsets"](stim)

x_mm = BC_UTILS["geometry"]["norm_to_mm_x"](df["x"], arena_width_mm=100.0)
y_mm = BC_UTILS["geometry"]["norm_to_mm_y"](df["y"], arena_height_mm=100.0)
speed = BC_UTILS["geometry"]["compute_speed_mm_per_s"](x_mm, y_mm, frame_span_sec=0.02)
```

---
Maintainers: apply these steps to any future large helper modules using the same cell→module mapping pattern.


