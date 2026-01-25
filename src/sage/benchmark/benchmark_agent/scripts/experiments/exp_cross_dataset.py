#!/usr/bin/env python3
"""
Section 5.4: Cross-Dataset Generalization

验证方法在不同数据集上的泛化能力。

数据集:
- SAGE-Bench (ours): 内部基准
- ACE-Bench: 外部工具选择数据集
- ToolBench: Qin et al. 工具选择
- API-Bank: API 调用数据集
- BFCL: Gorilla Function Calling

输出:
- figures/fig9_generalization_cross_dataset.pdf
- tables/table_cross_dataset_results.tex

Usage:
    python exp_cross_dataset.py
    python exp_cross_dataset.py --datasets sage,acebench
    python exp_cross_dataset.py --strategies keyword,embedding,hybrid
"""

from __future__ import annotations

import argparse
from typing import Any, Optional

from .exp_utils import (
    get_figures_dir,
    load_benchmark_data,
    print_section_header,
    print_subsection_header,
    save_results,
    setup_experiment_env,
)

# =============================================================================
# Dataset Configuration
# =============================================================================

DATASETS = {
    "sage": {
        "name": "SAGE-Bench",
        "source": "internal",
        "challenge": "selection",
        "loader": "load_benchmark_data",
    },
    "acebench": {
        "name": "ACE-Bench",
        "source": "external",
        "path": "acebench",
        "loader": "load_acebench_data",
    },
    "toolbench": {
        "name": "ToolBench",
        "source": "external",
        "path": "toolbench",
        "loader": "load_toolbench_data",
    },
    "apibank": {
        "name": "API-Bank",
        "source": "external",
        "path": "apibank",
        "loader": "load_apibank_data",
    },
    "bfcl": {
        "name": "BFCL",
        "source": "external",
        "path": "bfcl",
        "loader": "load_bfcl_data",
    },
}

DEFAULT_STRATEGIES = [
    "selector.keyword",
    "selector.embedding",
    "selector.hybrid",
]


# =============================================================================
# Data Loaders
# =============================================================================


def load_dataset(dataset_id: str, max_samples: int = 100) -> list[dict]:
    """
    加载指定数据集。

    Args:
        dataset_id: 数据集 ID
        max_samples: 最大样本数

    Returns:
        标准化的样本列表
    """
    if dataset_id not in DATASETS:
        print(f"  ⚠️  Unknown dataset: {dataset_id}")
        return []

    DATASETS[dataset_id]

    if dataset_id == "sage":
        return load_benchmark_data("selection", split="test", max_samples=max_samples)

    elif dataset_id == "acebench":
        return _load_acebench_data(max_samples)

    elif dataset_id == "toolbench":
        return _load_toolbench_data(max_samples)

    elif dataset_id == "apibank":
        return _load_apibank_data(max_samples)

    elif dataset_id == "bfcl":
        return _load_bfcl_data(max_samples)

    return []


def _load_acebench_data(max_samples: int) -> list[dict]:
    """加载 ACE-Bench 数据。"""
    # TODO: 实现实际的 ACE-Bench 加载
    # 这里返回模拟数据结构
    try:
        from sage.benchmark.benchmark_agent.acebench_loader import load_acebench_samples

        samples = load_acebench_samples(max_samples=max_samples)
        # 标准化字段
        return [
            {
                "instruction": s.get("query", s.get("instruction", "")),
                "candidate_tools": s.get("tools", s.get("candidate_tools", [])),
                "ground_truth": s.get("expected", s.get("ground_truth", [])),
            }
            for s in samples
        ]
    except ImportError:
        print("  ⚠️  ACE-Bench loader not available")
        return []


def _load_toolbench_data(max_samples: int) -> list[dict]:
    """加载 ToolBench 数据。"""
    # TODO: 实现实际的 ToolBench 加载
    print("  ⚠️  ToolBench loader not implemented")
    return []


