#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/__init__.py

Overview
	Aggregates the canonical read-only bundles from the Config package.
	Re-exports the following immutable registries:

	- PATH       → canonical folder map and helpers
	- PARAM      → parameter registry (column schema)
	- EXPERIMENT → experiment facts, timebase, periods, stimuli
	- COLOR      → color anchors, layer variants, and colormaps

Usage
	from Config import PATH, PARAM, EXPERIMENT, COLOR

Notes
	* Bundles are MappingProxyType-backed; treat them as immutable.
	* Submodules remain importable directly for deeper inspection.
"""


#%% CELL 01 — IMPORTS & PUBLIC API

from __future__ import annotations

from .experiment import EXPERIMENT
from .color import COLOR

# TODO: Import other config modules when they are refactored
# from .path import PATH
# from .param import PARAM

__all__ = ["EXPERIMENT", "COLOR"]
