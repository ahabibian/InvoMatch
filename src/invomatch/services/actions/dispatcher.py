from typing import Dict, Type


class ActionDispatcher:
    def __init__(self) -> None:
        self._handlers: Dict[str, Type] = {}

    def register(self, action_type: str, handler_cls: Type) -> None:
        self._handlers[action_type] = handler_cls

    def get_handler(self, action_type: str) -> Type:
        if action_type not in self._handlers:
            raise ValueError(f"No handler registered for action_type={action_type}")
        return self._handlers[action_type]