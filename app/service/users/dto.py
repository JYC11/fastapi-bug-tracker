# data transfer objects (inspired by nest.js)
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums import RecordStatusEnum, UserTypeEnum


class UserCreateIn(BaseModel):
    password: str
    username: str
    email: str
    user_type: UserTypeEnum
    user_status: RecordStatusEnum
    is_admin: bool
    security_question: str
    security_question_answer: str


class UserUpdateIn(BaseModel):
    password: str | None
    username: str | None
    email: str | None
    user_type: UserTypeEnum | None
    user_status: RecordStatusEnum | None
    is_admin: bool | None
    security_question: str | None
    security_question_answer: str | None


class UserOut(BaseModel):
    id: UUID
    create_dt: datetime
    update_dt: datetime | None
    username: str
    email: str
    user_type: UserTypeEnum
    user_status: RecordStatusEnum
    is_admin: bool

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
