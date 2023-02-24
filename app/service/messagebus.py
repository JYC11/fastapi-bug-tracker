import inspect
from collections import deque
from typing import Any, Callable, Type, Union

from argon2 import PasswordHasher

from app.domain.commands import Command
from app.domain.events import Event
from app.service.unit_of_work import AbstractUnitOfWork

Message = Union[Command, Event]


class MessageBus:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        event_handlers: dict[Type[Event], list[Callable]],
        command_handlers: dict[Type[Command], Callable],
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    async def handle(self, message: Message):
        self.queue = deque([message])
        results = []
        while self.queue:
            message = self.queue.popleft()
            if isinstance(message, Event):
                await self.handle_event(message)
            elif isinstance(message, Command):
                res = await self.handle_command(message)
                results.append(res)
            else:
                raise Exception(f"{message} was not a Command or Event")
        return results[0]

    async def handle_event(self, event: Event):
        for handler in self.event_handlers[type(event)]:
            try:
                task = handler(event)
                if inspect.isawaitable(task):
                    await task
                else:
                    pass
                self.queue.extend(self.uow.collect_new_events())
            except Exception:
                continue  # TODO: add logging when exception is raised

    async def handle_command(self, command: Command):
        try:
            handler = self.command_handlers[type(command)]
            task = handler(command)
            if inspect.isawaitable(task):
                res = await task
            else:
                res = task
            self.queue.extend(self.uow.collect_new_events())
            return res
        except Exception:
            raise


def inject_dependencies(handler: Callable, dependencies: dict[str, Any]):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency for name, dependency in dependencies.items() if name in params
    }
    return lambda message: handler(message, **deps)


EVENT_HANDLERS: dict[Type[Event], list[Callable]] = {}
COMMAND_HANDLERS: dict[Type[Command], Callable] = {}


class MessageBusFactory:
    def __init__(self, uow: AbstractUnitOfWork, password_hasher: PasswordHasher):
        self.uow = uow
        self.password_hasher = password_hasher

    def __call__(self) -> MessageBus:
        dependencies = {
            "uow": self.uow,
            "hasher": self.password_hasher,
        }
        injected_event_handlers: dict[Type[Event], list[Callable]] = {
            event_type: [
                inject_dependencies(handler, dependencies) for handler in handlers
            ]
            for event_type, handlers in EVENT_HANDLERS.items()
        }
        injected_command_handlers: dict[Type[Command], Callable] = {
            command_type: inject_dependencies(handler, dependencies)
            for command_type, handler in COMMAND_HANDLERS.items()
        }
        return MessageBus(
            uow=self.uow,
            event_handlers=injected_event_handlers,
            command_handlers=injected_command_handlers,
        )
