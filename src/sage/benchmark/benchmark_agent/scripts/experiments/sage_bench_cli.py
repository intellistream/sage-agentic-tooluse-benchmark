#!/usr/bin/env python3
"""
SAGE Agent Bench CLI - Agent 能力评测命令行入口

这是 SAGE Agent Benchmark 的官方入口，用于评测 Agent 工具调用能力。

Usage:
    sage-agent-bench <command> [options]

Commands:
    run         运行完整 Benchmark 实验
    eval        工具选择评测 (跨数据集)
    train       训练方法对比
    llm         LLM 服务管理
    list        列出可用资源

Examples:
    # 运行完整 benchmark
    sage-agent-bench run --quick
    sage-agent-bench run --section 5.2
    sage-agent-bench run --exp timing

    # 工具选择评测
    sage-agent-bench eval --dataset sage --samples 100
    sage-agent-bench eval --dataset acebench

    # 训练方法对比
    sage-agent-bench train --methods A_baseline,D_combined
    sage-agent-bench train --dry-run

    # LLM 服务管理
    sage-agent-bench llm status
    sage-agent-bench llm start
    sage-agent-bench llm stop

    # 列出资源
    sage-agent-bench list datasets
    sage-agent-bench list methods
    sage-agent-bench list experiments
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 获取脚本目录
SCRIPT_DIR = Path(__file__).resolve().parent

# 添加路径
sys.path.insert(0, str(SCRIPT_DIR.parent.parent.parent.parent))
sys.path.insert(0, str(SCRIPT_DIR / "experiments"))


# =============================================================================
# 子命令处理
# =============================================================================


def cmd_run(args):
    """运行 Benchmark 实验"""
    from experiments.run_paper1_experiments import main as run_main

    # 构建等效的 argparse args
    sys.argv = ["run_paper1_experiments.py"]

    if args.section:
        sys.argv.extend(["--section", args.section])
    if args.exp:
        sys.argv.extend(["--exp", args.exp])
    if args.quick:
        sys.argv.append("--quick")
    if args.skip_llm:
        sys.argv.append("--skip-llm")
    if args.generate_paper:
        sys.argv.append("--generate-paper")
    if args.output:
        sys.argv.extend(["--output-dir", args.output])

    run_main()
    return 0


def cmd_eval(args):
    """工具选择评测"""
    from experiments.exp_cross_dataset import run_cross_dataset_evaluation
    from experiments.exp_main_selection import run_selection_experiment
    from experiments.exp_utils import setup_experiment_env

    setup_experiment_env()

    if args.dataset == "all":
        # 跨数据集评测
        result = run_cross_dataset_evaluation(
            datasets=["sage", "acebench"],
            max_samples=args.samples,
            verbose=True,
        )
    else:
        # 单数据集评测
        result = run_selection_experiment(
            max_samples=args.samples,
            top_k=args.top_k,
            skip_llm=False,
            verbose=True,
        )

    return 0 if result else 1


def cmd_train(args):
    """训练方法对比"""
    from experiments.exp_training_comparison import run_training_comparison

    methods = args.methods.split(",") if args.methods else ["A_baseline", "D_combined"]

    run_training_comparison(
        methods=methods,
        base_model=args.model,
        quick=args.quick,
        dry_run=args.dry_run,
        verbose=True,
    )
    return 0


def cmd_llm(args):
    """LLM 服务管理"""
    from experiments.llm_service import (
        print_llm_status,
        start_llm_service,
        stop_llm_service,
    )

    if args.llm_action == "status":
        print_llm_status()
        return 0

    elif args.llm_action == "start":
        success = start_llm_service(
            model=args.model,
            port=args.port,
            gpu_memory=args.gpu_memory,
        )
        return 0 if success else 1

    elif args.llm_action == "stop":
        success = stop_llm_service()
        return 0 if success else 1

    return 0


def cmd_list(args):
    """列出可用资源"""
    if args.resource == "datasets":
        print("\n" + "=" * 70)
        print("Available Datasets for Tool Selection Evaluation")
        print("=" * 70)
        print()
        print(f"{'Dataset':<15} {'Description':<50} {'Status'}")
        print("-" * 70)

        datasets = [
            ("sage", "SAGE Agent Bench (1200 synthetic tools)", "Built-in"),
            ("acebench", "ToolACE from HuggingFace", "HuggingFace"),
            ("apibank", "API-Bank (Microsoft/Alibaba)", "External"),
            ("toolalpaca", "ToolAlpaca (Microsoft)", "External"),
            ("bfcl", "BFCL (Berkeley Function Calling)", "External"),
            ("toolbench", "ToolBench (Tsinghua/OpenBMB)", "External"),
            ("all", "Evaluate on ALL datasets", "-"),
        ]
        for name, desc, status in datasets:
            print(f"{name:<15} {desc:<50} {status}")
        print()
        return 0

    elif args.resource == "methods":
        print("\n" + "=" * 70)
        print("Available Methods")
        print("=" * 70)

        print("\n📋 Timing Detection Methods (RQ1):")
        print("-" * 50)
        timing_methods = [
            ("rule_based", "Keyword + Regex rules", "Classic"),
            ("embedding", "Semantic similarity", "Common"),
            ("llm_based", "Direct LLM inference", "LLM"),
            ("hybrid", "Rule filter + LLM judge", "Combined"),
        ]
        for name, desc, source in timing_methods:
            print(f"  {name:<15} {desc:<35} {source}")

        print("\n📋 Task Planning Methods (RQ2):")
        print("-" * 50)
        planning_methods = [
            ("simple", "Greedy matching", "Classic"),
            ("hierarchical", "HuggingGPT-style decomposition", "ICML'23"),
            ("llm_based", "CoT prompting", "Common"),
            ("react", "ReAct interleaved execution", "ICLR'23"),
            ("tot", "Tree-of-Thoughts search", "NeurIPS'23"),
        ]
        for name, desc, source in planning_methods:
            print(f"  {name:<15} {desc:<35} {source}")

        print("\n📋 Tool Selection Methods (RQ3):")
        print("-" * 50)
        methods = [
            ("keyword", "BM25 keyword matching", "Classic"),
            ("embedding", "Semantic embedding similarity", "Common"),
            ("hybrid", "Keyword + Embedding fusion", "Common"),
            ("gorilla", "Retrieval + LLM reranking", "Berkeley"),
            ("dfsdt", "Tree search (ToolLLM)", "Tsinghua"),
        ]
        for name, desc, source in methods:
            print(f"  {name:<15} {desc:<35} {source}")

        print("\n📋 Training Methods (Section 5.5):")
        print("-" * 50)
        print("  Paper 1 (Benchmark) - Published SOTA:")
        paper1_methods = [
            ("A_baseline", "Standard SFT (full parameters)"),
            ("A_lora", "LoRA (Hu et al., 2021)"),
            ("A_qlora", "QLoRA (Dettmers et al., 2023)"),
            ("A_dora", "DoRA (Liu et al., 2024)"),
            ("A_fireact", "FireAct trajectory tuning"),
            ("A_agenttuning", "AgentTuning multi-task"),
            ("A_toolllm", "ToolLLM tool-augmented"),
        ]
        for name, desc in paper1_methods:
            print(f"    {name:<20} {desc}")

        print("\n  Paper 2 (SIAS) - from sage.libs.sias:")
        sias_methods = [
            ("B1_coreset_loss", "[SIAS] Select high-loss samples"),
            ("B2_coreset_diversity", "[SIAS] Select diverse samples"),
            ("B3_coreset_hybrid", "[SIAS] 60% loss + 40% diversity"),
            ("C_continual", "[SIAS] Online learning with replay"),
            ("D_combined", "[SIAS] Coreset + Continual Learning"),
        ]
        for name, desc in sias_methods:
            print(f"    {name:<20} {desc}")
        print()
        return 0

    elif args.resource == "experiments":
        print("\n" + "=" * 70)
        print("Available Experiments (Paper 1: Benchmark)")
        print("=" * 70)

        print("\n📊 Section 5.2: Main Results")
        print("-" * 50)
        experiments = [
            ("timing", "RQ1: Timing Detection", "~10 min"),
            ("planning", "RQ2: Task Planning", "~15 min"),
            ("selection", "RQ3: Tool Selection", "~20 min"),
        ]
        for exp_id, name, time_est in experiments:
            print(f"  {exp_id:<20} {name:<30} {time_est}")

        print("\n🔬 Section 5.3: Analysis")
        print("-" * 50)
        experiments = [
            ("error", "Error Type Breakdown", "~5 min"),
            ("scaling", "Scaling Analysis", "~15 min"),
            ("robustness", "Robustness Analysis", "~10 min"),
            ("ablation", "Ablation Studies", "~10 min"),
        ]
        for exp_id, name, time_est in experiments:
            print(f"  {exp_id:<20} {name:<30} {time_est}")

        print("\n🌐 Section 5.4: Generalization")
        print("-" * 50)
        print(f"  {'cross-dataset':<20} {'Cross-Dataset Comparison':<30} ~30 min")

        print("\n🎓 Section 5.5: Training Comparison")
        print("-" * 50)
        print(f"  {'training':<20} {'Training Method Comparison':<30} ~2 hours")
        print()
        return 0

    return 1


# =============================================================================
# 主入口
# =============================================================================


def print_banner():
    print(
        """
