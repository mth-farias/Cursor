# Config/experiment.py Refactoring Guide

## ⚠️ CRITICAL: PRESERVE ALL EXISTING FUNCTIONALITY

**This refactoring is PURELY STRUCTURAL - we are NOT changing ANY functionality, constants, or behavior.**

- **Source**: `Codes_Working/Config/experiment.py` (570 lines, 6 cells) - WORKING REFERENCE
- **Goal**: Transform cell structure → modern Python modules **WITHOUT CHANGING ANYTHING ELSE**
- **API Compatibility**: All imports `from Config import EXPERIMENT` must work identically

---

## Current Usage Analysis

### How EXPERIMENT is Used Across the Codebase

**Import Pattern (PRESERVE EXACTLY):**
```python
from Config import EXPERIMENT  # Used in 7+ modules
```

**Key Usage Patterns (MUST REMAIN IDENTICAL):**
```python
# Frame rate access
NOISE_TOLERANCE = int(EXPERIMENT["NOISE_TOLERANCE"])
FRAME_RATE = EXPERIMENT["FRAME_RATE"]

# Time conversion functions
frames = EXPERIMENT["seconds_to_frames"](seconds)
seconds = EXPERIMENT["frames_to_seconds"](frames)

# Period queries
period_name = EXPERIMENT["period_by_frame"](frame_idx)
is_in_period = EXPERIMENT["in_period"]("Baseline", frame_idx)

# Experimental structure
total_frames = EXPERIMENT["EXPERIMENT_TOTAL_FRAMES"]
periods = EXPERIMENT["PERIODS_DERIVED"]
stimuli = EXPERIMENT["STIMULI_DERIVED"]
```

**Critical Dependencies:**
- **BehaviorClassifier modules**: `_classifier.py`, `_main.py`, `_utils.py`, `_qc_error_flag.py`, `_colab.py`
- **Colab notebooks**: `BehaviorClassifier_Run.ipynb`
- **All modules expect**: `MappingProxyType` immutable bundle with exact same keys and functions

---

## Current Structure Analysis (570 lines, 6 cells)

### CELL 00 — HEADER & OVERVIEW (Lines 1-16)
**Content**: Module docstring and overview
**Target**: Will be distributed across module docstrings
**Dependencies**: None

### CELL 01 — IMPORTS & TYPES (Lines 18-50)
**Content**: 
- `from __future__ import annotations`
- Standard library imports (`MappingProxyType`, `TypedDict`, `Optional`, `Tuple`)
- Third-party imports (`numpy`)
- Type definitions (`StimSpec`, `PeriodSpec`)

**Target Module**: `experiment/types.py`
**Dependencies**: None (foundational)

### CELL 02 — USER INPUT (Lines 52-165)
**Content**: All user-configurable constants
- **CELL 02.1**: Identity & Grouping (lines 65-90)
  - `POSE_SCORING`, `FILENAME_STRUCTURE`, `GROUP_IDENTIFIER`, `GROUPS`
- **CELL 02.2**: Stimulus Registry (lines 92-133)
  - `ALIGNMENT_STIM`, `STIMULI`
- **CELL 02.3**: Period Schedule (lines 136-148)
  - `EXPERIMENTAL_PERIODS`
- **CELL 02.4**: Timebase & Arena (lines 151-165)
  - `NOISE_TOLERANCE`, `FRAME_RATE`, `ARENA_WIDTH_MM`, `ARENA_HEIGHT_MM`

**Target Modules**: 
- `experiment/constants.py` (identity, timebase, arena)
- `experiment/stimuli.py` (stimulus registry)
- `experiment/periods.py` (period schedule)

**Dependencies**: None (pure constants)

### CELL 03 — DERIVED & VALIDATION (Lines 167-471)
**Content**: All computed values and validation logic
- **CELL 03.1**: Time Helpers (lines 177-237)
  - `SEC_PER_FRAME`, `seconds_to_frames()`, `frames_to_seconds()`
- **CELL 03.2**: Period Enrichment (lines 239-300)
  - Period validation, `PERIOD_ORDER`, `PERIOD_DUR_*`, `PERIODS_DERIVED`
- **CELL 03.3**: Stimulus Enrichment (lines 302-379)
  - Stimulus validation, `STIMULI_DERIVED`
- **CELL 03.4**: Period Query Helpers (lines 381-471)
  - `period_by_frame()`, `period_by_frames()`, `in_period()`

**Target Modules**:
- `experiment/conversions.py` (time conversion functions)
- `experiment/validation.py` (period and stimulus validation)
- `experiment/queries.py` (period lookup functions)

**Dependencies**: Constants from CELL 02, numpy

### CELL 04 — PUBLIC API (Lines 474-520)
**Content**: Assembly of the immutable EXPERIMENT bundle
- `_PUBLIC` dict with all exports
- `EXPERIMENT = MappingProxyType(_PUBLIC)`
- `__all__ = ["EXPERIMENT"]`

**Target Module**: `experiment/__init__.py`
**Dependencies**: All previous cells/modules

### CELL 05 — REPORT (Lines 522-570)
**Content**: Human-readable summary when run as `__main__`
- Prints experiment configuration
- Shows periods, stimuli, timing info

