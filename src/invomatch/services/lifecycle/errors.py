from __future__ import annotations


class RunLifecycleError(Exception):
    pass


class InvalidRunStateError(RunLifecycleError):
    pass


class InvalidRunTransitionError(RunLifecycleError):
    pass


class TerminalRunStateError(RunLifecycleError):
    pass


class LifecycleOperationNotAllowedError(RunLifecycleError):
    pass