# General Refactoring Strategy

## Mission: Cell-Based to Modern Python

### Core Objective
Transform a functional but cell-based scientific codebase into modern, publication-ready Python while preserving 100% functionality and maintaining scientific rigor.

## Revolutionary Pattern: Configuration-Based Architecture

### The Breakthrough (experiment.py Success)
We discovered a revolutionary pattern that dramatically simplifies Config modules:

```python
# Before: 570 lines of complex cell-based code
# After: 230 lines with clean separation

# User constants stay in main file (easy to edit)
FRAME_RATE = 60
EXPERIMENTAL_PERIODS = {...}

# Single configuration call (hides all complexity)
_experiment.configure(FRAME_RATE, EXPERIMENTAL_PERIODS, STIMULI, ALIGNMENT_STIM)

# Clean public API (immutable, safe)
EXPERIMENT = MappingProxyType(_PUBLIC)
```

### Pattern Benefits
- **Ultra-clean main files**: Users only see/edit what they need
- **Hidden complexity**: All processing logic in internal modules
- **Maintained interfaces**: Existing imports continue to work
- **Perfect separation**: User interface completely separate from implementation

## Core Principles

### 1. 100% Functionality Preservation (Non-Negotiable)
- **All constants**: Identical values after refactoring
- **All functions**: Identical outputs for identical inputs
- **All behavior**: Identical pipeline behavior
- **All imports**: Existing code continues to work unchanged

### 2. Scientific Software Standards
- **Quality over speed**: Take time to do things right
- **Comprehensive validation**: Test everything thoroughly
- **Documentation**: Document all changes and decisions
- **Reproducibility**: Maintain scientific reproducibility

### 3. Single Source of Truth (SSOT)
- **Config modules**: Centralized parameter management
- **No duplication**: Each parameter defined exactly once
- **Clear ownership**: Each module owns specific parameter domains

### 4. Clean Architecture
- **Separation of concerns**: User interface vs. implementation
- **Immutable APIs**: MappingProxyType for public bundles
- **Type safety**: Comprehensive type hints
- **Error handling**: Clear, descriptive error messages

## Refactoring Workflow

### Phase 1: Analysis & Planning
1. **Study current structure**: Understand all cells and functionality
2. **Map dependencies**: Document all internal and external dependencies
3. **Plan architecture**: Design internal module structure
4. **Create validation baseline**: Capture complete current functionality

### Phase 2: Implementation
1. **Create internal modules**: Build `_module/` package structure
2. **Implement configure() pattern**: Central configuration function
3. **Migrate content**: Move processing logic to internal modules
4. **Preserve user interface**: Keep user constants in main file
5. **Assemble public API**: Create immutable bundle

### Phase 3: Validation & Documentation
1. **Comprehensive validation**: Verify 100% functionality preservation
2. **Performance testing**: Ensure no regression
3. **Integration testing**: Test with other modules
4. **Create change log**: Document all changes made
5. **Update documentation**: Reflect new architecture

## Module Structure Template

### Target Architecture
```
Codes/Config/
├── module.py                    # Main controller & user interface
└── _module/                     # Internal processing (private)
    ├── __init__.py             # configure() function & exports
    ├── constants.py            # Process user constants
    ├── processing.py           # Core logic
    ├── utilities.py            # Helper functions
    └── report.py               # Report generation
```

### Content Organization
- **Main file**: User constants, configure() call, public API
- **_module/__init__.py**: configure() function, module coordination
- **_module/constants.py**: Process and validate user constants
- **_module/processing.py**: Core computational logic
- **_module/utilities.py**: Helper functions and utilities
- **_module/report.py**: Human-readable reporting

## Configuration Pattern Implementation

### 1. User Constants (Main File)
```python
# All user-editable constants stay here
USER_CONSTANT_1 = "value1"
USER_CONSTANT_2 = 42
USER_CONSTANT_3 = {"key": "value"}
```

### 2. Configuration Call (Main File)
```python
# Import and configure internal modules
from . import _module
_module.configure(USER_CONSTANT_1, USER_CONSTANT_2, USER_CONSTANT_3)
```

### 3. Public API Assembly (Main File)
```python
_PUBLIC = {
    # User constants (direct export)
    "USER_CONSTANT_1": USER_CONSTANT_1,
    "USER_CONSTANT_2": USER_CONSTANT_2,
    "USER_CONSTANT_3": USER_CONSTANT_3,
    
    # Processed results from internal modules
    **_module._PROCESSED_DATA,
    **_module._FUNCTIONS,
    **_module._DERIVED_STRUCTURES,
}

MODULE_BUNDLE = MappingProxyType(_PUBLIC)
```