**Target Module**: `experiment/reports.py`
**Dependencies**: EXPERIMENT bundle

---

## Proposed Module Structure

### Target Architecture
```
Codes/Config/                  # 🎯 NEW TARGET LOCATION
├── experiment.py              # User interface & main controller
└── _experiment/               # Internal processing modules (private)
    ├── __init__.py           # Exports internal bundles to experiment.py
    ├── stimuli.py            # Stimulus validation & enrichment
    ├── periods.py            # Period validation & enrichment
    ├── time.py               # Time conversion & query utilities
    └── report.py             # Report generation functions
```

### Module Breakdown

#### 1. `experiment.py` (Main Controller & User Interface)
**Purpose**: Where users edit settings and the main EXPERIMENT bundle is created
**Content**:
- **CELL 00**: Header & Overview
- **CELL 01**: Imports & Types (`StimSpec`, `PeriodSpec` TypedDict definitions)
- **CELL 02**: User Input (All user-configurable constants from original CELL 02)
  - `POSE_SCORING`, `FILENAME_STRUCTURE`, `GROUP_IDENTIFIER`, `GROUPS`
  - `ALIGNMENT_STIM`, `STIMULI` 
  - `EXPERIMENTAL_PERIODS`
  - `NOISE_TOLERANCE`, `FRAME_RATE`, `ARENA_WIDTH_MM`, `ARENA_HEIGHT_MM`
- **CELL 03**: Processing (Import internal bundles and pass user settings)
- **CELL 04**: Public API (Create final EXPERIMENT bundle)
- **CELL 05**: Report (Call report functions when `__main__`)

**Dependencies**: Internal `_experiment` modules
**Exports**: `EXPERIMENT` (final bundle)

#### 2. `_experiment/__init__.py`
**Purpose**: Exports internal module bundles for experiment.py to use
**Content**:
```python
from .stimuli import _STIMULI
from .periods import _PERIODS  
from .time import _TIME
from .report import _REPORT

__all__ = ["_STIMULI", "_PERIODS", "_TIME", "_REPORT"]
```
**Exports**: Internal bundles for main controller

#### 3. `_experiment/stimuli.py`
**Purpose**: Stimulus validation and enrichment
**Content**:
- **CELL 00**: Header & Overview
- **CELL 01**: Imports
- **CELL 02**: Stimulus validation logic (from original CELL 03.3)
- **CELL 03**: Public API
**Takes**: User `STIMULI`, `ALIGNMENT_STIM` from parent
**Exports**: `_STIMULI` bundle with `STIMULI_DERIVED` and validation functions

#### 4. `_experiment/periods.py`
**Purpose**: Period validation and enrichment
**Content**:
- **CELL 00**: Header & Overview
- **CELL 01**: Imports
- **CELL 02**: Period validation logic (from original CELL 03.2)
- **CELL 03**: Public API
**Takes**: User `EXPERIMENTAL_PERIODS` from parent
**Exports**: `_PERIODS` bundle with `PERIOD_ORDER`, `PERIODS_DERIVED`, `EXPERIMENT_TOTAL_*`, etc.

#### 5. `_experiment/time.py`
**Purpose**: Time conversion and query utilities
**Content**:
- **CELL 00**: Header & Overview
- **CELL 01**: Imports
- **CELL 02**: Time conversion functions (from original CELL 03.1)
- **CELL 03**: Period query functions (from original CELL 03.4)
- **CELL 04**: Public API
**Takes**: User `FRAME_RATE` and period data from `_PERIODS`
**Exports**: `_TIME` bundle with `SEC_PER_FRAME`, `seconds_to_frames`, `frames_to_seconds`, `period_by_frame`, `period_by_frames`, `in_period`

#### 6. `_experiment/report.py`
**Purpose**: Report generation functions
**Content**:
- **CELL 00**: Header & Overview
- **CELL 01**: Imports
- **CELL 02**: Report functions (from original CELL 05)
- **CELL 03**: Public API
**Takes**: Complete EXPERIMENT bundle when called
**Exports**: `_REPORT` bundle with report functions

---

## Pre-Implementation Requirements

### 📚 Complete Project Overview (MANDATORY)

**Before making ANY changes, read and understand ALL project context:**

#### 1. Project Standards & Guidelines
- **`.cursor/rules/`** - All coding standards and rules:
  - `.cursorrules.mdc` - Core project philosophy and override system
  - `code_style.mdc` - Formatting, imports, naming, documentation standards
  - `modules.mdc` - Cell structure, organization patterns, public API design
  - `scientific.mdc` - Data validation, reproducibility, error handling
  - `performance.mdc` - Large datasets, monitoring, optimization guidelines

#### 2. Template Examples & Patterns
- **`.cursor/docs/examples/`** - Template examples for consistent implementation:
  - `cell_structure.py` - Standard cell-based organization patterns
  - `data_validation.py` - Scientific data validation templates
  - `error_handling.py` - Robust error handling patterns
  - `variables_and_functions.py` - Naming conventions and function templates

#### 3. Project Context & Prompts
- **`.cursor/docs/prompts/`** - Project initialization and context:
  - `cursor_starter_prompt.md` - Complete project overview and philosophy
  - `config_general_refactor.md` - Config package refactoring instructions

