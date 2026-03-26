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

from dyco_repair.envs import load_issue
from dyco_repair.runner import run_episode
from dyco_repair.runtime import query_gpus, select_best_gpu


def maybe_warmup_gpu(auto_gpu: bool) -> dict:
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

    try:
        import torch
    except ImportError:
        runtime_info["gpu_mode"] = "torch_missing"
        return runtime_info

    if not torch.cuda.is_available():
        runtime_info["gpu_mode"] = "cuda_unavailable"
        return runtime_info

    device = torch.device("cuda:0")
    a = torch.randn(512, 512, device=device)
    b = torch.randn(512, 512, device=device)
    c = a @ b
    runtime_info["gpu_warmup"] = {
        "device_name": torch.cuda.get_device_name(device),
        "mean": float(c.mean().item()),
        "memory_allocated_mb": round(torch.cuda.max_memory_allocated(device) / (1024 * 1024), 2),
    }
    return runtime_info


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the end-to-end code-repair pipeline.")
    parser.add_argument("--env", default="mock", choices=["mock", "swebench-lite"], help="Task source type.")
    parser.add_argument("--task", required=True, help="Path to a task file. For swebench-lite this can be a JSON/JSONL file.")
    parser.add_argument("--task-id", default=None, help="Optional task identifier when the task file contains multiple records.")
    parser.add_argument("--output-dir", default="outputs/pipeline-run", help="Directory for trajectory and summary output.")
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--auto-gpu", action="store_true", help="Auto-detect and warm up the best available GPU.")
    parser.add_argument("--policy", default="heuristic", help="Orchestrator policy name.")
    args = parser.parse_args()

    issue = load_issue(args.env, args.task, task_id=args.task_id)
    runtime_info = maybe_warmup_gpu(args.auto_gpu)
    state, _, summary = run_episode(
        issue,
        output_dir=args.output_dir,
        max_steps=args.max_steps,
        policy_name=args.policy,
    )

    runtime_path = Path(args.output_dir) / "runtime.json"
    runtime_path.parent.mkdir(parents=True, exist_ok=True)
    with runtime_path.open("w", encoding="utf-8") as handle:
        json.dump(runtime_info, handle, indent=2)

    payload = {
        "issue_id": state.issue_id,
        "runtime": runtime_info,
        "summary": summary,
    }
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
