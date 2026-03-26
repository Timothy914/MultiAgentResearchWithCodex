from __future__ import annotations

from dyco_repair.types import PatchCandidate


class PatchEnsembler:
    def rank(self, candidates: list[PatchCandidate]) -> list[PatchCandidate]:
        return sorted(
            candidates,
            key=lambda candidate: (candidate.score, candidate.confidence, -len(candidate.touched_files)),
            reverse=True,
        )

