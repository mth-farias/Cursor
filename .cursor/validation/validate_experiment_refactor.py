#!/usr/bin/env python3
"""
Baseline Validation Script for Config/experiment.py Refactoring

This script captures the complete baseline behavior of the current experiment.py
module before refactoring, then validates that the refactored version produces
identical results.

Usage:
    # Before refactoring - capture baseline
    python validate_experiment_refactor.py --capture
    
    # After refactoring - validate identical behavior  
    python validate_experiment_refactor.py --validate
    
    # Clean up validation files
    python validate_experiment_refactor.py --clean
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from types import MappingProxyType
import numpy as np

# Setup path for imports
ROOT = Path(__file__).resolve().parents[2]  # .../Cursor
CODES_WORKING = ROOT / "Codes_Working"
CODES_NEW = ROOT / "Codes"

def capture_baseline():
    """Capture complete baseline from Codes_Working/Config/experiment.py"""
    print("🔍 Capturing baseline from Codes_Working/Config/experiment.py...")
    
    # Add Codes_Working to path
    if str(CODES_WORKING) not in sys.path:
        sys.path.insert(0, str(CODES_WORKING))
    
    try:
        from Config import experiment
        
        # Capture original EXPERIMENT bundle
        original_experiment = dict(experiment.EXPERIMENT)
        
        # Save baseline for comparison
        baseline_file = Path(__file__).parent / 'experiment_baseline.pkl'
        with open(baseline_file, 'wb') as f:
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
                'inputs': [1.0, 2.5, [1.0, 2.0, 3.0], np.array([0.5, 1.5, 2.5])],
                'outputs': []
            },
            'frames_to_seconds': {
                'inputs': [60, 150, [60, 120, 180], np.array([30, 90, 150])],
                'outputs': []
            },
            'period_by_frame': {
                'inputs': [0, 100, 1000, 5000, 10000, 50000],
                'outputs': []
            },
            'period_by_frames': {
                'inputs': [np.array([0, 100, 1000]), np.array([5000, 10000, 50000])],
                'outputs': []
            },
            'in_period': {
                'inputs': [('Baseline', 100), ('Stimulation', 5000), ('Recovery', 25000), ('Baseline', 50000)],
                'outputs': []
            }
        }
        
        # Execute function tests
        for func_name, test_data in function_tests.items():
            func = experiment.EXPERIMENT[func_name]
            for input_val in test_data['inputs']:
                try:
                    if isinstance(input_val, tuple):
                        result = func(*input_val)
                    else:
                        result = func(input_val)
                    
                    # Convert numpy arrays to lists for JSON serialization
                    if isinstance(result, np.ndarray):
                        result = result.tolist()
                    elif isinstance(result, np.integer):
                        result = int(result)
                    elif isinstance(result, np.floating):
                        result = float(result)
                        
                    test_data['outputs'].append(result)
                except Exception as e:
                    test_data['outputs'].append(f"ERROR: {str(e)}")
        
        # Capture derived structures
        derived_structures = {}
        for key in ['PERIOD_ORDER', 'PERIODS_DERIVED', 'STIMULI_DERIVED', 
                   'EXPERIMENT_TOTAL_FRAMES', 'EXPERIMENT_TOTAL_SECONDS',
                   'PERIOD_DUR_SEC', 'PERIOD_DUR_FRAMES', 'PERIOD_STARTS', 'PERIOD_ENDS_EXCLUSIVE']:
            value = experiment.EXPERIMENT[key]
            if isinstance(value, np.ndarray):
                derived_structures[key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                derived_structures[key] = value.item()
            else:
                derived_structures[key] = value
        
        # Save all baseline data
        baseline_data = {
            'constants': baseline_constants,
            'function_tests': function_tests,
            'derived_structures': derived_structures,
            'experiment_keys': list(original_experiment.keys()),
            'metadata': {
                'total_keys': len(original_experiment),
                'frame_rate': experiment.FRAME_RATE,
                'total_frames': experiment.EXPERIMENT_TOTAL_FRAMES,
                'total_seconds': experiment.EXPERIMENT_TOTAL_SECONDS,
            }
        }
        
        baseline_json = Path(__file__).parent / 'experiment_baseline.json'
        with open(baseline_json, 'w') as f:
            json.dump(baseline_data, f, indent=2, default=str)
        
        print("✅ Baseline captured successfully")
        print(f"   📁 Binary data: {baseline_file}")
        print(f"   📄 JSON data: {baseline_json}")
        print(f"   🔑 Total keys: {len(original_experiment)}")
        print(f"   ⏱️  Frame rate: {experiment.FRAME_RATE} fps")
        print(f"   📊 Total frames: {experiment.EXPERIMENT_TOTAL_FRAMES}")
        
    except Exception as e:
        print(f"❌ Error capturing baseline: {e}")
        raise
    finally:
        # Clean up sys.path
        if str(CODES_WORKING) in sys.path:
            sys.path.remove(str(CODES_WORKING))


def validate_refactored():
    """Validate that refactored version produces identical results"""
    print("🔍 Validating refactored Config/experiment.py...")
    
    # Load baseline
    baseline_file = Path(__file__).parent / 'experiment_baseline.pkl'
    baseline_json = Path(__file__).parent / 'experiment_baseline.json'
    
    if not baseline_file.exists() or not baseline_json.exists():
        print("❌ Baseline files not found. Run --capture first.")
        return False
    
    with open(baseline_file, 'rb') as f:
        original_experiment = pickle.load(f)
    
    with open(baseline_json, 'r') as f:
        baseline_data = json.load(f)
    
    # Add Codes to path for refactored version
    if str(CODES_NEW) not in sys.path:
        sys.path.insert(0, str(CODES_NEW))
    
    try:
        from Config import experiment  # New refactored version
        
        # Compare new EXPERIMENT bundle
        new_experiment = dict(experiment.EXPERIMENT)
        
        # CRITICAL: Verify all keys are identical
        missing_keys = set(original_experiment.keys()) - set(new_experiment.keys())
        extra_keys = set(new_experiment.keys()) - set(original_experiment.keys())
        
        if missing_keys:
            print(f"❌ MISSING KEYS: {missing_keys}")
            return False
        if extra_keys:
            print(f"❌ EXTRA KEYS: {extra_keys}")
            return False
        
        print("✅ All keys present and accounted for")
        
        # CRITICAL: Verify all constants are identical
        constants_ok = True
        for const_name, original_value in baseline_data['constants'].items():
            try:
                new_value = getattr(experiment, const_name, None)
                if new_value != original_value:
                    print(f"❌ CONSTANT CHANGED: {const_name}")
                    print(f"   Original: {original_value}")
                    print(f"   New: {new_value}")
                    constants_ok = False
                else:
                    print(f"✅ {const_name}: IDENTICAL")
            except Exception as e:
                print(f"❌ Error checking constant {const_name}: {e}")
                constants_ok = False
        
        if not constants_ok:
            return False
        
        # CRITICAL: Verify all functions produce identical outputs
        functions_ok = True
        for func_name, test_data in baseline_data['function_tests'].items():
            try:
                func = experiment.EXPERIMENT[func_name]
                for i, input_val in enumerate(test_data['inputs']):
                    if isinstance(input_val, tuple):
                        new_result = func(*input_val)
                    else:
                        new_result = func(input_val)
                    
                    original_result = test_data['outputs'][i]
                    
                    # Handle numpy arrays and different numeric types
                    if isinstance(new_result, np.ndarray):
                        new_result_list = new_result.tolist()
                        if new_result_list != original_result:
                            print(f"❌ FUNCTION OUTPUT CHANGED: {func_name}({input_val})")
                            print(f"   Original: {original_result}")
                            print(f"   New: {new_result_list}")
                            functions_ok = False
                    elif isinstance(new_result, (np.integer, np.floating)):
                        new_result_native = new_result.item()
                        if new_result_native != original_result:
                            print(f"❌ FUNCTION OUTPUT CHANGED: {func_name}({input_val})")
                            print(f"   Original: {original_result}")
                            print(f"   New: {new_result_native}")
                            functions_ok = False
                    else:
                        if new_result != original_result:
                            print(f"❌ FUNCTION OUTPUT CHANGED: {func_name}({input_val})")
                            print(f"   Original: {original_result}")
                            print(f"   New: {new_result}")
                            functions_ok = False
                
                if functions_ok:
                    print(f"✅ {func_name}: ALL OUTPUTS IDENTICAL")
                    
            except Exception as e:
                print(f"❌ Error testing function {func_name}: {e}")
                functions_ok = False
        
        if not functions_ok:
            return False
        
        # CRITICAL: Verify derived structures are identical
        structures_ok = True
        for struct_name, original_value in baseline_data['derived_structures'].items():
            try:
                new_value = experiment.EXPERIMENT[struct_name]
                
                if isinstance(new_value, np.ndarray):
                    new_value_list = new_value.tolist()
                    if new_value_list != original_value:
                        print(f"❌ DERIVED STRUCTURE CHANGED: {struct_name}")
                        structures_ok = False
                elif isinstance(new_value, (dict, MappingProxyType)):
                    if dict(new_value) != original_value:
                        print(f"❌ DERIVED STRUCTURE CHANGED: {struct_name}")
                        structures_ok = False
                elif isinstance(new_value, (np.integer, np.floating)):
                    if new_value.item() != original_value:
                        print(f"❌ DERIVED STRUCTURE CHANGED: {struct_name}")
                        structures_ok = False
                else:
                    if new_value != original_value:
                        print(f"❌ DERIVED STRUCTURE CHANGED: {struct_name}")
                        structures_ok = False
                
                if structures_ok:
                    print(f"✅ {struct_name}: IDENTICAL")
                    
            except Exception as e:
                print(f"❌ Error checking structure {struct_name}: {e}")
                structures_ok = False
        
        if structures_ok:
            print("🎉 ALL VALIDATION CHECKS PASSED!")
            print("✅ Refactoring preserved all functionality perfectly")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error validating refactored version: {e}")
        return False
    finally:
        # Clean up sys.path
        if str(CODES_NEW) in sys.path:
            sys.path.remove(str(CODES_NEW))


def clean_validation_files():
    """Remove validation files"""
    validation_dir = Path(__file__).parent
    files_to_remove = [
        validation_dir / 'experiment_baseline.pkl',
        validation_dir / 'experiment_baseline.json'
    ]
    
    removed_count = 0
    for file_path in files_to_remove:
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️  Removed: {file_path.name}")
            removed_count += 1
    
    if removed_count == 0:
        print("ℹ️  No validation files to clean")
    else:
        print(f"✅ Cleaned {removed_count} validation files")


def main():
    parser = argparse.ArgumentParser(description="Validate Config/experiment.py refactoring")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--capture', action='store_true', help='Capture baseline from current version')
    group.add_argument('--validate', action='store_true', help='Validate refactored version against baseline')
    group.add_argument('--clean', action='store_true', help='Clean up validation files')
    
    args = parser.parse_args()
    
    if args.capture:
        capture_baseline()
    elif args.validate:
        success = validate_refactored()
        sys.exit(0 if success else 1)
    elif args.clean:
        clean_validation_files()


if __name__ == "__main__":
    main()
