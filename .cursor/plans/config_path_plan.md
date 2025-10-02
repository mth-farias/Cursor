# Config path.py Refactoring Plan

## 🎯 **Mission: Apply Configuration Pattern to path.py**

Transform path.py using the proven configuration pattern, while handling file system operations, cross-platform compatibility, and path building utilities.

## 📊 **Module Analysis**

### **Current Structure Analysis**
```
Codes_Before/Config/path.py:    647 lines, 6 cells
Codes_Working/Config/path.py:   692 lines, 6 cells (enhanced version)
```

### **Complexity Assessment**
- **Moderate complexity**: File system operations, path building logic
- **Cross-platform considerations**: Windows/Linux/macOS compatibility
- **Dependencies**: None (standalone path utilities)
- **Processing**: Path building, glob operations, validation helpers

### **Cell Structure Analysis**
```
CELL 00: Header & Overview (85 lines) - Extensive documentation
CELL 01: Imports (10 lines) - pathlib, typing
CELL 02: Root Definition (20 lines) - Experiment root path
CELL 03: Base Paths (100+ lines) - Core directory definitions
CELL 04: Path Builders (200+ lines) - File path construction utilities
CELL 05: Glob Utilities (150+ lines) - File discovery and pattern matching
CELL 06: Validation Helpers (100+ lines) - Path validation and checking
```

## 🏗️ **Configuration Pattern Application**

### **Target Architecture**
```
Codes/Config/
├── path.py                      # Main controller & user interface (180 lines)
└── _path/                       # Internal processing modules
    ├── __init__.py             # Configuration function & exports (60 lines)
    ├── constants.py            # Path constants and policies (80 lines)
    ├── base.py                 # Base path definitions (120 lines)
    ├── builders.py             # Path building utilities (150 lines)
    ├── globs.py                # Glob operations and discovery (100 lines)
    ├── validation.py           # Path validation helpers (80 lines)
    └── report.py               # Path structure reports (60 lines)
```

### **User Constants (Stay in main path.py)**
```python
# From CELL 02-03 - All path constants:
# Experiment root (templated)
EXPERIMENTAL_FOLDER = Path("{{__EXP_FOLDER__}}")

# Directory structure constants
FOLDER_NAMES = {
    "codes": "Codes",
    "config": "Config", 
    "behavior_classifier": "BehaviorClassifier",
    "bonfly": "Bonfly",
    "raw_data": "RawData",
    "post_processing": "PostProcessing",
    "behavior_classification": "BehaviorClassification",
    # ... all folder name constants
}

# File suffix policies
FILE_SUFFIXES = {
    "tracked": "_tracked.csv",
    "sleap": "_sleap.csv",
    "scored": "_scored.csv",
    "pose": "_pose.csv",
    # ... all file suffix constants
}

# Path building policies
PATH_POLICIES = {
    "create_missing_dirs": True,
    "validate_paths": True,
    "cross_platform_safe": True,
    # ... other path policies
}
```

### **Configuration Function Design**
```python
# _path/__init__.py
def configure(
    experimental_folder,
    folder_names,
    file_suffixes,
    path_policies
):
    """Configure all path modules with user parameters."""
    global _CONSTANTS, _BASE, _BUILDERS, _GLOBS, _VALIDATION
    
    # Step 1: Create path constants bundle
    constants_bundle = constants.create_constants_bundle(
        folder_names, file_suffixes, path_policies
    )
    
    # Step 2: Create base paths bundle (needs constants)
    base_bundle = base.create_base_bundle(
        experimental_folder, constants_bundle
    )
    
    # Step 3: Create path builders bundle (needs base paths)
    builders_bundle = builders.create_builders_bundle(
        base_bundle, constants_bundle
    )
    
    # Step 4: Create glob utilities bundle (needs builders)
    globs_bundle = globs.create_globs_bundle(
        builders_bundle, constants_bundle
    )
    
    # Step 5: Create validation helpers bundle (needs all previous)
    validation_bundle = validation.create_validation_bundle(
        base_bundle, builders_bundle, constants_bundle
    )
    
    # Step 6: Update module-level variables
    _CONSTANTS = constants_bundle
    _BASE = base_bundle
    _BUILDERS = builders_bundle
    _GLOBS = globs_bundle
    _VALIDATION = validation_bundle
```

## 📋 **Detailed Implementation Plan**

### **Phase 1: Create Internal Module Structure**

#### **Step 1.1: Create _path/constants.py**
```python
# Move path constants and policies:
- Folder name definitions
- File suffix policies
- Path validation rules
- Cross-platform compatibility settings

# Functions to create:
def create_constants_bundle(folder_names, file_suffixes, path_policies):
    # Process path constants and policies
    return MappingProxyType({
        "FOLDER_NAMES": processed_folder_names,
        "FILE_SUFFIXES": processed_file_suffixes,
        "PATH_POLICIES": processed_policies,
        # ... other path constants
    })
```