#### 4. Documentation & Guides
- **`.cursor/docs/guides/`** - Comprehensive project documentation:
  - `project_context.md` - Mission, architecture, development approach
  - `guide_config_refactor.md` - Overall Config refactoring strategy
  - `schemas_guide.md` - Data schema documentation
  - `utils_segmentation_guide.md` - Utility function organization

#### 5. Working Reference Systems (CRITICAL)
- **`Codes_Before/`** - Original working system (cell-based):
  - `Config/` - Original config modules (color.py, experiment.py, param.py, path.py)
  - `BehaviorClassifier/` - Classification engine modules
  - Study the cell structure, function signatures, and data flow

- **`Codes_Working/`** - Enhanced working system (partially modernized):
  - `Config/` - Improved config modules with better organization
  - `BehaviorClassifier/` - Enhanced classification modules
  - This is the PRIMARY REFERENCE for current functionality

#### 6. Data Examples & Structure
- **`ExampleFiles/`** - Real data samples showing input/output formats:
  - `BASE.csv.csv` - Base tracking data format
  - `pose.csv.csv` - Pose estimation data format
  - `scored.csv.csv` - Behavior classification results format
  - `sleap.csv.csv` - SLEAP body-parts data format
  - `tracked.csv.csv` - Movement tracking data format

### 🎯 Understanding Requirements

**After reading all files, you must understand:**

1. **Project Mission**: Automated fly behavior classification for scientific research
2. **Development Philosophy**: Quality over speed, scientific rigor, flexible rule override system
3. **Code Standards**: Modern Python with complete type hints, scientific validation, immutable APIs
4. **Cell Structure**: Current organization pattern that needs to be preserved functionally
5. **Data Flow**: How tracking data flows through classification to produce behavior labels
6. **API Contracts**: Exact function signatures and return values that must be preserved
7. **Scientific Context**: Biological significance of parameters and validation requirements
8. **Performance Requirements**: Must handle 1000+ flies efficiently
9. **Error Handling**: Robust scientific workflows with graceful degradation
10. **Testing Philosophy**: Comprehensive validation with baseline comparison

### ❓ Mandatory Questions Before Starting

**If ANY of these are unclear after reading all files, STOP and ASK:**

1. "I've read all the project files. Should I proceed with the refactoring as outlined in this guide?"
2. "Are there any specific aspects of the current `experiment.py` implementation that need special attention?"
3. "Should I preserve the exact cell comments and structure in the refactored modules?"
4. "Are there any performance-critical sections that should not be modified?"
5. "Should I maintain backward compatibility with any specific import patterns?"

---

## Implementation Strategy

### Phase 1: Create Module Structure
1. **Create target directory**: `Codes/Config/_experiment/`
2. **Create empty modules**: All 5 target modules with basic cell structure
3. **Verify imports**: Ensure all modules can import their dependencies

### Phase 2: Move Content (Functionally Organized)
1. **`_experiment/stimuli.py`**: Move CELL 02.2 + CELL 03.3 content (stimulus registry + validation)
2. **`_experiment/periods.py`**: Move CELL 02.3 + CELL 03.2 content (period schedule + validation)
3. **`_experiment/time.py`**: Move CELL 03.1 + CELL 03.4 content (time conversions + queries)
4. **`_experiment/report.py`**: Move CELL 05 content (report functions)
5. **`_experiment/__init__.py`**: Create exports for internal bundles

### Phase 3: Create Main Controller
1. **`Codes/Config/experiment.py`**: 
   - Move CELL 01 (types) + CELL 02 (user constants) exactly as-is
   - Add CELL 03 (processing) to import internal bundles
   - Modify CELL 04 (public API) to create final EXPERIMENT bundle
   - Keep CELL 05 (report) to call report functions
2. **Update `Codes/Config/__init__.py`**: Ensure imports work
3. **Test imports**: Verify `from Config import EXPERIMENT` works

### Phase 4: Comprehensive Validation & Safety Checks
1. **Pre-refactoring baseline capture**
2. **Functional preservation verification**
3. **Integration testing**
4. **Compliance verification**
5. **Performance testing**
6. **Detailed change reporting**

### Phase 5: Documentation & Change Tracking
1. **Create comprehensive change log**
2. **Document all modifications made**
3. **Record rationale for each decision**
4. **Create future reference guide**

---

## Safety Checks & Validation Protocol

### 🛡️ Pre-Refactoring Baseline Capture

Before making any changes, capture the complete baseline:

