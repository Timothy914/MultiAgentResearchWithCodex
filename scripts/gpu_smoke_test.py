from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a tiny GPU smoke test on an idle CUDA device.")
    parser.add_argument("--device", type=int, default=0)
    args = parser.parse_args()

    try:
        import torch
    except ImportError:
        print(json.dumps({"ok": False, "reason": "torch_not_installed"}))
        return 1

    if not torch.cuda.is_available():
        print(json.dumps({"ok": False, "reason": "cuda_unavailable"}))
        return 1

    device = torch.device(f"cuda:{args.device}")
    a = torch.randn(1024, 1024, device=device)
    b = torch.randn(1024, 1024, device=device)
    c = a @ b
    result = {
        "ok": True,
        "device": args.device,
        "name": torch.cuda.get_device_name(device),
        "mean": float(c.mean().item()),
        "memory_allocated_mb": round(torch.cuda.max_memory_allocated(device) / (1024 * 1024), 2),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

