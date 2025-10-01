'''
{{COMMIT_DETAILS}}
#<github.com/MoitaLab/Repo>
#<full_commit_hash>
#<DD-MM-YYYY HH:MM:SS>

__init__.py

Config package: canonical registries for the experiment pipeline.

Exports
    PATH       → canonical folder map and helpers
    PARAM      → parameter registry
    EXPERIMENT → experiment facts and timing
    COLOR      → color palettes and colormaps

Usage
    from Config import PATH, PARAM, EXPERIMENT, COLOR

Notes
    - All bundles are MappingProxyType: read-only, safe to share.
    - Each submodule is still importable directly if deeper access is needed.
'''

from .path import PATH
from .param import PARAM
from .experiment import EXPERIMENT
from .color import COLOR

__all__ = ["PATH", "PARAM", "EXPERIMENT", "COLOR"]
