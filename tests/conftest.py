import os
import sys
from typing import Iterator, List, Tuple

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402

PIN = "123456"


class FakeController:
    """Records calls instead of touching the real mouse, keyboard and screen."""

    width = 1920
    height = 1080

    def __init__(self) -> None:
        self.calls: List[Tuple] = []
        self.fail_next = False

    def _record(self, *call) -> None:
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("boom")
        self.calls.append(call)

    def click(self, x: int, y: int) -> None:
        self._record("click", x, y)

    def write(self, text: str) -> None:
        self._record("write", text)

    def press(self, key: str) -> None:
        self._record("press", key)

    def key_down(self, key: str) -> None:
        self._record("key_down", key)

    def key_up(self, key: str) -> None:
        self._record("key_up", key)

    def frames(self) -> Iterator[bytes]:
        yield b"fake-jpeg"


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def desktop() -> FakeController:
    return FakeController()


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def app(desktop, clock):
    return create_app(controller=desktop, pin=PIN, clock=clock)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authed(app):
    client = app.test_client()
    response = client.post("/login", data={"pin": PIN})
    assert response.status_code == 302
    return client
