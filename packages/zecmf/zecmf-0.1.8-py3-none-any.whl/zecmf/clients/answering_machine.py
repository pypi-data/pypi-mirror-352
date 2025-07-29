"""Answering Machine API client and data models for interacting with the Answering Machine service.

This module provides the AnsweringMachineClient class for communicating with the Answering Machine API, as well as dataclasses for MessageCreate and Message.
"""

from dataclasses import dataclass

import requests
from flask import Flask


@dataclass
class MessageCreate:
    """Represents a request payload for creating a message."""

    content: str


@dataclass
class Message:
    """Represents a message returned by the Answering Machine API."""

    id: int
    content: str
    agent_id: str
    created_at: str
    read: bool


class _AnsweringMachineConfig:
    """Singleton config holder for Answering Machine client settings."""

    base_url: str | None = None
    api_key: str | None = None
    timeout: int = 100

    @classmethod
    def set_config(cls, base_url: str, api_key: str, timeout: int = 100) -> None:
        cls.base_url = base_url
        cls.api_key = api_key
        cls.timeout = timeout

    @classmethod
    def is_configured(cls) -> bool:
        return cls.base_url is not None and cls.api_key is not None


def init_app(app: Flask) -> None:
    """Register the Flask app for Answering Machine client configuration."""
    base_url = app.config.get("CLIENT_ANSWERING_MACHINE_URL")
    api_key = app.config.get("CLIENT_ANSWERING_MACHINE_KEY")
    timeout = app.config.get("CLIENT_ANSWERING_MACHINE_TIMEOUT", 100)
    if not base_url:
        raise ValueError("CLIENT_ANSWERING_MACHINE_URL must be set in app config.")
    if not api_key:
        raise ValueError("CLIENT_ANSWERING_MACHINE_KEY must be set in app config.")
    _AnsweringMachineConfig.set_config(base_url, api_key, timeout)


class AnsweringMachineClient:
    """Client for interacting with the Answering Machine API endpoints."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Initialize the AnsweringMachineClient with configuration.

        Args:
            base_url: Optional base URL for the Answering Machine API.
            api_key: Optional API key for authentication.
            timeout: Optional request timeout in seconds.

        Raises:
            ValueError: If required configuration is missing.

        """
        self.base_url = None
        self.api_key = None
        self.timeout = None
        if base_url is not None:
            self.base_url = base_url
        elif (
            _AnsweringMachineConfig.is_configured()
            and _AnsweringMachineConfig.base_url is not None
        ):
            self.base_url = _AnsweringMachineConfig.base_url
        if api_key is not None:
            self.api_key = api_key
        elif (
            _AnsweringMachineConfig.is_configured()
            and _AnsweringMachineConfig.api_key is not None
        ):
            self.api_key = _AnsweringMachineConfig.api_key
        if timeout is not None:
            self.timeout = timeout
        elif (
            _AnsweringMachineConfig.is_configured()
            and _AnsweringMachineConfig.timeout is not None
        ):
            self.timeout = _AnsweringMachineConfig.timeout
        if not self.base_url:
            raise ValueError(
                "Answering Machine API base URL not configured (CLIENT_ANSWERING_MACHINE_URL)"
            )
        if not self.api_key:
            raise ValueError(
                "Answering Machine API key not configured (CLIENT_ANSWERING_MACHINE_KEY)"
            )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def create_message(self, payload: MessageCreate) -> Message:
        """Create a new message (agent role required)."""
        resp = requests.post(
            f"{self.base_url}/api/v1/messages",
            headers=self._headers(),
            json={"content": payload.content},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return Message(**resp.json())
