from pathlib import Path

from dyco_repair.envs import load_issue, load_issues


def test_load_single_swebench_issue_by_task_id() -> None:
    issue = load_issue("swebench-lite", Path("tests/fixtures/swebench_lite_sample.jsonl"), task_id="django__django-11099")
    assert issue.issue_id == "django__django-11099"
    assert issue.target_files[0] == "django/contrib/admin/views/main.py"
    assert issue.metadata["repo"] == "django/django"


def test_load_multiple_swebench_issues() -> None:
    issues = load_issues("swebench-lite", Path("tests/fixtures/swebench_lite_sample.jsonl"))
    assert len(issues) == 2
    assert issues[0].failing_tests
    assert issues[1].success_patch_keywords

