# SAGE Agent Tooluse Benchmark Copilot Instructions

## Scope

- Standalone benchmark app for agent evaluation (L5 benchmark layer).
- Focus areas: tool selection, planning, timing detection.

## Critical rules

- Keep Python 3.11+ compatibility and typed public APIs.
- Do not create new local virtual environments (`venv`/`.venv`); use the existing configured Python environment.
- Use Pydantic for config validation.
- Follow experiment lifecycle: `prepare()` → `run()` → `finalize()`.
- Use centralized dataset/path handling (`data_paths.py`, `DataManager`), not hardcoded paths.
- Avoid L4+ runtime dependencies and keep benchmark constants centralized.

## Workflow

1. Update experiment/config/evaluation code consistently.
2. Preserve CLI behavior in `__main__.py` unless explicitly requested.
3. Add or update tests in `tests/` for new logic.

## Key paths

- `experiments/`, `evaluation/`, `adapter_registry.py`, `data_paths.py`, `config/`.
