"""
Duck Core Module

Core intelligence and functionality for the Duck ecosystem.
"""

from .system import create_duck, Duck
from .validation import DuckValidator, validate_module
from .patterns import PatternApplicator, apply_configuration_pattern
from .env import get_project_root, get_cursor_dir, path_in_repo

__all__ = [
    "create_duck",
    "Duck",
    "DuckValidator", 
    "validate_module",
    "PatternApplicator",
    "apply_configuration_pattern",
    "get_project_root",
    "get_cursor_dir",
    "path_in_repo",
]
