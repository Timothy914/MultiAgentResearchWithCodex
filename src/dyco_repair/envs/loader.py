from __future__ import annotations

from pathlib import Path

from dyco_repair.envs.mock_env import MockIssue
from dyco_repair.envs.swebench_lite import SweBenchLiteIssue, load_swebench_lite_issue, load_swebench_lite_issues


def load_issue(source_type: str, path: str | Path, task_id: str | None = None) -> MockIssue | SweBenchLiteIssue:
    if source_type == "mock":
        return MockIssue.from_path(path)
    if source_type == "swebench-lite":
        return load_swebench_lite_issue(path, task_id=task_id)
    raise ValueError(f"Unsupported source type: {source_type}")


def load_issues(source_type: str, path: str | Path, limit: int | None = None) -> list[MockIssue | SweBenchLiteIssue]:
    if source_type == "mock":
        issues = [MockIssue.from_path(path)]
    elif source_type == "swebench-lite":
        issues = load_swebench_lite_issues(path)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")
    if limit is not None:
        return issues[:limit]
    return issues

