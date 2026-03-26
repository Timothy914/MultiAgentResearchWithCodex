from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dyco_repair.types import TaskState

_FILE_PATTERN = re.compile(r"^\+\+\+\s+b/(.+)$", re.MULTILINE)
_WORD_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")
_STOPWORDS = {
    "this",
    "that",
    "with",
    "from",
    "when",
    "should",
    "after",
    "before",
    "return",
    "returns",
    "raise",
    "raises",
    "patch",
    "tests",
    "test",
    "issue",
    "repo",
    "problem",
    "statement",
    "file",
    "files",
    "diff",
    "index",
    "true",
    "false",
    "none",
}


def _normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return [line.strip() for line in stripped.splitlines() if line.strip()]
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return [str(parsed)]
    return [str(value)]


def _extract_target_files(*diffs: str) -> list[str]:
    files: list[str] = []
    for diff in diffs:
        if not diff:
            continue
        files.extend(_FILE_PATTERN.findall(diff))
    deduped: list[str] = []
    for path in files:
        if path not in deduped:
            deduped.append(path)
    return deduped or ["unknown_target.py"]


def _extract_keywords(*texts: str, limit: int = 3) -> list[str]:
    counts: dict[str, int] = {}
    for text in texts:
        for word in _WORD_PATTERN.findall(text.lower()):
            if word in _STOPWORDS or word.startswith("test_"):
                continue
            counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], -len(item[0]), item[0]))
    keywords = [word for word, _ in ranked[:limit]]
    return keywords or ["fix", "regression"]


def _load_records(path: str | Path) -> list[dict[str, Any]]:
    path_obj = Path(path)
    if path_obj.is_dir():
        candidates = sorted(path_obj.glob("*.jsonl")) + sorted(path_obj.glob("*.json"))
        if not candidates:
            raise FileNotFoundError(f"No JSON/JSONL task files found under {path_obj}")
        path_obj = candidates[0]
    if path_obj.suffix == ".jsonl":
        with path_obj.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    with path_obj.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return payload
    return [payload]


@dataclass
class SweBenchLiteIssue:
    issue_id: str
    description: str
    difficulty: str
    target_files: list[str]
    success_patch_keywords: list[str]
    failing_tests: list[str]
    budget_total: int = 8
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_record(cls, record: dict[str, Any], budget_total: int = 8) -> "SweBenchLiteIssue":
        patch = record.get("patch", "")
        test_patch = record.get("test_patch", "")
        description = record.get("problem_statement", "") or record.get("description", "")
        fail_to_pass = _normalize_list(record.get("FAIL_TO_PASS"))
        pass_to_pass = _normalize_list(record.get("PASS_TO_PASS"))
        target_files = _extract_target_files(patch, test_patch)
        keywords = _extract_keywords(description, patch, test_patch, record.get("hints_text", ""))
        tests = fail_to_pass or pass_to_pass or ["unknown_test"]
        difficulty = record.get("difficulty")
        if not difficulty:
            difficulty = "hard" if len(tests) > 1 or len(target_files) > 1 else "medium"
        metadata = {
            "repo": record.get("repo"),
            "base_commit": record.get("base_commit"),
            "version": record.get("version"),
            "hints_text": record.get("hints_text", ""),
            "oracle_patch_available": bool(patch),
        }
        return cls(
            issue_id=record.get("instance_id") or record.get("issue_id") or "unknown-instance",
            description=description,
            difficulty=difficulty,
            target_files=target_files,
            success_patch_keywords=keywords,
            failing_tests=tests,
            budget_total=budget_total,
            metadata=metadata,
        )

    def initial_state(self) -> TaskState:
        return TaskState(
            issue_id=self.issue_id,
            description=self.description,
            difficulty=self.difficulty,
            target_files=self.target_files,
            success_patch_keywords=self.success_patch_keywords,
            budget_total=self.budget_total,
            budget_remaining=self.budget_total,
            tests_remaining=len(self.failing_tests),
            metadata=self.metadata,
        )


def load_swebench_lite_issues(path: str | Path, budget_total: int = 8) -> list[SweBenchLiteIssue]:
    return [SweBenchLiteIssue.from_record(record, budget_total=budget_total) for record in _load_records(path)]


def load_swebench_lite_issue(path: str | Path, task_id: str | None = None, budget_total: int = 8) -> SweBenchLiteIssue:
    issues = load_swebench_lite_issues(path, budget_total=budget_total)
    if task_id is None:
        return issues[0]
    for issue in issues:
        if issue.issue_id == task_id:
            return issue
    raise KeyError(f"Could not find task_id={task_id} in {path}")

