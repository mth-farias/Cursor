#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_color/__init__.py

Overview
	Internal module exports for the color configuration system.
	This module aggregates processed bundles from internal modules and
	exports them for the main color.py controller to use.

Exports
	_PROCESSING → processed color structures and layer variants
	_COLORMAPS  → matplotlib colormap objects
	_RESOLVERS  → hex resolver functions and sophisticated lookups
	_REPORT     → visual report generation functions
	configure   → function to configure all bundles with user parameters

Notes
	- This is a private package (_color) for internal processing
	- Main user interface remains in Config/color.py
	- All bundles are MappingProxyType for immutability
	- Follows exact pattern from _experiment package
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

# Import modules, not the variables directly
from . import processing
from . import colormaps
from . import resolvers
from . import report

# Export the static report
_REPORT = report.create_report_bundle()

# These will be set by configure()
_PROCESSING = None
_COLORMAPS = None
_RESOLVERS = None

#%% CELL 02 — CONFIGURATION

def configure(
	group_colors_cmap: str,
	stimulus_base: dict[str, str],
	sentinel_colors: dict[str, str],
	behavior_colors: dict[str, str],
	layer_lightness_factors: dict[str, float],
	motion_speed_decisions: dict[str, object],
	view_colors: dict[str, str],
	sleap_colors: dict[str, str],
	orientation_decisions: dict[str, float],
	theme_dark: dict[str, str],
	theme_light: dict[str, str]
):
	"""
	Configure all color modules with user parameters.
	This updates the module-level _PROCESSING, _COLORMAPS, _RESOLVERS bundles.
	
	Args:
		group_colors_cmap: Matplotlib colormap name for group color fallback
		stimulus_base: Base stimulus colors
		sentinel_colors: Sentinel colors (NaN, NoMotion)
		behavior_colors: Base behavior colors
		layer_lightness_factors: Lightness scaling factors for layers
		motion_speed_decisions: Motion speed policy with control points
		view_colors: Camera view colors
		sleap_colors: SLEAP body part colors
		orientation_decisions: Orientation policy with rotation and dark factor
		theme_dark: Dark theme colors
		theme_light: Light theme colors
	"""
	global _PROCESSING, _COLORMAPS, _RESOLVERS
	
	# Step 1: Create processing bundle (layer generation, group handling)
	processing_bundle = processing.create_processing_bundle(
		stimulus_base,
		behavior_colors,
		sentinel_colors,
		view_colors,
		sleap_colors,
		layer_lightness_factors,
		theme_dark,
		theme_light,
		group_colors_cmap
	)
	
	# Step 2: Create colormaps bundle (needs processing results for over color)
	colormaps_bundle = colormaps.create_colormaps_bundle(
		motion_speed_decisions,
		orientation_decisions,
		processing_bundle["BEHAVIOR_LAYERS"]
	)
	
	# Step 3: Create resolvers bundle (needs all previous bundles)
	resolvers_bundle = resolvers.create_resolvers_bundle(
		processing_bundle,
		colormaps_bundle,
		motion_speed_decisions
	)
	
	# Step 4: Handle experiment.py group color integration (best effort)
	try:
		# Try to get group colors from experiment integration
		groups_dict = {}
		
		# Package-relative first, then absolute (standalone)
		try:
			from ..experiment import EXPERIMENT  # type: ignore
		except Exception:
			try:
				import experiment as _exp  # type: ignore
				EXPERIMENT = getattr(_exp, "EXPERIMENT")
			except Exception:
				EXPERIMENT = None
		
		if EXPERIMENT:
			_groups_obj = EXPERIMENT.get("GROUPS", None)
			if isinstance(_groups_obj, dict):
				for k, v in _groups_obj.items():
					lbl = str(k)
					if isinstance(v, dict) and "color" in v:
						col = v["color"]
						if isinstance(col, str) and col.startswith("#"):
							groups_dict[lbl] = col
					elif isinstance(v, str) and v.startswith("#"):
						groups_dict[lbl] = v
			elif isinstance(_groups_obj, (list, tuple)):
				groups_dict.update(
					processing_bundle["build_group_colors_from_labels"](
						[str(x) for x in _groups_obj], group_colors_cmap
					)
				)
		
		# Update the group proxy with explicit colors
		if groups_dict:
			group_proxy = resolvers_bundle["hex"]["group"]
			group_proxy.update(groups_dict)
			
	except Exception:
		# best-effort; never break session
		pass
	
	# Step 5: Update module-level variables in this module
	_PROCESSING = processing_bundle
	_COLORMAPS = colormaps_bundle
	_RESOLVERS = resolvers_bundle
	
	# Also update the individual module variables for consistency
	processing._PROCESSING = processing_bundle
	colormaps._COLORMAPS = colormaps_bundle
	resolvers._RESOLVERS = resolvers_bundle

__all__ = ["_PROCESSING", "_COLORMAPS", "_RESOLVERS", "_REPORT", "configure"]
