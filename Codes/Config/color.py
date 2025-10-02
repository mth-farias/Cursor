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

Architecture
	This is the main controller that orchestrates internal processing modules:
	- User constants defined here (CELL 02)
	- Processing delegated to _color/ modules
	- Final COLOR bundle assembled from internal results
"""

#%% CELL 01 — IMPORTS & TYPES

from __future__ import annotations

"""
Imports required for color registry, colormap construction, and the visual report.

Rules
	- All imports live here (used by Cells 02–04). No re-imports later.
	- Order: stdlib → typing → third-party → local.
"""

# Standard library
import sys
from pathlib import Path
from types import MappingProxyType

# Package path setup (for safe absolute imports)
ROOT = Path(__file__).resolve().parents[1]  # .../Codes
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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


#%% CELL 03 — PROCESSING & ASSEMBLY
"""
Import internal processing modules and create the final COLOR bundle.
Delegates all computation to specialized modules while maintaining the
exact same functionality as the original monolithic implementation.
"""

# Import internal processing modules - avoid circular imports
import importlib
import os

# Determine the correct module path
current_dir = Path(__file__).parent
color_module_path = current_dir / "_color"

if color_module_path.exists():
    # Direct import when running as script
    sys.path.insert(0, str(current_dir))
    _color = importlib.import_module("_color")
else:
    # Relative import when imported as module
    from . import _color

# Configure all color modules with user parameters
_color.configure(
	GROUP_COLORS_CMAP,
	STIMULUS_BASE,
	SENTINEL,
	BEHAVIOR,
	LAYER_LIGHTNESS_FACTORS,
	MOTION_SPEED_DECISIONS,
	VIEW,
	SLEAP,
	ORIENTATION_DECISIONS,
	THEME_DARK,
	THEME_LIGHT
)


#%% CELL 04 — PUBLIC API
"""
Immutable public bundle: COLOR.
Contains both user-declared inputs and derived structures.
Preserves the sophisticated nested structure from the working version.
"""

_PUBLIC = {
	# Enhanced processed results from internal modules
	"hex": _color._RESOLVERS["hex"],  # Nested hex structure only
	"cmap": _color._COLORMAPS,  # Matplotlib colormap objects
}

COLOR = MappingProxyType(_PUBLIC)
__all__ = ["COLOR"]


#%% CELL 05 — REPORT
"""
Human-readable summary of the COLOR bundle.
Renders comprehensive dual-theme visual report.
"""

if __name__ == "__main__":
	_color._REPORT["render_color_report"](COLOR)
