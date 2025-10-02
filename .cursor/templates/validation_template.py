#!/usr/bin/env python3
"""
Validation Template for Module Refactoring

This template provides a comprehensive validation framework for ensuring
100% functionality preservation during module refactoring.

Usage:
    python validation_template.py

Customize:
    - Update MODULE_NAME and file paths
    - Add specific validation tests for your module
    - Modify baseline capture and comparison logic
"""

import pickle
import json
import sys
from pathlib import Path
from types import MappingProxyType
import numpy as np

# Configuration
MODULE_NAME = "example_module"  # Update this
ORIGINAL_MODULE_PATH = "Codes_Working.Config.example_module"  # Update this
REFACTORED_MODULE_PATH = "Codes.Config.example_module"  # Update this

def capture_baseline():
    """Capture baseline from original working module."""
    print(f"📊 Capturing baseline from {ORIGINAL_MODULE_PATH}...")
    
    # Import original module
    original_module = __import__(ORIGINAL_MODULE_PATH, fromlist=[''])
    original_bundle = getattr(original_module, MODULE_NAME.upper())
    
    # Capture all constants
    baseline_constants = {}
    for key, value in original_bundle.items():
        if isinstance(value, (str, int, float, bool, tuple, list)):
            baseline_constants[key] = value
        elif isinstance(value, np.ndarray):
            baseline_constants[key] = value.tolist()  # Convert for JSON serialization
    
    # Test all functions with sample inputs
    function_tests = {}
    for key, value in original_bundle.items():
        if callable(value):
            function_tests[key] = {
                'inputs': [],  # Add your test inputs here
                'outputs': []
            }
            # Example: Add test cases for each function
            # function_tests[key]['inputs'] = [test_input_1, test_input_2, ...]
    
    # Execute function tests
    for func_name, test_data in function_tests.items():
        if test_data['inputs']:  # Only test if inputs are defined
            func = original_bundle[func_name]
            for input_val in test_data['inputs']:
                try:
                    if isinstance(input_val, tuple):
                        result = func(*input_val)
                    else:
                        result = func(input_val)
                    test_data['outputs'].append(result)
                except Exception as e:
                    test_data['outputs'].append(f"ERROR: {str(e)}")
    
    # Save baseline data
    baseline_data = {
        'constants': baseline_constants,
        'function_tests': function_tests,
        'bundle_keys': list(original_bundle.keys()),
        'bundle_type': str(type(original_bundle))
    }
    
    # Save as both pickle and JSON
    baseline_file = Path(f'.cursor/validation/baselines/{MODULE_NAME}_baseline.pkl')
    baseline_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(baseline_file, 'wb') as f:
        pickle.dump(baseline_data, f)
    
    json_file = baseline_file.with_suffix('.json')
    with open(json_file, 'w') as f:
        json.dump(baseline_data, f, indent=2, default=str)
    
    print(f"✅ Baseline saved to {baseline_file}")
    return baseline_data

