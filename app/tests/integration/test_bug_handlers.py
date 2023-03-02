from uuid import UUID

import pytest

# from app.domain import enums
from app.domain.models import Bugs, EventStore
from app.service.bugs import commands, handlers

# from app.service import exceptions as service_exc
from app.service.unit_of_work import AbstractUnitOfWork


@pytest.mark.asyncio
async def test_create_bug_handler(
    uow: AbstractUnitOfWork,
    bug_data_in: dict,
    create_user_id: UUID,
):
    bug_data_in["author_id"] = create_user_id
    bug_data_in["assignee_id"] = None
    cmd = commands.CreateBug(**bug_data_in)
    bug_id = await handlers.create_bug(cmd, uow=uow)
    assert bug_id
    async with uow:
        found_bugs: list[Bugs] = await uow.bugs.list()
        found_events: list[EventStore] = await uow.event_store.get(bug_id)
        assert len(found_bugs) == 1
        assert bug_id == found_bugs[0].id
        assert found_events, len(found_events) == 1
        assert bug_id == found_events[0].aggregate_id
        assert found_events[0].event_name == "BugCreated"


@pytest.mark.asyncio
async def test_update_bug_handler(
    uow: AbstractUnitOfWork,
    bug_data_in: dict,
    create_bug_id: tuple[UUID, UUID],
):
    bug_id, _user_id = create_bug_id
    bug_data_in["id"] = bug_id
    bug_data_in["urgency"] = "high"
    cmd = commands.UpdateBug(**bug_data_in)
    bug_id = await handlers.update_bug(cmd, uow=uow)
    assert bug_id
    async with uow:
        found_bugs: list[Bugs] = await uow.bugs.list()
        found_events: list[EventStore] = await uow.event_store.get(bug_id)
        assert len(found_bugs) == 1
        assert found_bugs[0].urgency == "high"
        assert found_bugs[0].edited is True
        assert bug_id == found_bugs[0].id
        assert found_events, len(found_events) == 2
        assert bug_id == found_events[0].aggregate_id
        assert found_events[1].event_name == "BugUpdated"


@pytest.mark.asyncio
async def test_soft_delete_bug_handler(
    uow: AbstractUnitOfWork,
    create_bug_id: tuple[UUID, UUID],
):
    bug_id, user_id = create_bug_id
    cmd = commands.SoftDeleteBug(id=bug_id, author_id=user_id)
    await handlers.soft_delete_bug(cmd, uow=uow)
    async with uow:
        found_bugs: list[Bugs] = await uow.bugs.list()
        found_events: list[EventStore] = await uow.event_store.get(bug_id)
        assert len(found_bugs) == 1
        assert found_bugs[0].record_status == "deleted"
        assert bug_id == found_bugs[0].id
        assert found_events, len(found_events) == 2
        assert bug_id == found_events[0].aggregate_id
        assert found_events[1].event_name == "BugSoftDeleted"


@pytest.mark.asyncio
async def test_create_comment_handler(
    uow: AbstractUnitOfWork,
    comment_data_in: dict,
    create_bug_id: tuple[UUID, UUID],
):
    bug_id, user_id = create_bug_id
    cmd = commands.CreateComment(bug_id=bug_id, author_id=user_id, text=comment_data_in["text"])
    comment_id = await handlers.create_comment(cmd, uow=uow)
    assert comment_id
    async with uow:
        found_bugs: list[Bugs] = await uow.bugs.list()
        found_events: list[EventStore] = await uow.event_store.get(bug_id)
        assert len(found_bugs[0].comments) == 1
        assert found_events, len(found_events) == 2
        assert found_events[1].event_name == "CommentCreated"


@pytest.mark.asyncio
async def test_update_comment_handler(
    uow: AbstractUnitOfWork,
    comment_data_in: dict,
    create_bug_id: tuple[UUID, UUID],
):
    bug_id, user_id = create_bug_id
    cmd = commands.CreateComment(bug_id=bug_id, author_id=user_id, text=comment_data_in["text"])
    comment_id = await handlers.create_comment(cmd, uow=uow)
    new_text = "witty and original comment"
    update_cmd = commands.UpdateComment(id=comment_id, bug_id=bug_id, author_id=user_id, text=new_text)
    await handlers.update_comment(update_cmd, uow=uow)
    async with uow:
        found_bugs: list[Bugs] = await uow.bugs.list()
        found_events: list[EventStore] = await uow.event_store.get(bug_id)
        assert len(found_bugs[0].comments) == 1
        assert found_bugs[0].comments[0].text == new_text
        assert found_bugs[0].comments[0].edited is True
        assert found_events, len(found_events) == 3
        assert found_events[2].event_name == "CommentUpdated"


@pytest.mark.asyncio
async def test_delete_comment_handler(
    uow: AbstractUnitOfWork,
    comment_data_in: dict,
    create_bug_id: tuple[UUID, UUID],
):
    bug_id, user_id = create_bug_id
    cmd = commands.CreateComment(bug_id=bug_id, author_id=user_id, text=comment_data_in["text"])
    comment_id = await handlers.create_comment(cmd, uow=uow)
    delete_cmd = commands.DeleteComment(id=comment_id, bug_id=bug_id, author_id=user_id)
    await handlers.delete_comment(delete_cmd, uow=uow)
    async with uow:
        found_bugs: list[Bugs] = await uow.bugs.list()
        found_events: list[EventStore] = await uow.event_store.get(bug_id)
        assert len(found_bugs[0].comments) == 0
        assert found_events, len(found_events) == 3
        assert found_events[2].event_name == "CommentDeleted"
