import asyncio
import random
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from faker import Faker
from faker.providers import (
    address,
    automotive,
    bank,
    barcode,
    color,
    company,
    credit_card,
    currency,
    date_time,
    emoji,
    file,
    geo,
    internet,
    isbn,
    job,
    lorem,
    misc,
    person,
    phone_number,
    profile,
    python,
    ssn,
    user_agent,
)
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from app.adapters.orm import metadata, start_mappers
from app.common.settings import db_settings
from app.domain import enums


def _add_providers(faker: Faker, *providers) -> Faker:
    for provider in providers:
        faker.add_provider(provider)
    return faker


# I want to go nuts with fake data
providers = [
    address,
    automotive,
    bank,
    barcode,
    color,
    company,
    credit_card,
    currency,
    date_time,
    emoji,
    file,
    geo,
    internet,
    isbn,
    job,
    lorem,
    misc,
    person,
    phone_number,
    profile,
    python,
    ssn,
    user_agent,
]

faker = Faker()
faker = _add_providers(faker, *providers)


# DB STUFF FROM HERE
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(db_settings.test_url, future=True, echo=True)
    async with engine.connect() as conn:
        async with conn.begin():
            drop_tables_statement = (
                f"DROP TABLE IF EXISTS {','.join(metadata.tables.keys())} CASCADE;"
            )
            await conn.execute(text(drop_tables_statement))
            await conn.run_sync(metadata.create_all)  # metadata creation here
        start_mappers()
    yield engine
    clear_mappers()


@pytest_asyncio.fixture(scope="function")
async def session_factory(async_engine: AsyncEngine):
    async with async_engine.connect() as conn:
        session_factory: sessionmaker = sessionmaker(
            conn,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )
        yield session_factory


@pytest_asyncio.fixture(scope="function")
async def session(session_factory: sessionmaker):
    session: AsyncSession = session_factory()
    yield session
    for table in metadata.tables.keys():
        delete_stmt = f"DELETE FROM {table};"
        await session.execute(text(delete_stmt))
        await session.commit()
    await session.close()


# DB STUFF ENDS HERE


# TEST CLIENT FROM HERE
@pytest.fixture(scope="function")
def client():
    from app.main import app

    # dependency injection here
    with TestClient(app) as c:
        yield c


# TEST CLIENT ENDS HERE


# FAKE DATA GENERATION FROM HERE
@pytest_asyncio.fixture
def username() -> str:
    return faker.user_name()


@pytest_asyncio.fixture
def email() -> str:
    return faker.email()


@pytest_asyncio.fixture
def password() -> str:
    return faker.pystr()


@pytest_asyncio.fixture
def user_type() -> enums.UserTypeEnum:
    return random.choice([e for e in enums.UserTypeEnum])


@pytest_asyncio.fixture
def user_status() -> enums.RecordStatusEnum:
    return enums.RecordStatusEnum.ACTIVE


@pytest_asyncio.fixture
def is_admin() -> bool:
    return False


@pytest_asyncio.fixture
def security_question() -> str:
    return faker.sentence(nb_words=10, variable_nb_words=False)


@pytest_asyncio.fixture
def security_question_answer() -> str:
    return faker.sentence(nb_words=5, variable_nb_words=False)


@pytest_asyncio.fixture
def user_data_in(
    username,
    email,
    password,
    user_type,
    user_status,
    is_admin,
    security_question,
    security_question_answer,
) -> dict[str, Any]:
    return {
        "username": username,
        "email": email,
        "password": password,
        "user_type": user_type,
        "user_status": user_status,
        "is_admin": is_admin,
        "security_question": security_question,
        "security_question_answer": security_question_answer,
    }


@pytest_asyncio.fixture
def user_data_to_generate() -> int:
    return 5


@pytest_asyncio.fixture
def user_data_list(user_data_to_generate) -> list[dict[str, Any]]:
    return [
        {
            "username": faker.user_name(),
            "email": faker.email(),
            "password": faker.pystr(),
            "user_type": random.choice([e for e in enums.UserTypeEnum]),
            "user_status": enums.RecordStatusEnum.ACTIVE,
            "is_admin": False,
            "security_question": faker.sentence(nb_words=10, variable_nb_words=False),
            "security_question_answer": faker.sentence(
                nb_words=5, variable_nb_words=False
            ),
        }
        for _ in range(user_data_to_generate)
    ]


