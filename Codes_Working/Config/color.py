#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/color.py

Overview
	Canonical color registry and colormaps for the project.
	Defines:
		- Anchor palettes for stimuli, behaviors, views, sentinels.
		- Derived layer variants (Layer1/Layer2/Resistant).
		- Matplotlib colormaps for orientation, position, and motion speed.
		- Hex resolvers (functions) for runtime lookups by label or value.
		- Optional group color assignment from Config.GROUPS (best-effort).
	Exports a single read-only bundle: COLOR.
"""


#%% CELL 01 — IMPORTS

from __future__ import annotations

"""
Imports required for color registry, colormap construction, and the visual report.

Rules
	- All imports live here (used by Cells 02–05). No re-imports later.
	- Order: stdlib → typing → third-party → local.
"""

# Standard library
from types import MappingProxyType
import colorsys

# Third-party
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib import pyplot as plt
from matplotlib import patches as patches
from matplotlib.collections import LineCollection
from matplotlib.axes import Axes


#%% CELL 02 — USER INPUT
"""
Authoritative anchors and visual policy. Edit 02.x cells only.
No logic or derivations here—just declarative values.

02.1 — Group colors policy
02.2 — Stimuli & Sentinels
02.3 — Behavior anchors & layer factors
02.4 — Motion–Speed policy
02.5 — Views & SLEAP body parts
02.6 — Orientation & Position policy
02.7 — Themes (Dark/Light primitives)
"""

#%% CELL 02.1 — GROUP COLORS POLICY
"""
Fallback when experiment.py lacks explicit group colors.

Behavior
	- If groups have no hex colors, sample evenly from this named matplotlib cmap.
	- The actual sampling happens later (utilities), not in this policy cell.
"""

GROUP_COLORS_CMAP: str = "viridis_r"


#%% CELL 02.2 — STIMULI & SENTINELS
"""
Stimulus hex anchors (incl. VisualStim variants) and sentinel colors.

Rules
	- Dark theme uses VisualStim_Light; Light theme uses VisualStim_Dark.
	- Sentinels are semantic (NaN / NoMotion) and independent of motion-speed cmaps.
"""

# Stimuli
STIMULUS_BASE: dict[str, str] = {
	"Stim0":            "#c92f26",  # red
	"Stim1":            "#018a58",  # emerald green
	"VisualStim_Dark":  "#2A2A2D",  # darker shade (used on Light theme)
	"VisualStim_Light": "#FFF7B2",  # lighter shade (used on Dark theme)
}

# Sentinels (not tied to speed==0; handled explicitly by resolvers)
SENTINEL: dict[str, str] = {
	"NaN":      "#898980",  # neutral gray
	"NoMotion": "#3E545C",  # subdued blue-gray
}


#%% CELL 02.3 — BEHAVIOR ANCHORS & LAYER FACTORS
"""
Behavior anchor colors and lightness factors for derived layers.
Layer1 brightest → Layer2 bright → (anchor) → Resistant darkest.
"""

# Behaviors (anchors)
BEHAVIOR: dict[str, str] = {
	"Jump":       "#8E44AD",  # purple
	"Walk":       "#EF6060",  # red
	"Stationary": "#F2D657",  # yellow
	"Freeze":     "#2CB5E3",  # blue
	"Noisy":      "#3E996B",  # green
}

# Lightness scaling factors applied in derivation
LAYER_LIGHTNESS_FACTORS: dict[str, float] = {
	"Layer1":    1.35,
	"Layer2":    1.25,
	"Resistant": 0.55,
}


#%% CELL 02.4 — MOTION–SPEED POLICY
"""
Piecewise speed colormap policy (mm/s).

Domain handled by cmap: up to 75.
Values > 75 use the 'over' color (Resistant_Jump).
'NoMotion' is a separate sentinel (02.2), not part of the colormap.
"""

MOTION_SPEED_DECISIONS: dict[str, object] = {
	# Ordered breakpoints and their colors at those points.
	# Hard visual break at 4.0 by jumping to a different orange.
	"control_points": [
		(0.0,  "#C0D16D"),  # green
		(4.0,  "#F2D357"),  # yellow (end of first segment; break occurs here)
		(4.0,  "#e09d39"),  # hard jump to different orange at 4.0
		(10.0, "#E07B39"),  # orange ramp end
		(16.0, "#C23B22"),  # red
		(25.0, "#A01313"),  # deepening toward dark red (pre-plateau)
		(75.0, "#7C0707"),  # plateau color (constant from 25→75)
	],
	"plateau_start": 25.0,
	"plateau_end":   75.0,
	"over_uses_resistant_jump": True,  # >75 rendered as Resistant_Jump
}


#%% CELL 02.5 — VIEWS & SLEAP BODY PARTS
"""
Static hexes for camera views and SLEAP body parts (stable for plot cohesion).
"""

# Views
VIEW: dict[str, str] = {
	"Left":     "#B54455",  # muted red
	"Right":    "#3E8663",  # muted green/teal
	"Top":      "#33619E",  # muted blue
	"Vertical": "#B9932C",  # muted yellow
}

# SLEAP body parts
SLEAP: dict[str, str] = {
	"Head":      "#D48FB3",  # pink-violet
	"Thorax":    "#B569C4",  # mid magenta-violet
	"Abdomen":   "#5E3A87",  # deep violet
	"LeftWing":  "#F57C00",  # orange
	"RightWing": "#708238",  # olive
}


#%% CELL 02.6 — ORIENTATION & POSITION POLICY
"""
HSV wheel policy for orientation; position gradients derive from wheel cardinals.

