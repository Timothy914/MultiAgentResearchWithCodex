from pathlib import Path

from dyco_repair.envs import MockIssue
from dyco_repair.runner import run_episode


def test_easy_issue_resolves_and_logs(tmp_path: Path) -> None:
    issue = MockIssue.from_path(Path("tests/fixtures/easy_issue.json"))
    state, transitions, summary = run_episode(issue, output_dir=tmp_path)
    assert state.tests_passed is True
    assert summary["final_status"] == "resolved"
    assert transitions
    assert (tmp_path / "trajectory.json").exists()
    assert (tmp_path / "summary.json").exists()


def test_hard_issue_uses_reflection_or_ensemble(tmp_path: Path) -> None:
    issue = MockIssue.from_path(Path("tests/fixtures/hard_issue.json"))
    _, transitions, summary = run_episode(issue, output_dir=tmp_path)
    actions = [transition.action.value for transition in transitions]
    assert "invoke_reflector" in actions or "invoke_ensemble" in actions
    assert summary["total_calls"] >= 4
