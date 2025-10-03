#%% CELL 00 — HEADER & SCOPE
'''
{{COMMIT_DETAILS}}
#<github.com/MoitaLab/Repo>
#<full_commit_hash>
#<DD-MM-YYYY HH:MM:SS>

color.py

What this file defines
    Canonical registry of all color anchors and colormaps for the BehaviorScoring pipeline.

Exports
    COLOR : dict
        Flat keyspace, no nesting. Includes:
          • Stimuli:
              "Stim0", "Stim1", "VisualStim", "VisualStim_Light"
          • Behaviors:
              "Jump", "Walk", "Stationary", "Freeze", "Noisy"
          • Behavior layer variants (derived from anchors via lightness scaling):
              "Layer1_<Behavior>", "Layer2_<Behavior>", "Resistant_<Behavior>"
          • Sentinels:
              "NaN", "NoMotion"
          • Views:
              "Left", "Right", "Top", "Vertical"
          • SLEAP body parts:
              "Head", "Thorax", "Abdomen", "LeftWing", "RightWing"
          • Continuous colormaps (matplotlib objects):
              "cmap_orientation", "cmap_position_x", "cmap_position_y", "cmap_motion_speed"
          • Themes:
              "Theme_Dark", "Theme_Light"

Principle
    The REPORT cell reads only from COLOR (single source of truth).

Dependencies
    Upstream: experiment.py (optional group colors)
    Downstream: visualization, legends, reports

Public surface
    __all__ = ["COLOR"]
'''


#%% CELL 01 — IMPORTS
"""
Imports only. Keep minimal and side-effect free.
Order: stdlib → typing → third-party.
"""
from typing import Dict
from types import MappingProxyType as _RO

import colorsys
import numpy as np

import matplotlib.colors as mcolors
from matplotlib import colormaps as mpl_cmaps
import matplotlib.pyplot as plt
import matplotlib.patches as P
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, ListedColormap


#%% CELL 02 — USER INPUT
"""
Authoritative anchors and visual policy. Edit 02.x cells only.

02.1 — Stimuli & Sentinels
02.2 — Behavior anchors & layer factors
02.3 — Views & SLEAP body parts
02.4 — Themes (Dark/Light primitives)
02.5 — Orientation & Position policy
02.6 — Motion–Speed policy
02.7 — Group colors policy
"""


#%%% CELL 02.1 — Stimuli & Sentinels
"""
Stimuli hexes (incl. VisualStim variants) and sentinel colors.
Rule: Dark theme uses VisualStim_Light; Light theme uses VisualStim.
"""

# Stimuli
STIMULUS_BASE: Dict[str, str] = {
	"Stim0":            "#c92f26",  # red
	"Stim1":            "#018a58",  # emerald green
	"VisualStim":       "#2A2A2D",  # darker shade (used on Light theme)
	"VisualStim_Light": "#FFF7B2",  # lighter shade (used on Dark theme)
}

# Sentinels (not tied to speed==0; you decide that via motion variable)
SENTINEL: Dict[str, str] = {
	"NaN":      "#898980",  # neutral gray
	"NoMotion": "#3E545C",  # subdued blue-gray
}


#%%% CELL 02.2 — Behavior anchors & layer factors
"""
Behavior anchor colors and lightness factors for derived layers.
Layer1 brightest → Layer2 bright → (anchor) → Resistant darkest.
"""

# Behaviors (anchors)
BEHAVIOR: Dict[str, str] = {
	"Jump":       "#8E44AD",  # purple
	"Walk":       "#EF6060",  # red
	"Stationary": "#F2D657",  # yellow
	"Freeze":     "#2CB5E3",  # blue
	"Noisy":      "#3E996B",  # green
}

# Lightness scaling factors applied in derivation
LAYER_LIGHTNESS_FACTORS: Dict[str, float] = {
	"Layer1":    1.35,
	"Layer2":    1.25,
	"Resistant": 0.55,
}


#%%% CELL 02.3 — Views & SLEAP body parts
"""
Static hexes for camera views and body parts (stable for plot cohesion).
"""

# Views
VIEW: Dict[str, str] = {
	"Left":     "#B54455",  # muted red
	"Right":    "#3E8663",  # muted green/teal
	"Top":      "#33619E",  # muted blue
	"Vertical": "#B9932C",  # muted yellow
}