def validate_refactored():
    """Validate refactored module against baseline."""
    print(f"🔍 Validating refactored {REFACTORED_MODULE_PATH}...")
    
    # Load baseline
    baseline_file = Path(f'.cursor/validation/baselines/{MODULE_NAME}_baseline.pkl')
    if not baseline_file.exists():
        print("❌ No baseline found. Run capture_baseline() first.")
        return False
    
    with open(baseline_file, 'rb') as f:
        baseline_data = pickle.load(f)
    
    # Import refactored module
    try:
        refactored_module = __import__(REFACTORED_MODULE_PATH, fromlist=[''])
        refactored_bundle = getattr(refactored_module, MODULE_NAME.upper())
    except ImportError as e:
        print(f"❌ Failed to import refactored module: {e}")
        return False
    
    success = True
    
    # Verify bundle structure
    print("\n📋 Verifying bundle structure...")
    original_keys = set(baseline_data['bundle_keys'])
    refactored_keys = set(refactored_bundle.keys())
    
    missing_keys = original_keys - refactored_keys
    extra_keys = refactored_keys - original_keys
    
    if missing_keys:
        print(f"❌ MISSING KEYS: {missing_keys}")
        success = False
    if extra_keys:
        print(f"❌ EXTRA KEYS: {extra_keys}")
        success = False
    if not missing_keys and not extra_keys:
        print("✅ All keys present and accounted for")
    
    # Verify constants
    print("\n🔢 Verifying constants...")
    for const_name, original_value in baseline_data['constants'].items():
        if const_name not in refactored_bundle:
            print(f"❌ MISSING CONSTANT: {const_name}")
            success = False
            continue
        
        refactored_value = refactored_bundle[const_name]
        
        # Handle numpy arrays
        if isinstance(original_value, list) and isinstance(refactored_value, np.ndarray):
            if not np.array_equal(np.array(original_value), refactored_value):
                print(f"❌ CONSTANT CHANGED: {const_name}")
                success = False
            else:
                print(f"✅ {const_name}: IDENTICAL")
        elif original_value != refactored_value:
            print(f"❌ CONSTANT CHANGED: {const_name}")
            print(f"   Original: {original_value}")
            print(f"   Refactored: {refactored_value}")
            success = False
        else:
            print(f"✅ {const_name}: IDENTICAL")
    
    # Verify functions
    print("\n🔧 Verifying functions...")
    for func_name, test_data in baseline_data['function_tests'].items():
        if not test_data['inputs']:
            print(f"⚠️  {func_name}: No test inputs defined")
            continue
        
        if func_name not in refactored_bundle:
            print(f"❌ MISSING FUNCTION: {func_name}")
            success = False
            continue
        
        func = refactored_bundle[func_name]
        for i, input_val in enumerate(test_data['inputs']):
            try:
                if isinstance(input_val, tuple):
                    new_result = func(*input_val)
                else:
                    new_result = func(input_val)
                
                original_result = test_data['outputs'][i]
                
                # Handle numpy arrays
                if isinstance(new_result, np.ndarray):
                    if isinstance(original_result, str) and original_result.startswith("ERROR:"):
                        print(f"❌ FUNCTION BEHAVIOR CHANGED: {func_name}({input_val})")
                        success = False
                    elif not np.array_equal(new_result, np.array(original_result)):
                        print(f"❌ FUNCTION OUTPUT CHANGED: {func_name}({input_val})")
                        success = False
                else:
                    if new_result != original_result:
                        print(f"❌ FUNCTION OUTPUT CHANGED: {func_name}({input_val})")
                        print(f"   Original: {original_result}")
                        print(f"   Refactored: {new_result}")
                        success = False
            except Exception as e:
                original_result = test_data['outputs'][i]
                if not (isinstance(original_result, str) and original_result.startswith("ERROR:")):
                    print(f"❌ FUNCTION ERROR: {func_name}({input_val}) - {e}")
                    success = False
        
        print(f"✅ {func_name}: ALL OUTPUTS IDENTICAL")
    
    # Verify bundle type
    if str(type(refactored_bundle)) != baseline_data['bundle_type']:
        print(f"❌ BUNDLE TYPE CHANGED: {baseline_data['bundle_type']} → {type(refactored_bundle)}")
        success = False
    else:
        print("✅ Bundle type preserved (MappingProxyType)")
    
    return success

def generate_report(success: bool):
    """Generate validation report."""
    report_file = Path(f'.cursor/validation/reports/{MODULE_NAME}_validation_report.md')
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    status = "✅ PASSED" if success else "❌ FAILED"
    
    report = f"""# {MODULE_NAME.title()} Validation Report

## Summary
- **Status**: {status}
- **Date**: {Path(__file__).stat().st_mtime}
- **Original Module**: {ORIGINAL_MODULE_PATH}
- **Refactored Module**: {REFACTORED_MODULE_PATH}

## Results
{'All validation checks passed! 🎉' if success else 'Some validation checks failed. See details above.'}

## Next Steps
{'Ready for production use.' if success else 'Fix failing checks before proceeding.'}
"""
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to {report_file}")

def main():
    """Main validation workflow."""
    if len(sys.argv) > 1 and sys.argv[1] == "baseline":
        capture_baseline()
    else:
        success = validate_refactored()
        generate_report(success)
        
        if success:
            print("\n🎉 ALL VALIDATION CHECKS PASSED!")
            print("The refactored module preserves 100% functionality.")
        else:
            print("\n❌ VALIDATION FAILED!")
            print("Fix the issues above before proceeding.")
            sys.exit(1)

if __name__ == "__main__":
    main()
