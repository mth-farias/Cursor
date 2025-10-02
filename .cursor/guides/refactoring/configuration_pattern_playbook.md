# Configuration Pattern Playbook

## 🎯 **Mission: Replicate experiment.py Success**

This playbook documents the exact step-by-step process to replicate the revolutionary configuration pattern that transformed experiment.py from 570 lines to 230 lines while achieving 100% functionality preservation.

**Use this playbook for color.py, param.py, path.py, and any future module refactoring.**

## 📊 **Success Metrics from experiment.py**
- **Lines reduced**: 570 → 230 (60% reduction in main file)
- **Functionality preservation**: 100% (validated)
- **Maintainability**: Dramatically improved
- **Testability**: Each component now testable in isolation
- **Architecture**: Clean separation of user interface vs implementation

## 🏗️ **The Configuration Pattern Architecture**

### **Core Principle**
```
User Constants → configure() Function → Use Configured Bundles
```

### **File Structure Template**
```
Codes/Config/
├── module.py                    # Main controller & user interface
└── _module/                     # Internal processing modules
    ├── __init__.py             # Configuration function & exports
    ├── component1.py           # Focused processing logic
    ├── component2.py           # Focused processing logic
    └── report.py               # Report generation
```

## 📋 **Step-by-Step Implementation Process**

### **Phase 1: Analysis & Planning**

#### **Step 1.1: Analyze Current Structure**
- [ ] Read the entire current module file
- [ ] Identify all cells and their purposes
- [ ] Map out dependencies between cells
- [ ] Document current public API (what gets exported)

**Template Questions:**
- What are the user constants? (stays in main file)
- What is processing logic? (moves to _module/)
- What are the dependencies between components?
- What is the final public API structure?

#### **Step 1.2: Create Module Breakdown Plan**
- [ ] List each cell and its destination
- [ ] Plan the _module/ submodule structure
- [ ] Identify the configure() function parameters
- [ ] Map dependencies and processing order

**Example from experiment.py:**
```
CELL 02 → User constants (stays in main file)
CELL 03 → _experiment/time.py (time conversion logic)
CELL 04 → _experiment/periods.py (period processing)
CELL 05 → _experiment/stimuli.py (stimulus processing)
CELL 06 → Public API assembly (stays in main file)
```

### **Phase 2: Create Internal Module Structure**

#### **Step 2.1: Create _module/ Package**
- [ ] Create `_module/` directory
- [ ] Create `_module/__init__.py` with configuration function
- [ ] Create individual component modules

**Template for _module/__init__.py:**
```python
#%% CELL 00 — HEADER & OVERVIEW
"""
Internal module exports for the [module] configuration system.
This module aggregates processed bundles from internal modules and
exports them for the main [module].py controller to use.
"""

#%% CELL 01 — IMPORTS
from . import component1, component2, report

_REPORT = report._REPORT
_COMPONENT1 = None  # Set by configure()
_COMPONENT2 = None  # Set by configure()

#%% CELL 02 — CONFIGURATION
def configure(user_param1, user_param2, user_param3):
    """Configure all [module] modules with user parameters."""
    global _COMPONENT1, _COMPONENT2
    
    # Step 1: Create first component
    comp1_bundle = component1.create_component1_bundle(user_param1)
    
    # Step 2: Create second component (may depend on first)
    comp2_bundle = component2.create_component2_bundle(
        user_param2, user_param3, comp1_bundle
    )
    
    # Step 3: Update module-level variables
    _COMPONENT1 = comp1_bundle
    _COMPONENT2 = comp2_bundle
```

#### **Step 2.2: Create Component Modules**
- [ ] Move cell content to appropriate component modules
- [ ] Create `create_[component]_bundle()` functions
- [ ] Ensure each module is focused and testable

**Template for component modules:**
```python
#%% CELL 00 — HEADER & OVERVIEW
"""
[Component] processing for [module] configuration.
Pure processing logic with no user constants.
"""

#%% CELL 01 — IMPORTS
from __future__ import annotations
from types import MappingProxyType

#%% CELL 02 — PROCESSING FUNCTIONS
def create_component_bundle(user_params, dependencies=None):
    """Create processed bundle for this component."""
    # Processing logic here
    return MappingProxyType({
        "processed_data": processed_data,
        "helper_functions": helper_functions,
    })
```

### **Phase 3: Transform Main Module File**

