#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_color/report.py

Overview
	Comprehensive dual-theme visual reporting for color validation.
	Extracted from the enhanced working version to support the configuration
	pattern while preserving sophisticated visualization capabilities.

Functions
	render_color_report() → Main dual-theme visual report
	_swatches_row() → Draw labeled color swatches
	_draw_behavior_matrix() → Draw 4-row behavior layer matrix
	_gradient_bar_mm() → Draw horizontal gradient bars
	create_report_bundle() → Main entry point for report functions

Notes
	- Preserves dual-theme side-by-side comparison
	- Maintains behavior matrix visualization
	- Supports HSV orientation spokes with cardinal labels
	- Includes motion speed trace with vectorized coloring
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

from types import MappingProxyType
import numpy as np
import matplotlib.colors as mcolors
from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib.collections import LineCollection
from matplotlib.axes import Axes

#%% CELL 02 — UTILITY FUNCTIONS

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


#%% CELL 03 — VISUALIZATION COMPONENTS

def _swatches_row(ax: Axes,
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


def _draw_behavior_matrix(ax: Axes,
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


def _gradient_bar_mm(ax: Axes,
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


#%% CELL 04 — COLORMAP HELPER FUNCTIONS

def _orientation_hex(angle_deg: float, color_bundle: MappingProxyType) -> str:
	"""Sample orientation colormap with FLOAT fraction and return hex."""
	cmap = color_bundle["cmap"]["orientation"]
	frac = (np.mod(float(angle_deg), 360.0)) / 360.0
	r, g, b, _ = cmap(frac)
	return mcolors.to_hex((r, g, b), keep_alpha=False)


def _position_x_hex(t: float, color_bundle: MappingProxyType) -> str:
	"""Return hex for X-position t∈[0,1] via COLOR['cmap']['position_X']."""
	cmap = color_bundle["cmap"]["position_X"]
	tc = float(np.clip(t, 0.0, 1.0))
	r, g, b, _ = cmap(tc)
	return mcolors.to_hex((r, g, b), keep_alpha=False)


def _position_y_hex(t: float, color_bundle: MappingProxyType) -> str:
	"""Return hex for Y-position t∈[0,1] via COLOR['cmap']['position_Y']."""
	cmap = color_bundle["cmap"]["position_Y"]
	tc = float(np.clip(t, 0.0, 1.0))
	r, g, b, _ = cmap(tc)
	return mcolors.to_hex((r, g, b), keep_alpha=False)


#%% CELL 05 — MAIN REPORT FUNCTION

def render_color_report(color_bundle: MappingProxyType, *, show: bool = True,
                        savepath: str | None = None) -> None:
	"""
	Render the full visual color report.

	Args:
		color_bundle: Complete COLOR bundle with hex and cmap sections
		show: Whether to display the figure.
		savepath: Optional path to save PNG.

	Notes:
		Consumes only the COLOR bundle for complete independence.
	"""
	hexspace = color_bundle["hex"]
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
				color=_orientation_hex(deg, color_bundle), edgecolor=None,
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
					color=_position_x_hex(uu, color_bundle), lw=0,
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
					color=_position_y_hex(uu, color_bundle), lw=0,
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


#%% CELL 06 — REPORT BUNDLE CREATION

def create_report_bundle() -> MappingProxyType:
	"""
	Create the report bundle with visual reporting functions.

	Returns:
		MappingProxyType: Immutable bundle with report functions
	"""
	return MappingProxyType({
		"render_color_report": render_color_report,
	})

__all__ = [
	"render_color_report",
	"create_report_bundle"
]
