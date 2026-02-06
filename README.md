# SAGE Tool Use Benchmark

Configuration-driven experiment framework for evaluating tool selection and use capabilities.

## Features

- **Tool Selection Evaluation**: Tool retrieval and ranking benchmarks
- **Planning Evaluation**: Multi-step planning with tool composition
- **Timing Detection**: Timing judgment for tool invocation decisions

## Quick Start

```bash
# Install
pip install isage-tooluse-benchmark

# Run tool selection experiment
sage-tooluse-bench tool-selection --config config/tool_selection_exp.yaml

# Run planning experiment
sage-tooluse-bench planning --config config/planning_exp.yaml
```

## Documentation

See [benchmark_agent/README.md](src/sage/benchmark/benchmark_agent/README.md) for detailed documentation.

## Development

```bash
# Clone
git clone https://github.com/intellistream/sage-tooluse-benchmark.git
cd sage-tooluse-benchmark

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License - see [LICENSE](LICENSE) for details.
