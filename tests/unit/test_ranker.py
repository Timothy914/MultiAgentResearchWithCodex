from dyco_repair.ensemble import PatchEnsembler
from dyco_repair.types import PatchCandidate


def test_ranker_prefers_high_score_then_confidence() -> None:
    ranker = PatchEnsembler()
    candidates = [
        PatchCandidate("a", "diff-a", 0.4, 0.9, ["a.py"], "dev"),
        PatchCandidate("b", "diff-b", 0.8, 0.4, ["b.py"], "dev"),
        PatchCandidate("c", "diff-c", 0.8, 0.7, ["c.py"], "dev"),
    ]
    ranked = ranker.rank(candidates)
    assert [candidate.candidate_id for candidate in ranked] == ["c", "b", "a"]

