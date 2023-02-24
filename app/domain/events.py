from abc import abstractmethod
from typing import Any


class Event:
    @abstractmethod
    def apply(self, model: Any):
        pass
