#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_color/resolvers.py

Overview
	Sophisticated hex resolver functions for runtime color lookups.
	Extracted from the enhanced working version to support the configuration
	pattern while preserving advanced vectorized resolvers and dynamic fallbacks.

Functions
	motion_speed_hex() → Advanced speed+motion resolver with sentinel logic
	orientation_hex() → Angle to hex conversion via orientation wheel
	_GroupProxy class → Dynamic group color fallback with caching
	_motion_speed_hex_resolver() → Vectorized resolver supporting arrays
	create_resolvers_bundle() → Main entry point for resolver creation

Notes
	- Preserves vectorized array support for motion speed resolution
	- Maintains sophisticated sentinel handling (NoMotion vs NaN)
	- Supports dynamic group color fallback with stable hashing
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

from types import MappingProxyType
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

#%% CELL 02 — BASIC RESOLVER FUNCTIONS

def stimulus_hex(label: str, stimulus_colors: dict[str, str]) -> str:
	"""
	Lookup hex for a stimulus label.

	Args:
		label: One of stimulus keys (e.g., "Stim0", "Stim1", "VisualStim_Dark", "VisualStim_Light").
		stimulus_colors: Stimulus color mapping.

	Returns:
		str: Hex color.

	Raises:
		KeyError: If the label is unknown.
	"""
	try:
		return stimulus_colors[label]
	except KeyError as e:
		raise KeyError(f"Unknown stimulus label: {label!r}") from e


def behavior_hex(layer: str, name: str, behavior_layers: dict[str, dict[str, str]], behavior_colors: dict[str, str]) -> str:
	"""
	Lookup hex for a behavior name within a specific layer.

	Args:
		layer: "Anchor" | "Layer1" | "Layer2" | "Resistant"
		name: Behavior name (e.g., "Walk", "Freeze", "Jump", ...).
		behavior_layers: Layer color mappings.
		behavior_colors: Base behavior colors.

	Returns:
		str: Hex color.

	Raises:
		KeyError: If the layer or behavior is unknown.
	"""
	if layer == "Anchor":
		table = behavior_colors
	elif layer in behavior_layers:
		table = behavior_layers[layer]
	else:
		raise KeyError(f"Unknown behavior layer: {layer!r}")
	try:
		return table[name]
	except KeyError as e:
		raise KeyError(f"Unknown behavior name: {name!r}") from e


def view_hex(label: str, view_colors: dict[str, str]) -> str:
	"""
	Lookup hex for a camera view.

	Args:
		label: One of view keys.
		view_colors: View color mapping.

	Returns:
		str: Hex color.

	Raises:
		KeyError: If the label is unknown.
	"""
	try:
		return view_colors[label]
	except KeyError as e:
		raise KeyError(f"Unknown view label: {label!r}") from e


def sleap_hex(label: str, sleap_colors: dict[str, str]) -> str:
	"""
	Lookup hex for a SLEAP body part.

	Args:
		label: One of SLEAP keys.
		sleap_colors: SLEAP color mapping.

	Returns:
		str: Hex color.

	Raises:
		KeyError: If the label is unknown.
	"""
	try:
		return sleap_colors[label]
	except KeyError as e:
		raise KeyError(f"Unknown SLEAP label: {label!r}") from e


#%% CELL 03 — ADVANCED RESOLVER FUNCTIONS

def motion_speed_hex(
	speed: float,
	motion: int,
	cmap: LinearSegmentedColormap,
	sentinel_colors: dict[str, str],
	plateau_end: float,
) -> str:
	"""
	Map (speed, motion) to a hex color with sentinel-aware policy.

	Args:
		speed: Speed in mm/s (float; may be 0.0).
		motion: Binary motion flag (0 or 1). Controls sentinel vs colormap.
		cmap: Motion–speed colormap.
		sentinel_colors: Sentinel color mapping.
		plateau_end: Upper domain bound used for colormap normalization.

	Returns:
		str: Hex color.

	Policy:
		- If motion == 0: return sentinel["NoMotion"] (semantic state).
		- Else if speed is non-finite: return sentinel["NaN"].
		- Else: map speed via the colormap. Values > plateau_end use the cmap's 'over' color.
		- Note: speed == 0.0 with motion == 1 is valid and maps to the low-end color.
	"""
	# Motion sentinel takes precedence over speed
	if motion == 0:
		return sentinel_colors["NoMotion"]

	# NaN/Inf handling for speed
	if not np.isfinite(speed):
		return sentinel_colors["NaN"]

	# Positive/zero speeds use the colormap (0 maps to low-end color).
	# Keep clip=False so 'over' color engages for speed > plateau_end.
	norm = mcolors.Normalize(vmin=0.0, vmax=plateau_end, clip=False)
	r, g, b, _ = cmap(norm(float(speed)))
	return mcolors.to_hex((r, g, b), keep_alpha=False)