# SLEAP body parts
SLEAP: Dict[str, str] = {
	"Head":      "#D48FB3",  # pink-violet
	"Thorax":    "#B569C4",  # mid magenta-violet
	"Abdomen":   "#5E3A87",  # deep violet
	"LeftWing":  "#F57C00",  # orange
	"RightWing": "#708238",  # olive
}


#%%% CELL 02.4 — Themes (Dark/Light primitives)
"""
UI theme primitives. Report and plots consume these for backgrounds/text.
"""

THEME_DARK: Dict[str, str] = {
	"background": "#0F0F10",
	"panel":      "#151517",
	"text":       "#E6E6E6",
	"grid":       "#2A2A2D",
	"muted":      "#8A8A8A",
	"accent":     "#5DADE2",
}
THEME_LIGHT: Dict[str, str] = {
	"background": "#FFFFFF",
	"panel":      "#F5F5F5",
	"text":       "#222222",
	"grid":       "#DDDDDD",
	"muted":      "#888888",
	"accent":     "#007ACC",
}


#%%% CELL 02.5 — Orientation & Position policy
"""
HSV wheel policy for orientation; position gradients derive from wheel extremes.
- rotation_deg chooses the hue alignment for cardinals.
- dark_factor dims the wheel to match themes.
Position X: West(0)→East(1) ; Position Y: South(0)→North(1)
"""
ORIENTATION_DECISIONS: Dict[str, float] = {
	"rotation_deg": 240.0,  # North=blue, East=green, South=yellow, West=red
	"dark_factor":  0.60,
}


