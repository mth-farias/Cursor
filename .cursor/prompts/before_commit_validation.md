# Before Commit Validation - Code Refactoring

Hey Cursor! I'm about to commit refactored code and need you to validate that I've preserved 100% functionality compared to the original working systems.

## What I'm About to Commit
**Refactored Module**: [e.g., Config/color.py, Config/param.py, etc.]
**Files Changed**: [LIST THE REFACTORED FILES]
**Refactoring Type**: [e.g., Applied configuration-based architecture pattern]

## Critical Validation: Before vs After Comparison

### **Reference Systems** (Original Working Code)
- **`@Codes_Before/`** - Original working system (cell-based)
- **`@Codes_Working/`** - Enhanced working system
- **Target**: Compare against whichever system I'm refactoring from

### **Refactored System** (New Code)
- **`@Codes/`** - My refactored modern Python code

## Comprehensive Functionality Validation

Please perform these critical comparisons:

### 1. 🔍 **Constants Preservation**
- [ ] **Read original module** from reference system
- [ ] **Read refactored module** from target system
- [ ] **Compare ALL constants** - values must be identical
- [ ] **Check data types** - int, float, str, dict, list must match exactly
- [ ] **Verify numpy arrays** - shape and values identical
- [ ] **Check nested structures** - dictionaries and lists preserve structure

### 2. 🔧 **Function Behavior Preservation**
- [ ] **Identify all functions** in original vs refactored
- [ ] **Compare function signatures** - parameters must match exactly
- [ ] **Test function outputs** with sample inputs (if possible to determine)
- [ ] **Check return types** - must be identical
- [ ] **Verify side effects** - any file operations, global state changes

### 3. 📦 **Public API Preservation**
- [ ] **Compare bundle exports** - original vs refactored bundle keys
- [ ] **Check MappingProxyType** - refactored should be immutable
- [ ] **Verify import compatibility** - `from Config import MODULE` still works
- [ ] **Test bundle access** - `MODULE["key"]` returns same values
- [ ] **Check bundle structure** - nested dictionaries preserved

### 4. 🧪 **Scientific Integrity Validation**
- [ ] **Biological constraints** - speed limits, time ranges preserved
- [ ] **Physical constraints** - arena dimensions, measurement units
- [ ] **Validation rules** - data type checking, domain validation
- [ ] **Error handling** - same error messages and behavior

### 5. 🔄 **Integration Compatibility**
- [ ] **Cross-module dependencies** - other Config modules still work
- [ ] **BehaviorClassifier imports** - pipeline still functions
- [ ] **File path references** - all paths resolve correctly
- [ ] **External integrations** - Google Colab compatibility

## Detailed Comparison Analysis

### **Step 1: Load and Compare Modules**
```python
# Load original system
import sys
sys.path.insert(0, 'Codes_Before')  # or Codes_Working
import Config as original_config

# Load refactored system  
sys.path.insert(0, 'Codes')
import Config as refactored_config

# Compare bundles
original_bundle = original_config.MODULE_NAME
refactored_bundle = refactored_config.MODULE_NAME
```

### **Step 2: Systematic Comparison**
Please check:
- **Bundle keys**: `set(original_bundle.keys()) == set(refactored_bundle.keys())`
- **Value equality**: For each key, `original_bundle[key] == refactored_bundle[key]`
- **Type preservation**: `type(original_bundle[key]) == type(refactored_bundle[key])`
- **Function testing**: Call functions with same inputs, compare outputs

### **Step 3: Scientific Validation**
- **Numerical precision**: Handle floating-point comparison appropriately
- **Array comparison**: Use `np.array_equal()` for numpy arrays
- **Nested structures**: Deep comparison of dictionaries and lists
- **Immutability**: Verify MappingProxyType prevents modification

## Validation Questions

After your analysis, answer:

1. **Are ALL constants identical** between original and refactored systems?
2. **Do ALL functions produce identical outputs** for the same inputs?
3. **Is the public API completely preserved** - no breaking changes?
4. **Are scientific constraints maintained** - no biological/physical violations?
5. **Will existing code continue to work** without any modifications?

## Red Flags to Check For

Watch out for these common refactoring issues:
- **Changed numerical values** (even tiny differences matter)
- **Modified function signatures** (parameter names, defaults, order)
- **Altered return types** (list vs numpy array, dict vs MappingProxyType)
- **Missing constants or functions** (incomplete migration)
- **Changed error behavior** (different exceptions or messages)
- **Performance regressions** (significantly slower imports/execution)

## Validation Results

Please provide:

### **✅ PASS Criteria**
- All constants identical: YES/NO
- All functions identical: YES/NO  
- Public API preserved: YES/NO
- Scientific integrity maintained: YES/NO
- Integration compatibility: YES/NO

### **❌ FAIL - Issues Found**
If any validation fails, list:
- Specific constants that changed
- Functions with different behavior
- API breaking changes
- Scientific constraint violations
- Integration problems

## Commit Decision

Based on validation results:

### **✅ READY TO COMMIT** 
If all validations pass:
- 100% functionality preserved
- Scientific integrity maintained
- No breaking changes detected
- Integration compatibility confirmed

### **❌ NOT READY - FIXES NEEDED**
If any validation fails:
- List specific issues to fix
- Recommend rollback if major problems
- Suggest incremental fixes
- Re-validate after corrections

## Success Confirmation

Before I commit, confirm:
- [ ] ✅ **100% functionality preservation** verified
- [ ] ✅ **All constants identical** between systems
- [ ] ✅ **All functions behave identically** 
- [ ] ✅ **Public API completely preserved**
- [ ] ✅ **Scientific constraints maintained**
- [ ] ✅ **No integration breaking changes**

**Only approve commit if ALL criteria are met. Scientific software requires absolute reliability.**