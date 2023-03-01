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
        found_bug: list[Bugs] = await uow.bugs.list()
        found_events: list[EventStore] = await uow.event_store.get(bug_id)
        assert len(found_bug) == 1
        assert bug_id == found_bug[0].id
        assert found_events, len(found_events) == 1
        assert bug_id == found_events[0].aggregate_id
        assert found_events[0].event_name == "BugCreated"


@pytest.mark.asyncio
async def test_update_bug_handler(uow: AbstractUnitOfWork, bug_data_in: dict, create_bug_id: tuple[UUID, UUID]):
    bug_id, _user_id = create_bug_id
    bug_data_in["id"] = bug_id
    bug_data_in["urgency"] = "high"
    cmd = commands.UpdateBug(**bug_data_in)
    bug_id = await handlers.update_bug(cmd, uow=uow)
    assert bug_id
    async with uow:
        found_bug: list[Bugs] = await uow.bugs.list()
        found_events: list[EventStore] = await uow.event_store.get(bug_id)
        assert len(found_bug) == 1
        assert found_bug[0].urgency == "high"
        assert bug_id == found_bug[0].id
        assert found_events, len(found_events) == 2
        assert bug_id == found_events[0].aggregate_id
        assert found_events[1].event_name == "BugUpdated"