╔═══════════════════════════════════════════════════════════════════════════╗
║                     SAGE Agent Bench CLI v3.0                             ║
║                                                                           ║
║  Unified benchmark for evaluating Agent tool-calling capabilities         ║
║  Paper 1: Agent Capability Evaluation Framework                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
    )


def main():
    parser = argparse.ArgumentParser(
        prog="sage-agent-bench",
        description="SAGE Agent Bench CLI - Agent 能力评测命令行入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    sage-agent-bench run --quick            # 快速运行完整 Benchmark
    sage-agent-bench eval --dataset all     # 跨数据集评测
    sage-agent-bench train --dry-run        # 模拟训练对比
    sage-agent-bench llm start              # 启动 LLM 服务
    sage-agent-bench list experiments       # 列出可用实验
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # =========================================================================
    # run 子命令
    # =========================================================================
    run_parser = subparsers.add_parser("run", help="运行 Benchmark 实验")
    run_parser.add_argument(
        "--section",
        choices=["5.2", "5.3", "5.4", "5.5", "all"],
        default="all",
        help="运行指定章节",
    )
    run_parser.add_argument(
        "--exp",
        choices=[
            "timing",
            "planning",
            "selection",
            "error",
            "scaling",
            "robustness",
            "ablation",
            "cross-dataset",
            "training",
            "all",
        ],
        help="运行指定实验",
    )
    run_parser.add_argument("--quick", "-q", action="store_true", help="快速模式")
    run_parser.add_argument("--skip-llm", action="store_true", help="跳过 LLM 方法")
    run_parser.add_argument("--generate-paper", action="store_true", help="生成论文材料")
    run_parser.add_argument("--output", "-o", type=str, help="输出目录")
    run_parser.set_defaults(func=cmd_run)

    # =========================================================================
    # eval 子命令
    # =========================================================================
    eval_parser = subparsers.add_parser("eval", help="工具选择评测")
    eval_parser.add_argument(
        "--dataset",
        "-d",
        default="sage",
        choices=["sage", "acebench", "apibank", "toolalpaca", "bfcl", "all"],
        help="评测数据集",
    )
    eval_parser.add_argument("--samples", "-n", type=int, default=100, help="最大样本数")
    eval_parser.add_argument("--top-k", "-k", type=int, default=5, help="Top-K 评测")
    eval_parser.set_defaults(func=cmd_eval)

    # =========================================================================
    # train 子命令
    # =========================================================================
    train_parser = subparsers.add_parser("train", help="训练方法对比")
    train_parser.add_argument(
        "--methods",
        "-m",
        default="A_baseline,D_combined",
        help="训练方法，逗号分隔",
    )
    train_parser.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct", help="基础模型")
    train_parser.add_argument("--quick", "-q", action="store_true", help="快速模式")
    train_parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    train_parser.set_defaults(func=cmd_train)

    # =========================================================================
    # llm 子命令
    # =========================================================================
    llm_parser = subparsers.add_parser("llm", help="LLM 服务管理")
    llm_parser.add_argument(
        "llm_action",
        choices=["start", "stop", "status"],
        help="操作: start/stop/status",
    )
    llm_parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct", help="LLM 模型")
    llm_parser.add_argument("--port", type=int, default=8901, help="端口")
    llm_parser.add_argument("--gpu-memory", type=float, default=0.5, help="GPU 显存比例")
    llm_parser.set_defaults(func=cmd_llm)

    # =========================================================================
    # list 子命令
    # =========================================================================
    list_parser = subparsers.add_parser("list", help="列出可用资源")
    list_parser.add_argument(
        "resource",
        choices=["datasets", "methods", "experiments"],
        help="资源类型",
    )
    list_parser.set_defaults(func=cmd_list)

    # =========================================================================
    # 解析并执行
    # =========================================================================
    args = parser.parse_args()

    if args.command is None:
        print_banner()
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