def _load_apibank_data(max_samples: int) -> list[dict]:
    """加载 API-Bank 数据。"""
    # TODO: 实现实际的 API-Bank 加载
    print("  ⚠️  API-Bank loader not implemented")
    return []


def _load_bfcl_data(max_samples: int) -> list[dict]:
    """加载 BFCL 数据。"""
    # TODO: 实现实际的 BFCL 加载
    print("  ⚠️  BFCL loader not implemented")
    return []


# =============================================================================
# Evaluation
# =============================================================================


def evaluate_on_dataset(
    strategy_name: str,
    samples: list[dict],
    top_k: int = 5,
    verbose: bool = True,
) -> dict[str, float]:
    """
    在单个数据集上评估策略。

    Returns:
        {metric: value}
    """
    if not samples:
        return {"top_k_accuracy": 0.0, "mrr": 0.0}

    try:
        from sage.benchmark.benchmark_agent import get_adapter_registry

        registry = get_adapter_registry()
        selector = registry.get(strategy_name)
    except Exception as e:
        if verbose:
            print(f"      ⚠️  Failed to create selector: {e}")
        return {"top_k_accuracy": 0.0, "mrr": 0.0}

    hits = 0
    rr_sum = 0.0

    for sample in samples:
        query = sample.get("instruction", "")
        candidate_tools = sample.get("candidate_tools", [])
        ground_truth = sample.get("ground_truth", [])

        try:
            preds = selector.select(query, candidate_tools=candidate_tools, top_k=top_k)
            pred_ids = (
                [p.tool_id if hasattr(p, "tool_id") else str(p) for p in preds] if preds else []
            )

            ref_set = set(ground_truth) if isinstance(ground_truth, list) else {ground_truth}

            # Top-K accuracy
            if set(pred_ids[:top_k]) & ref_set:
                hits += 1

            # MRR
            for i, p in enumerate(pred_ids):
                if p in ref_set:
                    rr_sum += 1.0 / (i + 1)
                    break

        except Exception:
            pass

    n = len(samples)
    return {
        "top_k_accuracy": hits / n if n > 0 else 0.0,
        "mrr": rr_sum / n if n > 0 else 0.0,
    }


# =============================================================================
# Main Experiment
# =============================================================================


def run_cross_dataset_evaluation(
    datasets: Optional[list[str]] = None,
    strategies: Optional[list[str]] = None,
    max_samples: int = 100,
    top_k: int = 5,
    verbose: bool = True,
) -> dict[str, dict[str, dict[str, float]]]:
    """
    运行跨数据集评估。

    Args:
        datasets: 要测试的数据集列表
        strategies: 要测试的策略列表
        max_samples: 每个数据集的最大样本数
        top_k: Top-K 参数
        verbose: 是否打印详细信息

    Returns:
        {strategy: {dataset: {metric: value}}}
    """
    setup_experiment_env(verbose=verbose)

    print_section_header("Section 5.4: Cross-Dataset Generalization")

    if datasets is None:
        datasets = ["sage", "acebench"]  # 默认只测试可用的

    if strategies is None:
        strategies = DEFAULT_STRATEGIES

    print(f"   Datasets: {datasets}")
    print(f"   Strategies: {[s.split('.')[-1] for s in strategies]}")
    print(f"   Max samples per dataset: {max_samples}")

    all_results: dict[str, dict[str, dict[str, float]]] = {}

    for strategy_name in strategies:
        strategy_short = strategy_name.split(".")[-1]
        print_subsection_header(f"Strategy: {strategy_short}")

        all_results[strategy_name] = {}

        for dataset_id in datasets:
            dataset_config = DATASETS.get(dataset_id, {})
            dataset_name = dataset_config.get("name", dataset_id)

            print(f"\n      Dataset: {dataset_name}")

            # 加载数据
            samples = load_dataset(dataset_id, max_samples=max_samples)

            if not samples:
                print("        No data available")
                all_results[strategy_name][dataset_id] = {"top_k_accuracy": 0.0, "mrr": 0.0}
                continue

            print(f"        Samples: {len(samples)}")

            # 评估
            metrics = evaluate_on_dataset(strategy_name, samples, top_k=top_k, verbose=verbose)
            all_results[strategy_name][dataset_id] = metrics

            if verbose:
                print(f"        Top-{top_k} Accuracy: {metrics['top_k_accuracy'] * 100:.1f}%")
                print(f"        MRR: {metrics['mrr'] * 100:.1f}%")

    # 保存结果
    output_file = save_results(all_results, "5_4_generalization", "cross_dataset")
    print(f"\n  Results saved to: {output_file}")

    # 生成图表
    _generate_cross_dataset_figures(all_results, datasets, top_k)

    # 打印汇总表
    _print_summary_table(all_results, datasets)

    return all_results