```python
# Create validation script: validate_experiment_refactor.py
import pickle
import json
from types import MappingProxyType
from Codes_Working.Config import experiment

# Capture original EXPERIMENT bundle
original_experiment = dict(experiment.EXPERIMENT)

# Save baseline for comparison
with open('experiment_baseline.pkl', 'wb') as f:
    pickle.dump(original_experiment, f)

# Capture all constants separately
baseline_constants = {
    'POSE_SCORING': experiment.POSE_SCORING,
    'FILENAME_STRUCTURE': experiment.FILENAME_STRUCTURE,
    'GROUP_IDENTIFIER': experiment.GROUP_IDENTIFIER,
    'GROUPS': experiment.GROUPS,
    'ALIGNMENT_STIM': experiment.ALIGNMENT_STIM,
    'STIMULI': experiment.STIMULI,
    'EXPERIMENTAL_PERIODS': experiment.EXPERIMENTAL_PERIODS,
    'NOISE_TOLERANCE': experiment.NOISE_TOLERANCE,
    'FRAME_RATE': experiment.FRAME_RATE,
    'ARENA_WIDTH_MM': experiment.ARENA_WIDTH_MM,
    'ARENA_HEIGHT_MM': experiment.ARENA_HEIGHT_MM,
}

# Test all functions with sample inputs
function_tests = {
    'seconds_to_frames': {
        'inputs': [1.0, 2.5, [1.0, 2.0, 3.0]],
        'outputs': []
    },
    'frames_to_seconds': {
        'inputs': [60, 150, [60, 120, 180]],
        'outputs': []
    },
    'period_by_frame': {
        'inputs': [0, 100, 1000],
        'outputs': []
    },
    'in_period': {
        'inputs': [('Baseline', 100), ('Stimulation', 500)],
        'outputs': []
    }
}

# Execute function tests
for func_name, test_data in function_tests.items():
    func = experiment.EXPERIMENT[func_name]
    for input_val in test_data['inputs']:
        if isinstance(input_val, tuple):
            result = func(*input_val)
        else:
            result = func(input_val)
        test_data['outputs'].append(result)

# Save all baseline data
baseline_data = {
    'constants': baseline_constants,
    'function_tests': function_tests,
    'derived_structures': {
        'PERIOD_ORDER': list(experiment.EXPERIMENT['PERIOD_ORDER']),
        'PERIODS_DERIVED': dict(experiment.EXPERIMENT['PERIODS_DERIVED']),
        'STIMULI_DERIVED': dict(experiment.EXPERIMENT['STIMULI_DERIVED']),
        'EXPERIMENT_TOTAL_FRAMES': experiment.EXPERIMENT['EXPERIMENT_TOTAL_FRAMES'],
        'EXPERIMENT_TOTAL_SECONDS': experiment.EXPERIMENT['EXPERIMENT_TOTAL_SECONDS'],
    }
}

with open('experiment_baseline.json', 'w') as f:
    json.dump(baseline_data, f, indent=2, default=str)

print("✅ Baseline captured successfully")
```

### 🔍 Post-Refactoring Validation

After refactoring, run comprehensive validation:

```python
# Post-refactoring validation script
import pickle
import json
import numpy as np
from Codes.Config import experiment  # New refactored version

# Load baseline
with open('experiment_baseline.pkl', 'rb') as f:
    original_experiment = pickle.load(f)

with open('experiment_baseline.json', 'r') as f:
    baseline_data = json.load(f)

# Compare new EXPERIMENT bundle
new_experiment = dict(experiment.EXPERIMENT)

# CRITICAL: Verify all keys are identical
missing_keys = set(original_experiment.keys()) - set(new_experiment.keys())
extra_keys = set(new_experiment.keys()) - set(original_experiment.keys())

if missing_keys:
    raise ValueError(f"❌ MISSING KEYS: {missing_keys}")
if extra_keys:
    raise ValueError(f"❌ EXTRA KEYS: {extra_keys}")

# CRITICAL: Verify all constants are identical
for const_name, original_value in baseline_data['constants'].items():
    new_value = getattr(experiment, const_name, None)
    if new_value != original_value:
        raise ValueError(f"❌ CONSTANT CHANGED: {const_name}")
    print(f"✅ {const_name}: IDENTICAL")

# CRITICAL: Verify all functions produce identical outputs
for func_name, test_data in baseline_data['function_tests'].items():
    func = experiment.EXPERIMENT[func_name]
    for i, input_val in enumerate(test_data['inputs']):
        if isinstance(input_val, tuple):
            new_result = func(*input_val)
        else:
            new_result = func(input_val)
        
        original_result = test_data['outputs'][i]
        
        # Handle numpy arrays
        if isinstance(new_result, np.ndarray):
            if not np.array_equal(new_result, np.array(original_result)):
                raise ValueError(f"❌ FUNCTION OUTPUT CHANGED: {func_name}({input_val})")
        else:
            if new_result != original_result:
                raise ValueError(f"❌ FUNCTION OUTPUT CHANGED: {func_name}({input_val})")
    
    print(f"✅ {func_name}: ALL OUTPUTS IDENTICAL")

# CRITICAL: Verify derived structures are identical
for struct_name, original_value in baseline_data['derived_structures'].items():
    new_value = experiment.EXPERIMENT[struct_name]
    
    if isinstance(new_value, np.ndarray):
        if not np.array_equal(new_value, np.array(original_value)):
            raise ValueError(f"❌ DERIVED STRUCTURE CHANGED: {struct_name}")
    elif isinstance(new_value, (dict, MappingProxyType)):
        if dict(new_value) != original_value:
            raise ValueError(f"❌ DERIVED STRUCTURE CHANGED: {struct_name}")
    else:
        if new_value != original_value:
            raise ValueError(f"❌ DERIVED STRUCTURE CHANGED: {struct_name}")
    
    print(f"✅ {struct_name}: IDENTICAL")

print("🎉 ALL VALIDATION CHECKS PASSED!")
```

