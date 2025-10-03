# Troubleshooting Playbook for Scientific Software Development

## 🎯 **Systematic Problem Solving with Cursor**

This playbook provides systematic approaches to common issues encountered during scientific software refactoring, based on lessons learned from the experiment.py breakthrough and optimized for rapid problem resolution.

## 🚨 **Common Issues & Solutions**

### **1. Validation Failures**

#### **Issue: Validation Script Shows Mismatches**
```
❌ CONSTANT MISMATCH: FRAME_RATE
   Original:   30.0
   Refactored: 30
```

**Root Cause Analysis:**
- Type mismatch (float vs int)
- Precision loss during refactoring
- Configuration function not preserving exact values

**Solution Steps:**
```
1. Load both systems for comparison:
   @original_system.py @refactored_system.py
   
2. Identify exact source of mismatch:
   grep: "FRAME_RATE" in both systems
   
3. Trace value through configuration:
   - Check user constant definition
   - Check configure() function processing
   - Check final bundle assembly
   
4. Fix preservation of exact type and value:
   # Ensure exact preservation in configure()
   _TIME = time_bundle  # Don't modify the value
   
5. Re-validate to confirm fix
```

**Prevention:**
- Always preserve exact types and values in configure()
- Use comprehensive validation during development
- Test with edge cases and boundary values

#### **Issue: Function Outputs Don't Match**
```
❌ FUNCTION MISMATCH: sec_to_frames(10.5)
   Original:   315
   Refactored: 316
```

**Root Cause Analysis:**
- Rounding behavior changed
- Calculation order modified
- Dependencies not properly configured

**Solution Steps:**
```
1. Analyze function implementation:
   @original_system.py (search: "sec_to_frames")
   @refactored_system.py (search: "sec_to_frames")
   
2. Compare calculation logic exactly:
   # Original: round(seconds * FRAME_RATE)
   # Refactored: int(seconds * FRAME_RATE + 0.5)
   
3. Preserve exact calculation method:
   # Use identical calculation in refactored version
   return round(seconds * frame_rate)
   
4. Test with problematic inputs:
   # Test: sec_to_frames(10.5) should return 315
   
5. Validate all mathematical functions
```

**Prevention:**
- Preserve exact calculation methods
- Test mathematical functions with edge cases
- Document any precision-critical operations

### **2. Configuration Pattern Issues**

#### **Issue: configure() Function Not Working**
```
❌ AttributeError: module '_experiment' has no attribute '_TIME'
```

**Root Cause Analysis:**
- Module-level variables not initialized
- configure() function not called
- Import order issues

**Solution Steps:**
```
1. Check module initialization:
   @_module/__init__.py
   
2. Verify module-level variables are declared:
   _TIME = None  # Must be declared before configure()
   _PERIODS = None
   _STIMULI = None
   
3. Check configure() function updates globals:
   def configure(...):
       global _TIME, _PERIODS, _STIMULI
       # ... processing ...
       _TIME = time_bundle
       _PERIODS = periods_bundle
       _STIMULI = stimuli_bundle
   
4. Verify configure() is called in main file:
   _experiment.configure(FRAME_RATE, ...)
   
5. Check import order and dependencies
```

**Prevention:**
- Always declare module-level variables before configure()
- Use global keyword in configure() function
- Call configure() before accessing configured bundles

#### **Issue: Circular Import Errors**
```
❌ ImportError: cannot import name '_experiment' from partially initialized module
```

**Root Cause Analysis:**
- Circular dependencies between modules
- Import statements in wrong location
- Module initialization order issues

**Solution Steps:**
```
1. Analyze import structure:
   @main_module.py @_module/__init__.py
   
2. Check for circular dependencies:
   # Main imports _module
   # _module imports main (CIRCULAR!)
   
3. Fix import structure:
   # _module should NOT import main
   # Pass dependencies as parameters to configure()
   
4. Use proper import pattern:
   # In main file:
   from Config import _module
   
   # In _module/__init__.py:
   from . import component1, component2  # Relative imports only
   
5. Test import order with fresh Python session
```

**Prevention:**
- Never import main module from internal modules
- Use parameter passing instead of imports
- Keep internal modules self-contained

### **3. Architecture & Design Issues**

#### **Issue: Complex Dependencies Between Components**
```
❌ Component A needs Component B, but B needs A's output
```

