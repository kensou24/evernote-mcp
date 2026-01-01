"""Configuration management for Evernote MCP server."""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class EvernoteConfig:
    """Evernote configuration from environment variables."""

    auth_token: str
    backend: str = "evernote"
    network_retry_count: int = 5
    use_system_ssl_ca: bool = False

    @classmethod
    def from_env(cls) -> "EvernoteConfig":
        """Load configuration from environment variables."""
        auth_token = os.getenv("EVERNOTE_AUTH_TOKEN")
        if not auth_token:
            raise ValueError(
                "EVERNOTE_AUTH_TOKEN environment variable is required. "
                "Get your token from: https://evernote.com/api/DeveloperToken.action"
            )

        backend = os.getenv("EVERNOTE_BACKEND", "evernote")
        if backend not in ("evernote", "china", "china:sandbox"):
            raise ValueError(f"Invalid backend: {backend}")

        return cls(
            auth_token=auth_token,
            backend=backend,
            network_retry_count=int(os.getenv("EVERNOTE_RETRY_COUNT", "5")),
            use_system_ssl_ca=os.getenv("EVERNOTE_USE_SYSTEM_SSL_CA", "false").lower() == "true",
        )
