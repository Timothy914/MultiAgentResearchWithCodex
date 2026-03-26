from dyco_repair.orchestrator import HeuristicOrchestrator
from dyco_repair.types import AgentAction, PatchCandidate, TaskState


def test_orchestrator_returns_legal_action() -> None:
    orchestrator = HeuristicOrchestrator()
    state = TaskState(
        issue_id="x",
        description="desc",
        difficulty="hard",
        target_files=["a.py"],
        success_patch_keywords=["fix"],
        budget_total=8,
        budget_remaining=6,
        history=["planned"],
        located_files=["a.py"],
        patch_candidates=[
            PatchCandidate(
                candidate_id="1",
                diff="partial",
                score=0.4,
                confidence=0.4,
                touched_files=["a.py"],
                provenance="developer",
            )
        ],
        uncertainty=0.9,
        last_action=AgentAction.DEVELOPER,
    )
    action = orchestrator.select(state)
    assert action in set(AgentAction)