#### **Step 1.2: Create _path/base.py**
```python
# Move from CELL 03 base path definitions:
- Core directory path definitions
- Experiment folder structure
- Base path calculations
- Directory hierarchy setup

# Functions to create:
def create_base_bundle(experimental_folder, constants_bundle):
    # Create all base path definitions
    return MappingProxyType({
        "pExperimentalFolder": experimental_folder,
        "pCodes": codes_path,
        "pConfig": config_path,
        "pBehaviorClassifier": behavior_classifier_path,
        "pBonfly": bonfly_path,
        "pRawData": raw_data_path,
        "pPostProcessing": post_processing_path,
        "pBehaviorClassification": behavior_classification_path,
        # ... all base paths
    })
```

#### **Step 1.3: Create _path/builders.py**
```python
# Move from CELL 04 path building logic:
- File path construction utilities
- Filename generation functions
- Path joining and manipulation
- Template-based path building

# Functions to create:
def create_builders_bundle(base_bundle, constants_bundle):
    # Create all path building functions
    return MappingProxyType({
        "build_tracked_path": path_builder_function,
        "build_sleap_path": path_builder_function,
        "build_scored_path": path_builder_function,
        "build_pose_path": path_builder_function,
        "build_error_path": error_path_builder,
        "build_flag_path": flag_path_builder,
        # ... other path builders
    })
```

#### **Step 1.4: Create _path/globs.py**
```python
# Move from CELL 05 glob operations:
- File discovery utilities
- Pattern matching functions
- Glob pattern generation
- File filtering and selection

# Functions to create:
def create_globs_bundle(builders_bundle, constants_bundle):
    # Create glob utilities
    return MappingProxyType({
        "discover_tracked_files": glob_function,
        "discover_sleap_files": glob_function,
        "discover_scored_files": glob_function,
        "find_files_by_pattern": pattern_matcher,
        "filter_files_by_suffix": file_filter,
        # ... other glob utilities
    })
```

#### **Step 1.5: Create _path/validation.py**
```python
# Move from CELL 06 validation logic:
- Path validation functions
- File existence checking
- Directory structure validation
- Cross-platform path checking

# Functions to create:
def create_validation_bundle(base_bundle, builders_bundle, constants_bundle):
    # Create validation utilities
    return MappingProxyType({
        "validate_path_structure": structure_validator,
        "check_file_exists": existence_checker,
        "validate_cross_platform": platform_validator,
        "ensure_directory_exists": directory_creator,
        # ... other validation utilities
    })
```

#### **Step 1.6: Create _path/report.py**
```python
# Move reporting logic:
- Path structure visualization
- Directory tree reports
- File discovery summaries
- Path validation reports

# Functions to create:
def create_report_bundle():
    # Create reporting functions
    return MappingProxyType({
        "render_path_report": report_function,
        "display_directory_tree": tree_display,
        "summarize_file_discovery": discovery_summary,
        # ... other report functions
    })
```

### **Phase 2: Transform Main path.py File**

#### **Step 2.1: Clean Main File Structure**
```python
#%% CELL 00 — HEADER & OVERVIEW
"""
Clean overview focused on path management and file system operations.
"""

#%% CELL 01 — IMPORTS & TYPES
from __future__ import annotations
import sys
from pathlib import Path
from types import MappingProxyType
from typing import Iterable, Callable

# Package path setup (for safe absolute imports)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Config import _path

#%% CELL 02 — USER INPUT
"""
Authoritative path constants and policies. Edit these values only.
"""
# Experiment root (templated)
EXPERIMENTAL_FOLDER = Path("{{__EXP_FOLDER__}}")

# All folder name constants
FOLDER_NAMES = {...}

# All file suffix policies
FILE_SUFFIXES = {...}

# Path building policies
PATH_POLICIES = {...}

#%% CELL 03 — CONFIGURATION
"""
Single function call handles all path processing complexity.
"""
_path.configure(
    EXPERIMENTAL_FOLDER,
    FOLDER_NAMES,
    FILE_SUFFIXES,
    PATH_POLICIES
)

#%% CELL 04 — PUBLIC API ASSEMBLY
"""
Clean assembly from configured bundles.
"""
_PUBLIC = {
    # User inputs
    "EXPERIMENTAL_FOLDER": EXPERIMENTAL_FOLDER,
    "FOLDER_NAMES": FOLDER_NAMES,
    "FILE_SUFFIXES": FILE_SUFFIXES,
    "PATH_POLICIES": PATH_POLICIES,
    
    # Processed results from internal modules
    **_path._BASE,
    **_path._BUILDERS,
    **_path._GLOBS,
    **_path._VALIDATION,
}

PATH = MappingProxyType(_PUBLIC)
__all__ = ["PATH"]

#%% CELL 05 — REPORT
if __name__ == "__main__":
    _path._REPORT["render_path_report"](PATH)
```

