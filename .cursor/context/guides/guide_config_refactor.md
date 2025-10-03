# Config Package Refactoring Guide

## ⚠️ CRITICAL: PRESERVE ALL EXISTING FUNCTIONALITY

**This refactoring is PURELY STRUCTURAL - we are NOT changing ANY functionality, constants, or behavior.**

- **`Codes_Before/`** = WORKING REFERENCE SYSTEM (cell-based, functional)
- **`Codes_Working/`** = CURRENT WORKING SYSTEM (partially modernized, functional)
- **Goal**: Transform cell structure → modern Python modules **WITHOUT CHANGING ANYTHING ELSE**

**We are NOT inventing, NOT forgetting, NOT modifying - only restructuring!**

---

## Overview

The **Config package** serves as the **Single Source of Truth (SSOT)** for all pipeline parameters in the fly behavior classification system. It provides four immutable bundles that centralize configuration across the entire codebase, ensuring reproducible scientific workflows and eliminating scattered magic numbers.

### Core Principle: Immutable Configuration Bundles

```python
from Config import PATH, PARAM, EXPERIMENT, COLOR

# All bundles are MappingProxyType - read-only and safe to share
experiment_duration = EXPERIMENT["EXPERIMENT_TOTAL_SECONDS"]  # ✅ Safe
PATH["pScored"] = new_path  # ❌ TypeError: 'mappingproxy' object does not support item assignment
```

### Scientific Rationale

**Reproducible Research**: Centralized configuration ensures that the same experimental parameters produce identical results across different runs, labs, and researchers.

---

## Current Architecture (WORKING SYSTEMS)

### Current Structure - What We Have Now
```
Codes_Before/Config/          # ✅ WORKING (cell-based)
├── __init__.py              # Exports PATH, PARAM, EXPERIMENT, COLOR
├── color.py                 # 689 lines - color schemes & visualization
├── experiment.py            # 358 lines - timing, stimuli, periods
├── param.py                 # 714 lines - column schemas & validation
└── path.py                  # 692 lines - file paths & I/O helpers

Codes_Working/Config/         # ✅ WORKING (partially modernized)
├── __init__.py              # Exports PATH, PARAM, EXPERIMENT, COLOR  
├── color.py                 # 1293 lines - enhanced color system
├── experiment.py            # 570 lines - enhanced timing system
├── param.py                 # 917 lines - enhanced validation
└── path.py                  # 647 lines - streamlined paths
```

### Current Cell Structure (PRESERVE ALL FUNCTIONALITY)

Each config file uses cell-based organization with `#%% CELL XX` markers:

**`color.py`** - Visual theming and color mapping
- **CELL 00**: Header & imports
- **CELL 01**: Constants (hex colors, matplotlib setup)
- **CELL 02**: Color mapping functions
- **CELL 03**: Colormap generation
- **CELL 04**: Public color resolvers
- **CELL 05**: Report generation

**`experiment.py`** - Temporal configuration  
- **CELL 00**: Header & timing constants
- **CELL 01**: Stimulus specifications
- **CELL 02**: Period definitions
- **CELL 03**: Frame conversion utilities
- **CELL 04**: Period lookup functions

**`param.py`** - Column schemas and validation
- **CELL 00**: Header & validation constants
- **CELL 01**: Column specifications
- **CELL 02**: Schema validation
- **CELL 03**: Domain checking
- **CELL 04**: Registry assembly

**`path.py`** - File system organization
- **CELL 00**: Header & path constants
- **CELL 01**: Base path definitions
- **CELL 02**: Path builders
- **CELL 03**: Glob utilities
- **CELL 04**: Validation helpers

---

## Planned Refactoring Structure

