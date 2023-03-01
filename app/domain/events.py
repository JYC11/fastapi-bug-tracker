from typing import Any
from uuid import UUID


class Event:
    def apply(self, model: Any):
        for key in self.__dict__.keys():
            if hasattr(model, key):
                val = getattr(self, key)
                setattr(model, key, val)
        return model

    def dict(self):
        out = {}
        for key, value in self.__dict__.items():
            if isinstance(value, UUID):
                value = str(value)
            out[key] = value
        return out

    def name(self):
        return self.__repr__().replace("()", "")