def _generate_cross_dataset_figures(results: dict, datasets: list[str], top_k: int) -> None:
    """生成跨数据集对比图表。"""
    try:
        from figure_generator import plot_cross_dataset_comparison

        figures_dir = get_figures_dir()

        # 转换数据格式
        plot_data = {}
        for strategy, dataset_results in results.items():
            strategy_short = strategy.split(".")[-1]
            plot_data[strategy_short] = {
                d: dataset_results.get(d, {}).get("top_k_accuracy", 0) for d in datasets
            }

        plot_cross_dataset_comparison(
            plot_data,
            metric=f"top_{top_k}_accuracy",
            output_path=figures_dir / "fig9_generalization_cross_dataset.pdf",
        )
        print("  Figure saved: fig9_generalization_cross_dataset.pdf")

    except Exception as e:
        print(f"  Warning: Could not generate figures: {e}")


def _print_summary_table(results: dict, datasets: list[str]) -> None:
    """打印汇总表格。"""
    print("\n" + "=" * 70)
    print("  Cross-Dataset Generalization Summary")
    print("=" * 70)

    # 表头
    header = f"{'Strategy':15s}"
    for d in datasets:
        header += f" | {DATASETS.get(d, {}).get('name', d):12s}"
    print(header)
    print("-" * 70)

    # 每个策略一行
    for strategy, dataset_results in results.items():
        strategy_short = strategy.split(".")[-1]
        row = f"{strategy_short:15s}"
        for d in datasets:
            acc = dataset_results.get(d, {}).get("top_k_accuracy", 0)
            row += f" | {acc * 100:10.1f}%"
        print(row)

    print("-" * 70)

    # 计算泛化得分 (跨数据集方差的倒数)
    print("\n  Generalization Scores (lower variance = better):")
    for strategy, dataset_results in results.items():
        strategy_short = strategy.split(".")[-1]
        accs = [dataset_results.get(d, {}).get("top_k_accuracy", 0) for d in datasets]
        if accs:
            mean_acc = sum(accs) / len(accs)
            variance = sum((a - mean_acc) ** 2 for a in accs) / len(accs)
            print(f"    {strategy_short:12s}: mean={mean_acc * 100:.1f}%, var={variance * 100:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Section 5.4: Cross-Dataset Generalization")
    parser.add_argument(
        "--datasets", type=str, default="sage,acebench", help="Comma-separated dataset IDs"
    )
    parser.add_argument(
        "--strategies", type=str, default=None, help="Comma-separated strategy names"
    )
    parser.add_argument("--max-samples", type=int, default=100, help="Maximum samples per dataset")
    parser.add_argument("--top-k", type=int, default=5, help="Top-K parameter")
    parser.add_argument("--verbose", action="store_true", default=True, help="Verbose output")
    args = parser.parse_args()

    datasets = args.datasets.split(",") if args.datasets else None
    strategies = args.strategies.split(",") if args.strategies else None

    run_cross_dataset_evaluation(
        datasets=datasets,
        strategies=strategies,
        max_samples=args.max_samples,
        top_k=args.top_k,
        verbose=args.verbose,
    )

    print("\n" + "=" * 70)
    print("📊 Cross-Dataset Evaluation Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
