"""Pytest configuration.

Shuts down the ddtrace tracer at session start so tests don't produce
"failed to send" noise when no Datadog Agent is running locally.
"""

import pytest
from ddtrace import tracer
from fastapi.testclient import TestClient

from app.main import fastapi_app


@pytest.fixture(autouse=True, scope="session")
def disable_ddtrace_writer():
    """Shut down the ddtrace tracer for the entire test session."""
    tracer.shutdown()
    yield


@pytest.fixture(scope="session")
def app():
    return fastapi_app


@pytest.fixture()
def client(app):
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def create_item(client):
    def _create_item(**overrides):
        payload = {"name": "Widget", "price": 9.99}
        payload.update(overrides)
        return client.post("/items", json=payload)

    return _create_item


@pytest.fixture(autouse=True)
def reset_items_store():
    from app.routes import items as items_module

    items_module._state["items"].clear()
    items_module._state["counter"] = 0
    yield
