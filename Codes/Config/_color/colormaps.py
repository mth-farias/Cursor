#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_color/colormaps.py

Overview
	Advanced matplotlib colormap generation for motion speed, orientation,
	and position mapping. Extracted from the enhanced working version to
	support the configuration pattern while preserving sophisticated colormap logic.

Functions
	_make_motion_speed_cmap() → Piecewise LinearSegmentedColormap for speed
	_make_orientation_cmap() → HSV wheel with rotation and value scaling
	_make_position_cmap() → Linear position gradients from orientation wheel
	position_hex() → Position to hex conversion utility
	create_colormaps_bundle() → Main entry point for colormap creation

Notes
	- Preserves advanced plateau handling for motion speed
	- Maintains vectorized HSV→RGB conversion for orientation
	- Supports cardinal angle sampling for position gradients
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

from types import MappingProxyType
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

#%% CELL 02 — MOTION SPEED COLORMAP

def _make_motion_speed_cmap(decisions: dict[str, object], over_color: str
) -> LinearSegmentedColormap:
	"""
	Build speed colormap per policy.

	Args:
		decisions: Policy dict with control_points, plateau_start, plateau_end.
		over_color: Hex used for values > plateau_end.

	Returns:
		LinearSegmentedColormap: Colormap with 'over' set to over_color.

	Raises:
		KeyError: If required keys are missing.
		ValueError: If control points are malformed.
	"""
	required = {"control_points", "plateau_start", "plateau_end"}
	missing = [k for k in required if k not in decisions]
	if missing:
		raise KeyError(f"MOTION_SPEED_DECISIONS missing keys: {', '.join(missing)}")

	cp = decisions["control_points"]
	plateau_end = float(decisions["plateau_end"])
	if plateau_end <= 0:
		raise ValueError("plateau_end must be > 0.")

	# Validate control points and produce normalized positions in [0, 1]
	try:
		values = [float(v) for v, _ in cp]
		colors = [str(c) for _, c in cp]
	except Exception as e:
		raise ValueError("Invalid control_points; expected [(value, '#RRGGBB'), ...].") from e
	if any(v < 0 for v in values):
		raise ValueError("Speed control point values must be >= 0.")
	if any((not isinstance(c, str)) or (not c.startswith("#")) for c in colors):
		raise ValueError("Speed control point colors must be hex strings.")

	norm = [min(v / plateau_end, 1.0) for v in values]
	color_list = [mcolors.to_hex(c, keep_alpha=False) for c in colors]

	cmap = LinearSegmentedColormap.from_list("motion_speed", list(zip(norm, color_list)))
	try:
		cmap.set_over(mcolors.to_hex(over_color, keep_alpha=False))
	except Exception:
		# best-effort; never break session
		pass
	return cmap


#%% CELL 03 — ORIENTATION COLORMAP

def _make_orientation_cmap(n: int,
                           rotation_deg: float,
                           dark_factor: float) -> ListedColormap:
	"""
	Build an HSV orientation wheel with rotation and value scaling.

	Args:
		n: Number of discrete entries.
		rotation_deg: Hue rotation in degrees.
		dark_factor: Value (V) multiplier in HSV (0..1).

	Returns:
		ListedColormap: Circular orientation wheel.
	"""
	angles = np.linspace(0.0, 360.0, n, endpoint=False)
	h = ((angles + float(rotation_deg)) % 360.0) / 360.0
	s = np.ones_like(h)
	v = np.full_like(h, float(dark_factor))
	hsv = np.stack([h, s, v], axis=1)  # (n, 3)
	rgb = mcolors.hsv_to_rgb(hsv)      # vectorized
	return ListedColormap(rgb, name="orientation_wheel")


def _rgb_from_orientation(angle_deg: float,
                          cmap: ListedColormap) -> tuple[float, float, float]:
	"""
	Sample the orientation wheel using FLOAT fraction.

	Args:
		angle_deg: Orientation angle in degrees (wraps mod 360).
		cmap: ORIENTATION_CMAP.

	Returns:
		Tuple (r, g, b).
	"""
	frac = (np.mod(float(angle_deg), 360.0)) / 360.0
	r, g, b, _ = cmap(frac)
	return float(r), float(g), float(b)


#%% CELL 04 — POSITION COLORMAPS

def _make_position_cmap(axis: str,
                        orientation_cmap: ListedColormap) -> LinearSegmentedColormap:
	"""
	Build a linear position colormap by sampling the orientation wheel.

	Args:
		axis: "x" or "y".
		orientation_cmap: ORIENTATION_CMAP to sample.

	Returns:
		LinearSegmentedColormap for the given axis.

	Raises:
		ValueError: If axis is not "x" or "y".
	"""
	if axis == "x":
		# West (270°) → East (90°).
		c0 = _rgb_from_orientation(90.0, orientation_cmap)
		c1 = _rgb_from_orientation(270.0, orientation_cmap)
	elif axis == "y":
		# South (180°) → North (0°).
		c0 = _rgb_from_orientation(180.0, orientation_cmap)
		c1 = _rgb_from_orientation(0.0, orientation_cmap)
	else:
		raise ValueError(f"axis must be 'x' or 'y', got {axis!r}")
	return LinearSegmentedColormap.from_list(f"position_{axis}", [c0, c1], N=256)


def position_hex(axis: str,
                 t: float,
                 position_cmap: LinearSegmentedColormap) -> str:
	"""
	Map a normalized position to hex via a position colormap.

	Args:
		axis: "x" or "y" (for error reporting).
		t: Position in [0, 1] (clamped).
		position_cmap: Colormap built for the axis.

	Returns:
		Hex string "#RRGGBB".
	"""
	tc = float(np.clip(t, 0.0, 1.0))
	r, g, b, _ = position_cmap(tc)
	return mcolors.to_hex((r, g, b), keep_alpha=False)


#%% CELL 05 — COLORMAP BUNDLE CREATION

def create_colormaps_bundle(
	motion_speed_decisions: dict[str, object],
	orientation_decisions: dict[str, float],
	behavior_layers: dict[str, dict[str, str]]
) -> MappingProxyType:
	"""
	Create the colormaps bundle with all matplotlib colormap objects.

	Args:
		motion_speed_decisions: Motion speed policy with control points and plateau
		orientation_decisions: Orientation policy with rotation and dark factor
		behavior_layers: Behavior layer mappings (for over color)

	Returns:
		MappingProxyType: Immutable bundle with all colormaps
	"""
	# Create motion speed colormap (using Resistant_Jump as over color)
	over_color = behavior_layers["Resistant"]["Jump"]
	speed_cmap = _make_motion_speed_cmap(motion_speed_decisions, over_color)
	
	# Create orientation colormap
	orientation_cmap = _make_orientation_cmap(
		n=360,
		rotation_deg=float(orientation_decisions["rotation_deg"]),
		dark_factor=float(orientation_decisions["dark_factor"]),
	)
	
	# Create position colormaps
	position_cmap_x = _make_position_cmap("x", orientation_cmap)
	position_cmap_y = _make_position_cmap("y", orientation_cmap)
	
	return MappingProxyType({
		"speed": speed_cmap,
		"orientation": orientation_cmap,
		"position_X": position_cmap_x,
		"position_Y": position_cmap_y,
		"position_hex": position_hex,
	})

__all__ = [
	"_make_motion_speed_cmap",
	"_make_orientation_cmap",
	"_make_position_cmap",
	"position_hex",
	"create_colormaps_bundle"
]
