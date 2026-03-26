from __future__ import annotations

import json
from pathlib import Path

from dyco_repair.types import Transition


class RunLogger:
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_trajectory(self, transitions: list[Transition]) -> Path:
        path = self.output_dir / "trajectory.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump([transition.to_dict() for transition in transitions], handle, indent=2)
        return path

    def save_summary(self, summary: dict) -> Path:
        path = self.output_dir / "summary.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        return path

