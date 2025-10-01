#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/param.py

Overview
	Single source of truth (SSOT) for CSV column metadata used across the pipeline.
	Defines the schema for every column: label, tags, type, unit, role, legal domain,
	and a short description. The registry is explicit (not generated), easy to diff,
	and consumed by QC, readers/writers, and documentation.

Allowed Enumerations (validated at assembly)
	Types:
		{"int", "float", "str", "bool"}
	Roles:
		{"index", "time", "value", "binary", "category", "vector", "position", "orientation"}
	Units:
		{"frame", "ns", "mm", "mm/s", "deg", "px", ""}
	Tags (origin / source tables):
		{"BASE", "tracked", "scored", "sleap", "pose", "stimuli"}

Domain Rules (validated at assembly)
	* Numeric range domains must be lists of length 2: [min, max] with min <= max.
	* Binary domains must be exactly [0, 1] (ints) when role == "binary".
	* Categorical domains must be non-empty, unique collections of literal values.
	* Units must match the declared type/role (e.g., "frame" for time index, "mm/s" for speed).
"""


#%% CELL 01 — IMPORTS

from __future__ import annotations

"""
Imports
	Stdlib-only imports for schema typing and public bundle freezing.
	No third-party or project-internal imports here to keep Config independent.
"""

from typing import TypedDict
from collections.abc import Mapping
from types import MappingProxyType


#%% CELL 02 — SCHEMA & ALLOWED ENUMS
"""
Schema & Allowed Enumerations
	Centralized, explicit constraints for the registry. These are validated during assembly.
"""

# ALLOWED SETS

ALLOWED_TYPES: set[str] = {"int", "float", "str", "bool"}

ALLOWED_ROLES: set[str] = {
	"index",        # primary indexing column (e.g., frame)
	"time",         # temporal variables (derived from index or timestamps)
	"value",        # continuous scalar values
	"binary",       # 0/1 coded variables (strictly [0, 1] domain)
	"category",     # nominal/categorical labels
	"vector",       # multi-component numeric values (e.g., [x, y] magnitudes)
	"position",     # spatial coordinates in mm or px
	"orientation",  # angles in degrees (or deg/s)
}

ALLOWED_UNITS: set[str] = {
	"frame",
	"ns",
	"mm", "mm/s",
	"deg",
	"px",
	"",
}

ALLOWED_TAGS: set[str] = {"BASE", "tracked", "scored", "sleap", "pose", "stimuli"}


# PARAMSPEC

class ParamSpec(TypedDict):
	"""
	Schema for a single column definition in the PARAM registry.

	Fields:
		label: Canonical column name as it appears in CSVs and dataframes.
		tags: Origin/source tags (subset of ALLOWED_TAGS). Drives per-table schema checks.
		type: Primitive storage type for the column ("int" | "float" | "str" | "bool").
		unit: Engineering unit, when applicable (subset of ALLOWED_UNITS). Empty string if N/A.
		role: Semantic role of the column (subset of ALLOWED_ROLES).
		domain: Legal values. One of:
			- Numeric range: [min, max] (list of 2 numbers, min <= max).
			- Binary: [0, 1] (exact ints) when role == "binary".
			- Categorical: list of unique literal values (non-empty).
			- Empty list [] when unconstrained (discouraged; prefer a real domain).
		description: Short human-readable description of the column’s domain role.

	Notes:
		* Half-open intervals [start, end) are the convention for frame/time spans used by consumers.
		* Units must be coherent with role (e.g., "frame" for index/timebase, "mm/s" for speed).
	"""
	label: str
	tags: list[str]
	type: str
	unit: str
	role: str
	domain: list[object]
	description: str


#%% CELL 03 — BASE
"""
BASE
	Hardware counters and GPIO stimulus markers sourced from BASE.csv.
	These columns provide the foundational timing and digital-state signals
	that other tables align to. Content preserved; formatting standardized.
