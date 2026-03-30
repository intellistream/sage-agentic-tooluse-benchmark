# SAGE Agent Bench 实验脚本

本目录包含 `sage-agentic-tooluse-benchmark` 的实验脚本与统一 CLI 入口，覆盖：

- Paper 1：Benchmark 主评测与分析
- Paper 2：SAGE-Agent 训练方法对比与消融

## 目录结构

```text
scripts/
├── sage-agent-bench                      # CLI 入口脚本
├── README.md                             # 本文档
└── experiments/
    ├── exp_utils.py                      # 环境、数据、结果保存工具
    ├── figure_generator.py               # 图表生成
    ├── table_generator.py                # 表格生成
    ├── llm_service.py                    # 本地 LLM 服务管理（sageLLM）
    ├── exp_main_timing.py                # Section 5.2.1
    ├── exp_main_planning.py              # Section 5.2.2
    ├── exp_main_selection.py             # Section 5.2.3
    ├── exp_analysis_error.py             # Section 5.3.1
    ├── exp_analysis_scaling.py           # Section 5.3.2
    ├── exp_analysis_robustness.py        # Section 5.3.3
    ├── exp_analysis_ablation.py          # Section 5.3.4
    ├── exp_cross_dataset.py              # Section 5.4
    ├── exp_training_comparison.py        # Section 5.5
    └── run_paper1_experiments.py         # Paper 1 全流程入口
```

## 快速开始

### 1) 环境准备

```bash
cd /path/to/SAGE
./quickstart.sh --dev --yes
export SAGE_TEST_MODE=true
```

### 2) 使用 CLI

```bash
# 查看帮助
./sage-agent-bench --help

# LLM 服务管理（sageLLM）
./sage-agent-bench llm status
./sage-agent-bench llm start --model Qwen/Qwen2.5-7B-Instruct --port 8901
./sage-agent-bench llm stop

# 运行实验
./sage-agent-bench run --section 5.2
./sage-agent-bench run --section 5.3
./sage-agent-bench run --all
./sage-agent-bench run --quick

# 资源列表
./sage-agent-bench list datasets
./sage-agent-bench list methods
./sage-agent-bench list experiments
```

### 3) Python API

```python
from sage.benchmark.benchmark_agent.scripts.experiments import exp_main_timing
from sage.benchmark.benchmark_agent.scripts.experiments import run_paper1_experiments

exp_main_timing.main()
run_paper1_experiments.main(sections=["5.2", "5.3", "5.4", "5.5"])
```

## 论文章节映射

| 章节 | 脚本 | 说明 |
| --- | --- | --- |
| 5.2.1 | `exp_main_timing.py` | 工具调用时机评测 |
| 5.2.2 | `exp_main_planning.py` | 任务规划能力评测 |
| 5.2.3 | `exp_main_selection.py` | 工具选择准确率评测 |
| 5.3.1 | `exp_analysis_error.py` | 错误类型分析 |
| 5.3.2 | `exp_analysis_scaling.py` | 扩展性分析 |
| 5.3.3 | `exp_analysis_robustness.py` | 鲁棒性分析 |
| 5.3.4 | `exp_analysis_ablation.py` | 消融实验 |
| 5.4 | `exp_cross_dataset.py` | 跨数据集泛化 |
| 5.5 | `exp_training_comparison.py` | 训练方法对比 |

## LLM 服务约定

- 默认端口：`SagePorts.BENCHMARK_LLM`（通常是 `8901`）
- 默认模型：`Qwen/Qwen2.5-0.5B-Instruct`
- 推荐通过 `sage llm` 或 `sage-agent-bench llm` 管理服务
- 云端模式可通过 `SAGE_CHAT_API_KEY`、`SAGE_CHAT_BASE_URL`、`SAGE_CHAT_MODEL` 配置

## 输出目录

实验结果默认输出到 `.sage/benchmark/paper1/`，常见结构：

```text
.sage/benchmark/paper1/
├── section_5_2_main/
├── section_5_3_analysis/
├── section_5_4_generalization/
├── section_5_5_training/
├── figures/
└── tables/
```

## 故障排查

```bash
# 端口占用
lsof -i :8901

# GPU 状态
nvidia-smi

# LLM 服务状态
./sage-agent-bench llm status
```

如需最小化资源占用，建议使用更小模型（如 `Qwen/Qwen2.5-0.5B-Instruct`）。