### 📋 Compliance Verification Checklist

**Before submitting refactored code, verify compliance with `.cursor/rules/` and `.cursor/docs/examples/`:**

#### Code Style Compliance (`.cursor/rules/code_style.mdc`)
- [ ] **Type hints**: All functions have complete type annotations
- [ ] **Docstrings**: All public functions have Google-style docstrings
- [ ] **Import organization**: Standard → typing → third-party → local
- [ ] **Naming conventions**: snake_case variables, ALL_CAPS constants, PascalCase classes
- [ ] **Line length**: Maximum 88 characters
- [ ] **Error handling**: Descriptive error messages, no silent failures

#### Module Structure Compliance (`.cursor/rules/modules.mdc`)
- [ ] **Cell structure**: Each module follows consistent cell organization
- [ ] **Public API**: Exactly one immutable bundle per module (`MappingProxyType`)
- [ ] **Import safety**: ROOT path setup for absolute imports
- [ ] **No stray globals**: Clean public API with `__all__`

#### Scientific Computing Compliance (`.cursor/rules/scientific.mdc`)
- [ ] **Data validation**: Rigorous validation of all inputs
- [ ] **Reproducibility**: Same inputs produce same outputs
- [ ] **Error recovery**: Graceful handling of edge cases
- [ ] **Domain context**: Comments explain biological/scientific significance

#### Performance Compliance (`.cursor/rules/performance.mdc`)
- [ ] **Vectorization**: Use NumPy operations where appropriate
- [ ] **Memory efficiency**: Avoid unnecessary copies
- [ ] **Import performance**: No significant regression in load times

### 🚨 When in Doubt Protocol

**If ANY of the following situations arise, STOP and ASK for clarification:**

1. **Ambiguous cell boundaries**: If it's unclear where to split content between modules
2. **Dependency conflicts**: If circular imports or complex dependencies emerge
3. **Function signature questions**: If unsure about preserving exact function interfaces
4. **Performance concerns**: If refactoring might impact critical performance paths
5. **Type annotation uncertainties**: If complex types need clarification
6. **Error handling decisions**: If unsure about preserving exact error behavior
7. **Import pattern changes**: If the refactoring affects how other modules import

**Questions to ask:**
- "Should this function signature be preserved exactly?"
- "Is it acceptable to change the internal implementation if the output is identical?"
- "Should this validation logic be moved or kept in place?"
- "How should we handle this circular dependency?"

### 📊 Detailed Change Report Template

After refactoring, provide a comprehensive report:

```markdown
# Experiment.py Refactoring Report

## Summary
- **Files created**: X new files
- **Lines of code**: Original XXX → New XXX (net change: +/-XX)
- **Functions moved**: X functions relocated
- **Constants preserved**: X/X constants identical

## File Structure Changes
### Before:
- `experiment.py` (570 lines, 6 cells)

### After:
- `experiment.py` (XXX lines, 5 cells) - Main controller
- `_experiment/__init__.py` (XX lines) - Bundle exports
- `_experiment/stimuli.py` (XX lines, 3 cells) - Stimulus processing
- `_experiment/periods.py` (XX lines, 3 cells) - Period processing
- `_experiment/time.py` (XX lines, 4 cells) - Time utilities
- `_experiment/report.py` (XX lines, 3 cells) - Report functions

## Content Migration Map
- **CELL 01** (Types) → `experiment.py` CELL 01
- **CELL 02.1** (Identity) → `experiment.py` CELL 02
- **CELL 02.2** (Stimuli) → `experiment.py` CELL 02 + `_experiment/stimuli.py`
- **CELL 02.3** (Periods) → `experiment.py` CELL 02 + `_experiment/periods.py`
- **CELL 02.4** (Timebase) → `experiment.py` CELL 02
- **CELL 03.1** (Time helpers) → `_experiment/time.py`
- **CELL 03.2** (Period enrichment) → `_experiment/periods.py`
- **CELL 03.3** (Stimulus enrichment) → `_experiment/stimuli.py`
- **CELL 03.4** (Period queries) → `_experiment/time.py`
- **CELL 04** (Public API) → `experiment.py` CELL 04 (modified)
- **CELL 05** (Report) → `_experiment/report.py` + `experiment.py` CELL 05

## Validation Results
- ✅ All constants preserved: XX/XX identical
- ✅ All functions preserved: XX/XX identical outputs
- ✅ All derived structures preserved: XX/XX identical
- ✅ Integration tests passed: XX/XX modules work
- ✅ Performance tests passed: Import time change: +/-X%

## Compliance Verification
- ✅ Code style rules: All checks passed
- ✅ Module structure rules: All checks passed
- ✅ Scientific computing rules: All checks passed
- ✅ Performance rules: All checks passed

## Risk Assessment
- **Low risk**: No breaking changes detected
- **Dependencies**: All existing imports work unchanged
- **Rollback**: Original file preserved as backup
```

---

## 🎯 Implementation Clarifications (From Development Interaction)

