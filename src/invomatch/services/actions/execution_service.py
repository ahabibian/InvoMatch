from typing import Any

from .dispatcher import ActionDispatcher


class ActionExecutionService:
    def __init__(self, dispatcher: ActionDispatcher) -> None:
        self._dispatcher = dispatcher

    def execute(self, command: Any) -> Any:
        handler_cls = self._dispatcher.get_handler(command.action_type)
        handler = handler_cls()
        return handler.handle(command)