#%% CELL 00 — HEADER & SCOPE
'''
{{COMMIT_DETAILS}}
#<github.com/MoitaLab/Repo>
#<full_commit_hash>
#<DD-MM-YYYY HH:MM:SS>

param.py

Overview:
  Canonical registry of all CSV parameters across the pipeline:
    - BASE, tracked, scored, sleap, pose
  Each entry declares:
    label, tags, type, unit, role, domain, description.

Use:
  - Single source of truth for parameter documentation.
  - Validation of CSV columns at load time.
  - Generation of human-readable reports.

Dependencies:
  None (standalone metadata module).
'''


#%% CELL 01 — IMPORTS
"""
Imports isolated (matching path.py / experiment.py style).
"""
from typing import TypedDict, Literal, Any
from types import MappingProxyType as _RO


#%% CELL 02 — SCHEMA
"""
Shape of each parameter entry in the registry.

Fields:
  label       — Human-readable name for reports/UI.
  tags        — Provenance tags (which file(s): BASE, tracked, sleap, pose, scored; plus "stimuli" if applicable).
  type        — Primitive storage type: "int" | "float" | "string" | "bool".
  unit        — Physical/logical unit: "frames","sec","mm","deg","px","unitless","fraction","state","classification","category" or None.
  role        — Semantic role: "binary" | "categorical" | "continuous".
  domain      — Legal values (list of categories or [min,max]) or None if unbounded.
  description — One-line explanation of the column.
"""
class ParamSpec(TypedDict, total=False):
	label: str
	tags: list[str]
	type: Literal["int","float","string","bool"]
	unit: str | None
	role: Literal["binary","categorical","continuous"]
	domain: list[Any] | None
	description: str


#%% CELL 03 — BASE
"""
Hardware counters and GPIO signals from BASE.csv.
"""
BASE: dict[str, ParamSpec] = {
	"GPIO": {
		"label": "GPIO State",
		"tags": ["BASE"],
		"type": "int",
		"unit": "state",
		"role": "categorical",
		"domain": None,
		"description": "Digital input state from GPIO pins aligned to frame clock (stimulus markers).",
	},
	"FrameID": {
		"label": "Frame ID",
		"tags": ["BASE"],
		"type": "int",
		"unit": "frames",
		"role": "continuous",
		"domain": None,
		"description": "Camera frame counter ticks aligned to frame clock (may not start at 0).",
	},
	"Timestamp": {
		"label": "Timestamp",
		"tags": ["BASE"],
		"type": "int",
		"unit": "ns",
		"role": "continuous",
		"domain": None,
		"description": "Acquisition clock time in nanoseconds (monotonic, not Unix time).",
	},
}


#%% CELL 04 — SHARED INDEX & STIMULI
"""
Signals shared across multiple files (single source of truth):
- FrameIndex: global per-frame reference aligned to BASE.FrameID.
- Stimuli channels: names/labels aligned with experiment.py::STIMULI.
"""
SHARED: dict[str, ParamSpec] = {
	"FrameIndex": {
		"label": "Frame Index",
		"tags": ["tracked", "sleap", "pose", "scored"],
		"type": "int",
		"unit": "frames",
		"role": "continuous",
		"domain": None,
		"description": "Reference aligned to BASE.FrameID; not a local 0..N counter.",
	},
	"VisualStim": {
		"label": "VisualStim",
		"tags": ["tracked", "scored", "stimuli"],
		"type": "int",
		"unit": "state",
		"role": "binary",
		"domain": [0, 1],
		"description": "Visual stimulus on/off per frame.",
	},
	"Stim0": {
		"label": "RedLED",
		"tags": ["tracked", "scored", "stimuli"],
		"type": "int",
		"unit": "state",
		"role": "binary",
		"domain": [0, 1],
		"description": "Red LED stimulus on/off per frame.",
	},
	"Stim1": {
		"label": "GreenLED",
		"tags": ["tracked", "scored", "stimuli"],
		"type": "int",
		"unit": "state",
		"role": "binary",
		"domain": [0, 1],
		"description": "Green LED stimulus on/off per frame.",
	},
}