@pytest_asyncio.fixture
def tag_name() -> str:
    return faker.company()


@pytest_asyncio.fixture
def tag_data_in(tag_name):
    return {
        "name": tag_name,
    }


@pytest_asyncio.fixture
def tag_data_to_generate() -> int:
    return 8


@pytest_asyncio.fixture
def tag_data_list(tag_data_to_generate):
    return [{"name": faker.company()} for _ in range(tag_data_to_generate)]


@pytest_asyncio.fixture
def comment_text() -> str:
    return faker.paragraph(nb_sentences=5)


@pytest_asyncio.fixture
def vote_count() -> int:
    return 0


@pytest_asyncio.fixture
def comment_is_edited() -> bool:
    return False


@pytest_asyncio.fixture
def comment_data_in(
    comment_text,
    vote_count,
    comment_is_edited,
):
    return {
        "bug_id": uuid4(),  # obviously replace with actual bug id
        "author_id": uuid4(),  # obviously replace with actual user id
        "text": comment_text,
        "vote_count": vote_count,
        "edited": comment_is_edited,
    }


@pytest_asyncio.fixture
def comment_data_to_generate() -> int:
    return 8


@pytest_asyncio.fixture
def comment_data_list(comment_data_to_generate):
    return [
        {
            "bug_id": uuid4(),  # obviously replace with actual bug id
            "author_id": uuid4(),  # obviously replace with actual user id
            "text": faker.paragraph(nb_sentences=5),
            "vote_count": 0,
            "edited": False,
        }
        for _ in range(comment_data_to_generate)
    ]


@pytest_asyncio.fixture
def bug_title() -> str:
    return faker.setence(nb_words=4, variable_nb_words=False)


@pytest_asyncio.fixture
def bug_description() -> str:
    return faker.paragraph(nb_sentences=5)


@pytest_asyncio.fixture
def bug_report_is_edited() -> bool:
    return False


@pytest_asyncio.fixture
def images() -> list[str]:
    return [faker.image_url() for _ in range(3)]


@pytest_asyncio.fixture
def urgency() -> enums.UrgencyEnum:
    return random.choice([e for e in enums.UrgencyEnum])


@pytest_asyncio.fixture
def status() -> enums.BugStatusEnum:
    return enums.BugStatusEnum.NEW


@pytest_asyncio.fixture
def record_status() -> enums.RecordStatusEnum:
    return enums.RecordStatusEnum.ACTIVE


@pytest_asyncio.fixture
def version() -> int:
    return 1


@pytest_asyncio.fixture
def bug_report_data_in(
    bug_title,
    bug_description,
    bug_report_is_edited,
    images,
    urgency,
    status,
    record_status,
    version,
):
    return {
        "title": bug_title,
        "author_id": uuid4(),  # obviously replace with actual user id
        "assigned_user_id": uuid4(),  # obviously replace with actual user id
        "description": bug_description,
        "edited": bug_report_is_edited,
        "images": images,
        "urgency": urgency,
        "status": status,
        "record_status": record_status,
        "version": version,
    }


@pytest_asyncio.fixture
def bug_report_data_to_generate() -> int:
    return 12


@pytest_asyncio.fixture
def bug_report_list(bug_report_data_to_generate) -> list[dict[str, Any]]:
    return [
        {
            "title": faker.setence(nb_words=4, variable_nb_words=False),
            "author_id": uuid4(),  # obviously replace with actual user id
            "assigned_user_id": uuid4(),  # obviously replace with actual user id
            "description": faker.paragraph(nb_sentences=5),
            "edited": False,
            "images": [faker.image_url() for _ in range(3)],
            "urgency": random.choice([e for e in enums.UrgencyEnum]),
            "status": enums.BugStatusEnum.NEW,
            "record_status": enums.RecordStatusEnum.ACTIVE,
            "version": 1,
        }
        for _ in range(bug_report_data_to_generate)
    ]


# FAKE DATA GENERATION ENDS HERE
