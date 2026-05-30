import asyncio
import pytest


def pytest_collection_modifyitems(config, items):
    """
    Re-order tests so that E2E (Playwright) tests run last.

    Playwright's sync API keeps an event loop running in a background
    greenlet for the entire session.  When pytest-asyncio tries to create
    a fresh loop for async tests that follow an E2E test,
    ``_get_running_loop()`` is not None and ``run_until_complete`` raises
    ``RuntimeError: Cannot run the event loop while another loop is running``.

    Running all non-E2E tests first avoids the conflict.
    """
    e2e_items = [item for item in items if "e2e" in item.nodeid]
    other_items = [item for item in items if "e2e" not in item.nodeid]
    items[:] = other_items + e2e_items


@pytest.fixture(autouse=True)
def _cleanup_asyncio():
    """
    Ensure any aiosqlite connections or async fixtures are properly
    closed between tests so background threads do not callback into a
    closed event loop.
    """
    yield
    try:
        loop = asyncio.get_running_loop()
        if not loop.is_closed() and not loop.is_running():
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
    except RuntimeError:
        pass
