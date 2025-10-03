"""
Environment and Path Management for Duck

Centralizes path logic for accessing the project repository from within Duck.
Handles both nested .duck/ execution and standalone package installation.
"""

from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    When running inside nested .duck/, uses parent directory as project root.
    When installed as a package, uses current working directory as project root.
    
    Returns:
        Path: The project root directory
    """
    current_file = Path(__file__).resolve()
    
    # Check if we're running inside .duck/ directory
    if current_file.parts[-3:] == ('.duck', 'duck', 'core'):
        # Running from .duck/duck/core/env.py
        # Project root is 3 levels up: .duck/ -> repo root
        return current_file.parents[2]
    
    # Check if we're running from .duck/duck.py
    elif current_file.parts[-2:] == ('.duck', 'duck.py'):
        # Running from .duck/duck.py
        # Project root is 2 levels up: .duck/ -> repo root
        return current_file.parents[1]
    
    # Default: use current working directory (for installed package)
    return Path.cwd()


def get_cursor_dir() -> Path:
    """
    Get the .cursor directory path relative to project root.
    
    Returns:
        Path: The .cursor directory path
    """
    project_root = get_project_root()
    return project_root / ".cursor"


def path_in_repo(*parts: str) -> Path:
    """
    Get a path within the repository relative to project root.
    
    Args:
        *parts: Path components to join
        
    Returns:
        Path: The full path within the repository
        
    Example:
        path_in_repo("Codes", "Config", "experiment.py")
        path_in_repo(".cursor", "rules", "core_rules.mdc")
    """
    project_root = get_project_root()
    return project_root / Path(*parts)


def get_validation_dir() -> Path:
    """
    Get the validation directory path.
    
    Returns:
        Path: The .cursor/validation directory path
    """
    return get_cursor_dir() / "validation"


def get_backup_dir() -> Path:
    """
    Get a backup directory path with timestamp.
    
    Returns:
        Path: A backup directory path
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return get_project_root() / f".cursor_backup_{timestamp}"


def is_nested_execution() -> bool:
    """
    Check if Duck is running from nested .duck/ directory.
    
    Returns:
        bool: True if running from .duck/, False if installed package
    """
    current_file = Path(__file__).resolve()
    return '.duck' in current_file.parts


def get_duck_root() -> Path:
    """
    Get the Duck package root directory.
    
    Returns:
        Path: The .duck directory path
    """
    current_file = Path(__file__).resolve()
    
    if is_nested_execution():
        # Find .duck directory
        for part in current_file.parts:
            if part == '.duck':
                idx = current_file.parts.index('.duck')
                return Path(*current_file.parts[:idx + 1])
    
    # For installed package, Duck root is the package directory
    return current_file.parents[1]  # duck/core -> duck -> package root


# Convenience functions for common paths
def get_codes_dir() -> Path:
    """Get the Codes directory path."""
    return path_in_repo("Codes")


def get_codes_before_dir() -> Path:
    """Get the Codes_Before directory path."""
    return path_in_repo("Codes_Before")


def get_codes_working_dir() -> Path:
    """Get the Codes_Working directory path."""
    return path_in_repo("Codes_Working")


def get_example_files_dir() -> Path:
    """Get the ExampleFiles directory path."""
    return path_in_repo("ExampleFiles")


def get_meta_agent_plan_dir() -> Path:
    """Get the MetaAgentPlan directory path."""
    return path_in_repo("MetaAgentPlan")