### 4. Configure Function (_module/__init__.py)
```python
def configure(user_const_1, user_const_2, user_const_3):
    """Configure all internal modules with user parameters."""
    # Process constants
    constants_bundle = constants.process_constants(user_const_1, user_const_2)
    
    # Perform computations
    processing_bundle = processing.compute_derived_data(constants_bundle, user_const_3)
    
    # Create functions
    functions_bundle = utilities.create_functions(processing_bundle)
    
    # Update module-level variables
    global _PROCESSED_DATA, _FUNCTIONS, _DERIVED_STRUCTURES
    _PROCESSED_DATA = constants_bundle
    _FUNCTIONS = functions_bundle
    _DERIVED_STRUCTURES = processing_bundle
```

## Validation Strategy

### Comprehensive Baseline Capture
```python
# Capture all constants
baseline_constants = {key: value for key, value in original_bundle.items() 
                     if not callable(value)}

# Test all functions
function_tests = {}
for key, func in original_bundle.items():
    if callable(func):
        # Test with representative inputs
        function_tests[key] = test_function_with_inputs(func)

# Save baseline for comparison
save_baseline(baseline_constants, function_tests)
```

### Post-Refactoring Validation
```python
# Compare all constants
for key, original_value in baseline_constants.items():
    refactored_value = refactored_bundle[key]
    assert original_value == refactored_value, f"Constant {key} changed"

# Compare all function outputs
for func_name, test_cases in function_tests.items():
    refactored_func = refactored_bundle[func_name]
    for inputs, expected_output in test_cases:
        actual_output = refactored_func(*inputs)
        assert actual_output == expected_output, f"Function {func_name} output changed"
```

## Risk Management

### High-Risk Areas
1. **Complex interdependencies**: Functions that depend on multiple constants
2. **Derived calculations**: Computed values that depend on user inputs
3. **External integrations**: Code that interfaces with other modules
4. **Performance-critical paths**: Code that runs frequently

### Mitigation Strategies
1. **Incremental approach**: Refactor one module at a time
2. **Comprehensive testing**: Test every aspect thoroughly
3. **Rollback readiness**: Keep working versions as reference
4. **Pattern validation**: Prove pattern works before applying widely

## Success Metrics

### Functionality Preservation
- ✅ **100% constant preservation**: All values identical
- ✅ **100% function preservation**: All outputs identical
- ✅ **100% behavior preservation**: Pipeline works identically
- ✅ **100% interface preservation**: All imports work unchanged

### Code Quality Improvement
- ✅ **Reduced complexity**: Simpler main files
- ✅ **Better organization**: Clear separation of concerns
- ✅ **Improved maintainability**: Easier to understand and modify
- ✅ **Enhanced testability**: Better unit testing capabilities

### Scientific Standards
- ✅ **Reproducibility maintained**: Identical scientific results
- ✅ **Documentation improved**: Better understanding of code
- ✅ **Validation comprehensive**: Thorough testing performed
- ✅ **Quality assured**: Publication-ready code quality

## Module-Specific Considerations

### Config Package Priority Order
1. **✅ experiment.py**: COMPLETED - Revolutionary pattern established
2. **🎯 color.py**: NEXT - Apply pattern to color processing
3. **📋 path.py**: PLANNED - File system operations
4. **📋 param.py**: FINAL - Most complex, extensive validation

### Complexity Assessment
- **experiment.py**: High complexity → **SUCCESS** (pattern proven)
- **color.py**: High complexity (matplotlib, colormaps)
- **path.py**: Moderate complexity (file operations)
- **param.py**: Highest complexity (validation, schemas)

## Future Extensions

### BehaviorClassifier Package
After Config package completion, apply lessons learned to:
- **_classifier.py**: Core classification algorithms
- **_utils.py**: Utility functions
- **_qc_error_flag.py**: Quality control logic

### Pattern Refinements
- **Performance optimization**: Optimize configure() functions
- **Error handling**: Improve error messages and recovery
- **Testing framework**: Automated validation testing
- **Documentation**: Enhanced inline documentation

---

This strategy ensures systematic, safe transformation of the codebase while maintaining scientific integrity and achieving modern Python standards.
