from argon2 import PasswordHasher

from app.domain.models import Users

def test_user_creation(user_data_in: dict, password_hasher: PasswordHasher):
    original_password = user_data_in["password"]
    security_question_answer = user_data_in["security_question_answer"]
    new_user = Users.create_user(user_data_in, password_hasher)

    for key, value in user_data_in.items():
        if key == "password":
            assert new_user.verify_password(original_password, password_hasher)
        elif key == "security_question_answer":
            assert new_user.verify_security_question_answer(security_question_answer, password_hasher)
        else:
            assert value == getattr(new_user, key)
    

