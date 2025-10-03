# Duck Development Starter Prompt

Goal: continue Duck development seamlessly in any agent/chat.

## About Duck (short):
- Duck is a portable, project-agnostic AI dev assistant in `.duck/`.
- Python 3.11+. CLI: `python .duck/duck.py` (or `duck` after `pip install -e .duck`).
- Package layout: `duck/core/` (system, validation, patterns, env), `duck/tools/`, `duck/cli/`.
- Docs: `.duck/docs/` (quickstart, guides, reports, MetaAgentPlan archive).

## Repo context:
- Duck lives under `.duck/`; project code under `Codes/`, etc.
- Use `duck/core/env.py` helpers for paths (no hard-coded `../.cursor`).

## How to continue now:
1) Load context:
   - `.duck/docs/README.md`, `.duck/pyproject.toml`
   - `.duck/duck/cli/commands.py`
   - `.duck/duck/core/{system.py,validation.py,patterns.py,env.py}`

2) Standards:
   - Python 3.11+
   - Package-relative imports only
   - Update docs for new features under `.duck/docs/`

3) Run (if available):
   - `python .duck/duck.py status`
   - Optional: `pip install -e .duck` then `duck status`

## Open tasks (examples):
- Add guides in `.duck/docs/guides/`
- Expand validation in `duck/core/validation.py`
- Add power-user CLI commands in `duck/cli/commands.py`

---

**You are the agent continuing Duck development. Confirm understanding and propose the next 1–3 concrete steps.**
