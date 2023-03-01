from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from app.domain.enums import RecordStatusEnum, UserTypeEnum
from app.domain.events import Event

if TYPE_CHECKING:
    from app.domain.models import Users


@dataclass(repr=True, eq=False)
class UserCreated(Event):
    id: UUID = field(repr=False)
    username: str = field(repr=False)
    email: str = field(repr=False)
    password: str = field(repr=False)
    user_type: UserTypeEnum = field(repr=False)
    user_status: RecordStatusEnum = field(repr=False)
    is_admin: bool = field(repr=False)
    security_question: str = field(repr=False)
    security_question_answer: str = field(repr=False)

    def apply(self, model: "Users"):
        for key in self.__dict__.keys():
            val = getattr(self, key)
            setattr(model, key, val)
        return model


@dataclass(repr=True, eq=False)
class UserUpdated(Event):
    id: UUID | None = field(default_factory=lambda: None, repr=False)
    username: str | None = field(default_factory=lambda: None, repr=False)
    email: str | None = field(default_factory=lambda: None, repr=False)
    password: str | None = field(default_factory=lambda: None, repr=False)
    user_type: UserTypeEnum | None = field(default_factory=lambda: None, repr=False)
    user_status: RecordStatusEnum | None = field(default_factory=lambda: None, repr=False)
    is_admin: bool | None = field(default_factory=lambda: None, repr=False)
    security_question: str | None = field(default_factory=lambda: None, repr=False)
    security_question_answer: str | None = field(default_factory=lambda: None, repr=False)

    def apply(self, model: "Users"):
        for key in self.__dict__.keys():
            val = getattr(self, key)
            if val is not None:
                setattr(model, key, val)
        return model


@dataclass(repr=True, eq=False)
class UserSoftDeleted(Event):
    id: UUID = field(repr=False)
    user_status: RecordStatusEnum = field(default_factory=lambda: RecordStatusEnum.DELETED, repr=False)

    def apply(self, model: "Users"):
        setattr(model, "user_status", self.user_status)
        return model
