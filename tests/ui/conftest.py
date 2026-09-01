"""Fixtures for the Playwright UI tests.

Playwright drives a real browser, so it needs a real HTTP server rather than
Flask's test client. This starts the app on a free port in a background
thread for the duration of the test session and shuts it down afterwards,
so ``pytest`` on its own is enough - nothing has to be started by hand.
"""

import os
import socket
import threading

import pytest
from werkzeug.serving import make_server

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from mytemplate import create_app
from mytemplate.models import db
from mytemplate.models.user import User

UI_USER_EMAIL = "user@example.com"
UI_USER_PASSWORD = "safepassword"


def _free_port():
    """Ask the OS for an unused port so parallel runs don't collide."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    """Run the app on a background thread and yield its base URL."""
    app = create_app("mytemplate.settings.TestConfig")

    ctx = app.app_context()
    ctx.push()
    db.create_all()
    db.session.add(User(UI_USER_EMAIL, UI_USER_PASSWORD))
    db.session.commit()

    port = _free_port()
    server = make_server("127.0.0.1", port, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield f"http://127.0.0.1:{port}"

    server.shutdown()
    thread.join(timeout=5)
    db.session.remove()
    db.drop_all()
    ctx.pop()


@pytest.fixture(autouse=True)
def block_external_requests(page, live_server):
    """Fail fast instead of waiting on third-party CDNs.

    The templates pull Bootstrap, jQuery, Font Awesome, Stripe and Google
    Fonts from public CDNs. Waiting on those makes the suite depend on the
    network, so every request that is not served by the app under test is
    aborted. The tests then exercise our own markup and nothing else.
    """
    page.route(
        "**/*",
        lambda route: route.continue_()
        if route.request.url.startswith(live_server)
        else route.abort(),
    )
    return page
