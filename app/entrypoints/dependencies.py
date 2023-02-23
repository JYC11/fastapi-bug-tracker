from argon2 import PasswordHasher

from app.common.db import async_autocommit_session_factory
from app.service.messagebus import MessageBus, MessageBusFactory
from app.service.unit_of_work import SqlAlchemyUnitOfWork

MESSAGEBUS = MessageBusFactory(
    uow=SqlAlchemyUnitOfWork(),
    password_hasher=PasswordHasher(),
)


def get_message_bus() -> MessageBus:
    return MESSAGEBUS()


def get_reader_session():
    with async_autocommit_session_factory() as session:
        yield session