- rotation_deg aligns hues with cardinals.
- dark_factor dims the wheel to harmonize with themes.
- Position X: West(0)→East(1) ; Position Y: South(0)→North(1)
"""
ORIENTATION_DECISIONS: dict[str, float] = {
	"rotation_deg": 240.0,  # North=blue, East=green, South=yellow, West=red
	"dark_factor":  0.60,
}


#%% CELL 02.7 — THEMES (DARK/LIGHT PRIMITIVES)
"""
UI theme primitives consumed by reports/plots for backgrounds and text.
"""

THEME_DARK: dict[str, str] = {
	"background": "#0F0F10",
	"panel":      "#151517",
	"text":       "#E6E6E6",
	"grid":       "#2A2A2D",
	"muted":      "#8A8A8A",
	"accent":     "#5DADE2",
}

THEME_LIGHT: dict[str, str] = {
	"background": "#FFFFFF",
	"panel":      "#F5F5F5",
	"text":       "#222222",
	"grid":       "#DDDDDD",
	"muted":      "#888888",
	"accent":     "#007ACC",
}


#%% CELL 03 — DERIVED & HELPERS
"""
Derived palettes, colormaps, and tiny resolvers.
Helpers are stateless and policy-light (consume values from 02.x only).

03.1 — Group colors (best-effort assignment from labels)
03.2 — Behavior layer variants
03.3 — Motion–Speed colormap
03.4 — Orientation & Position colormaps
03.5 — Resolvers (Hex APIs)
"""

#%% CELL 03.1 — GROUP COLORS
"""
Assign colors to group labels by sampling a named matplotlib colormap.

Policy
	- Pure best-effort helper: no Config imports here.
	- Call from assembly with the list of labels to get a stable mapping.
	- Uses GROUP_COLORS_CMAP (02.1) as the sampler source.
"""

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


def build_group_colors_from_labels(labels: list[str]) -> dict[str, str]:
	"""
    Produce a stable label→hex mapping by sampling GROUP_COLORS_CMAP.

	Args:
		labels: Unique group labels.

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
	hexes = _sample_cmap_hex(GROUP_COLORS_CMAP, len(labels))
	return {lab: hexes[i] for i, lab in enumerate(labels)}


#%% CELL 03.2 — BEHAVIOR LAYER VARIANTS
"""
Derive Layer1/Layer2/Resistant variants from behavior anchor colors.

Policy
	- Adjust Lightness (L) channel in HLS color space:
		Layer1    → lighten strongly
		Layer2    → lighten mildly
		Resistant → darken
	- Hue/Saturation are preserved so categorical identity is consistent.
"""

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


# Derived behavior layers (using HLS lightness adjustments)
BEHAVIOR_LAYER1: dict[str, str] = {
	name: _adjust_lightness_hls(hex_hex, LAYER_LIGHTNESS_FACTORS["Layer1"])
	for name, hex_hex in BEHAVIOR.items()
}

BEHAVIOR_LAYER2: dict[str, str] = {
	name: _adjust_lightness_hls(hex_hex, LAYER_LIGHTNESS_FACTORS["Layer2"])
	for name, hex_hex in BEHAVIOR.items()
}

BEHAVIOR_RESISTANT: dict[str, str] = {
	name: _adjust_lightness_hls(hex_hex, LAYER_LIGHTNESS_FACTORS["Resistant"])
	for name, hex_hex in BEHAVIOR.items()
}


#%% CELL 03.3 — MOTION–SPEED COLORMAP
"""
Construct a piecewise LinearSegmentedColormap for motion speed (mm/s).

Inputs
	- MOTION_SPEED_DECISIONS (02.4)
	- BEHAVIOR_RESISTANT["Jump"] (03.2) as the 'over' color.

Domain
	- Colormap domain is [0, plateau_end]; values > plateau_end use 'over'.
"""

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


# Construct canonical speed colormap
SPEED_CMAP: LinearSegmentedColormap = _make_motion_speed_cmap(
	MOTION_SPEED_DECISIONS,
	BEHAVIOR_RESISTANT["Jump"],  # over color for > plateau_end
)