### Target Architecture
```
Codes/Config/                 # 🎯 TARGET (modern Python)
├── __init__.py              # Clean exports: PATH, PARAM, EXPERIMENT, COLOR
├── color.py                 # User interface - imports & delegates
├── experiment.py            # User interface - imports & delegates  
├── param.py                 # User interface - imports & delegates
├── path.py                  # User interface - imports & delegates
├── color/                   # Logic modules (from color.py cells)
│   ├── __init__.py         # Exports for color.py
│   ├── constants.py        # CELL 01 → hex colors, matplotlib setup
│   ├── mapping.py          # CELL 02 → color mapping functions
│   ├── colormaps.py        # CELL 03 → colormap generation
│   ├── resolvers.py        # CELL 04 → public color resolvers
│   └── reports.py          # CELL 05 → report generation
├── experiment/             # Logic modules (from experiment.py cells)
│   ├── __init__.py         # Exports for experiment.py
│   ├── timing.py           # CELL 00 → timing constants
│   ├── stimuli.py          # CELL 01 → stimulus specifications
│   ├── periods.py          # CELL 02 → period definitions
│   ├── conversions.py      # CELL 03 → frame conversion utilities
│   └── lookups.py          # CELL 04 → period lookup functions
├── param/                  # Logic modules (from param.py cells)
│   ├── __init__.py         # Exports for param.py
│   ├── constants.py        # CELL 00 → validation constants
│   ├── schemas.py          # CELL 01 → column specifications
│   ├── validation.py       # CELL 02 → schema validation
│   ├── domains.py          # CELL 03 → domain checking
│   └── registry.py         # CELL 04 → registry assembly
└── path/                   # Logic modules (from path.py cells)
    ├── __init__.py         # Exports for path.py
    ├── constants.py        # CELL 00 → path constants
    ├── base.py             # CELL 01 → base path definitions
    ├── builders.py         # CELL 02 → path builders
    ├── globs.py            # CELL 03 → glob utilities
    └── validation.py       # CELL 04 → validation helpers
```

### User Interface Pattern

Each top-level config file becomes a clean interface:

```python
# Config/color.py (NEW - user interface)
"""
Color configuration for the behavior classification pipeline.
User-friendly interface that delegates to internal modules.
"""

# Import all functionality from submodules
from .color.constants import *
from .color.mapping import *
from .color.colormaps import *
from .color.resolvers import *
from .color.reports import *

# Re-export the main COLOR bundle
from .color import COLOR

# When run directly, show color report
if __name__ == "__main__":
    render_color_report()
```

---

## Module Breakdown

### 1. COLOR Module (color.py → color/)

**Current Responsibilities** (PRESERVE ALL):
- Hex color constants for all behavior labels
- Matplotlib colormap generation
- Color resolvers for visualization
- Theme management and color reports

**Current User Inputs** (PRESERVE ALL):
```python
# From Codes_Working/Config/color.py - KEEP EXACTLY AS-IS
MOTION_SPEED_DECISIONS = {
    "plateau_end": 15.0,        # mm/s where plateau ends
    "over_color": "#FF0000",    # color for speeds > plateau
    # ... all other constants
}

BEHAVIOR_COLORS = {
    "Jump": "#FF6B35",
    "Walk": "#2E8B57", 
    # ... all behavior mappings
}
```

**Refactoring Benefits**:
- Separate colormap generation from color constants
- Isolate matplotlib dependencies
- Cleaner testing of color logic

### 2. EXPERIMENT Module (experiment.py → experiment/)

**Current Responsibilities** (PRESERVE ALL):
- Frame rate and timing constants
- Stimulus channel specifications
- Experimental period definitions
- Frame ↔ seconds conversion utilities

**Current User Inputs** (PRESERVE ALL):
```python
# From Codes_Working/Config/experiment.py - KEEP EXACTLY AS-IS
FRAME_RATE = 30.0  # fps

STIMULI = {
    "VisualStim": {
        "name": "VisualStim",
        "trials": 10,
        "duration_sec": 1.0,
        "detection": (0, 1),
    },
    # ... all stimulus definitions
}

EXPERIMENTAL_PERIODS = {
    "Baseline": {"duration_sec": 120.0},
    "Experiment": {"duration_sec": 600.0}, 
    "Recovery": {"duration_sec": 120.0},
}
```

