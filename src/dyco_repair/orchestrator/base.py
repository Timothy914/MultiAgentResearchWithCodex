from __future__ import annotations

from abc import ABC, abstractmethod

from dyco_repair.types import AgentAction, TaskState


class BaseOrchestratorPolicy(ABC):
    @abstractmethod
    def select(self, state: TaskState) -> AgentAction:
        raise NotImplementedError

