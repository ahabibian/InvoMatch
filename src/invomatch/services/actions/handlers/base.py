from typing import Any


class BaseActionHandler:
    def handle(self, command: Any) -> Any:
        raise NotImplementedError()