"""

BASE: dict[str, ParamSpec] = {
	"GPIO": {
		"label": "GPIO State",
		"tags": ["BASE"],
		"type": "int",
		"unit": "",
		"role": "category",
		"domain": None,
		"description": "Digital input state from GPIO pins aligned to frame clock (stimulus markers).",
	},
	"FrameID": {
		"label": "Frame ID",
		"tags": ["BASE"],
		"type": "int",
		"unit": "frame",
		"role": "value",
		"domain": None,
		"description": "Camera frame counter ticks aligned to frame clock (may not start at 0).",
	},
	"Timestamp": {
		"label": "Timestamp",
		"tags": ["BASE"],
		"type": "int",
		"unit": "ns",
		"role": "value",
		"domain": None,
		"description": "Acquisition device tick count in nanoseconds; strictly monotonic, not wall-clock Unix time.",
	},
}


#%% CELL 04 — SHARED INDEX & STIMULI
"""
SHARED
	Signals shared across multiple files (single source of truth):
	- FrameIndex: global per-frame reference aligned to BASE frame number.
	- Stimuli channels: names/labels aligned with experiment.py::STIMULI.
"""

SHARED: dict[str, ParamSpec] = {
	"FrameIndex": {
		"label": "FrameIndex",
		"tags": ["tracked", "sleap", "pose", "scored"],
		"type": "int",
		"unit": "frame",
		"role": "value",
		"domain": None,
		"description": "Reference aligned to BASE frames; not a local 0..N counter.",
	},
	"VisualStim": {
		"label": "VisualStim",
		"tags": ["tracked", "scored", "stimuli"],
		"type": "int",
		"unit": "",
		"role": "binary",
		"domain": [0, 1],
		"description": "Visual stimulus on/off per frame.",
	},
	"Stim0": {
		"label": "RedLED",
		"tags": ["tracked", "scored", "stimuli"],
		"type": "int",
		"unit": "",
		"role": "binary",
		"domain": [0, 1],
		"description": "Red LED stimulus on/off per frame.",
	},
	"Stim1": {
		"label": "GreenLED",
		"tags": ["tracked", "scored", "stimuli"],
		"type": "int",
		"unit": "",
		"role": "binary",
		"domain": [0, 1],
		"description": "Green LED stimulus on/off per frame.",
	},
}


#%% CELL 05 — TRACKED
"""
TRACKED
	Columns from tracked.csv. Provide normalized centroid location (0–1) and a
	per-frame motion proxy from pixel-change counts. These feed scored features.
"""

TRACKED: dict[str, ParamSpec] = {
	"NormalizedCentroidX": {
		"label": "Normalized Centroid X",
		"tags": ["tracked"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Centroid X normalized to arena width (0–1).",
	},
	"NormalizedCentroidY": {
		"label": "Normalized Centroid Y",
		"tags": ["tracked"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Centroid Y normalized to arena height (0–1).",
	},
	"PixelChange": {
		"label": "Pixel Change",
		"tags": ["tracked"],
		"type": "int",
		"unit": "px",
		"role": "value",
		"domain": None,
		"description": "Count of changed pixels between consecutive frames (motion proxy).",
	},
}


#%% CELL 06 — SCORED
"""
SCORED
	Derived kinematics and multi-layer classifier labels from scored.csv.
	Categorical domains are written in canonical order inline. Content preserved.
