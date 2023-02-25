import abc
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from argon2 import PasswordHasher

from app.domain.enums import BugStatusEnum, RecordStatusEnum, UrgencyEnum, UserTypeEnum
from app.domain.events import Event


@dataclass(repr=True, eq=False)
class Base(abc.ABC):
    id: UUID
    create_dt: datetime = field(init=False, repr=False)
    update_dt: datetime = field(init=False, repr=False)

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
            if not attr.startswith("__")
            and type(getattr(self, attr, "")).__name__ != "method"
        }

    @classmethod
    def create(cls, data: dict[str, Any]):
        return cls(**data)

    def update(self, data: dict[str, Any]):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)
        return


@dataclass(repr=True, eq=False)
class Users(Base):
    username: str
    email: str
    password: str
    user_type: UserTypeEnum
    user_status: RecordStatusEnum
    is_admin: bool
    security_question: str
    security_question_answer: str
    comments: list["Comments"] = field(default_factory=list)
    raised_bugs: list["Bugs"] = field(default_factory=list)
    assigned_bugs: list["Bugs"] = field(default_factory=list)
    events: deque[Event] = field(default_factory=deque)

    def verify_password(self, password: str, hasher: PasswordHasher):
        return hasher.verify(self.password, password)

    def verify_security_question_answer(self, answer: str, hasher: PasswordHasher):
        return hasher.verify(self.security_question_answer, answer)

    @classmethod
    def create_user(cls, data: dict[str, Any], hasher: PasswordHasher):
        password = data.get("password")
        if not password:
            raise ValueError  # TODO: custom exception
        security_question_answer = data.get("security_question_answer")
        if security_question_answer:
            data["security_question_answer"] = hasher.hash(security_question_answer)
        data["password"] = hasher.hash(password)
        return cls.create(data)

    def delete_user(self):
        self.user_status = RecordStatusEnum.DELETED
        # emit event


@dataclass(repr=True, eq=False)
class Tags(Base):
    name: str
    bug_tags: list["BugTags"]


@dataclass(repr=True, eq=False)
class BugTags(Base):  # many-to-many with bugs
    tag_id: UUID
    tag: Tags
    bug_id: UUID
    bug: "Bugs"


@dataclass(repr=True, eq=False)
class Comments(Base):
    bug_id: UUID
    bug: "Bugs"
    author_id: UUID
    author: Users
    text: str
    vote_count: int = 0
    edited: bool = False

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
    title: str
    author_id: UUID
    author: Users
    assigned_user_id: UUID
    assigned_to: Users
    description: str
    urgency: UrgencyEnum
    status: BugStatusEnum
    record_status: RecordStatusEnum
    version: int = 1
    edited: bool = False
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
    create_dt: datetime
    aggregate_id: UUID
    event_name: str
    event_data: dict
