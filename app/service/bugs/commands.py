from uuid import UUID

from app.domain.commands import Command
from app.domain.enums import BugStatusEnum, EnvironmentEnum, RecordStatusEnum, UrgencyEnum


class CreateBug(Command):
    title: str
    author_id: UUID
    assignee_id: UUID | None
    description: str
    environment: EnvironmentEnum
    urgency: UrgencyEnum
    status: BugStatusEnum
    record_status: RecordStatusEnum
    edited: bool = False


class UpdateBug(Command):
    id: UUID
    title: str
    author_id: UUID
    assignee_id: UUID | None
    description: str
    environment: EnvironmentEnum
    urgency: UrgencyEnum
    status: BugStatusEnum
    record_status: RecordStatusEnum
    edited: bool = True
    images: list[str]


class SoftDeleteBug(Command):
    id: UUID
    author_id: UUID


class CreateComment(Command):
    id: UUID
    bug_id: UUID
    author_id: UUID
    text: str
    edited: bool = False


class UpdateComment(Command):
    id: UUID
    bug_id: UUID
    author_id: UUID
    text: str
    edited: bool = True


class SoftDeleteComment(Command):
    id: UUID
    bug_id: UUID
    author_id: UUID


class Upvote(Command):
    id: UUID


class Downvote(Command):
    id: UUID