#%%% CELL 02.6 — Motion–Speed policy
"""
Piecewise speed colormap policy (mm/s).
Domain handled by cmap: up to 75. Values >75 use the 'over' color (Resistant_Jump).
NoMotion is a separate sentinel color (from 02.1), not part of the cmap.
"""
MOTION_SPEED_DECISIONS: Dict[str, object] = {
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


#%%% CELL 02.7 — Group colors policy
"""
Fallback policy when experiment.py lacks explicit group colors.
We sample evenly from this named matplotlib cmap.
"""
GROUP_COLORS_CMAP: str = "viridis_r"


#%% CELL 03 — UTILITIES
"""
Helper functions for color manipulation.
No global state; pure utilities.
"""
def _hls_adjust_lightness(hex_color: str, factor: float) -> str:
	"""Adjust lightness of a hex color using HLS conversion."""
	r, g, b = mcolors.to_rgb(hex_color)
	h, l, s = colorsys.rgb_to_hls(r, g, b)
	l = max(0, min(1, l * factor))
	r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
	return mcolors.to_hex((r2, g2, b2))

def _to_hex(color_like) -> str:
	"""Convert matplotlib color spec to hex string."""
	return mcolors.to_hex(color_like)

def _sample_cmap_hex(cmap, n: int) -> list[str]:
	"""Return n evenly spaced samples from cmap as hex list."""
	return [_to_hex(cmap(i)) for i in np.linspace(0, 1, n)]


#%%% CELL 03.1 — BEHAVIOR LAYER VARIANTS
"""
Build layer-specific behavior colors from anchors and lightness factors.
"""
BEHAVIOR_L1: dict[str, str] = {
	f"Layer1_{name}": _hls_adjust_lightness(hex, LAYER_LIGHTNESS_FACTORS["Layer1"])
	for name, hex in BEHAVIOR.items()
}
BEHAVIOR_L2: dict[str, str] = {
	f"Layer2_{name}": _hls_adjust_lightness(hex, LAYER_LIGHTNESS_FACTORS["Layer2"])
	for name, hex in BEHAVIOR.items()
}
BEHAVIOR_RESISTANT: dict[str, str] = {
	f"Resistant_{name}": _hls_adjust_lightness(hex, LAYER_LIGHTNESS_FACTORS["Resistant"])
	for name, hex in BEHAVIOR.items()
}


#%%% CELL 03.2 — ORIENTATION & POSITION COLORMAPS
"""
Derive orientation HSV wheel and position X/Y colormaps.
"""
def _make_orientation_cmap(rotation_deg: float, dark_factor: float) -> ListedColormap:
	"""Build a rotated/darkened HSV wheel colormap."""
	# modern API (no deprecation warning)
	n = 256
	hues = np.linspace(0, 1, n, endpoint=False)
	shift = rotation_deg / 360.0
	shifted = (hues + shift) % 1.0
	colors = [mcolors.hsv_to_rgb((h, 1, dark_factor)) for h in shifted]
	return ListedColormap(colors, name="orientation")

cmap_orientation = _make_orientation_cmap(
	ORIENTATION_DECISIONS["rotation_deg"],
	ORIENTATION_DECISIONS["dark_factor"],
)

# Position colormaps (sample orientation wheel at cardinal directions)
def _make_position_cmap(axis: str) -> LinearSegmentedColormap:
	if axis == "x":
		# West→East
		start = cmap_orientation(0.00)  # red-ish
		end   = cmap_orientation(0.50)  # green-ish
	elif axis == "y":
		# South→North
		start = cmap_orientation(0.25)  # yellow-ish
		end   = cmap_orientation(0.75)  # blue-ish
	else:
		raise ValueError("axis must be 'x' or 'y'")
	return LinearSegmentedColormap.from_list(f"position_{axis}", [start, end])

cmap_position_x = _make_position_cmap("x")
cmap_position_y = _make_position_cmap("y")


#%%% CELL 03.3 — MOTION–SPEED COLORMAP
"""
Build piecewise colormap for motion speed with:
- Hard visual break at 4.0 (two points at x=4.0 with different colors).
- Plateau from plateau_start→plateau_end at a constant color.
- Values > plateau_end use the colormap's 'over' color (Resistant_Jump).
"""
def _make_motion_speed_cmap(decisions: dict, resistant_jump_hex: str) -> LinearSegmentedColormap:
	cps = list(decisions["control_points"])
	p_start = float(decisions.get("plateau_start", 25.0))
	p_end   = float(decisions.get("plateau_end",   75.0))

	# Determine plateau color: last specified color at/after p_start; else fallback.
	plateau_color = None
	for x, c in reversed(cps):
		if float(x) >= p_start:
			plateau_color = c
			break
	if plateau_color is None:
		plateau_color = "#7C0707"  # safe fallback

	# Compress plateau: keep all points strictly before p_start, then add (p_start, color) and (p_end, same color)
	cps = [(float(x), c) for (x, c) in cps if float(x) < p_start]
	cps.append((p_start, plateau_color))
	cps.append((p_end,   plateau_color))

	# Keep p_end just outside the inclusive domain so values == p_end map to last color,
	# and values > p_end hit the colormap's 'over' color.
	vmax = p_end - 1e-3
	positions = [min(max(x / vmax, 0.0), 1.0) for (x, _) in cps]
	colors    = [c for (_, c) in cps]

	cmap = LinearSegmentedColormap.from_list("motion_speed", list(zip(positions, colors)))
	if decisions.get("over_uses_resistant_jump", True):
		cmap.set_over(resistant_jump_hex)
	return cmap

cmap_motion_speed = _make_motion_speed_cmap(MOTION_SPEED_DECISIONS, BEHAVIOR_RESISTANT["Resistant_Jump"])


#%%% CELL 03.4 — RESOLVERS (HEX API)
"""
Functional resolvers to map values to hex strings.
These are the only functions that emit hex; cmap_* remain matplotlib objects.
"""
def orientation(angle_deg: float) -> str:
	"""Return hex color for orientation angle in degrees [0,360)."""
	return mcolors.to_hex(cmap_orientation((angle_deg % 360.0) / 360.0))

def position_x(t: float) -> str:
	"""Return hex color for normalized X position (0–1)."""
	return mcolors.to_hex(cmap_position_x(np.clip(t, 0.0, 1.0)))

def position_y(t: float) -> str:
	"""Return hex color for normalized Y position (0–1)."""
	return mcolors.to_hex(cmap_position_y(np.clip(t, 0.0, 1.0)))

def motion_speed(v: float) -> str:
	"""Return hex color for motion speed value (mm/s). Uses 'over' policy for v > plateau_end."""
	if v < 0:
		return COLOR.get("NoMotion", "NaN")  # sentinel

	p_end = float(MOTION_SPEED_DECISIONS.get("plateau_end", 75.0))
	# Over-range → explicit resistant jump (since Colormap.__call__ won't apply 'over' by itself)
	if v > p_end:
		return BEHAVIOR_RESISTANT["Resistant_Jump"]

	# Map 0..p_end into [0..1] using same epsilon as the colormap build
	scale = p_end - 1e-3
	return mcolors.to_hex(cmap_motion_speed(np.clip(v/scale, 0.0, 1.0)))


#%%% CELL 03.5 — GROUP COLORS
"""
Try to import experiment.GROUPS for explicit colors.
If absent or color missing, sample evenly from GROUP_COLORS_CMAP.
"""
GROUP_COLORS: dict[str, str] = {}
try:
	import experiment
	groups = experiment.GROUPS
	labels = list(groups.keys())
	explicit = [g.get("color") for g in groups.values()]
	if all(c is not None for c in explicit):
		GROUP_COLORS = {lbl: mcolors.to_hex(c) for lbl, c in zip(labels, explicit)}
	else:
		cmap = mpl_cmaps.get(GROUP_COLORS_CMAP).resampled(len(labels))
		GROUP_COLORS = {lbl: mcolors.to_hex(cmap(i/(len(labels)-1 if len(labels)>1 else 1)))
		                for i, lbl in enumerate(labels)}
except Exception:
	GROUP_COLORS = {}



#%% CELL 04 — ASSEMBLY: COLOR
"""
Assemble the flat COLOR registry.
Order:
  1) Stimuli & Sentinels
  2) Behavior anchors + layer variants
  3) Views & SLEAP parts
  4) Themes
  5) Colormaps (matplotlib objects)
  6) Resolvers (hex API)
  7) Group colors (prefixed as 'group:<Label>')
Rule:
  - Dark theme uses VisualStim_Light; Light theme uses VisualStim.
"""
COLOR: dict[str, object] = {}

# 1) Stimuli & Sentinels
COLOR.update(STIMULUS_BASE)
COLOR.update(SENTINEL)

# 2) Behaviors (anchors + layer variants)
COLOR.update(BEHAVIOR)
COLOR.update(BEHAVIOR_L1)
COLOR.update(BEHAVIOR_L2)
COLOR.update(BEHAVIOR_RESISTANT)

# 3) Views & SLEAP parts
COLOR.update(VIEW)
COLOR.update(SLEAP)

# 4) Themes (as nested dicts)
COLOR["Theme_Dark"] = THEME_DARK
COLOR["Theme_Light"] = THEME_LIGHT

# 5) Colormaps (matplotlib objects; *not* hex)
COLOR["cmap_orientation"] = cmap_orientation
COLOR["cmap_position_x"] = cmap_position_x
COLOR["cmap_position_y"] = cmap_position_y
COLOR["cmap_motion_speed"] = cmap_motion_speed

# 6) Resolvers (store under keys expected by the report)
COLOR["orientation"]  = orientation
COLOR["position_x"]   = position_x
COLOR["position_y"]   = position_y
COLOR["motion_speed"] = motion_speed

# 7) Group colors
for label, hx in GROUP_COLORS.items():
	COLOR[f"{label}"] = hx

COLOR = _RO(COLOR)


#%% CELL 05 — PUBLIC SURFACE
"""
Explicit export list for downstream modules.
"""
__all__ = ["COLOR"]


#%% CELL 06 — REPORT (visual inspection sheet; uses ONLY COLOR)
"""
Renders a single figure previewing all palette decisions on Dark (left) and Light (right).

Rows (per column):
  1) Groups (explicit from experiment.py or auto-fallback already injected into COLOR)
  2) Stimuli
  3) Sentinels
  4) Behavior layers matrix (Layer1 → Layer2 → Behavior → Resistant)
  5) View
  6) Bodyparts
  7) Orientation — HSV spokes (slim bars, hollow center, cardinal labels)
  8) Position — X (West→East) and Y (South→North) gradients derived from COLOR["position_x"/"position_y"]
  9) Motion–Speed — NoMotion block, gradient bar (0..75; ≥75 would be over), and colored trace

Rules:
- This cell relies ONLY on COLOR (anchors + resolvers). No direct access to internal cmaps.
- VisualStim is theme-specific: VisualStim_Light for Dark theme; VisualStim for Light theme.
"""


# --- tiny helpers (purely for drawing; consume COLOR, create nothing new) ----
def _is_hex(x):
    try:
        mcolors.to_rgb(x)
        return True
    except Exception:
        return False

def _collect_groups_from_COLOR(COLOR):
    """Heuristic: any hex-colored key not in our known tokens/prefixes is a Group label."""
    known_exact = {
        # stimuli
        "Stim0","Stim1","VisualStim","VisualStim_Light",
        # sentinels
        "NaN","NoMotion",
        # behavior anchors
        "Jump","Walk","Stationary","Freeze","Noisy",
        # view
        "Left","Right","Top","Vertical",
        # sleap
        "Head","Thorax","Abdomen","LeftWing","RightWing",
        # themes
        "Theme_Dark","Theme_Light",
    }
    known_prefixes = ("Layer1_","Layer2_","Resistant_","cmap_")
    known_funcs    = {"motion_speed","orientation","position_x","position_y"}

    out = {}
    for k,v in COLOR.items():
        if k in known_exact: continue
        if any(k.startswith(p) for p in known_prefixes): continue
        if k in known_funcs: continue
        if isinstance(v, str) and v.startswith("#") and _is_hex(v):
            out[k] = v
    return dict(out)

def swatches_one_row(ax, theme, title, mapping):
    ax.set_facecolor(theme["panel"]); ax.set_xticks([]); ax.set_yticks([]); ax.spines[:].set_visible(False)
    ax.set_title(title, color=theme["text"], fontsize=12, pad=8)
    x = .08
    for k,v in mapping.items():
        ax.add_patch(P.Rectangle((x,.45), .10,.25, color=v, ec=theme["grid"], lw=.6, transform=ax.transAxes))
        ax.text(x+.05, .40, k, ha="center", va="top", color=theme["text"], fontsize=8, transform=ax.transAxes)
        x += .12

def draw_behavior_layers_from_COLOR(ax, theme, COLOR, order=None, cell_w=.11, cell_h=.18, x0=.14, y0=.10):
    """Render 4-row matrix using keys inside COLOR: Layer1_<B>, Layer2_<B>, <B>, Resistant_<B>."""
    ax.set_facecolor(theme["panel"]); ax.set_xticks([]); ax.set_yticks([]); ax.spines[:].set_visible(False)
    beh_order = order if order else ["Jump","Walk","Stationary","Freeze","Noisy"]
    # column labels
    for j, beh in enumerate(beh_order):
        ax.text(x0 + j*cell_w + cell_w/2, y0 + 4*cell_h + .03, beh,
                color=theme["text"], fontsize=8, ha="center", va="bottom", transform=ax.transAxes)
    # rows top→bottom
    rows = [("Layer1_", "Layer1"), ("Layer2_", "Layer2"), ("", "Behavior"), ("Resistant_", "Resistant")]
    for i, (prefix, label) in enumerate(rows):
        ax.text(x0 - .03, y0 + (3-i)*cell_h + cell_h/2, label,
                color=theme["text"], fontsize=9, ha="right", va="center", transform=ax.transAxes, weight="bold")
        for j, beh in enumerate(beh_order):
            key = f"{prefix}{beh}" if prefix else beh
            ax.add_patch(P.Rectangle((x0 + j*cell_w, y0 + (3-i)*cell_h),
                                     cell_w*.92, cell_h*.9, color=COLOR[key], ec=theme["grid"], lw=.5,
                                     transform=ax.transAxes))

def gradient_bar_from_resolver(ax, theme, resolver, vmin, vmax, extent):
    """Horizontal gradient bar by sampling resolver(value)->hex across [vmin, vmax]."""
    n = 512
    xs = np.linspace(vmin, vmax, n)
    x0,x1,y0,y1 = extent
    for i, val in enumerate(xs):
        x = x0 + (x1 - x0) * (i/(n-1))
        ax.add_patch(P.Rectangle((x, y0), (x1-x0)/n, (y1-y0), color=resolver(val), lw=0, transform=ax.transAxes))

def colorline_from_resolver(ax, x, y, resolver, no_motion_hex=None, lw=2.0):
    """Line colored segment-wise by resolver(midpoint)."""
    pts = np.array([x,y]).T.reshape(-1,1,2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    mids = 0.5*(y[:-1] + y[1:])
    cols = []
    for s in mids:
        if (no_motion_hex is not None) and (abs(s) <= 1e-12):
            cols.append(no_motion_hex)
        else:
            cols.append(resolver(float(s)))
    lc = LineCollection(segs, colors=cols, linewidths=lw)
    ax.add_collection(lc)


def render_color_report(*, show: bool = True, savepath: str | None = None) -> None:
    # ---- consume ONLY COLOR --------------------------------------------------
    THEME_D = COLOR["Theme_Dark"]; THEME_L = COLOR["Theme_Light"]
    THEMES = [("Dark", THEME_D), ("Light", THEME_L)]

    # resolvers
    motion_speed = COLOR["motion_speed"]
    orientation  = COLOR["orientation"]
    position_x   = COLOR["position_x"]
    position_y   = COLOR["position_y"]

    # anchors
    BEH_LIST = ["Jump","Walk","Stationary","Freeze","Noisy"]

    # groups row from COLOR
    GROUPS_ROW = _collect_groups_from_COLOR(COLOR)

    # demo data for motion–speed trace
    t = np.linspace(0,100,600)
    speed = np.zeros_like(t)
    m = (t>=20)&(t<90)
    speed[m] = 8 + 6*np.sin(2*np.pi*(t[m]-20)/60)
    speed[t>=90] = 76  # top of map (≥75 would be over-color if plotted beyond)

    # --- build figure layout --------------------------------------------------
    fig = plt.figure(figsize=(14,19))
    bg = fig.add_axes([0,0,1,1]); bg.axis("off")
    bg.add_patch(P.Rectangle((0,0), .5,1, color=THEME_D["background"]))
    bg.add_patch(P.Rectangle((.5,0), .5,1, color=THEME_L["background"]))

    # Rows: Groups, Stimuli, Sentinels, Matrix, View, Bodyparts, Orientation, Position, Motion–Speed
    gs = fig.add_gridspec(9,2, height_ratios=[0.7, 0.7, 0.55, 1.1, 0.8, 0.8, 0.9, 0.9, 1.3],
                          hspace=.55, wspace=.18)

    for col,(label,th) in enumerate(THEMES):

        # 1) Groups (first)
        ax_grp = fig.add_subplot(gs[0,col])
        title = f"{label} — Groups" if GROUPS_ROW else f"{label} — Groups (none)"
        swatches_one_row(ax_grp, th, title, GROUPS_ROW or {})

        # theme-specific VisualStim choice
        stim_map = {
            "VisualStim": COLOR["VisualStim_Light"] if label=="Dark" else COLOR["VisualStim"],
            "Stim0": COLOR["Stim0"], "Stim1": COLOR["Stim1"],
        }

        # 2) Stimuli
        ax_stim = fig.add_subplot(gs[1,col])
        swatches_one_row(ax_stim, th, f"{label} — Stimuli", stim_map)

        # 3) Sentinels
        ax_sent = fig.add_subplot(gs[2,col])
        swatches_one_row(ax_sent, th, f"{label} — Sentinels", {"NaN": COLOR["NaN"], "NoMotion": COLOR["NoMotion"]})

        # 4) Behavior matrix
        ax_mat = fig.add_subplot(gs[3,col])
        ax_mat.set_title(f"{label} — Behavior Layers (Layer1 → Layer2 → Behavior → Resistant)",
                         color=th["text"], fontsize=12, pad=8)
        draw_behavior_layers_from_COLOR(ax_mat, th, COLOR, order=BEH_LIST)

        # 5) View
        ax_view = fig.add_subplot(gs[4,col])
        swatches_one_row(ax_view, th, f"{label} — View",
                         {k:COLOR[k] for k in ("Left","Right","Top","Vertical")})

        # 6) Bodyparts
        ax_body = fig.add_subplot(gs[5,col])
        swatches_one_row(ax_body, th, f"{label} — Bodyparts",
                         {k:COLOR[k] for k in ("Head","Thorax","Abdomen","LeftWing","RightWing")})

        # 7) Orientation — HSV spokes (slim bars, hollow center)
        ax_ori = fig.add_subplot(gs[6,col]); ax_ori.set_facecolor(th["panel"]); ax_ori.set_xticks([]); ax_ori.set_yticks([]); ax_ori.spines[:].set_visible(False)
        ax_ori.set_title(f"{label} — Orientation (HSV Spokes)", color=th["text"], fontsize=12, pad=8)
        wheel = ax_ori.inset_axes([.10,.05,.80,.90], projection="polar")
        wheel.set_facecolor(th["panel"]); wheel.set_theta_offset(np.pi/2)
        wheel.set_xticklabels([]); wheel.set_yticklabels([]); wheel.grid(False)
        for deg in range(0,360,15):
            ang = np.radians(deg)
            wheel.bar(ang, 0.7, width=np.radians(6), bottom=0.3, color=orientation(deg), edgecolor=None)
        for d,lbl in [(0,'N'),(90,'W'),(180,'S'),(270,'E')]:
            wheel.text(np.radians(d), 1.07, lbl, ha="center", va="center", fontsize=11, fontweight="bold", color=th["text"])
        wheel.spines['polar'].set_color(th["grid"])

        # 8) Position gradients — sample resolvers
        ax_pos = fig.add_subplot(gs[7,col]); ax_pos.set_facecolor(th["panel"]); ax_pos.set_xticks([]); ax_pos.set_yticks([]); ax_pos.spines[:].set_visible(False)
        ax_pos.set_title(f"{label} — Position Gradients", color=th["text"], fontsize=12, pad=8, loc="center")
        # X: West(0) → East(1)
        n = 256; x0,x1 = .06,.94
        y_top0,y_top1 = .62,.88
        for i,u in enumerate(np.linspace(0,1,n)):
            x = x0 + (x1-x0)*(i/(n-1))
            ax_pos.add_patch(P.Rectangle((x, y_top0), (x1-x0)/n, (y_top1-y_top0), color=position_x(u), lw=0, transform=ax_pos.transAxes))
        ax_pos.text(.50,.91,"Position X — West(0)→East(1)", color=th["text"], transform=ax_pos.transAxes, ha="center", fontsize=10)
        # Y: South(0) → North(1)
        y_bot0,y_bot1 = .12,.38
        for i,u in enumerate(np.linspace(0,1,n)):
            x = x0 + (x1-x0)*(i/(n-1))
            ax_pos.add_patch(P.Rectangle((x, y_bot0), (x1-x0)/n, (y_bot1-y_bot0), color=position_y(u), lw=0, transform=ax_pos.transAxes))
        ax_pos.text(.50,.43,"Position Y — South(0)→North(1)", color=th["text"], transform=ax_pos.transAxes, ha="center", fontsize=10)
        ax_pos.plot([.06,.94],[.50,.50], color=th["grid"], lw=.8, transform=ax_pos.transAxes)

        # 9) Motion–Speed: NoMotion, gradient bar, Jump, trace (via resolver)
        ax_ms = fig.add_subplot(gs[8,col]); ax_ms.set_facecolor(th["panel"]); ax_ms.set_xticks([]); ax_ms.set_yticks([]); ax_ms.spines[:].set_visible(False)
        ax_ms.set_title(f"{label} — Motion | Speed Colormap", color=th["text"], fontsize=12, pad=8)
        # No Motion block
        ax_ms.add_patch(P.Rectangle((.03,.70), .12,.22, color=COLOR["NoMotion"], ec=th["grid"]))
        ax_ms.text(.09,.66,"No Motion", color=th["text"], ha="center", va="center", fontsize=9)
        # Gradient bar (0..75) sampled from resolver
        extent = (.20,.80,.74,.90)
        gradient_bar_from_resolver(ax_ms, th, motion_speed, 0.0, 75.0, extent)
        for v in [0,4,10,16,25,75]:
            xx = extent[0] + (extent[1]-extent[0])*(v/75)
            ax_ms.plot([xx,xx],[.71,.74], color=th["grid"], lw=.9)
            ax_ms.text(xx,.69, str(v), color=th["text"], ha="center", va="top", fontsize=8)
        # Jump block (resistant jump)
        ax_ms.add_patch(P.Rectangle((.84,.70), .12,.22, color=COLOR["Resistant_Jump"], ec=th["grid"]))
        ax_ms.text(.90,.66,"Jump", color=th["text"], ha="center", va="center", fontsize=9)
        # Trace colored by resolver
        ax_line = ax_ms.inset_axes([0.05, 0.08, 0.90, 0.5]); ax_line.set_facecolor(th["panel"])
        colorline_from_resolver(ax_line, t, speed, motion_speed, no_motion_hex=COLOR["NoMotion"], lw=2.0)
        ax_line.plot(t, speed, color=th["muted"], lw=.6, alpha=.6)
        ax_line.set_xlim(t.min(), t.max()); ax_line.set_ylim(-2,80)
        ax_line.set_xlabel("Time (a.u.)", color=th["text"], fontsize=9)
        ax_line.set_ylabel("Speed (mm/s)", color=th["text"], fontsize=9)
        ax_line.tick_params(colors=th["text"], labelsize=8)
        ax_line.grid(True, color=th["grid"], lw=.8, alpha=.85)

    if show:
        plt.show()


if __name__ == "__main__":
    # Run the visual report when executed directly:
    #   python -m Config.color
    render_color_report(show=True)