### Directory Structure & Validation
- **Target Location**: `Codes/Config/` (confirmed)
- **Validation Scripts**: Place in `.cursor/validation/` (development phase only)
- **Implementation Approach**: Complete all phases in one go, then review process

### Code Style & Structure  
- **Cell Comments**: Keep `#%% CELL XX —` style (developer preference)
- **Modernization**: Follow patterns from `.cursor/docs/examples/cell_structure.py`
- **Docstrings**: Use modern Python docstrings alongside cell structure

### Dependencies & Compatibility
- **Import Analysis**: Must examine current usage patterns before refactoring
- **Fresh Start**: No backward compatibility constraints - can improve patterns
- **Performance**: Only functionality preservation is critical, everything else can be modernized

### Error Handling Protocol
- **Stop and Ask**: For any ambiguities, unclear cell boundaries, or complex dependencies
- **Document Decisions**: Record all choices made during implementation
- **Conservative Approach**: When in doubt, preserve exact behavior and ask for guidance

### Key Questions to Address Before Starting
1. **Current Import Patterns**: How do other modules import from experiment.py?
2. **Dependency Chain**: What circular import risks exist?
3. **Cell Boundaries**: Are there any ambiguous splits between cells?
4. **Critical Sections**: Any performance-sensitive code that needs special attention?

---

## 📋 Change Tracking & Documentation

### Mandatory Change Log Creation

**After completing the refactoring, create a comprehensive change log:**

**File**: `.cursor/docs/guides/refactored/config_experiment.md`

**Target Location**: `Codes/Config/` (new modernized home)

**Required Content:**
```markdown
# Config/experiment.py Refactoring Change Log

## Refactoring Summary
- **Date**: [YYYY-MM-DD]
- **Original File**: `Codes_Working/Config/experiment.py` (570 lines, 6 cells)
- **Refactored Structure**: `Codes/Config/experiment.py` + `Codes/Config/_experiment/` modules
- **Total Files Created**: [X] new files
- **Total Lines**: [XXX] lines (net change: +/-XX)

## File Structure Changes

### Before Refactoring
```
Codes_Working/Config/experiment.py (570 lines, 6 cells)
```

### After Refactoring
```
Codes/Config/
├── experiment.py (XXX lines, 5 cells) - Main controller & user interface
└── _experiment/
    ├── __init__.py (XX lines) - Internal bundle exports
    ├── stimuli.py (XX lines, 3 cells) - Stimulus processing
    ├── periods.py (XX lines, 3 cells) - Period processing  
    ├── time.py (XX lines, 4 cells) - Time utilities
    └── report.py (XX lines, 3 cells) - Report functions
```

## Detailed Content Migration

### CELL 00 — HEADER & OVERVIEW
- **Original Location**: Lines 1-16
- **New Location**: Distributed across module docstrings
- **Changes**: Split overview across relevant modules
- **Rationale**: Each module now has focused documentation

### CELL 01 — IMPORTS & TYPES  
- **Original Location**: Lines 18-50
- **New Location**: `experiment.py` CELL 01
- **Changes**: TypedDict definitions preserved exactly
- **Rationale**: Types remain in main user interface file

### CELL 02 — USER INPUT
- **Original Location**: Lines 52-165 (4 sub-cells)
- **New Location**: `experiment.py` CELL 02
- **Changes**: All user constants preserved in main file
- **Rationale**: Users edit settings in one central location

#### CELL 02.1 — Identity & Grouping (Lines 65-90)
- **Constants**: `POSE_SCORING`, `FILENAME_STRUCTURE`, `GROUP_IDENTIFIER`, `GROUPS`
- **Migration**: → `experiment.py` CELL 02
- **Changes**: None (preserved exactly)

#### CELL 02.2 — Stimulus Registry (Lines 92-133)  
- **Constants**: `ALIGNMENT_STIM`, `STIMULI`
- **Migration**: → `experiment.py` CELL 02
- **Changes**: None (preserved exactly)
- **Processing Logic**: → `_experiment/stimuli.py`

#### CELL 02.3 — Period Schedule (Lines 136-148)
- **Constants**: `EXPERIMENTAL_PERIODS`
- **Migration**: → `experiment.py` CELL 02  
- **Changes**: None (preserved exactly)
- **Processing Logic**: → `_experiment/periods.py`

#### CELL 02.4 — Timebase & Arena (Lines 151-165)
- **Constants**: `NOISE_TOLERANCE`, `FRAME_RATE`, `ARENA_WIDTH_MM`, `ARENA_HEIGHT_MM`
- **Migration**: → `experiment.py` CELL 02
- **Changes**: None (preserved exactly)

### CELL 03 — DERIVED & VALIDATION
- **Original Location**: Lines 167-471 (4 sub-cells)
- **New Location**: Split across `_experiment/` modules
- **Changes**: Logic preserved, organized by function
- **Rationale**: Better separation of concerns

#### CELL 03.1 — Time Helpers (Lines 177-237)
- **Functions**: `SEC_PER_FRAME`, `seconds_to_frames()`, `frames_to_seconds()`
- **Migration**: → `_experiment/time.py` CELL 02
- **Changes**: Function signatures preserved exactly
- **Rationale**: Time conversion utilities grouped together

#### CELL 03.2 — Period Enrichment (Lines 239-300)
- **Logic**: Period validation, `PERIOD_ORDER`, `PERIOD_DUR_*`, `PERIODS_DERIVED`
- **Migration**: → `_experiment/periods.py` CELL 02
- **Changes**: Validation logic preserved exactly
- **Rationale**: Period processing isolated for maintainability

#### CELL 03.3 — Stimulus Enrichment (Lines 302-379)
- **Logic**: Stimulus validation, `STIMULI_DERIVED`
- **Migration**: → `_experiment/stimuli.py` CELL 02
- **Changes**: Validation logic preserved exactly
- **Rationale**: Stimulus processing isolated for maintainability

#### CELL 03.4 — Period Query Helpers (Lines 381-471)
- **Functions**: `period_by_frame()`, `period_by_frames()`, `in_period()`
- **Migration**: → `_experiment/time.py` CELL 03
- **Changes**: Function signatures preserved exactly
- **Rationale**: Query functions grouped with time utilities

### CELL 04 — PUBLIC API
- **Original Location**: Lines 474-520
- **New Location**: `experiment.py` CELL 04 (modified)
- **Changes**: Now imports from `_experiment` modules and assembles final bundle
- **Rationale**: Main controller orchestrates internal modules

### CELL 05 — REPORT
- **Original Location**: Lines 522-570
- **New Location**: Split between `_experiment/report.py` and `experiment.py` CELL 05
- **Changes**: Report functions moved to dedicated module, main file calls them
- **Rationale**: Report logic isolated, main file provides interface

## Function Signature Preservation

### Time Conversion Functions
- `seconds_to_frames(seconds: float) -> int | np.ndarray` - **PRESERVED**
- `frames_to_seconds(frames: int | np.ndarray) -> float | np.ndarray` - **PRESERVED**

### Period Query Functions  
- `period_by_frame(frame: int) -> str` - **PRESERVED**
- `period_by_frames(frames: np.ndarray) -> np.ndarray` - **PRESERVED**
- `in_period(name: str, frame: int) -> bool` - **PRESERVED**

### All Constants
- Every constant value preserved exactly as in original file
- No changes to any numerical values, strings, or data structures

## Data Flow Changes

### Original Flow
```
experiment.py (monolithic) → EXPERIMENT bundle
```

### New Flow
```
experiment.py (user settings) 
    ↓
