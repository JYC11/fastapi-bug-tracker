from argon2 import PasswordHasher

from app.domain import enums
from app.domain.events import UserCreated, UserRemoved, UserUpdated
from app.domain.models import Users


def verify(
    user: Users,
    data: dict,
    password_hasher: PasswordHasher,
    original_password: str,
    security_question_answer: str,
):
    for key, value in data.items():
        if key == "password":
            assert user.verify_password(original_password, password_hasher)
        elif key == "security_question_answer":
            assert user.verify_security_question_answer(security_question_answer, password_hasher)
        else:
            assert value == getattr(user, key)


def test_user_creation(user_data_in: dict, password_hasher: PasswordHasher):
    original_password = user_data_in["password"]
    security_question_answer = user_data_in["security_question_answer"]
    new_user = Users.create_user(user_data_in, password_hasher)
    verify(
        new_user,
        user_data_in,
        password_hasher,
        original_password,
        security_question_answer,
    )

    assert len(new_user.events) == 1, isinstance(new_user.events[0], UserCreated)
    blank_user = Users()
    created_event = new_user.events[0]
    user_from_event = created_event.apply(blank_user)
    verify(
        user_from_event,
        user_data_in,
        password_hasher,
        original_password,
        security_question_answer,
    )


def test_user_update(user_data_in: dict, password_hasher: PasswordHasher):
    new_user = Users.create_user(user_data_in, password_hasher)
    update_data = {"user_type": enums.UserTypeEnum.PM, "is_admin": True}
    new_user.update_user(update_data, password_hasher)
    assert new_user.is_admin is True
    assert new_user.user_type == enums.UserTypeEnum.PM

    assert len(new_user.events) == 2
    assert isinstance(new_user.events[0], UserCreated), isinstance(new_user.events[1], UserUpdated)

    user_from_event = Users()
    for event in new_user.events:
        event.apply(user_from_event)

    assert user_from_event.is_admin is True
    assert user_from_event.user_type == enums.UserTypeEnum.PM


def test_user_delete(user_data_in: dict, password_hasher: PasswordHasher):
    new_user = Users.create_user(user_data_in, password_hasher)
    new_user.delete_user()
    assert new_user.user_status == enums.RecordStatusEnum.DELETED

    assert len(new_user.events) == 2
    assert isinstance(new_user.events[0], UserCreated), isinstance(new_user.events[1], UserRemoved)

    user_from_event = Users()
    for event in new_user.events:
        event.apply(user_from_event)

    assert new_user.user_status == enums.RecordStatusEnum.DELETED