#### **Step 3.1: Clean Up Main File Structure**
- [ ] Keep only user constants in CELL 02
- [ ] Add single configure() call
- [ ] Clean up public API assembly
- [ ] Add proper imports and path setup

**Template for main module file:**
```python
#%% CELL 00 — HEADER & OVERVIEW
"""
Clean overview focused on user interface.
"""

#%% CELL 01 — IMPORTS & TYPES
from __future__ import annotations
import sys
from pathlib import Path
from types import MappingProxyType

# Package path setup (for safe absolute imports)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Config import _module

#%% CELL 02 — USER INPUT
"""
Authoritative user inputs. Purely declarative (no derivations).
"""
USER_CONSTANT_1 = value1
USER_CONSTANT_2 = value2
# ... all user constants

#%% CELL 03 — CONFIGURATION
"""
Single function call handles all complexity.
"""
_module.configure(USER_CONSTANT_1, USER_CONSTANT_2, ...)

#%% CELL 04 — PUBLIC API ASSEMBLY
"""
Clean assembly from configured bundles.
"""
_PUBLIC = {
    # User inputs
    "USER_CONSTANT_1": USER_CONSTANT_1,
    "USER_CONSTANT_2": USER_CONSTANT_2,
    
    # Processed results from internal modules
    **_module._COMPONENT1,
    **_module._COMPONENT2,
}

MODULE_BUNDLE = MappingProxyType(_PUBLIC)
__all__ = ["MODULE_BUNDLE"]

#%% CELL 05 — REPORT
if __name__ == "__main__":
    _module._REPORT["render_module_report"](MODULE_BUNDLE)
```

### **Phase 4: Validation & Testing**

#### **Step 4.1: Create Validation Script**
- [ ] Create comprehensive validation script
- [ ] Test all constants match exactly
- [ ] Test all functions produce identical outputs
- [ ] Test all imports work unchanged

**Use template from `.cursor/templates/validation_template.py`**

#### **Step 4.2: Run Comprehensive Testing**
- [ ] Load both original and refactored modules
- [ ] Compare all public API elements
- [ ] Test edge cases and error conditions
- [ ] Verify performance is maintained

#### **Step 4.3: Document Results**
- [ ] Create detailed change log
- [ ] Document architectural innovations
- [ ] Update project status files
- [ ] Create success metrics summary

## 🔧 **Key Implementation Tips**

### **Dependency Management**
- Process dependencies in correct order in configure()
- Pass processed bundles between components as needed
- Update bundles when dependencies change

### **Error Handling**
- Preserve all original error messages and conditions
- Add clear error messages for configuration failures
- Maintain scientific validation constraints

### **Performance**
- Import modules, not variables (avoid circular imports)
- Use global variables in _module/__init__.py for configured state
- Maintain lazy evaluation where it existed

### **Testing Strategy**
- Test each component module independently
- Test configure() function with various inputs
- Test main module public API matches exactly

## 🎯 **Success Criteria Checklist**

### **Functionality Preservation**
- [ ] All constants have identical values
- [ ] All functions produce identical outputs
- [ ] All imports work unchanged
- [ ] All error conditions preserved

### **Architecture Quality**
- [ ] Clean separation: user interface vs implementation
- [ ] Configuration pattern implemented cleanly
- [ ] Each module has single responsibility
- [ ] Dependencies handled correctly

### **Code Quality**
- [ ] Type hints maintained/improved
- [ ] Documentation clear and focused
- [ ] Cell structure preserved in new modules
- [ ] Performance maintained or improved

### **Project Integration**
- [ ] Change log created
- [ ] Status files updated
- [ ] Validation results documented
- [ ] Next steps planned

## 🚀 **Pattern Variations for Different Modules**

### **For color.py (matplotlib integration)**
- User constants: color themes, matplotlib settings
- Components: color generation, matplotlib setup, colormap creation
- Dependencies: matplotlib → colors → colormaps

### **For param.py (validation heavy)**
- User constants: validation parameters, schema definitions
- Components: schema validation, domain checking, registry assembly
- Dependencies: constants → schemas → validation → registry

### **For path.py (file system operations)**
- User constants: path constants, directory structures
- Components: base paths, path builders, glob utilities
- Dependencies: constants → base paths → builders → globs

This playbook is your blueprint for success. Follow it systematically and you'll achieve the same breakthrough results as experiment.py!
