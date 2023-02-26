from uuid import UUID

from app.domain.commands import Command
from app.domain.enums import RecordStatusEnum, UserTypeEnum


class CreateUser(Command):
    username: str
    email: str
    password: str
    user_type: UserTypeEnum
    user_status: RecordStatusEnum
    is_admin: bool
    security_question: str
    security_question_answer: str


class UpdateUser(Command):
    id: UUID
    username: str | None
    email: str | None
    password: str | None
    user_type: UserTypeEnum | None
    user_status: RecordStatusEnum | None
    is_admin: bool | None
    security_question: str | None
    security_question_answer: str | None


class DeleteUser(Command):
    id: UUID


class Login(Command):
    email: str
    password: str


class Refresh(Command):
    refresh_token: str
    grant_type: str
