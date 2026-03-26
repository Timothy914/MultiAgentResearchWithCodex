from pathlib import Path

from dyco_repair.envs import load_issue
from dyco_repair.runner import run_episode


def test_swebench_style_issue_runs_end_to_end(tmp_path: Path) -> None:
    issue = load_issue("swebench-lite", Path("tests/fixtures/swebench_lite_sample.jsonl"), task_id="sympy__sympy-13501")
    state, transitions, summary = run_episode(issue, output_dir=tmp_path)
    assert state.issue_id == "sympy__sympy-13501"
    assert transitions
    assert summary["final_status"] in {"resolved", "stopped"}
    assert (tmp_path / "trajectory.json").exists()
