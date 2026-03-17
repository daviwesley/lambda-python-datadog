"""Pytest configuration.

Shuts down the ddtrace tracer at session start so tests don't produce
"failed to send" noise when no Datadog Agent is running locally.
"""

import pytest
from ddtrace import tracer


@pytest.fixture(autouse=True, scope="session")
def disable_ddtrace_writer():
    """Shut down the ddtrace tracer for the entire test session."""
    tracer.shutdown()
    yield
