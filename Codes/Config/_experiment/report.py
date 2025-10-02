#%% CELL 00 — HEADER & OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/YourLab/Repo>
# <commit_hash>
# <DD-MM-YYYY HH:MM:SS>

Config/_experiment/report.py

Overview
	Report generation functions for the experiment configuration.
	Provides human-readable summaries of the EXPERIMENT bundle for
	quick inspection and debugging.

Functions
	- render_experiment_report: Print comprehensive experiment summary
	- format_period_info: Format period details for display
	- format_stimulus_info: Format stimulus details for display

Exports
	_REPORT → MappingProxyType bundle with report functions
"""

#%% CELL 01 — IMPORTS

from __future__ import annotations

from types import MappingProxyType

#%% CELL 02 — REPORT FUNCTIONS

def render_experiment_report(experiment_bundle: MappingProxyType) -> None:
    """
    Human-readable summary of the EXPERIMENT bundle.
    Prints key sections for quick inspection.
    
    Args:
        experiment_bundle: Complete EXPERIMENT bundle to summarize
    """
    print("=== EXPERIMENT SUMMARY ===\n")
    
    print("Noise tolerance:", experiment_bundle["NOISE_TOLERANCE"], "frames")
    print("Frame rate:", experiment_bundle["FRAME_RATE"], "fps")
    print(
        "Arena:",
        experiment_bundle["ARENA_WIDTH_MM"],
        "x",
        experiment_bundle["ARENA_HEIGHT_MM"],
        "mm",
    )
    
    print("\n-- Periods --")
    for name in experiment_bundle["PERIOD_ORDER"]:
        spec = experiment_bundle["PERIODS_DERIVED"][name]
        start_f = spec["start_frame"]
        end_f = spec["end_frame_exclusive"] - 1  # inclusive display
        print(
            f"{name:12s} "
            f"{spec['duration_sec']:.1f} s "
            f"({spec['duration_frames']} frames), "
            f"frames {start_f}–{end_f}"
        )
    
    print(
        "\nTotal experiment:",
        experiment_bundle["EXPERIMENT_TOTAL_SECONDS"],
        "s",
        f"({experiment_bundle['EXPERIMENT_TOTAL_FRAMES']} frames)",
    )
    
    print("\n-- Stimuli --")
    for label, spec in experiment_bundle["STIMULI_DERIVED"].items():
        dur_sec = spec["duration_sec"]
        dur_str = f"{dur_sec:.2f} s" if dur_sec is not None else "variable"
        print(
            f"{label:12s} "
            f"trials={spec['trials']} "
            f"dur={dur_str} "
            f"ignore={spec['ignore']}"
        )

def format_period_info(period_name: str, period_spec: dict) -> str:
    """Format period information for display."""
    start_f = period_spec["start_frame"]
    end_f = period_spec["end_frame_exclusive"] - 1  # inclusive display
    return (
        f"{period_name:12s} "
        f"{period_spec['duration_sec']:.1f} s "
        f"({period_spec['duration_frames']} frames), "
        f"frames {start_f}–{end_f}"
    )

def format_stimulus_info(stimulus_name: str, stimulus_spec: dict) -> str:
    """Format stimulus information for display."""
    dur_sec = stimulus_spec["duration_sec"]
    dur_str = f"{dur_sec:.2f} s" if dur_sec is not None else "variable"
    return (
        f"{stimulus_name:12s} "
        f"trials={stimulus_spec['trials']} "
        f"dur={dur_str} "
        f"ignore={stimulus_spec['ignore']}"
    )

#%% CELL 03 — PUBLIC API

_PUBLIC = {
    "render_experiment_report": render_experiment_report,
    "format_period_info": format_period_info,
    "format_stimulus_info": format_stimulus_info,
}

_REPORT = MappingProxyType(_PUBLIC)
