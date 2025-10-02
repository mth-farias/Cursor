#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_experiment/__init__.py

Overview
	Internal module exports for the experiment configuration system.
	This module aggregates processed bundles from internal modules and
	exports them for the main experiment.py controller to use.

Exports
	_STIMULI  → processed stimulus registry and validation
	_PERIODS  → processed period definitions and derived structures
	_TIME     → time conversion functions and period queries
	_REPORT   → report generation functions

Notes
	- This is a private package (_experiment) for internal processing
	- Main user interface remains in Config/experiment.py
	- All bundles are MappingProxyType for immutability
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

from .stimuli import _STIMULI
from .periods import _PERIODS
from .time import _TIME
from .report import _REPORT

__all__ = ["_STIMULI", "_PERIODS", "_TIME", "_REPORT"]