"""

SCORED: dict[str, ParamSpec] = {
	"Position_X": {
		"label": "Position X",
		"tags": ["scored"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Centroid X position (mm) in arena coordinates.",
	},
	"Position_Y": {
		"label": "Position Y",
		"tags": ["scored"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Centroid Y position (mm) in arena coordinates.",
	},
	"Speed": {
		"label": "Speed",
		"tags": ["scored"],
		"type": "float",
		"unit": "mm/s",
		"role": "value",
		"domain": None,
		"description": "Instantaneous centroid speed (mm/s).",
	},
	"Motion": {
		"label": "Motion",
		"tags": ["scored"],
		"type": "int",
		"unit": "",
		"role": "binary",
		"domain": [0, 1],
		"description": "Binary motion flag from PixelChange (1 = motion).",
	},

	# Layered labels
	"Layer1": {
		"label": "Layer 1",
		"tags": ["scored"],
		"type": "str",
		"unit": "",
		"role": "category",
		"domain": ["Layer1_Jump", "Layer1_Walk", "Layer1_Stationary", "Layer1_Freeze"],
		"description": "First-pass classifier label per frame.",
	},
	"Layer1_Denoised": {
		"label": "Layer 1 (Denoised)",
		"tags": ["scored"],
		"type": "str",
		"unit": "",
		"role": "category",
		"domain": ["Layer1_Jump", "Layer1_Walk", "Layer1_Stationary", "Layer1_Freeze"],
		"description": "Layer1 with micro-bouts removed (jump preserved).",
	},
	"Layer2": {
		"label": "Layer 2",
		"tags": ["scored"],
		"type": "str",
		"unit": "",
		"role": "category",
		"domain": ["Layer2_Jump", "Layer2_Walk", "Layer2_Stationary", "Layer2_Freeze"],
		"description": "Windowed consensus over Layer1 (jump override).",
	},
	"Layer2_Denoised": {
		"label": "Layer 2 (Denoised)",
		"tags": ["scored"],
		"type": "str",
		"unit": "",
		"role": "category",
		"domain": ["Layer2_Jump", "Layer2_Walk", "Layer2_Stationary", "Layer2_Freeze"],
		"description": "Consensus over Layer1_Denoised with half-missing rule.",
	},

	# Resistant tiers
	"Resistant": {
		"label": "Resistant",
		"tags": ["scored"],
		"type": "str",
		"unit": "",
		"role": "category",
		"domain": ["Resistant_Walk", "Resistant_Stationary", "Resistant_Freeze"],
		"description": "Summary when a full bout covers a startle window.",
	},
	"Resistant_Denoised": {
		"label": "Resistant (Denoised)",
		"tags": ["scored"],
		"type": "str",
		"unit": "",
		"role": "category",
		"domain": ["Resistant_Walk", "Resistant_Stationary", "Resistant_Freeze"],
		"description": "Resistant summary using denoised paths.",
	},

	# Behavior labels
	"Behavior": {
		"label": "Behavior",
		"tags": ["scored"],
		"type": "str",
		"unit": "",
		"role": "category",
		"domain": ["Jump", "Walk", "Stationary", "Freeze", "Resistant_Freeze"],
		"description": "Behavior mapped from Layer2; Freeze may promote to Resistant_Freeze.",
	},
	"Behavior_Denoised": {
		"label": "Behavior (Denoised)",
		"tags": ["scored"],
		"type": "str",
		"unit": "",
		"role": "category",
		"domain": ["Jump", "Walk", "Stationary", "Freeze", "Resistant_Freeze"],
		"description": "Behavior from Layer2_Denoised",
	},
}


#%% CELL 07 — SLEAP
"""
SLEAP
	Normalized view/body-part positions and confidences from sleap.csv.
	Views listed first (Left, Right, Top), followed by body parts
	(Head, Thorax, Abdomen, LeftWing, RightWing).
"""

SLEAP: dict[str, ParamSpec] = {
	# View positions (normalized)
	"Left.Position.X": {
		"label": "Left View X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the left camera view.",
	},
	"Left.Position.Y": {
		"label": "Left View Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the left camera view.",
	},
	"Left.Confidence": {
		"label": "Left View Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the left view.",
	},

	"Right.Position.X": {
		"label": "Right View X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the right camera view.",
	},
	"Right.Position.Y": {
		"label": "Right View Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the right camera view.",
	},
	"Right.Confidence": {
		"label": "Right View Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the right view.",
	},

	"Top.Position.X": {
		"label": "Top View X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the top view.",
	},
	"Top.Position.Y": {
		"label": "Top View Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the top view.",
	},
	"Top.Confidence": {
		"label": "Top View Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the top view.",
	},

	# Body parts (normalized)
	"Head.Position.X": {
		"label": "Head X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the head keypoint.",
	},
	"Head.Position.Y": {
		"label": "Head Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the head keypoint.",
	},
	"Head.Confidence": {
		"label": "Head Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the head keypoint.",
	},

	"Thorax.Position.X": {
		"label": "Thorax X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the thorax keypoint.",
	},
	"Thorax.Position.Y": {
		"label": "Thorax Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the thorax keypoint.",
	},
	"Thorax.Confidence": {
		"label": "Thorax Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the thorax keypoint.",
	},

	"Abdomen.Position.X": {
		"label": "Abdomen X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the abdomen keypoint.",
	},
	"Abdomen.Position.Y": {
		"label": "Abdomen Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the abdomen keypoint.",
	},
	"Abdomen.Confidence": {
		"label": "Abdomen Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the abdomen keypoint.",
	},

	"LeftWing.Position.X": {
		"label": "Left Wing X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the left wing keypoint.",
	},
	"LeftWing.Position.Y": {
		"label": "Left Wing Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the left wing keypoint.",
	},
	"LeftWing.Confidence": {
		"label": "Left Wing Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the left wing keypoint.",
	},

	"RightWing.Position.X": {
		"label": "Right Wing X",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized X coordinate of the right wing keypoint.",
	},
	"RightWing.Position.Y": {
		"label": "Right Wing Y",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Normalized Y coordinate of the right wing keypoint.",
	},
	"RightWing.Confidence": {
		"label": "Right Wing Confidence",
		"tags": ["sleap"],
		"type": "float",
		"unit": "",
		"role": "value",
		"domain": [0.0, 1.0],
		"description": "Detection confidence score for the right wing keypoint.",
	},
}


#%% CELL 08 — POSE
"""
POSE
	Arena-calibrated positions in mm and orientation from pose.csv.
	Starts with selected view and orientation, followed by body-part positions
	in the order: Head, Thorax, Abdomen, LeftWing, RightWing.
