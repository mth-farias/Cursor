#%% CELL 00 — HEADER & OVERVIEW
"""
Configuration Pattern Example

This demonstrates the revolutionary configuration pattern established
by the experiment.py refactoring. Use this as a template for all
Config module refactoring.

Pattern:
1. User constants stay in main module
2. Processing logic moves to _module/ package  
3. configure() function handles all complexity
4. Clean separation: interface vs implementation
"""

#%% CELL 01 — IMPORTS
from __future__ import annotations
import sys
from pathlib import Path
from types import MappingProxyType

# Package path setup (for safe absolute imports)
ROOT = Path(__file__).resolve().parents[1]  # .../Codes
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#%% CELL 02 — USER INPUT
"""
All user-editable constants stay here.
Users should only need to edit this section.
"""

# Example user constants
USER_SETTING_1: str = "example_value"
USER_SETTING_2: int = 42
USER_SETTING_3: dict = {
    "option_a": {"value": 1.0, "enabled": True},
    "option_b": {"value": 2.0, "enabled": False},
}

#%% CELL 03 — PROCESSING & ASSEMBLY
"""
Import internal processing modules and create the final bundle.
This is where the configuration pattern magic happens.
"""

# Import internal processing modules
import importlib
current_dir = Path(__file__).parent
module_path = current_dir / "_module"

if module_path.exists():
    sys.path.insert(0, str(current_dir))
    _module = importlib.import_module("_module")
else:
    from . import _module

# Single configuration call - all complexity hidden here!
_module.configure(USER_SETTING_1, USER_SETTING_2, USER_SETTING_3)

#%% CELL 04 — PUBLIC API
"""
Immutable public bundle assembled from user constants + processed results.
"""

_PUBLIC = {
    # User constants (direct export)
    "USER_SETTING_1": USER_SETTING_1,
    "USER_SETTING_2": USER_SETTING_2, 
    "USER_SETTING_3": USER_SETTING_3,
    
    # Processed results from internal modules
    **_module._PROCESSED_DATA,
    **_module._FUNCTIONS,
    **_module._DERIVED_STRUCTURES,
}

MODULE_BUNDLE = MappingProxyType(_PUBLIC)
__all__ = ["MODULE_BUNDLE"]

#%% CELL 05 — REPORT
"""
Human-readable summary when run directly.
"""

if __name__ == "__main__":
    _module._REPORT["render_module_report"](MODULE_BUNDLE)
