import copy

from app.domain import enums
from app.domain.models import Bugs, Comments
from app.service.bugs import events


def test_bug_creation(bug_data_in: dict):
    new_bug = Bugs.create_bug(bug_data_in)
    for key, value in bug_data_in.items():
        assert value == getattr(new_bug, key)

    assert len(new_bug.events) == 1, isinstance(new_bug.events[0], events.BugCreated)

    created_event = new_bug.events[0]
    bug_from_event = created_event.apply(Bugs())
    for key, value in bug_data_in.items():
        assert value == getattr(bug_from_event, key)


def test_bug_update(bug_data_in: dict):
    new_bug = Bugs.create_bug(bug_data_in)
    update_data = copy.deepcopy(bug_data_in)
    update_data["id"] = new_bug.id
    update_data["status"] = enums.BugStatusEnum.IN_PROGRESS
    new_bug.update_bug(update_data)
    assert new_bug.status == enums.BugStatusEnum.IN_PROGRESS
    assert new_bug.edited is True

    assert len(new_bug.events) == 2
    assert isinstance(new_bug.events[0], events.BugCreated)
    assert isinstance(new_bug.events[1], events.BugUpdated)

    bug_from_event = Bugs()
    for event in new_bug.events:
        event.apply(bug_from_event)
    assert new_bug.status == enums.BugStatusEnum.IN_PROGRESS
    assert new_bug.edited is True


def test_bug_delete(bug_data_in: dict):
    new_bug = Bugs.create_bug(bug_data_in)
    new_bug.delete_bug()
    assert new_bug.record_status == enums.RecordStatusEnum.DELETED

    assert len(new_bug.events) == 2
    assert isinstance(new_bug.events[0], events.BugCreated)
    assert isinstance(new_bug.events[1], events.BugSoftDeleted)

    bug_from_event = Bugs()
    for event in new_bug.events:
        event.apply(bug_from_event)
    assert new_bug.record_status == enums.RecordStatusEnum.DELETED


def test_comment_creation(bug_data_in: dict, comment_data_in: dict):
    new_bug = Bugs.create_bug(bug_data_in)
    comment_data_in["bug_id"] = new_bug.id
    new_bug.add_comment(comment_data_in)
    assert len(new_bug.comments) == 1
    assert len(new_bug.events) == 2
    assert isinstance(new_bug.events[1], events.CommentCreated)

    comment = new_bug.comments[0]
    for key, value in comment_data_in.items():
        if key == "bug_id":
            assert value == new_bug.id
        else:
            assert value == getattr(comment, key)

    comment_created = new_bug.events[1]
    comment_from_event = comment_created.apply(Comments())
    for key, value in comment_data_in.items():
        if key == "bug_id":
            assert value == new_bug.id
        else:
            assert value == getattr(comment_from_event, key)


def test_comment_update(bug_data_in: dict, comment_data_in: dict):
    new_bug = Bugs.create_bug(bug_data_in)
    comment_data_in["bug_id"] = new_bug.id
    comment = new_bug.add_comment(comment_data_in)

    update_data = copy.deepcopy(comment_data_in)
    update_data["id"] = comment.id
    update_data["text"] = "funny and original comment"
    updated_comment = new_bug.update_comment(comment.id, update_data)
    assert updated_comment.text == update_data["text"]
    assert updated_comment.edited is True

    assert len(new_bug.comments) == 1
    assert len(new_bug.events) == 3
    assert isinstance(new_bug.events[-1], events.CommentUpdated)

    comment_from_event = Comments()
    for event in new_bug.events:
        if isinstance(event, events.BugCreated):
            pass
        else:
            event.apply(comment_from_event)
    assert comment_from_event.text == update_data["text"]
    assert comment_from_event.edited is True


def test_comment_delete(bug_data_in: dict, comment_data_in: dict):
    new_bug = Bugs.create_bug(bug_data_in)
    comment_data_in["bug_id"] = new_bug.id
    comment = new_bug.add_comment(comment_data_in)
    new_bug.delete_comment(comment.id)
    assert len(new_bug.comments) == 0