### **Phase 3: Handle Special Considerations**

#### **Cross-Platform Compatibility**
- **Challenge**: Path operations must work on Windows, Linux, macOS
- **Solution**: Use pathlib consistently, test on multiple platforms
- **Validation**: Test path operations on different operating systems

#### **File System Operations**
- **Challenge**: Path building without actual I/O operations
- **Solution**: Pure path math in _path modules, I/O handled elsewhere
- **Validation**: Test path building logic without file system dependencies

#### **Template-Based Paths**
- **Challenge**: Experiment folder templating ({{__EXP_FOLDER__}})
- **Solution**: Handle templating in configure() function
- **Validation**: Test template resolution and path substitution

#### **Glob Pattern Generation**
- **Challenge**: Complex glob patterns for file discovery
- **Solution**: Isolate glob logic in _path/globs.py
- **Validation**: Test glob patterns with various file structures

## 🧪 **Validation Strategy**

### **Path Building Validation**
```python
# Test all path builders produce identical results
def test_path_builders():
    original_paths = load_original_path_system()
    refactored_paths = load_refactored_path_system()
    
    test_cases = [
        ("BASE", "fly1", "tracked"),
        ("BASE", "fly2", "sleap"),
        # ... more test cases
    ]
    
    for base, fly, suffix in test_cases:
        original_path = original_paths.build_path(base, fly, suffix)
        refactored_path = refactored_paths.build_path(base, fly, suffix)
        assert original_path == refactored_path
```

### **Cross-Platform Validation**
```python
# Test cross-platform path compatibility
def test_cross_platform_paths():
    # Test Windows-style paths
    # Test Unix-style paths
    # Test path separator handling
    # Test drive letter handling (Windows)
```

### **Glob Pattern Validation**
```python
# Test glob patterns work identically
def test_glob_patterns():
    # Test file discovery patterns
    # Test pattern matching logic
    # Test file filtering operations
```

## ⚠️ **Risk Assessment & Mitigation**

### **Medium Risk Areas**
1. **Cross-platform compatibility**: Path operations vary by OS
   - **Mitigation**: Use pathlib consistently, test on multiple platforms
2. **Template resolution**: Experiment folder templating complexity
   - **Mitigation**: Handle templating carefully, test edge cases
3. **Glob pattern complexity**: Complex file discovery patterns
   - **Mitigation**: Test glob patterns thoroughly, validate discovery logic

### **Low Risk Areas**
1. **Path building logic**: Relatively straightforward operations
   - **Mitigation**: Comprehensive testing, preserve exact logic
2. **File system independence**: No actual I/O operations
   - **Mitigation**: Maintain pure path math approach

### **Mitigation Strategies**
- **Cross-platform testing**: Test on Windows, Linux, macOS
- **Comprehensive path validation**: Test all path building scenarios
- **Template testing**: Validate template resolution edge cases
- **Glob pattern testing**: Test file discovery with various structures

## 📊 **Success Metrics**

### **Target Outcomes**
- **Line reduction**: 692 → ~180 lines in main file (74% reduction)
- **Functionality preservation**: 100% (all paths, builders, globs identical)
- **Cross-platform compatibility**: Perfect operation on all platforms
- **Template resolution**: Flawless experiment folder templating
- **Glob operations**: All file discovery patterns work identically

### **Validation Criteria**
- [ ] All path constants match exactly
- [ ] All path builders produce identical results
- [ ] All glob patterns work identically
- [ ] Cross-platform compatibility maintained
- [ ] Template resolution works perfectly
- [ ] Validation helpers function correctly
- [ ] Performance maintained or improved

## 🎯 **Implementation Timeline**

### **Day 1: Analysis & Cross-Platform Setup**
- Comprehensive analysis of path building logic
- Set up cross-platform testing environment
- Create validation baseline for all platforms

### **Day 2: Internal Module Creation**
- Create _path/ package structure
- Implement constants.py and base.py with exact path preservation
- Test base path definitions

### **Day 3: Path Builders & Glob Utilities**
- Implement builders.py with all path construction logic
- Implement globs.py with file discovery patterns
- Test path building and glob operations

### **Day 4: Integration & Main File**
- Create configure() function with template handling
- Transform main path.py file
- Test integration and configuration

### **Day 5: Cross-Platform Validation**
- Comprehensive cross-platform testing
- Template resolution validation
- Final validation and optimization

This plan applies the configuration pattern to path.py while addressing its file system operation complexity and cross-platform requirements. The result will be a dramatically simplified main file with perfect functionality preservation and enhanced maintainability.