#%% CELL 03.4 — ORIENTATION & POSITION COLORMAPS
"""
Build the orientation HSV wheel and the X/Y position colormaps.

Inputs (from 02.6)
	ORIENTATION_DECISIONS:
		- rotation_deg: float   (degrees; hue rotation)
		- dark_factor:  float   (0..1; scales value V)

Outputs
	- ORIENTATION_CMAP: ListedColormap
	- POSITION_CMAP_X:  LinearSegmentedColormap (West→East, aligned with wheel)
	- POSITION_CMAP_Y:  LinearSegmentedColormap (South→North)

Design
	- Orientation wheel: vectorized HSV→RGB.
	- Position-X/Y: sample the wheel at cardinal angles with FLOAT sampling.
"""

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


#  build colormaps

ORIENTATION_CMAP: ListedColormap = _make_orientation_cmap(
	n=360,
	rotation_deg=float(ORIENTATION_DECISIONS["rotation_deg"]),
	dark_factor=float(ORIENTATION_DECISIONS["dark_factor"]),
)

POSITION_CMAP_X: LinearSegmentedColormap = _make_position_cmap("x", ORIENTATION_CMAP)
POSITION_CMAP_Y: LinearSegmentedColormap = _make_position_cmap("y", ORIENTATION_CMAP)



#%% CELL 03.5 — RESOLVERS (HEX APIS)
"""
Stateless hex resolvers. These apply semantic policy on top of raw dicts/cmaps.

Separation of concerns
	- The speed colormap (03.3) handles only numeric speed → color mapping.
	- The motion flag (binary) is applied here:
		* motion == 0 → SENTINEL["NoMotion"]
		* motion == 1 → use SPEED_CMAP(speed)
	- This ensures "speed == 0" (a valid float) maps to the low end of the
	  speed colormap (green), while "motion == 0" uses the sentinel color
	  (blue-gray). NaN speeds always map to SENTINEL["NaN"].
"""

def stimulus_hex(label: str) -> str:
	"""
	Lookup hex for a stimulus label.

	Args:
		label: One of STIMULUS_BASE keys (e.g., "Stim0", "Stim1",
		       "VisualStim_Dark", "VisualStim_Light").

	Returns:
		str: Hex color.

	Raises:
		KeyError: If the label is unknown.
	"""
	try:
		return STIMULUS_BASE[label]
	except KeyError as e:
		raise KeyError(f"Unknown stimulus label: {label!r}") from e


def behavior_hex(layer: str, name: str) -> str:
	"""
	Lookup hex for a behavior name within a specific layer.

	Args:
		layer: "Anchor" | "Layer1" | "Layer2" | "Resistant"
		name: Behavior name (e.g., "Walk", "Freeze", "Jump", ...).

	Returns:
		str: Hex color.

	Raises:
		KeyError: If the layer or behavior is unknown.
	"""
	if layer == "Anchor":
		table = BEHAVIOR
	elif layer == "Layer1":
		table = BEHAVIOR_LAYER1
	elif layer == "Layer2":
		table = BEHAVIOR_LAYER2
	elif layer == "Resistant":
		table = BEHAVIOR_RESISTANT
	else:
		raise KeyError(f"Unknown behavior layer: {layer!r}")
	try:
		return table[name]
	except KeyError as e:
		raise KeyError(f"Unknown behavior name: {name!r}") from e


def view_hex(label: str) -> str:
	"""
	Lookup hex for a camera view.

	Args:
		label: One of VIEW keys.

	Returns:
		str: Hex color.

	Raises:
		KeyError: If the label is unknown.
	"""
	try:
		return VIEW[label]
	except KeyError as e:
		raise KeyError(f"Unknown view label: {label!r}") from e


def sleap_hex(label: str) -> str:
	"""
	Lookup hex for a SLEAP body part.

	Args:
		label: One of SLEAP keys.

	Returns:
		str: Hex color.

	Raises:
		KeyError: If the label is unknown.
	"""
	try:
		return SLEAP[label]
	except KeyError as e:
		raise KeyError(f"Unknown SLEAP label: {label!r}") from e


