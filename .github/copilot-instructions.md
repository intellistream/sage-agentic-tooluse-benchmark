# SAGE Benchmark Agent - Copilot Instructions

## Project Summary

This repo is the standalone benchmark for agent algorithm evaluation. It contains the
experiment framework, configs, and evaluation logic for:

1. Tool selection
2. Task planning
3. Timing detection

**Layer**: L5 (Applications - Benchmarking)
**Dependencies**: isage-common (L1), isage-libs (agent interfaces)

## Key Architecture

- Entry point: `sage.benchmark.benchmark_agent.__main__`
- Core configs: `experiments/base_experiment.py`
- Experiment impls: `experiments/{tool_selection,planning,timing_detection}_exp.py`
- Evaluation: `evaluation/` (metrics, evaluator, report builder)
- Registry: `adapter_registry.py` (maps strategy names to adapters)
- Data paths: `data_paths.py` + `DATA_PATHS.md`

## Non-Negotiables

- Use Pydantic models for config validation.
- Follow prepare/run/finalize lifecycle in experiments.
- Keep code compatible with Python 3.11+.
- Prefer centralized paths via `data_paths.py` and `DataManager`.
- Preserve CLI behavior in `__main__.py`.

## Config Schema (Actual)

- `experiment` is a literal: `tool_selection | planning | timing_detection`.
- Common fields are in `ExperimentConfig`.
- Specific fields exist in:
    - `ToolSelectionConfig`
    - `PlanningConfig`
    - `TimingDetectionConfig`

If adding new config fields, update the relevant Pydantic model and defaults.

## Adapter Registry Rules

- Strategy names are string keys resolved in `adapter_registry.py`.
- Adapters must expose `predict()` and conform to the internal protocols.
- Keep benchmark constants (e.g., embedding model, temperature) centralized.

## Coding Style

- Type hints on all public APIs.
- Google-style docstrings.
- Format with Black (line length 100) and lint with Ruff.
- Avoid breaking public import paths in `__init__.py`.

## Testing Expectations

- Add or update tests under `tests/` for new logic.
- Prefer deterministic outputs; seed is already in config.
- If you add metrics, add unit tests for edge cases.

## What Not To Do

- Do not import L4+ middleware packages.
- Do not bypass `DataManager` for data sources.
- Do not hardcode data paths or model names in experiment classes.
- Do not change CLI flags without updating docs and tests.

## Typical Workflows

- CLI:
    - `sage-agent-bench --config config/tool_selection_exp.yaml`
- Programmatic:
    - load config via `ConfigLoader`
    - instantiate experiment and call `prepare()`, `run()`, `finalize()`
    pass
```

### 2. Configuration Pattern

Always use Pydantic models for config validation:

```python
from pydantic import BaseModel, Field, field_validator