_experiment/stimuli.py (validates STIMULI → _STIMULI)
_experiment/periods.py (validates PERIODS → _PERIODS)  
_experiment/time.py (creates time functions → _TIME)
_experiment/report.py (creates report functions → _REPORT)
    ↓
_experiment/__init__.py (exports internal bundles)
    ↓
experiment.py (assembles final EXPERIMENT bundle)
```

## Validation Results

### Pre-Refactoring Baseline
- **Constants captured**: [XX/XX] all constants preserved
- **Function tests**: [XX/XX] all functions tested with sample inputs
- **Derived structures**: [XX/XX] all derived data captured

### Post-Refactoring Validation
- ✅ **All constants identical**: [XX/XX] values match exactly
- ✅ **All functions identical**: [XX/XX] outputs match exactly  
- ✅ **All derived structures identical**: [XX/XX] data structures match
- ✅ **Integration tests passed**: All BehaviorClassifier modules work
- ✅ **Performance tests passed**: Import time change: +/-X%

## Compliance Verification

### Code Style Compliance
- ✅ **Type hints**: All functions have complete type annotations
- ✅ **Docstrings**: All public functions have Google-style docstrings
- ✅ **Import organization**: Standard → typing → third-party → local
- ✅ **Naming conventions**: snake_case variables, ALL_CAPS constants
- ✅ **Line length**: Maximum 88 characters maintained
- ✅ **Error handling**: Descriptive error messages, no silent failures

### Module Structure Compliance  
- ✅ **Cell structure**: Each module follows consistent cell organization
- ✅ **Public API**: Exactly one immutable bundle per module (MappingProxyType)
- ✅ **Import safety**: ROOT path setup for absolute imports
- ✅ **No stray globals**: Clean public API with __all__

### Scientific Computing Compliance
- ✅ **Data validation**: Rigorous validation of all inputs preserved
- ✅ **Reproducibility**: Same inputs produce same outputs
- ✅ **Error recovery**: Graceful handling of edge cases maintained
- ✅ **Domain context**: Comments explain biological/scientific significance

### Performance Compliance
- ✅ **Vectorization**: NumPy operations preserved where used
- ✅ **Memory efficiency**: No unnecessary copies introduced
- ✅ **Import performance**: No significant regression in load times

## Decisions Made & Rationale

### 1. User Settings Location
- **Decision**: Keep all user-editable constants in main `experiment.py`
- **Rationale**: Single location for users to modify experiment parameters
- **Alternative Considered**: Distribute constants across modules (rejected for UX)

### 2. Private Module Structure
- **Decision**: Use `_experiment/` private package for internal logic
- **Rationale**: Clear separation between user interface and implementation
- **Alternative Considered**: Flat module structure (rejected for organization)

### 3. Data Flow Architecture
- **Decision**: Main controller imports internal bundles and assembles final bundle
- **Rationale**: Clear orchestration pattern, easy to understand and maintain
- **Alternative Considered**: Direct exports from internal modules (rejected for control)

### 4. Function Placement
- **Decision**: Group time functions together, separate from period processing
- **Rationale**: Time utilities are used across multiple contexts
- **Alternative Considered**: Keep all period-related code together (rejected for reusability)

## Future Maintenance Notes

### Adding New Stimulus Types
1. Edit `STIMULI` in `experiment.py` CELL 02
2. Validation logic in `_experiment/stimuli.py` will automatically handle it
3. No other changes needed

### Adding New Experimental Periods
1. Edit `EXPERIMENTAL_PERIODS` in `experiment.py` CELL 02  
2. Validation logic in `_experiment/periods.py` will automatically handle it
3. No other changes needed

### Modifying Time Conversion Logic
1. Edit functions in `_experiment/time.py`
2. Function signatures must remain identical
3. Test with validation script to ensure compatibility

### Adding New Report Features
1. Add functions to `_experiment/report.py`
2. Export in `_REPORT` bundle
3. Call from `experiment.py` CELL 05 when `__main__`

## Rollback Information

### Backup Locations
- **Original file**: `Codes_Working/Config/experiment.py` (preserved)
- **Git commit**: [commit-hash] before refactoring started
- **Validation baseline**: `experiment_baseline.pkl` and `experiment_baseline.json`

### Rollback Procedure
1. Delete new `Codes/Config/experiment.py` and `Codes/Config/_experiment/` directory
2. Copy `Codes_Working/Config/experiment.py` to `Codes/Config/experiment.py`  
3. Update `Codes/Config/__init__.py` imports if needed
4. Run validation script to confirm restoration

## Lessons Learned

### What Worked Well
- [Document successful approaches and techniques]

### Challenges Encountered  
- [Document any difficulties and how they were resolved]

### Recommendations for Future Refactoring
- [Document insights for refactoring other Config modules]

---

*This change log serves as a complete record of the experiment.py refactoring for future reference and maintenance.*
```

