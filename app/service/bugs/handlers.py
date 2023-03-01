from sqlalchemy.future import select

from app.domain.models import Bugs, Comments
from app.service import exceptions as exc
from app.service.bugs import commands
from app.service.unit_of_work import AbstractUnitOfWork


async def create_bug(cmd: commands.CreateBug, *, uow: AbstractUnitOfWork):
    async with uow:
        new_bug: Bugs = Bugs.create_bug(cmd.dict())
        uow.bugs.add(new_bug)
        uow.event_store.add(new_bug.generate_event_store())
        await uow.commit()
        return new_bug.id


async def update_bug(cmd: commands.UpdateBug, *, uow: AbstractUnitOfWork):
    async with uow:
        bug: Bugs | None = await uow.bugs.get(cmd.id)
        if not bug:
            raise exc.ItemNotFound(f"bug with id {cmd.id} not found")
        if bug.author_id != cmd.author_id:
            raise exc.Forbidden("user is forbidden from editing this report")
        bug.update_bug(cmd.dict(exclude_unset=True))
        uow.event_store.add(bug.generate_event_store())
        await uow.commit()
        return bug.id


async def soft_delete_bug(cmd: commands.SoftDeleteBug, *, uow: AbstractUnitOfWork):
    async with uow:
        bug: Bugs | None = await uow.bugs.get(cmd.id)
        if not bug:
            raise exc.ItemNotFound(f"bug with id {cmd.id} not found")
        if bug.author_id != cmd.author_id:
            raise exc.Forbidden("user is forbidden from editing this report")
        bug.delete_bug()
        uow.event_store.add(bug.generate_event_store())
        await uow.commit()
        return


async def create_comment(cmd: commands.CreateComment, *, uow: AbstractUnitOfWork):
    async with uow:
        bug: Bugs | None = await uow.bugs.get(cmd.bug_id)
        if not bug:
            raise exc.ItemNotFound(f"bug with id {cmd.bug_id} not found")
        comment: Comments = bug.add_comment(cmd.dict())
        uow.event_store.add(bug.generate_event_store())
        await uow.commit()
        return comment.id


async def update_comment(cmd: commands.UpdateComment, *, uow: AbstractUnitOfWork):
    async with uow:
        bug: Bugs | None = await uow.bugs.get(cmd.bug_id)
        if not bug:
            raise exc.ItemNotFound(f"bug with id {cmd.bug_id} not found")
        comment: Comments | None = bug.find_comment(cmd.id)
        if not comment:
            raise exc.ItemNotFound(f"comment with id {cmd.id} not found")
        if comment.author_id != cmd.author_id:
            raise exc.Forbidden("user is forbidden from editing")
        bug.update_comment(cmd.id, {"text": cmd.text})
        uow.event_store.add(bug.generate_event_store())
        await uow.commit()
        return comment.id


async def soft_delete_comment(cmd: commands.SoftDeleteComment, *, uow: AbstractUnitOfWork):
    async with uow:
        bug: Bugs | None = await uow.bugs.get(cmd.bug_id)
        if not bug:
            raise exc.ItemNotFound(f"bug with id {cmd.bug_id} not found")
        comment: Comments | None = bug.find_comment(cmd.id)
        if not comment:
            raise exc.ItemNotFound(f"comment with id {cmd.id} not found")
        if comment.author_id != cmd.author_id:
            raise exc.Forbidden("user is forbidden from editing")
        bug.delete_comment(cmd.id)
        uow.event_store.add(bug.generate_event_store())
        await uow.commit()
        return


async def upvote_downvote_comment(cmd: commands.Upvote | commands.Downvote, *, uow: AbstractUnitOfWork):
    async with uow:
        query = select(Bugs).join(Comments, Comments.bug_id == Bugs.id).where(Comments.id == cmd.id)
        execution = await uow.session.execute(query)
        bug: Bugs | None = execution.scalar_one_or_none()
        if bug:
            if isinstance(cmd, commands.Upvote):
                bug.upvote_comment(cmd.id)
            elif isinstance(cmd, commands.Downvote):
                bug.downvote_comment(cmd.id)
            uow.event_store.add(bug.generate_event_store())
            await uow.commit()
            return
        return None