class ModelConfig(BaseModel):
    """LLM model configuration."""
    
    name: str = Field(description="Model name")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, gt=0)
    
    @field_validator("name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate model name."""
        allowed_models = ["gpt-4", "gpt-3.5-turbo", "claude-3"]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of {allowed_models}")
        return v
```

### 3. Data Loading

Use the centralized `data_paths.py` for all data paths:

```python
from sage.benchmark.benchmark_agent.data_paths import get_data_path

# Get ACE Bench data
acebench_path = get_data_path("acebench", "test")

# Get tool descriptions
tools_path = get_data_path("tools", "descriptions")
```

### 4. Error Handling

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def load_experiment_data(path: Path) -> Optional[dict]:
    """Load experiment data with proper error handling.
    
    Args:
        path: Path to data file
        
    Returns:
        Loaded data or None if loading fails
    """
    if not path.exists():
        logger.error(f"Data file not found: {path}")
        raise FileNotFoundError(f"Missing data file: {path}")
    
    try:
        data = yaml.safe_load(path.read_text())
        logger.info(f"Loaded {len(data)} samples from {path}")
        return data
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML: {e}")
        raise ValueError(f"Invalid YAML in {path}") from e
```

### 5. Testing

```python
import pytest
from sage.benchmark.benchmark_agent.experiments import ToolSelectionExperiment


@pytest.fixture
def sample_config():
    """Provide sample experiment config."""
    return {
        "experiment": {"name": "test", "output_dir": "/tmp"},
        "model": {"name": "gpt-4", "temperature": 0.0},
        "evaluation": {"metrics": ["precision@5"]},
    }


def test_tool_selection_experiment(sample_config):
    """Test basic tool selection experiment."""
    exp = ToolSelectionExperiment(sample_config)
    exp.prepare()
    
    result = exp.run()
    
    assert "precision@5" in result.metrics
    assert result.metrics["precision@5"] >= 0.0
    assert result.metrics["precision@5"] <= 1.0
    
    exp.finalize()


@pytest.mark.slow
def test_full_benchmark_pipeline(sample_config):
    """Test complete benchmark pipeline (slow test)."""
    # Full integration test
    pass
```

## CLI Usage

The package provides a CLI entry point:

```bash
# Tool selection experiment
sage-agent-bench tool-selection --config config/tool_selection_exp.yaml

# Planning experiment
sage-agent-bench planning --config config/planning_exp.yaml --verbose

# Timing detection experiment  
sage-agent-bench timing --config config/timing_detection_exp.yaml --output results/

# Custom config
sage-agent-bench tool-selection --config my_config.yaml
```

Or use as Python module:
```bash
python -m sage.benchmark.benchmark_agent --config config/tool_selection_exp.yaml
```

## Common Tasks

### Adding a New Experiment Type

1. Create experiment class in `experiments/`
2. Inherit from `BaseExperiment`
3. Implement `prepare()`, `run()`, `finalize()`
4. Add config schema
5. Register in `__main__.py` CLI
6. Add tests
7. Update documentation

### Adding a New Metric

1. Implement metric function in `evaluation/metrics.py`
2. Add to relevant evaluator class
3. Update config schema to include metric
4. Add tests for metric calculation
5. Document metric in README

### Adding a New Agent Adapter

1. Create adapter class
2. Implement required methods
3. Register in `adapter_registry.py`
4. Add tests
5. Document usage

### Working with New Datasets

1. Add data loader in appropriate module
2. Update `data_paths.py` if needed
3. Add data documentation to `DATA_PATHS.md`
4. Include sample data in tests
5. Update experiment configs

## Integration with SAGE Ecosystem

### Dependencies

This package depends on:
- **sage.common**: Configuration utilities, path management
- **sage.libs** (optional): Agent interface definitions

### Usage in Other Projects

```python
# Install package
pip install isage-benchmark-agent

# Use in code
from sage.benchmark.benchmark_agent import ToolSelectionExperiment
from sage.benchmark.benchmark_agent.evaluation import calculate_metrics

# Run experiment
config = load_config("config.yaml")
exp = ToolSelectionExperiment(config)
results = exp.run()

# Calculate metrics
metrics = calculate_metrics(results.predictions, results.ground_truth)
```

### Development Setup

For local development with other SAGE packages:

```bash
# Clone repos
git clone https://github.com/intellistream/sage-agent-benchmark.git
git clone https://github.com/intellistream/sage-agentic.git

# Install in editable mode
cd sage-agent-benchmark
pip install -e ".[dev]"

cd ../sage-agentic
pip install -e .

# Or use VS Code workspace to work with multiple repos
code sage-agent-benchmark.code-workspace
```

## Performance Considerations

- **Batch Processing**: Process samples in batches for efficiency
- **Caching**: Cache model outputs and embeddings
- **Async Operations**: Use async for I/O-bound operations
- **Resource Management**: Clean up in `finalize()` methods
- **Progress Tracking**: Use `rich.progress` for long-running tasks

## CI/CD

- **Tests**: Automated testing on PR (pytest)
- **Linting**: Black, Ruff checks
- **Type Checking**: mypy validation
- **Coverage**: Codecov integration
- **Publishing**: Automated PyPI release on tags

## Tips for Copilot

When helping with sage-agent-benchmark:

1. **Experiment Pattern**: Always follow prepare/run/finalize lifecycle
2. **Config-Driven**: Use YAML configs with Pydantic validation
3. **Type Hints**: All public APIs need type annotations
4. **Testing**: Include tests for new functionality
5. **Documentation**: Update README and docstrings
6. **Error Handling**: Validate inputs, provide clear errors
7. **Logging**: Use proper logging levels
8. **CLI Consistency**: Follow existing CLI patterns with typer
9. **Metrics**: Document metric calculations clearly
10. **Integration**: Consider usage with sage.libs agents

## Version Information

- **Package**: isage-benchmark-agent
- **Python**: 3.11+
- **License**: MIT
- **Maintainer**: IntelliStream Team

---

*Last Updated: January 2026*
