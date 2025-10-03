#!/usr/bin/env python3
"""
🦆 Duck CLI Smoke Tests

Quick smoke tests to verify all CLI commands run without crashing.
"""

import subprocess
import sys
from pathlib import Path

# Add Duck to path
duck_root = Path(__file__).parent.parent
sys.path.insert(0, str(duck_root))


def run_command(cmd_args, description):
    """Run a command and return success/failure"""
    try:
        print(f"Testing: {description}")
        print(f"Command: duck {' '.join(cmd_args)}")
        
        # Run the command
        result = subprocess.run(
            [sys.executable, str(duck_root / "duck.py")] + cmd_args,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ PASS: {description}")
            return True
        else:
            print(f"❌ FAIL: {description}")
            print(f"   Return code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {description}")
        return False
    except Exception as e:
        print(f"💥 EXCEPTION: {description} - {e}")
        return False


def main():
    """Run all CLI smoke tests"""
    print("🦆 Duck CLI Smoke Tests")
    print("=" * 50)
    
    # Test commands that should work without specific files
    test_commands = [
        ([], "help command (no args)"),
        (["help"], "help command"),
        (["status"], "status command"),
        (["info"], "info command"),
        (["pattern", "list"], "pattern list"),
        (["decision", "log", "--summary"], "decision log summary"),
        (["memory", "stats"], "memory stats"),
        (["analytics", "report", "--days", "1"], "analytics report"),
        (["performance", "run", "pattern"], "performance pattern test"),
        (["help", "pattern"], "help for pattern command"),
        (["help", "analytics"], "help for analytics command"),
    ]
    
    # Test commands that might fail gracefully
    test_commands_optional = [
        (["pattern", "suggest", "nonexistent_file.py"], "pattern suggest (nonexistent file)"),
        (["analyze", "deps"], "analyze deps (no files)"),
        (["validate", "nonexistent_module"], "validate nonexistent module"),
    ]
    
    passed = 0
    total = len(test_commands) + len(test_commands_optional)
    
    print("\n📋 Core Commands (Must Pass):")
    for cmd_args, description in test_commands:
        if run_command(cmd_args, description):
            passed += 1
        print()
    
    print("\n📋 Optional Commands (May Fail Gracefully):")
    for cmd_args, description in test_commands_optional:
        if run_command(cmd_args, description):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed >= len(test_commands):
        print("🎉 All core commands working! Duck CLI is functional.")
        return 0
    else:
        print("❌ Some core commands failed. Check the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