def orientation_hex(angle_deg: float, orientation_cmap: ListedColormap) -> str:
	"""
	Map a compass angle (degrees) to a hex via the orientation wheel.

	Args:
		angle_deg: Angle in degrees (0..360; wraps via modulo).
		orientation_cmap: ListedColormap for orientation.

	Returns:
		str: Hex color.
	"""
	idx = int(np.mod(angle_deg, 360.0) / 360.0 * orientation_cmap.N)
	r, g, b, _ = orientation_cmap(idx)
	return mcolors.to_hex((r, g, b), keep_alpha=False)


#%% CELL 04 — GROUP COLOR PROXY

def _sample_group_color(label: str, group_colors_cmap: str) -> str:
	"""Stable fallback for unknown group labels via hashed sampling."""
	h = (hash(str(label)) & 0xFFFFFFFF) / 0xFFFFFFFF
	r, g, b, _ = mcolors.get_cmap(group_colors_cmap)(h)
	return mcolors.to_hex((r, g, b), keep_alpha=False)


class _GroupProxy(dict):
	"""Mapping that returns/caches a stable fallback color when a label is missing."""
	
	def __init__(self, initial_groups: dict[str, str], group_colors_cmap: str):
		super().__init__(initial_groups)
		self._group_colors_cmap = group_colors_cmap
	
	def __missing__(self, key: str) -> str:
		hexv = _sample_group_color(key, self._group_colors_cmap)
		self[key] = hexv
		return hexv


#%% CELL 05 — VECTORIZED RESOLVER

def create_motion_speed_hex_resolver(
	speed_cmap: LinearSegmentedColormap,
	sentinel_colors: dict[str, str],
	behavior_all: dict[str, str],
	plateau_end: float
):
	"""
	Create a vectorized motion speed resolver supporting arrays.

	Args:
		speed_cmap: Motion speed colormap
		sentinel_colors: Sentinel color mapping
		behavior_all: All behavior colors (for over color)
		plateau_end: Plateau cutoff value

	Returns:
		Callable: Vectorized resolver function
	"""
	over_hex = behavior_all.get("Resistant_Jump", "#000000")
	
	def _motion_speed_hex_resolver(speed_value, motion_flag=None):
		"""
		Map speed+motion to hex with gate and cutoff baked in.

		Args:
			speed_value: float|int|array — physical speed (mm/s) preferred; if [0..1], still OK.
			motion_flag: int|array|None — 0 ⇒ NoMotion; 1 ⇒ use speed; None ⇒ treat as 1.

		Returns:
			Hex string for scalar inputs, or list[str] for arrays.

		Notes:
			- Cutoff = plateau_end mm/s internally. Values > cutoff snap to Resistant_Jump.
			- NaN speed ⇒ NaN sentinel (when motion=1); motion=0 overrides to NoMotion.
		"""
		def _resolve_one(v: float, m) -> str:
			# motion gate (0 dominates)
			if m == 0:
				return sentinel_colors["NoMotion"]
			# handle NaN speed under motion=1 (or None treated as 1)
			if not np.isfinite(v):
				return sentinel_colors["NaN"]
			# normalize mm/s to [0,1] against cutoff
			u = float(v) / plateau_end
			if u > 1.0:
				return over_hex
			u = float(np.clip(u, 0.0, 1.0))
			r, g, b, _ = speed_cmap(u)
			return mcolors.to_hex((r, g, b), keep_alpha=False)

		# vectorize for arrays; broadcast motion if needed
		s_arr = np.asarray(speed_value)
		m_arr = np.asarray(1 if motion_flag is None else motion_flag)

		if s_arr.ndim == 0 and m_arr.ndim == 0:
			return _resolve_one(float(s_arr), int(m_arr))

		# broadcast to same shape
		s_b = np.asarray(s_arr, dtype=float)
		m_b = np.asarray(m_arr, dtype=int)
		if m_b.shape != s_b.shape:
			try:
				m_b = np.broadcast_to(m_b, s_b.shape)
			except Exception:
				# fallback: treat missing shape as "moving"
				m_b = np.ones_like(s_b, dtype=int)

		out = []
		for vv, mm in zip(s_b.ravel().tolist(), m_b.ravel().tolist()):
			out.append(_resolve_one(float(vv), int(mm)))
		return out
	
	return _motion_speed_hex_resolver


