from abc import abstractmethod
from typing import Any
from uuid import UUID


class Event:
    @abstractmethod
    def apply(self, model: Any):
        pass

    def dict(self):
        out = {}
        for key, value in self.__dict__.items():
            if isinstance(value, UUID):
                value = str(value)
            out[key] = value
        return out

    def name(self):
        return self.__repr__().replace("()", "")
