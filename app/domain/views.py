from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import BugStatusEnum, RecordStatusEnum, UrgencyEnum, UserTypeEnum


@dataclass
class UserView:
    user_create_dt: datetime
    user_update_dt: datetime
    username: str
    email: str
    user_type: UserTypeEnum
    user_status: RecordStatusEnum
    is_admin: bool
    comment_count: int
    bugs_raised_count: int
    bugs_assigned_to_count: int
    bugs_closed_count: int
    votes_count: int


@dataclass
class CommentView:
    user_create_dt: datetime
    user_update_dt: datetime
    username: str
    email: str
    user_type: UserTypeEnum
    user_status: RecordStatusEnum
    is_admin: bool
    comment_create_dt: datetime
    comment_update_dt: datetime
    text: str
    vote_count: int
    edited: bool


@dataclass
class BugsView:
    bug_created_dt: datetime
    bug_updated_dt: datetime
    author_id: UUID
    assigned_user_id: UUID
    description: str
    urgency: UrgencyEnum
    status: BugStatusEnum
    record_status: RecordStatusEnum
    version: int
    edited: bool
    images: list[str]
    author_create_dt: datetime
    author_update_dt: datetime
    author_username: str
    author_email: str
    author_user_type: UserTypeEnum
    author_user_status: RecordStatusEnum
    author_is_admin: bool
    assignee_create_dt: datetime | None
    assignee_update_dt: datetime | None
    assignee_username: str | None
    assignee_email: str | None
    assignee_user_type: UserTypeEnum | None
    assignee_user_status: RecordStatusEnum | None
    assignee_is_admin: bool | None
