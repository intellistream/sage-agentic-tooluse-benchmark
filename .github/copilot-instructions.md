# SAGE Benchmark Agent - GitHub Copilot Instructions

## Project Overview

**SAGE Benchmark Agent** is a configuration-driven experiment framework for evaluating agent capabilities through three core experiments:

1. **Tool Selection** - Tool retrieval and ranking evaluation
2. **Planning** - Multi-step planning with tool composition  
3. **Timing Detection** - Timing judgment for tool invocation decisions

**Architecture**: Layer L5 (Applications - Benchmarking)
**Dependencies**: sage.libs (for agent interfaces), sage.common (L1)

## Repository Structure

```
sage-benchmark-agent/
├── src/sage/benchmark/benchmark_agent/
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   ├── acebench_loader.py       # ACE Bench data loader
│   ├── adapter_registry.py      # Agent adapter registry
│   ├── data_paths.py            # Data path management
│   ├── tools_loader.py          # Tool loading utilities
│   ├── config/                  # Experiment configurations
│   │   ├── config_loader.py
│   │   ├── default_config.yaml
│   │   ├── tool_selection_exp.yaml
│   │   ├── planning_exp.yaml
│   │   └── timing_detection_exp.yaml
│   ├── evaluation/              # Evaluation framework
│   │   ├── evaluator.py
│   │   ├── metrics.py
│   │   ├── report_builder.py
│   │   └── unified_tool_selection.py
│   ├── experiments/             # Experiment implementations
│   │   ├── base_experiment.py
│   │   ├── tool_selection_exp.py
│   │   ├── planning_exp.py
│   │   └── timing_detection_exp.py
│   └── scripts/                 # Utility scripts
├── tests/                       # Test suite
│   ├── conftest.py
│   ├── test_evaluation.py
│   ├── test_experiments.py
│   └── ...
├── .github/
│   ├── copilot-instructions.md  # This file
│   └── workflows/
│       ├── ci.yml
│       └── publish.yml
├── pyproject.toml
└── README.md
```

## Core Concepts

### 1. Experiment Framework

All experiments follow the standard lifecycle pattern:

```python
class BaseExperiment:
    """Base class for all benchmark experiments."""
    
    def prepare(self) -> None:
        """Prepare experiment (load data, initialize models)."""
        pass
    
    def run(self) -> ExperimentResult:
        """Run experiment and return results."""
        pass
    
    def finalize(self) -> None:
        """Clean up resources."""
        pass
```

### 2. Configuration System

- **YAML-based**: All experiments configured via YAML files
- **Environment Variables**: Support `${VAR:default}` substitution
- **Pydantic Validation**: Config models use Pydantic for validation
- **Hierarchical**: Configs can inherit from `default_config.yaml`

Example config structure:
```yaml
experiment:
  name: "tool_selection_benchmark"
  type: "tool_selection"
  output_dir: "${SAGE_OUTPUT_DIR:./output}"

data:
  source: "acebench"
  split: "test"
  max_samples: 100

model:
  name: "gpt-4"
  temperature: 0.0
  max_tokens: 2048

evaluation:
  metrics:
    - "precision@k"
    - "recall@k"
    - "ndcg@k"
    - "mrr"
```

### 3. Agent Adapters

The system supports different agent implementations through adapters:

- **ReactPlanner**: ReAct-style planning agents
- **ToolSelectionAgent**: Specialized tool selection agents
- **CustomAgent**: User-defined agent implementations

Adapters registered in `adapter_registry.py`:
```python
from sage.benchmark.benchmark_agent.adapter_registry import register_adapter

@register_adapter("my_agent")
class MyAgentAdapter:
    def __init__(self, config: dict):
        self.config = config
    
    def select_tools(self, query: str, tools: list) -> list:
        """Select tools for the given query."""
        pass
```

### 4. Evaluation Metrics

Core metrics for agent evaluation:

- **Tool Selection**:
  - Precision@k, Recall@k
  - NDCG@k (Normalized Discounted Cumulative Gain)
  - MRR (Mean Reciprocal Rank)
  
- **Planning**:
  - Plan accuracy
  - Step efficiency
  - Tool composition quality
  
- **Timing Detection**:
  - Decision accuracy
  - False positive/negative rates

## Coding Guidelines

### 1. Python Style

- **Python Version**: 3.11+
- **Type Hints**: Required for all public APIs
- **Docstrings**: Google style for all modules, classes, functions
- **Formatting**: Black (line length 100)
- **Linting**: Ruff
- **Testing**: pytest with >80% coverage

Example:
```python
"""Experiment module for tool selection benchmarks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel


class ExperimentConfig(BaseModel):
    """Configuration for tool selection experiment.
    
    Attributes:
        name: Experiment name
        output_dir: Directory to save results
        max_samples: Maximum number of samples to evaluate
    """
    name: str
    output_dir: Path
    max_samples: int = 100


def run_experiment(config: ExperimentConfig) -> dict[str, float]:
    """Run tool selection experiment.
    
    Args:
        config: Experiment configuration
        
    Returns:
        Dictionary mapping metric names to values
        
    Raises:
        ValueError: If configuration is invalid
        FileNotFoundError: If data files not found
    """
    # Implementation
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
git clone https://github.com/intellistream/sage-benchmark-agent.git
git clone https://github.com/intellistream/sage-agentic.git

# Install in editable mode
cd sage-benchmark-agent
pip install -e ".[dev]"

cd ../sage-agentic
pip install -e .

# Or use VS Code workspace to work with multiple repos
code sage-benchmark-agent.code-workspace
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

When helping with sage-benchmark-agent:

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
