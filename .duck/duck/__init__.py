"""
🦆 Duck - Revolutionary Personal AI Ecosystem

A maximally automated, auto-upgradable personal AI ecosystem that serves as your
virtual copy and development buddy with universal invocation across all platforms.

Version: 1.0.0-beta
Python: >=3.11
"""

__version__ = "1.0.0-beta"
__author__ = "Matheus"
__description__ = "Revolutionary Personal AI Ecosystem"

# Core imports for easy access
from .core.system import create_duck, Duck
from .core.validation import DuckValidator, validate_module
from .core.patterns import PatternApplicator, apply_configuration_pattern

__all__ = [
    "create_duck",
    "Duck", 
    "DuckValidator",
    "validate_module",
    "PatternApplicator",
    "apply_configuration_pattern",
]
