import abc
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.domain.enums import BugStatusEnum, RecordStatusEnum, UrgencyEnum, UserTypeEnum
from app.domain.events import Event
from app.service.users.events import UserCreated, UserDeleted, UserUpdated


@dataclass(repr=True, eq=False)
class Base(abc.ABC):
    id: UUID = field(default_factory=lambda: uuid4())
    create_dt: datetime = field(init=False, repr=True)
    update_dt: datetime = field(init=False, repr=True)

    def __eq__(self, other):
        if not isinstance(other, Base):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def _to_dict(self):
        return {
            attr: getattr(self, attr, "")
            for attr in self.__dir__()
            if not attr.startswith("__") and type(getattr(self, attr, "")).__name__ != "method"
        }

    @classmethod
    def create(cls, data: dict[str, Any]):
        return cls(id=uuid4(), **data)

    def update(self, data: dict[str, Any]):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)
        return self

    def generate_event_store(self):
        if hasattr(self, "events"):
            events = getattr(self, "events")
            latest: Event = events[-1]
            event_store = EventStore(
                id=uuid4(),
                aggregate_id=self.id,
                event_name=latest.name(),
                event_data=latest.dict(),
            )
            return event_store
        return None


@dataclass(repr=True, eq=False)
class Users(Base):
    username: str = field(default_factory=lambda: "")
    email: str = field(default_factory=lambda: "")
    password: str = field(default_factory=lambda: "")
    user_type: UserTypeEnum = field(default_factory=lambda: UserTypeEnum.BACKEND)
    user_status: RecordStatusEnum = field(default_factory=lambda: RecordStatusEnum.ACTIVE)
    is_admin: bool = field(default_factory=lambda: False)
    security_question: str = field(default_factory=lambda: "")
    security_question_answer: str = field(default_factory=lambda: "")
    comments: list["Comments"] = field(default_factory=list)
    raised_bugs: list["Bugs"] = field(default_factory=list)
    assigned_bugs: list["Bugs"] = field(default_factory=list)
    events: deque[Event] = field(default_factory=deque)

    @property
    def is_active(self) -> bool:
        return self.user_status == RecordStatusEnum.ACTIVE

    def verify_password(self, password: str, hasher: PasswordHasher):
        try:
            hasher.verify(self.password, password)
            return True
        except VerifyMismatchError:
            return False

    def verify_security_question_answer(self, answer: str, hasher: PasswordHasher):
        try:
            hasher.verify(self.security_question_answer, answer)
            return True
        except VerifyMismatchError:
            return False

    @classmethod
    def create_user(cls, data: dict[str, Any], hasher: PasswordHasher):
        password = data.get("password")
        if not password:
            raise ValueError  # TODO: custom exception
        security_question_answer = data.get("security_question_answer")
        if security_question_answer:
            data["security_question_answer"] = hasher.hash(security_question_answer)
        data["password"] = hasher.hash(password)
        user = cls.create(data)
        user.events.append(UserCreated(id=user.id, **data))
        return user

    def update_user(self, data: dict[str, Any], hasher: PasswordHasher):
        password = data.get("password")
        if password is not None:
            data["password"] = hasher.hash(password)
        security_question_answer = data.get("security_question_answer")
        if security_question_answer is not None:
            data["security_question_answer"] = hasher.hash(security_question_answer)
        event = UserUpdated(**data)
        event.id = self.id
        self.events.append(event)
        return self.update(data)

    def delete_user(self):
        self.user_status = RecordStatusEnum.DELETED
        self.events.append(UserDeleted(id=self.id))
        return self

    def set_password(self, password: str, hasher: PasswordHasher):
        self.password = hasher.hash(password)


@dataclass(repr=True, eq=False)
class Tags(Base):
    name: str = field(default_factory=lambda: "")
    bug_tags: list["BugTags"] = field(default_factory=list)


@dataclass(repr=True, eq=False)
class BugTags(Base):  # many-to-many with bugs
    tag_id: UUID = field(default_factory=lambda: uuid4())
    tag: Tags = field(default_factory=lambda: Tags())
    bug_id: UUID = field(default_factory=lambda: uuid4())
    bug: "Bugs" = field(default_factory=lambda: Bugs())