"""

POSE: dict[str, ParamSpec] = {
	"View": {
		"label": "View",
		"tags": ["pose"],
		"type": "str",
		"unit": "",
		"role": "category",
		"domain": ["Left", "Right", "Top", "Vertical"],
		"description": "Selected camera view label (Bottom→Top normalized).",
	},
	"View_X": {
		"label": "View X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "X coordinate (mm) in the selected view, post-calibration.",
	},
	"View_Y": {
		"label": "View Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Y coordinate (mm) in the selected view, post-calibration.",
	},
	"Orientation": {
		"label": "Orientation",
		"tags": ["pose"],
		"type": "float",
		"unit": "deg",
		"role": "value",
		"domain": [0.0, 360.0],
		"description": "Body orientation (deg) from Thorax→View axis; 0–360 wrap.",
	},

	# Per-part positions in the selected view (mm)
	"Head_X": {
		"label": "Head X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Head keypoint X (mm) in the selected view.",
	},
	"Head_Y": {
		"label": "Head Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Head keypoint Y (mm) in the selected view.",
	},
	"Thorax_X": {
		"label": "Thorax X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Thorax keypoint X (mm) in the selected view.",
	},
	"Thorax_Y": {
		"label": "Thorax Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Thorax keypoint Y (mm) in the selected view.",
	},
	"Abdomen_X": {
		"label": "Abdomen X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Abdomen keypoint X (mm) in the selected view.",
	},
	"Abdomen_Y": {
		"label": "Abdomen Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Abdomen keypoint Y (mm) in the selected view.",
	},
	"LeftWing_X": {
		"label": "Left Wing X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Left wing keypoint X (mm) in the selected view.",
	},
	"LeftWing_Y": {
		"label": "Left Wing Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Left wing keypoint Y (mm) in the selected view.",
	},
	"RightWing_X": {
		"label": "Right Wing X",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Right wing keypoint X (mm) in the selected view.",
	},
	"RightWing_Y": {
		"label": "Right Wing Y",
		"tags": ["pose"],
		"type": "float",
		"unit": "mm",
		"role": "value",
		"domain": None,
		"description": "Right wing keypoint Y (mm) in the selected view.",
	},
}


#%% CELL 09 — ASSEMBLY & PUBLIC API
"""
Assembly & Public API
	Validate all per-section registries and assemble the immutable PARAM bundle.
	Pure in-memory checks; no I/O. Raises on first inconsistency.