def motion_speed_hex(
	speed: float,
	motion: int,
	cmap: LinearSegmentedColormap,
	plateau_end: float = float(MOTION_SPEED_DECISIONS["plateau_end"]),
) -> str:
	"""
Map (speed, motion) to a hex color with sentinel-aware policy.

Args:
	speed: Speed in mm/s (float; may be 0.0).
	motion: Binary motion flag (0 or 1). Controls sentinel vs colormap.
	cmap: Motion–speed colormap (e.g., SPEED_CMAP from 03.3).
	plateau_end: Upper domain bound used for colormap normalization.

Returns:
	str: Hex color.

Policy:
	- If motion == 0: return SENTINEL["NoMotion"] (semantic state).
	- Else if speed is non-finite: return SENTINEL["NaN"].
	- Else: map speed via the colormap. Values > plateau_end use the cmap's 'over' color.
	- Note: speed == 0.0 with motion == 1 is valid and maps to the low-end color.
"""
	# Motion sentinel takes precedence over speed
	if motion == 0:
		return SENTINEL["NoMotion"]

	# NaN/Inf handling for speed
	if not np.isfinite(speed):
		return SENTINEL["NaN"]

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
		orientation_cmap: ListedColormap constructed in 03.4.

	Returns:
		str: Hex color.
	"""
	idx = int(np.mod(angle_deg, 360.0) / 360.0 * orientation_cmap.N)
	r, g, b, _ = orientation_cmap(idx)
	return mcolors.to_hex((r, g, b), keep_alpha=False)


#%% CELL 04 — ASSEMBLY & PUBLIC SURFACE
"""
Assemble the single public bundle with one unified layer.

Access patterns
	COLOR["hex"]["stimuli"]["Stim0"]
	COLOR["hex"]["stimuli"]["VisualStim"]          # alias → VisualStim_Light
	COLOR["hex"]["behavior"]["Walk"]
	COLOR["hex"]["behavior"]["Layer1_Walk"]
	COLOR["hex"]["view"]["Top"]
	COLOR["hex"]["sleap"]["Head"]
	COLOR["hex"]["group"]["Control"]               # explicit or stable fallback
	COLOR["hex"]["theme_light"]["background"]
	COLOR["hex"]["theme_dark"]["text"]
	COLOR["hex"]["sentinel"]["NaN"]
	COLOR["hex"]["sentinel"]["NoMotion"]
	COLOR["hex"]["motion_speed"](speed_mm_s, motion_flag)  # gate + cutoff aware

	COLOR["cmap"]["speed"](0.5)
	COLOR["cmap"]["orientation"](0.25)
	COLOR["cmap"]["position_X"](0.1)
	COLOR["cmap"]["position_Y"](0.9)

Notes
	- Assembly only; policies were defined earlier.
	- Exception: legacy alias "VisualStim" → "VisualStim_Light".
	- Groups intake reads EXPERIMENT["GROUPS"] as dict-of-dicts (uses "color") or
	  list/tuple (sampled). Import robust for package/standalone runs.
	- motion_speed resolver uses an internal 75 mm/s cutoff (no policy export).