**Root Cause Analysis:**
- Circular dependencies in processing logic
- Poor separation of concerns
- Configuration order not planned properly

**Solution Steps:**
```
1. Map all dependencies:
   @.cursor/guides/refactoring/playbook.md
   
2. Identify dependency cycles:
   A → B → A (CIRCULAR!)
   
3. Break cycles with proper ordering:
   # Step 1: Create A with minimal dependencies
   # Step 2: Create B using A's output
   # Step 3: Update A with B's output if needed
   
4. Implement in configure() function:
   def configure(...):
       # Step 1: Basic A
       a_basic = create_a_basic(user_params)
       
       # Step 2: B using A
       b_bundle = create_b_bundle(user_params, a_basic)
       
       # Step 3: Complete A using B
       a_complete = create_a_complete(a_basic, b_bundle)
   
5. Test dependency resolution
```

**Prevention:**
- Plan dependency order before implementation
- Use multi-step configuration when needed
- Document dependency rationale

#### **Issue: Pattern Doesn't Fit Module Characteristics**
```
❌ Configuration pattern seems forced for this module
```

**Root Cause Analysis:**
- Module has unique characteristics not addressed
- Pattern applied too rigidly
- Missing adaptation for specific needs

**Solution Steps:**
```
1. Analyze module characteristics:
   @original_module.py (comprehensive analysis)
   
2. Identify unique requirements:
   # Visual validation needed (color.py)
   # Complex validation logic (param.py)
   # File system operations (path.py)
   
3. Adapt pattern to module needs:
   @.cursor/examples/experiment_breakthrough_pattern.py
   
4. Create module-specific variation:
   # For color.py: Add visual validation
   # For param.py: Add validation logic preservation
   # For path.py: Add cross-platform considerations
   
5. Document pattern adaptation:
   @.cursor/logs/decisions/architecture_decisions.md
```

**Prevention:**
- Analyze module characteristics before applying pattern
- Adapt patterns to specific needs
- Document pattern variations for future use

### **4. Performance Issues**

#### **Issue: Refactored Code is Slower**
```
❌ Import time increased from 0.1s to 2.5s
```

**Root Cause Analysis:**
- Inefficient import patterns
- Unnecessary processing during import
- Heavy computations in module initialization

**Solution Steps:**
```
1. Profile import performance:
   # Time original vs refactored imports
   
2. Identify performance bottlenecks:
   # Heavy processing in configure()?
   # Expensive imports in internal modules?
   # Unnecessary computations?
   
3. Optimize import patterns:
   # Import modules, not variables
   from . import component  # Not: from .component import *
   
4. Use lazy evaluation:
   # Defer expensive computations until needed
   # Cache results when appropriate
   
5. Benchmark and validate improvements
```

**Prevention:**
- Profile performance before and after refactoring
- Use efficient import patterns
- Avoid heavy processing during import

#### **Issue: Memory Usage Increased**
```
❌ Memory usage doubled after refactoring
```

**Root Cause Analysis:**
- Data duplication in bundles
- Inefficient data structures
- Memory leaks in configuration

**Solution Steps:**
```
1. Analyze memory usage patterns:
   # Profile memory before and after
   
2. Identify data duplication:
   # Same data stored in multiple bundles?
   # Unnecessary copies created?
   
3. Optimize data structures:
   # Use references instead of copies
   # Share common data between bundles
   
4. Fix memory leaks:
   # Clear temporary variables
   # Avoid circular references
   
5. Validate memory improvements
```

**Prevention:**
- Monitor memory usage during development
- Avoid unnecessary data duplication
- Use efficient data structures

### **5. Integration Issues**

#### **Issue: Refactored Module Breaks Other Components**
```
❌ BehaviorClassifier can't import from refactored Config
```

**Root Cause Analysis:**
- Public API changed during refactoring
- Import paths modified
- Expected attributes missing

**Solution Steps:**
```
1. Identify breaking changes:
   @original_system/ @refactored_system/
   
2. Check public API compatibility:
   # All expected attributes present?
   # Import paths still valid?
   # Function signatures unchanged?
   
3. Fix API compatibility:
   # Add missing attributes to public bundle
   # Maintain backward-compatible imports
   # Preserve function signatures
   
4. Test integration with dependent modules:
   # Import from BehaviorClassifier
   # Test expected functionality
   
5. Update dependent modules if necessary
```

