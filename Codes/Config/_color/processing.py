#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_color/processing.py

Overview
	Color processing functions for layer generation, group color assignment,
	and theme resolution. Extracted from the enhanced working version to
	support the configuration pattern while preserving all advanced functionality.

Functions
	_sample_cmap_hex() → Sample matplotlib colormap for group colors
	build_group_colors_from_labels() → Stable group color assignment
	_adjust_lightness_hls() → HLS lightness scaling for layer variants
	create_processing_bundle() → Main entry point for color processing

Notes
	- All functions are stateless and policy-light
	- Modern error handling and validation patterns preserved
	- Supports both explicit and fallback group color assignment
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

from types import MappingProxyType
import colorsys
import numpy as np
import matplotlib.colors as mcolors
from matplotlib import pyplot as plt

#%% CELL 02 — GROUP COLOR FUNCTIONS

def _sample_cmap_hex(name: str, n: int) -> list[str]:
	"""
	Sample `n` evenly spaced colors from a named matplotlib colormap.

	Args:
		name: Matplotlib colormap name.
		n: Number of samples (n >= 1).

	Returns:
		list[str]: Hex color list length n.

	Raises:
		ValueError: If n < 1 or the colormap is unknown.
	"""
	if not isinstance(n, int) or n < 1:
		raise ValueError("n must be an integer >= 1.")
	try:
		cmap = plt.get_cmap(name)
	except Exception as e:
		raise ValueError(f"Unknown colormap: {name!r}") from e
	samples = cmap(np.linspace(0.0, 1.0, n, dtype=float))
	return [mcolors.to_hex(tuple(c[:3]), keep_alpha=False) for c in samples]


def build_group_colors_from_labels(labels: list[str], group_colors_cmap: str) -> dict[str, str]:
	"""
    Produce a stable label→hex mapping by sampling the specified colormap.

	Args:
		labels: Unique group labels.
		group_colors_cmap: Matplotlib colormap name to sample.

	Returns:
		dict[str, str]: Mapping label -> hex color.

	Raises:
		ValueError: If labels are not unique or empty.
	"""
	arr = np.asarray(labels, dtype=object)
	if arr.size == 0:
		raise ValueError("labels must be non-empty.")
	if arr.size != np.unique(arr).size:
		raise ValueError("Group labels must be unique.")
	hexes = _sample_cmap_hex(group_colors_cmap, len(labels))
	return {lab: hexes[i] for i, lab in enumerate(labels)}


#%% CELL 03 — BEHAVIOR LAYER FUNCTIONS

def _adjust_lightness_hls(hex_color: str, factor: float) -> str:
	"""
	Lighten or darken a hex color by scaling its HLS lightness.

	Args:
		hex_color: Hex string "#RRGGBB".
		factor: Multiplier for lightness L (>0). >1 brightens, <1 darkens.

	Returns:
		str: Hex string after adjustment.

	Raises:
		ValueError: If factor is not finite or <= 0, or hex_color is invalid.
	"""
	if not np.isfinite(factor) or factor <= 0:
		raise ValueError(f"Invalid lightness factor: {factor!r}")
	try:
		r, g, b = mcolors.to_rgb(hex_color)
	except Exception as e:
		raise ValueError(f"Invalid hex color: {hex_color!r}") from e
	h, l, s = colorsys.rgb_to_hls(r, g, b)
	l = np.clip(l * float(factor), 0.0, 1.0)
	r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
	return mcolors.to_hex((r2, g2, b2), keep_alpha=False)


def generate_behavior_layers(
	behavior_colors: dict[str, str],
	layer_factors: dict[str, float]
) -> dict[str, dict[str, str]]:
	"""
	Generate Layer1, Layer2, and Resistant variants from behavior anchor colors.

	Args:
		behavior_colors: Base behavior color mapping.
		layer_factors: Lightness scaling factors for each layer.

	Returns:
		Dict with keys "Layer1", "Layer2", "Resistant" containing color mappings.
	"""
	layers = {}
	
	for layer_name, factor in layer_factors.items():
		layers[layer_name] = {
			name: _adjust_lightness_hls(hex_color, factor)
			for name, hex_color in behavior_colors.items()
		}
	
	return layers


#%% CELL 04 — PROCESSING BUNDLE CREATION

def create_processing_bundle(
	stimulus_base: dict[str, str],
	behavior_colors: dict[str, str],
	sentinel_colors: dict[str, str],
	view_colors: dict[str, str],
	sleap_colors: dict[str, str],
	layer_factors: dict[str, float],
	theme_dark: dict[str, str],
	theme_light: dict[str, str],
	group_colors_cmap: str
) -> MappingProxyType:
	"""
	Create the processing bundle with all derived color structures.

	Args:
		stimulus_base: Base stimulus colors
		behavior_colors: Base behavior colors
		sentinel_colors: Sentinel colors (NaN, NoMotion)
		view_colors: Camera view colors
		sleap_colors: SLEAP body part colors
		layer_factors: Lightness factors for layer generation
		theme_dark: Dark theme colors
		theme_light: Light theme colors
		group_colors_cmap: Colormap name for group color fallback

	Returns:
		MappingProxyType: Immutable bundle with all processed colors
	"""
	# Generate behavior layer variants
	behavior_layers = generate_behavior_layers(behavior_colors, layer_factors)
	
	# Create stimuli with legacy alias (VisualStim → VisualStim_Light)
	stimuli_all = dict(stimulus_base)
	stimuli_all["VisualStim"] = stimulus_base["VisualStim_Light"]
	
	# Create comprehensive behavior mapping (anchors + layered)
	behavior_all = {
		**{f"Layer1_{name}": hex_color for name, hex_color in behavior_layers["Layer1"].items()},
		**{f"Layer2_{name}": hex_color for name, hex_color in behavior_layers["Layer2"].items()},
		**{f"Resistant_{name}": hex_color for name, hex_color in behavior_layers["Resistant"].items()},
		**{name: hex_color for name, hex_color in behavior_colors.items()},
	}
	
	# Prepare sentinel mapping
	sentinel_all = {
		"NaN": sentinel_colors["NaN"],
		"NoMotion": sentinel_colors["NoMotion"],
	}
	
	return MappingProxyType({
		"STIMULI_ALL": stimuli_all,
		"BEHAVIOR_ALL": behavior_all,
		"BEHAVIOR_LAYERS": behavior_layers,
		"SENTINEL_ALL": sentinel_all,
		"VIEW_COLORS": view_colors,
		"SLEAP_COLORS": sleap_colors,
		"THEME_DARK": theme_dark,
		"THEME_LIGHT": theme_light,
		"GROUP_COLORS_CMAP": group_colors_cmap,
		"build_group_colors_from_labels": build_group_colors_from_labels,
	})

__all__ = [
	"_sample_cmap_hex",
	"build_group_colors_from_labels", 
	"_adjust_lightness_hls",
	"generate_behavior_layers",
	"create_processing_bundle"
]