"""

# stimuli (add legacy alias)
_STIMULI_ALL = dict(STIMULUS_BASE)
_STIMULI_ALL["VisualStim"] = STIMULUS_BASE["VisualStim_Light"]

# behavior (anchors + layered)
_BEHAVIOR_ALL: dict[str, str] = {
	**{f"Layer1_{name}": hx for name, hx in BEHAVIOR_LAYER1.items()},
	**{f"Layer2_{name}": hx for name, hx in BEHAVIOR_LAYER2.items()},
	**{f"Resistant_{name}": hx for name, hx in BEHAVIOR_RESISTANT.items()},
	**{name: hx for name, hx in BEHAVIOR.items()},
}

# sentinels
_SENTINEL_ALL = {
	"NaN": SENTINEL["NaN"],
	"NoMotion": SENTINEL["NoMotion"],
}

# groups (explicit from EXPERIMENT; else sampled)
_GROUPS: dict[str, str] = {}
try:
	# package-relative first, then absolute (standalone)
	try:
		from .experiment import EXPERIMENT  # type: ignore
	except Exception:
		import experiment as _exp  # type: ignore
		EXPERIMENT = getattr(_exp, "EXPERIMENT")

	_groups_obj = EXPERIMENT.get("GROUPS", None)
	if isinstance(_groups_obj, dict):
		for k, v in _groups_obj.items():
			lbl = str(k)
			if isinstance(v, dict) and "color" in v:
				col = v["color"]
				if isinstance(col, str) and col.startswith("#"):
					_GROUPS[lbl] = col
			elif isinstance(v, str) and v.startswith("#"):
				_GROUPS[lbl] = v
	elif isinstance(_groups_obj, (list, tuple)):
		_GROUPS.update(build_group_colors_from_labels([str(x) for x in _groups_obj]))
except Exception:
	# best-effort; never break session
	pass

def _sample_group_color(label: str) -> str:
	"""Stable fallback for unknown group labels via hashed sampling on GROUP_COLORS_CMAP."""
	h = (hash(str(label)) & 0xFFFFFFFF) / 0xFFFFFFFF
	r, g, b, _ = mcolors.get_cmap(GROUP_COLORS_CMAP)(h)
	return mcolors.to_hex((r, g, b), keep_alpha=False)

class _GroupProxy(dict):
	"""Mapping that returns/caches a stable fallback color when a label is missing."""
	def __missing__(self, key: str) -> str:
		hexv = _sample_group_color(key)
		self[key] = hexv
		return hexv

def _motion_speed_hex_resolver(speed_value, motion_flag=None):
	"""
	Map speed+motion to hex with gate and cutoff baked in.

	Args:
		speed_value: float|int|array — physical speed (mm/s) preferred; if [0..1], still OK.
		motion_flag: int|array|None — 0 ⇒ NoMotion; 1 ⇒ use speed; None ⇒ treat as 1.

	Returns:
		Hex string for scalar inputs, or list[str] for arrays.

	Notes
		- Cutoff = 75 mm/s internally. Values > 75 snap to Resistant_Jump.
		- NaN speed ⇒ NaN sentinel (when motion=1); motion=0 overrides to NoMotion.
	"""
	cmap = SPEED_CMAP
	sentinel = _SENTINEL_ALL
	over_hex = _BEHAVIOR_ALL.get("Resistant_Jump", "#000000")
	cutoff = MOTION_SPEED_DECISIONS['plateau_end']  # internal, not exported

	def _resolve_one(v: float, m) -> str:
		# motion gate (0 dominates)
		if m == 0:
			return sentinel["NoMotion"]
		# handle NaN speed under motion=1 (or None treated as 1)
		if not np.isfinite(v):
			return sentinel["NaN"]
		# normalize mm/s to [0,1] against cutoff
		u = float(v) / cutoff
		if u > 1.0:
			return over_hex
		u = float(np.clip(u, 0.0, 1.0))
		r, g, b, _ = cmap(u)
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

# public bundle
_PUBLIC: dict[str, object] = {
	"hex": {
		"stimuli": _STIMULI_ALL,
		"behavior": _BEHAVIOR_ALL,
		"view": VIEW,
		"sleap": SLEAP,
		"group": _GroupProxy(_GROUPS),
		"theme_dark": THEME_DARK,
		"theme_light": THEME_LIGHT,
		"sentinel": _SENTINEL_ALL,
		"motion_speed": _motion_speed_hex_resolver,
	},
	"cmap": {
		"speed": SPEED_CMAP,
		"orientation": ORIENTATION_CMAP,
		"position_X": POSITION_CMAP_X,
		"position_Y": POSITION_CMAP_Y,
	},
}

COLOR = MappingProxyType(_PUBLIC)
__all__ = ["COLOR"]


#%% CELL 05 — REPORT
"""
Visual report (final cell).
Consumes only COLOR; no other module state.

Layout per column (Dark left, Light right):
  1) Groups • 2) Stimuli • 3) Sentinels • 4) Behavior matrix
  5) View • 6) Bodyparts • 7) Orientation spokes • 8) Position gradients
  9) Motion–Speed panel

Policy
  - Dark column uses VisualStim_Light
  - Light column uses VisualStim_Dark
  - Motion–Speed coloring uses COLOR["hex"]["motion_speed"](speed_mm_s, motion_flag).