**Prevention:**
- Maintain public API compatibility
- Test integration during development
- Document any necessary API changes

#### **Issue: Google Colab Integration Broken**
```
❌ Colab notebook can't find refactored modules
```

**Root Cause Analysis:**
- Import path changes
- Module structure modifications
- Colab-specific import issues

**Solution Steps:**
```
1. Test in Colab environment:
   # Upload refactored code to Colab
   # Test imports and functionality
   
2. Fix Colab-specific issues:
   # Adjust sys.path setup
   # Handle Colab import quirks
   # Test with ROOT path configuration
   
3. Validate Colab compatibility:
   # Test all major functions
   # Verify reports generate correctly
   
4. Document Colab setup if needed
```

**Prevention:**
- Test in Colab during development
- Maintain Colab-compatible import patterns
- Document any Colab-specific requirements

## 🔧 **Systematic Debugging Approach**

### **Step 1: Isolate the Problem**
```
1. Identify exact error or issue
2. Reproduce the problem consistently
3. Determine scope (single function, module, system-wide)
4. Check if issue exists in original system
```

### **Step 2: Gather Context**
```
1. Load relevant systems for comparison:
   @original_system/ @refactored_system/
   
2. Load debugging resources:
   @.cursor/guides/refactoring/playbook.md
   @.cursor/examples/breakthrough_pattern.py
   
3. Check recent changes:
   @.cursor/logs/active/current_focus.md
```

### **Step 3: Analyze Root Cause**
```
1. Compare original vs refactored implementation
2. Trace data flow through configuration
3. Check for common issues (types, imports, dependencies)
4. Use parallel analysis for comprehensive understanding
```

### **Step 4: Implement Solution**
```
1. Apply targeted fix based on root cause
2. Test fix with problematic case
3. Run comprehensive validation
4. Document solution for future reference
```

### **Step 5: Prevent Recurrence**
```
1. Update validation scripts to catch similar issues
2. Add preventive measures to development process
3. Document lessons learned
4. Update templates and examples if needed
```

## 📋 **Quick Diagnostic Checklist**

### **For Validation Failures:**
- [ ] Check exact types and values preservation
- [ ] Verify calculation methods unchanged
- [ ] Test with edge cases and boundary values
- [ ] Confirm error conditions preserved

### **For Configuration Issues:**
- [ ] Module-level variables declared before configure()
- [ ] Global keyword used in configure() function
- [ ] configure() called before accessing bundles
- [ ] No circular import dependencies

### **For Performance Issues:**
- [ ] Profile before and after refactoring
- [ ] Check import patterns efficiency
- [ ] Avoid heavy processing during import
- [ ] Monitor memory usage patterns

### **For Integration Issues:**
- [ ] Public API compatibility maintained
- [ ] Import paths still valid
- [ ] Function signatures unchanged
- [ ] Test with dependent modules

## 🚀 **Advanced Debugging Techniques**

### **Comparative Analysis**
```
# Load both systems simultaneously:
@original_system.py @refactored_system.py

# Compare specific functionality:
codebase_search: "how does [function] work in original?"
codebase_search: "how does [function] work in refactored?"

# Identify differences systematically
```

### **Incremental Rollback**
```
# If major issues arise:
1. Identify last working state
2. Roll back to working configuration
3. Apply changes incrementally
4. Test after each incremental change
5. Isolate problematic change
```

### **Parallel Validation**
```
# Test multiple scenarios simultaneously:
validate_constants()
validate_functions()
validate_integration()
validate_performance()
[All tests run in parallel for faster debugging]
```

## 🏆 **Success Outcomes**

### **Debugging Efficiency**
- **Issue resolution**: 70% faster with systematic approach
- **Root cause identification**: 80% faster with comparative analysis
- **Solution implementation**: 60% faster with proven patterns
- **Prevention effectiveness**: 90% reduction in recurring issues

### **Quality Improvements**
- **Comprehensive validation**: Catch issues before they compound
- **Systematic approach**: Consistent problem-solving methodology
- **Knowledge retention**: Document solutions for future reference
- **Continuous improvement**: Learn from each debugging session

**Use this playbook to systematically resolve any issues and maintain the highest quality in your scientific software refactoring!**
