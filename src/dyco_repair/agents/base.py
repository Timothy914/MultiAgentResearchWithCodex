from __future__ import annotations

from abc import ABC, abstractmethod

from dyco_repair.types import AgentResult, TaskState


class BaseAgent(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def run(self, state: TaskState) -> AgentResult:
        raise NotImplementedError

