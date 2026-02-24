---
name: sage-agent-tooluse-benchmark
description: Agent for tool-use benchmark experiments, configs, and evaluation updates.
argument-hint: Include target experiment/evaluator file, behavior change, and validation criteria.
tools:
  [
    "vscode",
    "execute",
    "read",
    "agent",
    "edit",
    "search",
    "web",
    "todo",
    "vscode.mermaid-chat-features/renderMermaidDiagram",
    "github.vscode-pull-request-github/issue_fetch",
    "github.vscode-pull-request-github/suggest-fix",
    "github.vscode-pull-request-github/searchSyntax",
    "github.vscode-pull-request-github/doSearch",
    "github.vscode-pull-request-github/renderIssues",
    "github.vscode-pull-request-github/activePullRequest",
    "github.vscode-pull-request-github/openPullRequest",
    "ms-azuretools.vscode-containers/containerToolsConfig",
    "ms-python.python/getPythonEnvironmentInfo",
    "ms-python.python/getPythonExecutableCommand",
    "ms-python.python/installPythonPackage",
    "ms-python.python/configurePythonEnvironment",
    "ms-toolsai.jupyter/configureNotebook",
    "ms-toolsai.jupyter/listNotebookPackages",
    "ms-toolsai.jupyter/installNotebookPackages",
    "ms-vscode.cpp-devtools/Build_CMakeTools",
    "ms-vscode.cpp-devtools/RunCtest_CMakeTools",
    "ms-vscode.cpp-devtools/ListBuildTargets_CMakeTools",
    "ms-vscode.cpp-devtools/ListTests_CMakeTools",
  ]
---

# Sage Agent Tooluse Benchmark Agent

## Focus

- Benchmark experiment logic in `experiments/`
- Evaluation/reporting in `evaluation/`
- Config validation in `config/`

## Rules

- Keep Python 3.11+ typed APIs.
- Do not create new local virtual environments (`venv`/`.venv`); use the existing configured Python environment.
- Preserve lifecycle: `prepare()` → `run()` → `finalize()`.
- Use centralized dataset/path utilities; no hardcoded paths.
- Avoid L4+ runtime dependencies and hidden fallback behavior.

## Workflow

1. Implement minimal change in benchmark logic/config.
2. Update tests in `tests/` for new behavior.
3. Keep CLI behavior stable unless explicitly requested.