**Refactoring Benefits**:
- Separate timing logic from stimulus definitions
- Isolate frame conversion utilities
- Better organization of period calculations

### 3. PARAM Module (param.py → param/)

**Current Responsibilities** (PRESERVE ALL):
- Column schema definitions for all CSV types
- Data type and domain validation
- Schema registry assembly
- Validation error reporting

**Current User Inputs** (PRESERVE ALL):
```python
# From Codes_Working/Config/param.py - KEEP EXACTLY AS-IS
# All column definitions, validation rules, domains
# Every ParamSpec entry must be preserved exactly
```

**Refactoring Benefits**:
- Separate schema definitions from validation logic
- Isolate domain checking utilities
- Cleaner registry assembly process

### 4. PATH Module (path.py → path/)

**Current Responsibilities** (PRESERVE ALL):
- Base directory structure
- File naming conventions and suffixes
- Path builder functions
- Glob utilities for file discovery

**Current User Inputs** (PRESERVE ALL):
```python
# From Codes_Working/Config/path.py - KEEP EXACTLY AS-IS
# All path constants, suffixes, builders
# Every path function must work identically
```

**Refactoring Benefits**:
- Separate path constants from builders
- Isolate file system utilities
- Better organization of glob functions

---

## Implementation Strategy

### Phase 1: Analysis & Preservation
1. **Document every constant, function, and behavior** from working systems
2. **Create comprehensive test suite** to verify identical behavior
3. **Map each cell to target module** with exact functionality preservation

### Phase 2: Module Creation
1. **Create submodule structure** (color/, experiment/, param/, path/)
2. **Move cell contents** to appropriate modules **without modification**
3. **Ensure all imports and dependencies** work identically

### Phase 3: Interface Layer
1. **Create clean top-level interfaces** (color.py, experiment.py, etc.)
2. **Import and re-export** all functionality from submodules
3. **Verify identical public API** - no breaking changes

### Phase 4: Validation
1. **Run full test suite** - everything must work identically
2. **Test all import patterns** used by BehaviorClassifier
3. **Verify all constants and functions** produce same results

---

## Critical Success Criteria

### ✅ Functional Preservation
- **Every constant** has identical value
- **Every function** produces identical output
- **Every import** works exactly as before
- **All existing code** continues to work without changes

### ✅ API Compatibility  
- `from Config import PATH, PARAM, EXPERIMENT, COLOR` - unchanged
- All function signatures - unchanged
- All return values - unchanged
- All side effects - unchanged

### ✅ Performance Preservation
- Import times - no significant regression
- Memory usage - no significant increase
- Function performance - identical or better

---

## Testing Strategy

### Before Refactoring
```python
# Capture current behavior
import Config
original_path = Config.PATH.copy()
original_param = Config.PARAM.copy()
# ... capture all bundles and test all functions
```

### After Refactoring
```python
# Verify identical behavior
import Config
assert Config.PATH == original_path
assert Config.PARAM == original_param
# ... verify all bundles and test all functions
```

### Comprehensive Test Coverage
- **All constants** - exact value matching
- **All functions** - input/output verification
- **All imports** - compatibility testing
- **Integration tests** - full pipeline verification

---

## Risk Mitigation

### Backup Strategy
- Keep `Codes_Before/` and `Codes_Working/` as reference
- Create `Codes_Backup/` before any changes
- Incremental commits with rollback capability

### Validation Checkpoints
- Test after each module creation
- Verify imports at each step
- Run integration tests frequently
- Document any discovered dependencies

### Rollback Plan
- Clear criteria for success/failure
- Automated rollback scripts
- Preserved working systems as fallback
- Staged deployment approach

---

This refactoring transforms the Config package from cell-based to modern Python modules while preserving every aspect of the current working functionality. The result will be more maintainable, testable, and extensible code that serves as a solid foundation for the scientific pipeline.