#%% CELL 05 — TRACKED
"""
Tracked geometry and motion proxy from tracked.csv.
"""
TRACKED: dict[str, ParamSpec] = {
	"NormalizedCentroidX": {
		"label": "Normalized Centroid X",
		"tags": ["tracked"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Centroid X normalized to arena width (0–1).",
	},
	"NormalizedCentroidY": {
		"label": "Normalized Centroid Y",
		"tags": ["tracked"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Centroid Y normalized to arena height (0–1).",
	},
	"PixelChange": {
		"label": "Pixel Change",
		"tags": ["tracked"],
		"type": "int",
		"unit": "px",
		"role": "continuous",
		"domain": None,
		"description": "Count of changed pixels between consecutive frames (motion proxy).",
	},
}


#%% CELL 06 — SCORED
"""
Derived kinematics and multi-layer classifier labels from scored.csv.
Categorical domains are written in canonical order inline.
"""
SCORED: dict[str, ParamSpec] = {
	"Position_X": {
		"label": "Position X",
		"tags": ["scored"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Centroid X position (mm) in arena coordinates.",
	},
	"Position_Y": {
		"label": "Position Y",
		"tags": ["scored"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Centroid Y position (mm) in arena coordinates.",
	},
	"Speed": {
		"label": "Speed",
		"tags": ["scored"],
		"type": "float",
		"unit": "mm/s",
		"role": "continuous",
		"domain": None,
		"description": "Instantaneous centroid speed (mm/s).",
	},
	"Motion": {
		"label": "Motion",
		"tags": ["scored"],
		"type": "int",
		"unit": "state",
		"role": "binary",
		"domain": [0, 1],
		"description": "Binary motion flag from PixelChange (1 = motion).",
	},

	# Layered labels
	"Layer1": {
		"label": "Layer 1",
		"tags": ["scored"],
		"type": "string",
		"unit": "classification",
		"role": "categorical",
		"domain": ["Layer1_Jump", "Layer1_Walk", "Layer1_Stationary", "Layer1_Freeze"],
		"description": "First-pass classifier label per frame.",
	},
	"Layer1_Denoised": {
		"label": "Layer 1 (Denoised)",
		"tags": ["scored"],
		"type": "string",
		"unit": "classification",
		"role": "categorical",
		"domain": ["Layer1_Jump", "Layer1_Walk", "Layer1_Stationary", "Layer1_Freeze"],
		"description": "Layer1 with micro-bouts removed (jump preserved).",
	},
	"Layer2": {
		"label": "Layer 2",
		"tags": ["scored"],
		"type": "string",
		"unit": "classification",
		"role": "categorical",
		"domain": ["Layer2_Jump", "Layer2_Walk", "Layer2_Stationary", "Layer2_Freeze"],
		"description": "Windowed consensus over Layer1 (jump override).",
	},
	"Layer2_Denoised": {
		"label": "Layer 2 (Denoised)",
		"tags": ["scored"],
		"type": "string",
		"unit": "classification",
		"role": "categorical",
		"domain": ["Layer2_Jump", "Layer2_Walk", "Layer2_Stationary", "Layer2_Freeze"],
		"description": "Consensus over Layer1_Denoised with half-missing rule.",
	},

	# Resistant tiers
	"Resistant": {
		"label": "Resistant",
		"tags": ["scored"],
		"type": "string",
		"unit": "classification",
		"role": "categorical",
		"domain": ["Resistant_Walk", "Resistant_Stationary", "Resistant_Freeze"],
		"description": "Summary when a full bout covers a startle window.",
	},
	"Resistant_Denoised": {
		"label": "Resistant (Denoised)",
		"tags": ["scored"],
		"type": "string",
		"unit": "classification",
		"role": "categorical",
		"domain": ["Resistant_Walk", "Resistant_Stationary", "Resistant_Freeze"],
		"description": "Resistant summary using denoised paths.",
	},

	# Behavior labels
	"Behavior": {
		"label": "Behavior",
		"tags": ["scored"],
		"type": "string",
		"unit": "classification",
		"role": "categorical",
		"domain": ["Jump", "Walk", "Stationary", "Freeze", "Resistant_Freeze"],
		"description": "Behavior mapped from Layer2; Freeze may promote to Resistant_Freeze.",
	},
	"Behavior_Denoised": {
		"label": "Behavior (Denoised)",
		"tags": ["scored"],
		"type": "string",
		"unit": "classification",
		"role": "categorical",
		"domain": ["Jump", "Walk", "Stationary", "Freeze", "Resistant_Freeze", "Noisy"],
		"description": "Behavior from Layer2_Denoised; may include Noisy when gap-filled.",
	},
}


#%% CELL 07 — SLEAP
"""
Normalized view/body-part positions and confidences from sleap.csv.
Views listed first (Left, Right, Top), followed by body parts
(Head, Thorax, Abdomen, LeftWing, RightWing).
"""
SLEAP: dict[str, ParamSpec] = {
	# Left view
	"Left.Position.X": {
		"label": "Left View X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the left camera view.",
	},
	"Left.Position.Y": {
		"label": "Left View Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the left camera view.",
	},
	"Left.Confidence": {
		"label": "Left View Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the left view.",
	},

	# Right view
	"Right.Position.X": {
		"label": "Right View X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the right camera view.",
	},
	"Right.Position.Y": {
		"label": "Right View Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the right camera view.",
	},
	"Right.Confidence": {
		"label": "Right View Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the right view.",
	},

	# Top view
	"Top.Position.X": {
		"label": "Top View X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the top view.",
	},
	"Top.Position.Y": {
		"label": "Top View Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the top view.",
	},
	"Top.Confidence": {
		"label": "Top View Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the top view.",
	},

	# Body parts (normalized)
	"Head.Position.X": {
		"label": "Head X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the head keypoint.",
	},
	"Head.Position.Y": {
		"label": "Head Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the head keypoint.",
	},
	"Head.Confidence": {
		"label": "Head Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the head keypoint.",
	},

	"Thorax.Position.X": {
		"label": "Thorax X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the thorax keypoint.",
	},
	"Thorax.Position.Y": {
		"label": "Thorax Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the thorax keypoint.",
	},
	"Thorax.Confidence": {
		"label": "Thorax Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the thorax keypoint.",
	},

	"Abdomen.Position.X": {
		"label": "Abdomen X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the abdomen keypoint.",
	},
	"Abdomen.Position.Y": {
		"label": "Abdomen Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the abdomen keypoint.",
	},
	"Abdomen.Confidence": {
		"label": "Abdomen Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the abdomen keypoint.",
	},

	"LeftWing.Position.X": {
		"label": "Left Wing X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the left wing keypoint.",
	},
	"LeftWing.Position.Y": {
		"label": "Left Wing Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the left wing keypoint.",
	},
	"LeftWing.Confidence": {
		"label": "Left Wing Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the left wing keypoint.",
	},

	"RightWing.Position.X": {
		"label": "Right Wing X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the right wing keypoint.",
	},
	"RightWing.Position.Y": {
		"label": "Right Wing Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the right wing keypoint.",
	},
	"RightWing.Confidence": {
		"label": "Right Wing Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "fraction",
		"role": "continuous",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the right wing keypoint.",
	},
}


#%% CELL 08 — POSE
"""
Arena-calibrated positions in mm and orientation from pose.csv.
Starts with selected view and orientation, followed by body-part
positions in the order: Head, Thorax, Abdomen, LeftWing, RightWing.
"""
POSE: dict[str, ParamSpec] = {
	"View": {
		"label": "View",
		"tags": ["pose"],
		"type": "string",
		"unit": "category",
		"role": "categorical",
		"domain": ["Left", "Right", "Top", "Vertical"],
		"description": "Selected camera view label (Bottom→Top normalized).",
	},
	"View_X": {
		"label": "View X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "X coordinate (mm) in the selected view, post-calibration.",
	},
	"View_Y": {
		"label": "View Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Y coordinate (mm) in the selected view, post-calibration.",
	},
	"Orientation": {
		"label": "Orientation",
		"tags": ["pose"],
		"type": "float",
		"unit": "deg",
		"role": "continuous",
		"domain": [0.0, 360.0],
		"description": "Body orientation (deg) from Thorax→View axis; 0–360 wrap.",
	},

	# Per-part positions in the selected view (mm)
	"Head_X": {
		"label": "Head X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Head keypoint X (mm) in the selected view.",
	},
	"Head_Y": {
		"label": "Head Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Head keypoint Y (mm) in the selected view.",
	},
	"Thorax_X": {
		"label": "Thorax X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Thorax keypoint X (mm) in the selected view.",
	},
	"Thorax_Y": {
		"label": "Thorax Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Thorax keypoint Y (mm) in the selected view.",
	},
	"Abdomen_X": {
		"label": "Abdomen X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Abdomen keypoint X (mm) in the selected view.",
	},
	"Abdomen_Y": {
		"label": "Abdomen Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Abdomen keypoint Y (mm) in the selected view.",
	},
	"LeftWing_X": {
		"label": "Left Wing X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Left wing keypoint X (mm) in the selected view.",
	},
	"LeftWing_Y": {
		"label": "Left Wing Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Left wing keypoint Y (mm) in the selected view.",
	},
	"RightWing_X": {
		"label": "Right Wing X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Right wing keypoint X (mm) in the selected view.",
	},
	"RightWing_Y": {
		"label": "Right Wing Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "continuous",
		"domain": None,
		"description": "Right wing keypoint Y (mm) in the selected view.",
	},
}


#%% CELL 09 — ASSEMBLY & PUBLIC SURFACE
"""
Assemble the final registry and expose a single public symbol.
Order of merge: BASE → SHARED → TRACKED → SCORED → SLEAP → POSE
"""
PARAM: dict[str, ParamSpec] = {
	**BASE,
	**SHARED,
	**TRACKED,
	**SCORED,
	**SLEAP,
	**POSE,
}

PARAM = _RO(PARAM)

__all__ = ["PARAM"]


#%% CELL 10 — REPORT
"""
Compact summary when running this file directly.
Lists total count and per-section parameter names.
"""
if __name__ == "__main__":
	print("PARAM registry summary")
	print(f"Total parameters: {len(PARAM)}\n")

	sections = [
		("BASE", BASE),
		("SHARED", SHARED),
		("TRACKED", TRACKED),
		("SCORED", SCORED),
		("SLEAP", SLEAP),
		("POSE", POSE),
	]

	for title, reg in sections:
		print(f"{title} ({len(reg)})")
		for name in reg:
			print(f"  - {name}")
		print()

