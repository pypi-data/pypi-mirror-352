"""Tests for the AnsweringMachineClient and related configuration logic."""

import pytest
import requests
from flask import Flask

from zecmf.clients import answering_machine
from zecmf.clients.answering_machine import (
    AnsweringMachineClient,
    MessageCreate,
    _AnsweringMachineConfig,  # noqa: PLC2701
)

HTTP_ERROR_STATUS = 400


class DummyResponse:
    """A dummy response object to mock requests.Response for testing."""

    def __init__(self, json_data: object, status_code: int = 201) -> None:
        """Initialize DummyResponse.

        Args:
            json_data: The JSON data to return from .json().
            status_code: The HTTP status code to simulate.

        """
        self._json = json_data
        self.status_code = status_code
        self.text = str(json_data)

    def json(self) -> object:
        """Return the stored JSON data."""
        return self._json

    def raise_for_status(self) -> None:
        """Raise HTTPError if status code indicates an error."""
        if self.status_code >= HTTP_ERROR_STATUS:
            raise requests.exceptions.HTTPError(response=None)  # type: ignore[arg-type]


TIMEOUT_APP_CONFIG = 42
TIMEOUT_DIRECT_ARGS = 5


def test_answering_machine_client_init_with_app(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test initialization of AnsweringMachineClient using Flask app config."""
    app = Flask("test")
    app.config["CLIENT_ANSWERING_MACHINE_URL"] = "https://am.example.com"
    app.config["CLIENT_ANSWERING_MACHINE_KEY"] = "test-key"
    app.config["CLIENT_ANSWERING_MACHINE_TIMEOUT"] = TIMEOUT_APP_CONFIG
    answering_machine.init_app(app)
    client = AnsweringMachineClient()
    assert client.base_url == "https://am.example.com"
    assert client.api_key == "test-key"
    assert client.timeout == TIMEOUT_APP_CONFIG


def test_answering_machine_client_init_with_direct_args() -> None:
    """Test initialization of AnsweringMachineClient using direct arguments."""
    client = AnsweringMachineClient(
        base_url="https://direct.example.com",
        api_key="direct-key",
        timeout=TIMEOUT_DIRECT_ARGS,
    )
    assert client.base_url == "https://direct.example.com"
    assert client.api_key == "direct-key"
    assert client.timeout == TIMEOUT_DIRECT_ARGS


def test_answering_machine_client_init_missing_config() -> None:
    """Test that missing configuration raises ValueError."""
    _AnsweringMachineConfig.base_url = None
    _AnsweringMachineConfig.api_key = None
    _AnsweringMachineConfig.timeout = 100
    with pytest.raises(
        ValueError, match="Answering Machine API base URL not configured"
    ):
        AnsweringMachineClient()


def test_answering_machine_client_create_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test creating a message using the AnsweringMachineClient."""
    app = Flask("test")
    app.config["CLIENT_ANSWERING_MACHINE_URL"] = "https://am.example.com"
    app.config["CLIENT_ANSWERING_MACHINE_KEY"] = "test-key"
    answering_machine.init_app(app)
    client = AnsweringMachineClient()
    message_data = {
        "id": 1,
        "content": "Hello!",
        "agent_id": "agent-123",
        "created_at": "2025-05-28T12:00:00Z",
        "read": False,
    }
    monkeypatch.setattr(requests, "post", lambda *a, **k: DummyResponse(message_data))
    req = MessageCreate(content="Hello!")
    resp = client.create_message(req)
    assert resp.id == 1
    assert resp.content == "Hello!"
    assert resp.agent_id == "agent-123"
    assert resp.read is False


def test_answering_machine_client_error_handling(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test error handling when the AnsweringMachineClient receives an error response."""
    app = Flask("test")
    app.config["CLIENT_ANSWERING_MACHINE_URL"] = "https://am.example.com"
    app.config["CLIENT_ANSWERING_MACHINE_KEY"] = "test-key"
    answering_machine.init_app(app)
    client = AnsweringMachineClient()
    monkeypatch.setattr(
        requests,
        "post",
        lambda *a, **k: DummyResponse({"error": "fail"}, status_code=401),
    )
    req = MessageCreate(content="fail")
    with pytest.raises(requests.exceptions.HTTPError):
        client.create_message(req)
