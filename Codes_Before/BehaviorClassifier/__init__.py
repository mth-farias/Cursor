#%%% CELL 00 — PACKAGE OVERVIEW
"""
{{COMMIT_DETAILS}}
# <github.com/MoitaLab/Repo>
# <full_commit_hash>
# <DD-MM-YYYY HH:MM:SS>

BehaviorClassifier/__init__.py

Purpose
    Provide clean, lazy accessors for the package public surfaces so notebooks can:
        from BehaviorClassifier import BC_COLAB, BC_MAIN, BC_QC, BC_UTILS
    without importing heavy modules too early or freezing PATH at import time.

Exports
    BC_COLAB  → Colab/staging adapter (Mixed mode, batch sync)
    BC_MAIN   → Orchestrator (runs the full behavior classification session)
    BC_QC     → QC/flags/errors public surface
    BC_UTILS  → Shared mechanics/helpers surface

Usage (Colab, Mixed mode)
    # Import the staging adapter early:
    from BehaviorClassifier import BC_COLAB

    # ... build RUNTIME_PATH via BC_COLAB, flip Config.PATH, reload modules ...

    # Import the runner AFTER flipping/reloading so it binds to Mixed PATH:
    from BehaviorClassifier import BC_MAIN
    result = BC_MAIN["behavior_classifier_main"]()

Notes
    - Lazy exports via __getattr__ (PEP 562): submodules load only when requested.
    - Works with your Mixed PATH flow: import BC_COLAB early; import BC_MAIN after flip.
    - Public surfaces are MappingProxyType dicts defined in the respective modules.
"""

#%%% CELL 01 — PUBLIC SURFACE (LAZY EXPORTS, NO SIDE EFFECTS)
__all__ = ("BC_COLAB", "BC_MAIN", "BC_QC", "BC_UTILS", "BC_CLASSIFIER")

def __getattr__(name: str):
    if name == "BC_COLAB":
        from ._colab import BC_COLAB
        return BC_COLAB

    if name == "BC_MAIN":
        from ._main import BC_MAIN
        return BC_MAIN

    if name == "BC_QC":
        from ._qc_error_flag import BC_QC
        return BC_QC

    if name == "BC_UTILS":
        from ._utils import BC_UTILS
        return BC_UTILS

    if name == "BC_CLASSIFIER":                 # ← add this
        from ._classifier import BC_CLASSIFIER
        return BC_CLASSIFIER

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")



def __dir__():
    # Nice autocomplete surface
    return sorted(set(globals().keys()) | set(__all__))
