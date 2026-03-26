from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dyco_repair.envs import MockIssue
from dyco_repair.runner import run_episode


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a mock multi-agent code repair episode.")
    parser.add_argument("--task", required=True, help="Path to a mock issue JSON file.")
    parser.add_argument("--output-dir", default="outputs/mock-run", help="Directory for trajectory and summary output.")
    parser.add_argument("--max-steps", type=int, default=8)
    args = parser.parse_args()

    issue = MockIssue.from_path(args.task)
    state, _, summary = run_episode(issue, output_dir=args.output_dir, max_steps=args.max_steps)
    print(json.dumps({"issue_id": state.issue_id, **summary}, indent=2))


if __name__ == "__main__":
    main()