"""

def _is_hex(x: object) -> bool:
	"""Return True if x parses as a color hex."""
	try:
		mcolors.to_rgb(x)  # type: ignore[arg-type]
		return True
	except Exception:
		return False

def _groups_from_color_hex(hexspace: dict) -> dict[str, str]:
	"""
	Collect explicitly materialized group hexes.

	Args:
		hexspace: COLOR["hex"] mapping.

	Returns:
		Dict[label, "#RRGGBB"] with explicit entries only.
	"""
	group_map = hexspace.get("group", {})
	if hasattr(group_map, "items"):
		return {k: v for k, v in group_map.items() if isinstance(v, str) and _is_hex(v)}
	return {}

def _swatches_row(ax: "Axes",
                  theme: dict,
                  title: str,
                  mapping: dict[str, str]) -> None:
	"""
	Draw a single row of labeled swatches.

	Args:
		ax: Matplotlib axes.
		theme: Theme dictionary (colors).
		title: Row title.
		mapping: Dict[label, hex].
	"""
	ax.set_facecolor(theme["panel"])
	ax.set_xticks([])
	ax.set_yticks([])
	for spine in ax.spines.values():
		spine.set_visible(False)
	ax.set_title(title, color=theme["text"], fontsize=12, pad=8)

	if not mapping:
		ax.text(0.5, 0.5, "(none)", color=theme["text"], fontsize=10,
		        ha="center", va="center", transform=ax.transAxes)
		return

	x = .08
	for k, v in mapping.items():
		ax.add_patch(
			patches.Rectangle(
				(x, .45), .10, .25,
				color=v, ec=theme["grid"], lw=.6,
				transform=ax.transAxes,
			)
		)
		ax.text(
			x + .05, .40, k,
			ha="center", va="top",
			color=theme["text"], fontsize=8,
			transform=ax.transAxes,
		)
		x += .12

def _draw_behavior_matrix(ax: "Axes",
                          theme: dict,
                          hexspace: dict,
                          anchors_order: tuple[str, ...] = (
	                          "Jump", "Walk", "Stationary", "Freeze", "Noisy"
                          ),
                          cell_w: float = .11,
                          cell_h: float = .18,
                          x0: float = .14,
                          y0: float = .10) -> None:
	"""
	Draw the 4-row behavior matrix.

	Args:
		ax: Matplotlib axes.
		theme: Theme dict.
		hexspace: COLOR["hex"] mapping.
		anchors_order: Column order for anchors.
		cell_w/cell_h/x0/y0: Layout parameters (axes fraction).
	"""
	ax.set_facecolor(theme["panel"])
	ax.set_xticks([])
	ax.set_yticks([])
	for spine in ax.spines.values():
		spine.set_visible(False)

	ax.set_title(
		"Behavior Layers (Layer1 → Layer2 → Behavior → Resistant)",
		color=theme["text"], fontsize=12, pad=8,
	)

	beh_map = hexspace["behavior"]

	# Column labels
	for j, beh in enumerate(anchors_order):
		ax.text(
			x0 + j * cell_w + cell_w / 2,
			y0 + 4 * cell_h + .03,
			beh,
			color=theme["text"], fontsize=8, ha="center", va="bottom",
			transform=ax.transAxes,
		)

	rows = [
		("Layer1_", "Layer1"),
		("Layer2_", "Layer2"),
		("", "Behavior"),
		("Resistant_", "Resistant"),
	]
	for i, (prefix, label) in enumerate(rows):
		ax.text(
			x0 - .03, y0 + (3 - i) * cell_h + cell_h / 2,
			label,
			color=theme["text"], fontsize=9, ha="right", va="center",
			transform=ax.transAxes, weight="bold",
		)
		for j, beh in enumerate(anchors_order):
			key = f"{prefix}{beh}" if prefix else beh
			hx = beh_map[key]
			ax.add_patch(
				patches.Rectangle(
					(x0 + j * cell_w, y0 + (3 - i) * cell_h),
					cell_w * .92, cell_h * .9,
					color=hx, ec=theme["grid"], lw=.5,
					transform=ax.transAxes,
				)
			)

def _orientation_hex(angle_deg: float) -> str:
	"""Sample orientation colormap with FLOAT fraction and return hex."""
	cmap = COLOR["cmap"]["orientation"]
	frac = (np.mod(float(angle_deg), 360.0)) / 360.0
	r, g, b, _ = cmap(frac)
	return mcolors.to_hex((r, g, b), keep_alpha=False)

def _position_x_hex(t: float) -> str:
	"""Return hex for X-position t∈[0,1] via COLOR['cmap']['position_X']."""
	cmap = COLOR["cmap"]["position_X"]
	tc = float(np.clip(t, 0.0, 1.0))
	r, g, b, _ = cmap(tc)
	return mcolors.to_hex((r, g, b), keep_alpha=False)

def _position_y_hex(t: float) -> str:
	"""Return hex for Y-position t∈[0,1] via COLOR['cmap']['position_Y']."""
	cmap = COLOR["cmap"]["position_Y"]
	tc = float(np.clip(t, 0.0, 1.0))
	r, g, b, _ = cmap(tc)
	return mcolors.to_hex((r, g, b), keep_alpha=False)

def _gradient_bar_mm(ax: "Axes",
                     theme: dict,
                     resolver_hex,
                     vmin_mm: float,
                     vmax_mm: float,
                     extent: tuple[float, float, float, float]) -> None:
	"""
	Draw a horizontal gradient in mm/s by sampling resolver_hex(mm/s, motion=1).

	Args:
		ax: Matplotlib axes.
		theme: Theme dict.
		resolver_hex: Callable (speed_mm_s, motion_flag) → hex.
		vmin_mm/vmax_mm: Range in mm/s (0..75).
		extent: (x0, x1, y0, y1) in axes fraction.
	"""
	n = 512
	x0, x1, y0, y1 = extent
	for i, v in enumerate(np.linspace(vmin_mm, vmax_mm, n)):
		x = x0 + (x1 - x0) * (i / (n - 1))
		ax.add_patch(
			patches.Rectangle(
				(x, y0), (x1 - x0) / n, (y1 - y0),
				color=resolver_hex(v, 1), lw=0,
				transform=ax.transAxes,
			)
		)

def render_color_report(*, show: bool = True,
                        savepath: str | None = None) -> None:
	"""
	Render the full visual color report.

	Args:
		show: Whether to display the figure.
		savepath: Optional path to save PNG.