@dataclass(repr=True, eq=False)
class Comments(Base):
    bug_id: UUID = field(default_factory=lambda: uuid4())
    bug: "Bugs" = field(default_factory=lambda: Bugs())
    author_id: UUID = field(default_factory=lambda: uuid4())
    author: Users = field(default_factory=lambda: Users())
    text: str = field(default_factory=lambda: "")
    vote_count: int = field(default_factory=lambda: 0)
    edited: bool = field(default_factory=lambda: False)

    def increase_vote_count(self):
        self.vote_count += 1

    def decrease_vote_count(self):
        self.vote_count -= 1

    def set_edited(self):
        self.edited = True

    def update_comment(self, data: dict[str, Any]):
        self.update(data)
        self.set_edited()
        return


@dataclass(repr=True, eq=False)
class Bugs(Base):
    title: str = field(default_factory=lambda: "")
    author_id: UUID = field(default_factory=lambda: uuid4())
    author: Users = field(default_factory=lambda: Users())
    assignee_id: UUID = field(default_factory=lambda: uuid4())
    assignee: Users = field(default_factory=lambda: Users())
    description: str = field(default_factory=lambda: "")
    urgency: UrgencyEnum = field(default_factory=lambda: UrgencyEnum.LOW)
    status: BugStatusEnum = field(default_factory=lambda: BugStatusEnum.NEW)
    record_status: RecordStatusEnum = field(default_factory=lambda: RecordStatusEnum.ACTIVE)
    version: int = field(default_factory=lambda: 1)
    edited: bool = field(default_factory=lambda: False)
    images: list[str] = field(default_factory=list)
    comments: list[Comments] = field(default_factory=list)
    bug_tags: list[BugTags] = field(default_factory=list)
    events: deque[Event] = field(default_factory=deque)

    @property
    def tags(self) -> list[Tags]:
        return [m.tag for m in self.bug_tags]

    def set_urgency(self, urgency: UrgencyEnum):
        self.urgency = urgency

    def set_status(self, status: BugStatusEnum):
        self.status = status

    def set_record_status(self, record_status: RecordStatusEnum):
        self.record_status = record_status

    def set_edited(self):
        self.edited = True

    def update_report(self, data: dict[str, Any]):
        self.update(data)
        self.set_edited()
        return

    def remove_bug_report(self):
        self.set_record_status(RecordStatusEnum.DELETED)
        # emit event
        return

    def add_comment(self, data: dict[str, Any]):
        comment = Comments.create(data)
        self.comments.append(comment)
        # emit event
        return

    def _find_comment(self, ident: UUID) -> Comments | None:
        comment = [c for c in self.comments if c.id == ident]
        if comment:
            return comment[0]
        return None

    def update_comment(self, ident: UUID, data: dict[str, Any]):
        comment = self._find_comment(ident)
        if comment:
            comment.update_comment(data)
            # emit event
            return True
        return False

    def remove_comment(self, ident: UUID):
        comment = self._find_comment(ident)
        if comment:
            idx = self.comments.index(comment)
            self.comments.pop(idx)
            # emit event
            return True
        return False

    def _find_tag_mapper(self, ident: UUID) -> BugTags | None:
        tag = [c for c in self.bug_tags if c.tag_id == ident]
        if tag:
            return tag[0]
        return None

    def add_tag(self, ident: UUID):
        tag = self._find_tag_mapper(ident)
        if not tag:
            data = {"id": uuid4(), "tag_id": ident, "bug_id": self.id}
            bug_tag_mapper = BugTags.create(data)
            self.bug_tags.append(bug_tag_mapper)
            # emit event
            return True
        return False

    def remove_tag_mapper(self, ident: UUID):
        tag = self._find_tag_mapper(ident)
        if tag:
            idx = self.bug_tags.index(tag)
            self.bug_tags.pop(idx)
            # emit event
            return True
        return False


@dataclass(eq=False)
class EventStore:
    id: UUID
    create_dt: datetime = field(init=False, repr=True)
    aggregate_id: UUID
    event_name: str
    event_data: dict