#%% CELL 06 — RESOLVER BUNDLE CREATION

def create_resolvers_bundle(
	processing_bundle: MappingProxyType,
	colormaps_bundle: MappingProxyType,
	motion_speed_decisions: dict[str, object]
) -> MappingProxyType:
	"""
	Create the resolvers bundle with all hex resolver functions.

	Args:
		processing_bundle: Processing results with color mappings
		colormaps_bundle: Colormap bundle with matplotlib objects
		motion_speed_decisions: Motion speed policy for plateau_end

	Returns:
		MappingProxyType: Immutable bundle with all resolver functions
	"""
	# Extract needed data
	stimuli_all = processing_bundle["STIMULI_ALL"]
	behavior_all = processing_bundle["BEHAVIOR_ALL"]
	behavior_layers = processing_bundle["BEHAVIOR_LAYERS"]
	behavior_colors = {name: hex_color for name, hex_color in behavior_all.items() 
	                  if not any(name.startswith(f"{layer}_") for layer in ["Layer1", "Layer2", "Resistant"])}
	sentinel_all = processing_bundle["SENTINEL_ALL"]
	view_colors = processing_bundle["VIEW_COLORS"]
	sleap_colors = processing_bundle["SLEAP_COLORS"]
	group_colors_cmap = processing_bundle["GROUP_COLORS_CMAP"]
	
	# Get colormaps
	speed_cmap = colormaps_bundle["speed"]
	orientation_cmap = colormaps_bundle["orientation"]
	position_cmap_x = colormaps_bundle["position_X"]
	position_cmap_y = colormaps_bundle["position_Y"]
	position_hex_func = colormaps_bundle["position_hex"]
	
	# Create vectorized motion speed resolver
	motion_speed_resolver = create_motion_speed_hex_resolver(
		speed_cmap, sentinel_all, behavior_all, 
		float(motion_speed_decisions["plateau_end"])
	)
	
	# Create position resolver functions
	def position_x_hex(t: float) -> str:
		return position_hex_func("x", t, position_cmap_x)
	
	def position_y_hex(t: float) -> str:
		return position_hex_func("y", t, position_cmap_y)
	
	def orientation_hex_resolver(angle_deg: float) -> str:
		return orientation_hex(angle_deg, orientation_cmap)
	
	# Try to get group colors from experiment integration (best effort)
	groups_dict = {}
	try:
		# This will be handled in the main configure function
		pass
	except Exception:
		pass
	
	group_proxy = _GroupProxy(groups_dict, group_colors_cmap)
	
	return MappingProxyType({
		"hex": {
			"stimuli": stimuli_all,
			"behavior": behavior_all,
			"view": view_colors,
			"sleap": sleap_colors,
			"group": group_proxy,
			"theme_dark": processing_bundle["THEME_DARK"],
			"theme_light": processing_bundle["THEME_LIGHT"],
			"sentinel": sentinel_all,
			"motion_speed": motion_speed_resolver,
		},
		"resolvers": {
			"stimulus_hex": lambda label: stimulus_hex(label, stimuli_all),
			"behavior_hex": lambda layer, name: behavior_hex(layer, name, behavior_layers, behavior_colors),
			"view_hex": lambda label: view_hex(label, view_colors),
			"sleap_hex": lambda label: sleap_hex(label, sleap_colors),
			"motion_speed_hex": lambda speed, motion: motion_speed_hex(
				speed, motion, speed_cmap, sentinel_all, 
				float(motion_speed_decisions["plateau_end"])
			),
			"orientation_hex": orientation_hex_resolver,
			"position_x_hex": position_x_hex,
			"position_y_hex": position_y_hex,
		}
	})

__all__ = [
	"stimulus_hex",
	"behavior_hex", 
	"view_hex",
	"sleap_hex",
	"motion_speed_hex",
	"orientation_hex",
	"_GroupProxy",
	"create_motion_speed_hex_resolver",
	"create_resolvers_bundle"
]
