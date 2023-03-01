from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from app.domain.enums import RecordStatusEnum, UserTypeEnum
from app.domain.events import Event

if TYPE_CHECKING:
    pass


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


@dataclass(repr=True, eq=False)
class UserUpdated(Event):
    id: UUID = field(repr=False)
    username: str = field(repr=False)
    email: str = field(repr=False)
    password: str = field(repr=False)
    user_type: UserTypeEnum = field(repr=False)
    user_status: RecordStatusEnum = field(repr=False)
    is_admin: bool = field(repr=False)
    security_question: str = field(repr=False)
    security_question_answer: str = field(repr=False)


@dataclass(repr=True, eq=False)
class UserSoftDeleted(Event):
    id: UUID = field(repr=False)
    user_status: RecordStatusEnum = field(default_factory=lambda: RecordStatusEnum.DELETED, repr=False)