---

## Critical Success Criteria

### ✅ API Preservation
- `from Config import EXPERIMENT` - unchanged
- `EXPERIMENT["key"]` access - all keys identical
- `EXPERIMENT["function"](args)` calls - identical behavior
- `MappingProxyType` immutability - preserved

### ✅ Functional Preservation
- **Every constant**: Identical values
- **Every function**: Identical input/output behavior
- **Every validation**: Same error messages and conditions
- **All derived structures**: Identical arrays and dicts

### ✅ Dependency Compatibility
- **BehaviorClassifier modules**: No changes needed
- **Colab notebooks**: No changes needed
- **Import performance**: No significant regression

---

## Risk Mitigation

### Validation Strategy
1. **Before refactoring**: Capture all EXPERIMENT keys and values
2. **After each phase**: Verify identical behavior
3. **Integration tests**: Run BehaviorClassifier modules
4. **Performance tests**: Measure import times

### Rollback Plan
- Keep `Codes_Working/Config/experiment.py` as reference
- Incremental commits for each phase
- Clear success/failure criteria
- Automated rollback if tests fail

---

## Expected Benefits

### Maintainability
- **Clearer separation**: Each module has single responsibility
- **Easier testing**: Can test individual components
- **Better documentation**: Each module can have focused docs

### Extensibility
- **Add new periods**: Modify only `periods.py`
- **Add new stimuli**: Modify only `stimuli.py`
- **Enhance validation**: Modify only `validation.py`

### Performance
- **Lazy loading**: Only import needed components
- **Better caching**: Smaller modules load faster
- **Reduced memory**: Don't load unused functionality

---

## Data Flow Summary

### 🔄 Processing Flow
1. **User edits** constants in `Config/experiment.py` (CELL 02)
2. **Internal modules** in `_experiment/` process user inputs:
   - `stimuli.py` validates `STIMULI` → creates `STIMULI_DERIVED`
   - `periods.py` validates `EXPERIMENTAL_PERIODS` → creates `PERIODS_DERIVED`, `PERIOD_ORDER`, etc.
   - `time.py` uses `FRAME_RATE` → creates time conversion functions
   - `report.py` provides report functions
3. **`_experiment/__init__.py`** exports internal bundles (`_STIMULI`, `_PERIODS`, `_TIME`, `_REPORT`)
4. **`experiment.py`** imports internal bundles and creates final `EXPERIMENT` bundle
5. **Users import** `EXPERIMENT` from `Config.experiment`

### 🎯 Key Benefits
- **User-friendly**: All settings in one place (`experiment.py`)
- **Modular**: Internal processing separated by function
- **Private**: `_experiment` modules are implementation details
- **Clean API**: Single `EXPERIMENT` bundle export
- **Maintainable**: Each module has single responsibility

---

This refactoring transforms the experiment configuration from a monolithic cell-based file to a clean, functionally-organized modular structure while preserving every aspect of the current working functionality. The result will be more maintainable, testable, and extensible code that continues to serve as the authoritative timebase for the scientific pipeline.
