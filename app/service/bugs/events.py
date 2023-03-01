from dataclasses import dataclass, field
from uuid import UUID

from app.domain.enums import BugStatusEnum, EnvironmentEnum, RecordStatusEnum, UrgencyEnum
from app.domain.events import Event


@dataclass
class BugCreated(Event):
    id: UUID = field(repr=False)
    title: str = field(repr=False)
    author_id: UUID = field(repr=False)
    assignee_id: UUID | None = field(repr=False)
    description: str = field(repr=False)
    environment: EnvironmentEnum = field(repr=False)
    urgency: UrgencyEnum = field(repr=False)
    status: BugStatusEnum = field(repr=False)
    record_status: RecordStatusEnum = field(repr=False)
    version: int = field(repr=False)
    edited: bool = field(repr=False)
    images: list[str] = field(repr=False)


@dataclass
class BugUpdated(Event):
    id: UUID = field(repr=False)
    title: str = field(repr=False)
    author_id: UUID = field(repr=False)
    assignee_id: UUID | None = field(repr=False)
    description: str = field(repr=False)
    environment: EnvironmentEnum = field(repr=False)
    urgency: UrgencyEnum = field(repr=False)
    status: BugStatusEnum = field(repr=False)
    record_status: RecordStatusEnum = field(repr=False)
    version: int = field(repr=False)
    edited: bool = field(repr=False)
    images: list[str] = field(repr=False)


@dataclass
class BugSoftDeleted(Event):
    id: UUID = field(repr=False)
    record_status: RecordStatusEnum = field(default_factory=lambda: RecordStatusEnum.DELETED, repr=False)


@dataclass
class CommentCreated(Event):
    id: UUID = field(repr=False)
    bug_id: UUID = field(repr=False)
    author_id: UUID = field(repr=False)
    text: str = field(repr=False)
    vote_count: int = field(default_factory=lambda: 0, repr=False)
    edited: bool = field(default_factory=lambda: True, repr=False)

    # TODO: custom event applier to add Comment to Bug


@dataclass
class CommentUpdated(Event):
    id: UUID = field(repr=False)
    bug_id: UUID = field(repr=False)
    author_id: UUID = field(repr=False)
    text: str = field(repr=False)
    vote_count: int = field(repr=False)
    edited: bool = field(repr=False)

    # TODO: custom event applier to update Comment already in Bug


@dataclass
class CommentDeleted(Event):
    id: UUID = field(repr=False)
    record_status: RecordStatusEnum = field(default_factory=lambda: RecordStatusEnum.DELETED, repr=False)

    # TODO: custom event applier to delete Comment already in Bug


@dataclass
class Upvoted(Event):
    comment_id: UUID = field(repr=False)


@dataclass
class Downvoted(Event):
    comment_id: UUID = field(repr=False)
