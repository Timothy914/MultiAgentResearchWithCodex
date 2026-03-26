from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dyco_repair.envs import load_issues
from dyco_repair.runner import run_episode
from dyco_repair.runtime import query_gpus, select_best_gpu


def maybe_select_gpu(auto_gpu: bool) -> dict:
    runtime_info: dict = {"gpu_mode": "cpu"}
    if not auto_gpu:
        return runtime_info
    selected_gpu = select_best_gpu(query_gpus(), max_memory_used_mib=2048, max_utilization=10)
    if selected_gpu is None:
        runtime_info["gpu_mode"] = "no_gpu_found"
        return runtime_info
    os.environ["CUDA_VISIBLE_DEVICES"] = str(selected_gpu.index)
    runtime_info["gpu_mode"] = "selected"
    runtime_info["selected_gpu"] = selected_gpu.to_dict()
    return runtime_info


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect rollouts from a task file and save a JSONL summary.")
    parser.add_argument("--env", default="mock", choices=["mock", "swebench-lite"])
    parser.add_argument("--tasks", required=True, help="Path to the task source.")
    parser.add_argument("--output-dir", default="outputs/rollouts")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--policy", default="heuristic")
    parser.add_argument("--auto-gpu", action="store_true")
    args = parser.parse_args()

    runtime_info = maybe_select_gpu(args.auto_gpu)
    issues = load_issues(args.env, args.tasks, limit=args.limit)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    dataset_path = output_root / "policy_dataset.jsonl"
    aggregate_path = output_root / "aggregate_summary.json"

    aggregate = {
        "env": args.env,
        "policy": args.policy,
        "runtime": runtime_info,
        "num_tasks": len(issues),
        "resolved": 0,
        "stopped": 0,
        "summaries": [],
    }

    with dataset_path.open("w", encoding="utf-8") as handle:
        for issue in issues:
            issue_dir = output_root / issue.issue_id
            state, transitions, summary = run_episode(
                issue,
                output_dir=issue_dir,
                max_steps=args.max_steps,
                policy_name=args.policy,
            )
            record = {
                "issue_id": issue.issue_id,
                "summary": summary,
                "transitions": [transition.to_dict() for transition in transitions],
                "metadata": getattr(issue, "metadata", {}),
            }
            handle.write(json.dumps(record) + "\n")
            aggregate["summaries"].append({"issue_id": issue.issue_id, **summary})
            if state.tests_passed:
                aggregate["resolved"] += 1
            else:
                aggregate["stopped"] += 1

    with aggregate_path.open("w", encoding="utf-8") as handle:
        json.dump(aggregate, handle, indent=2)

    print(json.dumps({"aggregate_summary": aggregate_path.as_posix(), "policy_dataset": dataset_path.as_posix(), **aggregate}, indent=2))


if __name__ == "__main__":
    main()

