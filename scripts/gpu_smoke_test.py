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

from dyco_repair.runtime import query_gpus, select_best_gpu


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a tiny GPU smoke test on an idle CUDA device.")
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--auto", action="store_true", help="Auto-select an available GPU with the lowest memory usage.")
    args = parser.parse_args()

    selected_device = args.device
    selected_gpu = None
    if args.auto:
        selected_gpu = select_best_gpu(query_gpus(), max_memory_used_mib=2048, max_utilization=10)
        if selected_gpu is None:
            print(json.dumps({"ok": False, "reason": "no_gpu_found"}))
            return 1
        selected_device = selected_gpu.index
        os.environ["CUDA_VISIBLE_DEVICES"] = str(selected_device)

    try:
        import torch
    except ImportError:
        print(json.dumps({"ok": False, "reason": "torch_not_installed"}))
        return 1

    if not torch.cuda.is_available():
        print(json.dumps({"ok": False, "reason": "cuda_unavailable"}))
        return 1

    device = torch.device("cuda:0" if args.auto else f"cuda:{selected_device}")
    a = torch.randn(1024, 1024, device=device)
    b = torch.randn(1024, 1024, device=device)
    c = a @ b
    result = {
        "ok": True,
        "device": selected_device,
        "name": torch.cuda.get_device_name(device),
        "mean": float(c.mean().item()),
        "memory_allocated_mb": round(torch.cuda.max_memory_allocated(device) / (1024 * 1024), 2),
    }
    if selected_gpu is not None:
        result["selected_gpu"] = selected_gpu.to_dict()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
