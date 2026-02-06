# SAGE Benchmark Agent

Configuration-driven experiment framework for evaluating agent capabilities.

## Features

- **Tool Selection Evaluation**: Tool retrieval and ranking benchmarks
- **Planning Evaluation**: Multi-step planning with tool composition
- **Timing Detection**: Timing judgment for tool invocation decisions

## Quick Start

```bash
# Install
pip install isage-benchmark-agent

# Run tool selection experiment
sage-agent-bench tool-selection --config config/tool_selection_exp.yaml

# Run planning experiment
sage-agent-bench planning --config config/planning_exp.yaml
```

## Documentation

See [benchmark_agent/README.md](src/sage/benchmark/benchmark_agent/README.md) for detailed documentation.

## Development

```bash
# Clone
git clone https://github.com/intellistream/sage-agent-benchmark.git
cd sage-agent-benchmark

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
