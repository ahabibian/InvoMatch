from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient


def _import_app():
    candidates = [
        "invomatch.api.app:app",
        "invomatch.api.main:app",
        "invomatch.main:app",
        "app.main:app",
    ]
    errors = []

    for candidate in candidates:
        module_name, app_name = candidate.split(":")
        try:
            module = __import__(module_name, fromlist=[app_name])
            return getattr(module, app_name)
        except Exception as exc:  # pragma: no cover
            errors.append(f"{candidate} -> {exc}")

    joined = "\n".join(errors)
    raise RuntimeError(f"Unable to import FastAPI app from known candidates:\n{joined}")


@pytest.fixture(scope="session")
def app():
    os.environ.setdefault("PYTHONPATH", "src")
    return _import_app()


@pytest.fixture()
def client(app):
    return TestClient(app)