from invomatch.services.actions.dispatcher import ActionDispatcher


class DummyHandler:
    def handle(self, command):
        return "ok"


def test_dispatcher_resolves_handler():
    dispatcher = ActionDispatcher()
    dispatcher.register("test_action", DummyHandler)

    handler_cls = dispatcher.get_handler("test_action")

    assert handler_cls == DummyHandler