Notes:
	Consumes only COLOR and imports from Cell 01.
	"""
	hexspace = COLOR["hex"]
	theme_dark = hexspace["theme_dark"]
	theme_light = hexspace["theme_light"]
	themes = [("Dark", theme_dark), ("Light", theme_light)]

	groups_row = _groups_from_color_hex(hexspace)
	beh_order = ("Jump", "Walk", "Stationary", "Freeze", "Noisy")

	# Demo speed trace (mm/s) and motion flag (0/1), like the legacy report
	t = np.linspace(0, 100, 600)
	speed_mm = np.zeros_like(t)
	motion = np.zeros_like(t, dtype=int)
	seg = (t >= 20) & (t < 90)
	speed_mm[seg] = 8 + 6 * np.sin(2 * np.pi * (t[seg] - 20) / 60)
	motion[seg] = 1
	speed_mm[t >= 90] = 90.0  # push over 75 to show Jump at the tail
	motion[t >= 90] = 1

	# Figure background
	fig = plt.figure(figsize=(14, 19))
	bg = fig.add_axes([0, 0, 1, 1])
	bg.axis("off")
	bg.add_patch(patches.Rectangle((0, 0), .5, 1, color=theme_dark["background"]))
	bg.add_patch(patches.Rectangle((.5, 0), .5, 1, color=theme_light["background"]))

	gs = fig.add_gridspec(
		9, 2,
		height_ratios=[0.7, 0.7, 0.55, 1.1, 0.8, 0.8, 0.9, 0.9, 1.3],
		hspace=.55, wspace=.18,
	)

	for col, (label, th) in enumerate(themes):
		# 1) Groups
		ax_grp = fig.add_subplot(gs[0, col])
		title = f"{label} — Groups" if groups_row else f"{label} — Groups (none)"
		_swatches_row(ax_grp, th, title, groups_row or {})

		# 2) Stimuli
		stim = hexspace["stimuli"]
		if label == "Dark":
			stims_map = {
				"VisualStim_Light": stim["VisualStim_Light"],
				"Stim0": stim["Stim0"],
				"Stim1": stim["Stim1"],
			}
		else:
			stims_map = {
				"VisualStim_Dark": stim["VisualStim_Dark"],
				"Stim0": stim["Stim0"],
				"Stim1": stim["Stim1"],
			}
		ax_stim = fig.add_subplot(gs[1, col])
		_swatches_row(ax_stim, th, f"{label} — Stimuli", stims_map)

		# 3) Sentinels
		ax_sent = fig.add_subplot(gs[2, col])
		_swatches_row(
			ax_sent, th, f"{label} — Sentinels",
			{"NaN": hexspace["sentinel"]["NaN"],
			 "NoMotion": hexspace["sentinel"]["NoMotion"]},
		)

		# 4) Behavior matrix
		ax_mat = fig.add_subplot(gs[3, col])
		_draw_behavior_matrix(ax_mat, th, hexspace, anchors_order=beh_order)

		# 5) View
		ax_view = fig.add_subplot(gs[4, col])
		_swatches_row(
			ax_view, th, f"{label} — View",
			{k: hexspace["view"][k] for k in ("Left", "Right", "Top", "Vertical")},
		)

		# 6) Bodyparts
		ax_body = fig.add_subplot(gs[5, col])
		_swatches_row(
			ax_body, th, f"{label} — Bodyparts",
			{k: hexspace["sleap"][k] for k in
			 ("Head", "Thorax", "Abdomen", "LeftWing", "RightWing")},
		)

		# 7) Orientation — HSV spokes
		ax_ori = fig.add_subplot(gs[6, col])
		ax_ori.set_facecolor(th["panel"])
		ax_ori.set_xticks([])
		ax_ori.set_yticks([])
		for spine in ax_ori.spines.values():
			spine.set_visible(False)
		ax_ori.set_title(
			f"{label} — Orientation (HSV Spokes)",
			color=th["text"], fontsize=12, pad=8,
		)
		wheel = ax_ori.inset_axes([.10, .05, .80, .90], projection="polar")
		wheel.set_facecolor(th["panel"])
		wheel.set_theta_offset(np.pi / 2)
		wheel.set_xticklabels([])
		wheel.set_yticklabels([])
		wheel.grid(False)
		for deg in range(0, 360, 15):
			ang = np.radians(deg)
			wheel.bar(
				ang, 0.7, width=np.radians(6), bottom=0.3,
				color=_orientation_hex(deg), edgecolor=None,
			)
		for d, lbl in [(0, 'N'), (90, 'W'), (180, 'S'), (270, 'E')]:
			wheel.text(
				np.radians(d), 1.07, lbl,
				ha="center", va="center", fontsize=11,
				fontweight="bold", color=th["text"],
			)
		wheel.spines['polar'].set_color(th["grid"])

		# 8) Position gradients
		ax_pos = fig.add_subplot(gs[7, col])
		ax_pos.set_facecolor(th["panel"])
		ax_pos.set_xticks([])
		ax_pos.set_yticks([])
		for spine in ax_pos.spines.values():
			spine.set_visible(False)
		ax_pos.set_title(
			f"{label} — Position Gradients",
			color=th["text"], fontsize=12, pad=8, loc="center",
		)

		# X: West→East
		n = 256
		x0, x1 = .06, .94
		y_top0, y_top1 = .62, .88
		for i, uu in enumerate(np.linspace(0, 1, n)):
			x = x0 + (x1 - x0) * (i / (n - 1))
			ax_pos.add_patch(
				patches.Rectangle(
					(x, y_top0), (x1 - x0) / n, (y_top1 - y_top0),
					color=_position_x_hex(uu), lw=0,
					transform=ax_pos.transAxes,
				)
			)
		ax_pos.text(
			.50, .91, "Position X — West(0)→East(1)",
			color=th["text"], transform=ax_pos.transAxes,
			ha="center", fontsize=10,
		)

		# Y: South→North
		y_bot0, y_bot1 = .12, .38
		for i, uu in enumerate(np.linspace(0, 1, n)):
			x = x0 + (x1 - x0) * (i / (n - 1))
			ax_pos.add_patch(
				patches.Rectangle(
					(x, y_bot0), (x1 - x0) / n, (y_bot1 - y_bot0),
					color=_position_y_hex(uu), lw=0,
					transform=ax_pos.transAxes,
				)
			)
		ax_pos.text(
			.50, .43, "Position Y — South(0)→North(1)",
			color=th["text"], transform=ax_pos.transAxes,
			ha="center", fontsize=10,
		)
		ax_pos.plot(
			[.06, .94], [.50, .50],
			color=th["grid"], lw=.8, transform=ax_pos.transAxes,
		)

		# 9) Motion–Speed (mm/s line; colors via resolver)
		ax_ms = fig.add_subplot(gs[8, col])
		ax_ms.set_facecolor(th["panel"])
		ax_ms.set_xticks([])
		ax_ms.set_yticks([])
		for spine in ax_ms.spines.values():
			spine.set_visible(False)
		ax_ms.set_title(
			f"{label} — Motion | Speed Colormap",
			color=th["text"], fontsize=12, pad=8,
		)

		# No Motion block
		ax_ms.add_patch(
			patches.Rectangle(
				(.03, .70), .12, .22,
				color=hexspace["sentinel"]["NoMotion"], ec=th["grid"],
			)
		)
		ax_ms.text(
			.09, .66, "No Motion",
			color=th["text"], ha="center", va="center", fontsize=9,
		)

		# Gradient bar 0..75 mm/s using resolver directly (motion=1)
		extent = (.20, .80, .74, .90)
		_gradient_bar_mm(ax_ms, th, hexspace["motion_speed"], 0.0, 75.0, extent)
		for v in [0, 4, 10, 16, 25, 75]:
			xx = extent[0] + (extent[1] - extent[0]) * (v / 75.0)
			ax_ms.plot([xx, xx], [.71, .74], color=th["grid"], lw=.9)
			ax_ms.text(xx, .69, str(v), color=th["text"],
			           ha="center", va="top", fontsize=8)

		# Resistant_Jump block
		ax_ms.add_patch(
			patches.Rectangle(
				(.84, .70), .12, .22,
				color=hexspace["behavior"]["Resistant_Jump"], ec=th["grid"],
			)
		)
		ax_ms.text(
			.90, .66, "Jump",
			color=th["text"], ha="center", va="center", fontsize=9,
		)

		# mm/s trace colored by resolver
		ax_line = ax_ms.inset_axes([0.05, 0.08, 0.90, 0.5])
		ax_line.set_facecolor(th["panel"])
		cols = hexspace["motion_speed"](speed_mm, motion)  # vectorized list[str]
		pts = np.array([t, speed_mm]).T.reshape(-1, 1, 2)
		segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
		lc = LineCollection(segs, colors=cols[:-1], linewidths=2.0)
		ax_line.add_collection(lc)
		ax_line.plot(t, speed_mm, color=th["muted"], lw=.6, alpha=.6)
		ax_line.set_xlim(t.min(), t.max())
		ax_line.set_ylim(-2, 100)  # mm/s axis like legacy
		ax_line.set_xlabel("Time (a.u.)", color=th["text"], fontsize=9)
		ax_line.set_ylabel("Speed (mm/s)", color=th["text"], fontsize=9)
		ax_line.tick_params(colors=th["text"], labelsize=8)
		ax_line.grid(True, color=th["grid"], lw=.8, alpha=.85)

	if savepath:
		try:
			fig.savefig(savepath, dpi=200, facecolor=fig.get_facecolor())
		except Exception:
			# best-effort; never break session
			pass
	if show:
		plt.show()


if __name__ == "__main__":
	render_color_report(show=True)