"""

# VALIDATION HELPERS

def _assert_subset(name: str, vals: list[str], allowed: set[str]) -> None:
	"""
	Check that vals are a subset of allowed. Raise with a precise message on first hit.

	Args:
		name: Field name for error context (e.g., "tags", "role").
		vals: Values to validate.
		allowed: Allowed set for that field.

	Raises:
		ValueError: If any value is not in the allowed set.
	"""
	for v in vals:
		if v not in allowed:
			raise ValueError(f"Invalid {name!s} value: {v!r}. Allowed: {sorted(allowed)!r}")


def _is_number(x: object) -> bool:
	"""Return True if x is an int or float (bools excluded)."""
	return isinstance(x, (int, float)) and not isinstance(x, bool)


def _validate_domain(entry: ParamSpec) -> None:
	"""
	Validate the domain field according to role.

	Raises:
		ValueError: On malformed numeric range, binary, or categorical domains.
	"""
	role = entry["role"]
	domain = entry["domain"]

	# None means unconstrained (explicit choice in this registry).
	# Allow empty list only as explicit "no constraint" (discouraged but allowed).
	if domain is None or domain == []:
		return

	# Binary role: must be exactly [0, 1] (ints).
	if role == "binary":
		if not isinstance(domain, list) or len(domain) != 2:
			raise ValueError(f"Binary domain must be [0, 1], got: {domain!r}")
		if domain != [0, 1]:
			raise ValueError(f"Binary domain must be exactly [0, 1], got: {domain!r}")
		return

	# Numeric range: [min, max] with min <= max, numbers only.
	if (
		isinstance(domain, list)
		and len(domain) == 2
		and all(_is_number(e) for e in domain)
	):
		min_v, max_v = domain
		if min_v > max_v:
			raise ValueError(f"Numeric domain min>max: {domain!r}")
		return

	# Categorical: non-empty list of unique literals.
	if isinstance(domain, list) and len(domain) > 0:
		seen = set()
		for val in domain:
			if val in seen:
				raise ValueError(f"Duplicate value in categorical domain: {val!r}")
			seen.add(val)
		return

	raise ValueError(f"Malformed domain for {entry.get('label', '<unknown>')!r}: {domain!r}")


def _validate_entry(name: str, entry: ParamSpec) -> None:
	"""
	Validate a single ParamSpec entry against the global allowed sets.

	Raises:
		ValueError: If any field violates the policy.
	"""
	label = entry["label"]
	if not isinstance(label, str) or not label:
		raise ValueError(f"Empty label for key {name!r}")

	_assert_subset("tags", entry["tags"], ALLOWED_TAGS)
	_assert_subset("type", [entry["type"]], ALLOWED_TYPES)
	_assert_subset("role", [entry["role"]], ALLOWED_ROLES)
	if entry["unit"] != "":
		_assert_subset("unit", [entry["unit"]], ALLOWED_UNITS)

	_validate_domain(entry)


def _merge_sections(
	sections: list[tuple[str, dict[str, ParamSpec]]]
) -> dict[str, ParamSpec]:
	"""
	Merge section registries, enforcing no duplicate keys and valid entries.

	Args:
		sections: List of (title, registry) section pairs.

	Returns:
		Merged mapping of all entries.

	Raises:
		ValueError: On duplicate keys or invalid entries.
	"""
	merged: dict[str, ParamSpec] = {}
	seen: set[str] = set()

	for title, reg in sections:
		if not isinstance(reg, dict):
			raise ValueError(f"Section {title!r} is not a dict.")
		for key, spec in reg.items():
			if key in seen:
				raise ValueError(f"Duplicate key across sections: {key!r} (in {title})")
			_validate_entry(key, spec)
			merged[key] = spec
			seen.add(key)

	return merged


# PUBLIC SURFACE

_SECTIONS: list[tuple[str, dict[str, ParamSpec]]] = [
	("BASE", BASE),
	("SHARED", SHARED),
	("TRACKED", TRACKED),
	("SCORED", SCORED),
	("SLEAP", SLEAP),
	("POSE", POSE),
]

_PARAM: dict[str, ParamSpec] = _merge_sections(_SECTIONS)
PARAM: Mapping[str, ParamSpec] = MappingProxyType(_PARAM)
__all__ = ["PARAM"]


#%% CELL 10 — REPORT
"""
REPORT
	Compact summary when running this file directly.
	Lists the total number of parameters and names grouped by section.

Notes:
	This report performs no validation or I/O; it simply prints a human-readable overview
	of the PARAM registry. Run this module directly (e.g., `python param_temp.py`) to
	see the summary in your console.
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


