"""Unit tests for Evernote configuration management."""

import os

import pytest

from evernote_mcp.config import EvernoteConfig


class TestEvernoteConfig:
    """Test EvernoteConfig dataclass and factory methods."""

    def test_config_creation_with_defaults(self):
        """Test creating a config with default values."""
        config = EvernoteConfig(auth_token="test_token")

        assert config.auth_token == "test_token"
        assert config.backend == "evernote"
        assert config.network_retry_count == 5
        assert config.use_system_ssl_ca is False

    def test_config_creation_with_custom_values(self):
        """Test creating a config with custom values."""
        config = EvernoteConfig(
            auth_token="test_token",
            backend="china",
            network_retry_count=10,
            use_system_ssl_ca=True,
        )

        assert config.auth_token == "test_token"
        assert config.backend == "china"
        assert config.network_retry_count == 10
        assert config.use_system_ssl_ca is True

    def test_from_env_with_valid_token(self, mock_env_token):
        """Test loading config from environment variables."""
        config = EvernoteConfig.from_env()

        assert config.auth_token == "test_auth_token"
        assert config.backend == "evernote"
        assert config.network_retry_count == 5
        assert config.use_system_ssl_ca is False

    def test_from_env_missing_token(self, monkeypatch):
        """Test that missing auth token raises ValueError."""
        monkeypatch.delenv("EVERNOTE_AUTH_TOKEN", raising=False)

        with pytest.raises(ValueError) as exc_info:
            EvernoteConfig.from_env()

        assert "EVERNOTE_AUTH_TOKEN" in str(exc_info.value)

    def test_from_env_custom_backend(self, monkeypatch):
        """Test loading custom backend from environment."""
        monkeypatch.setenv("EVERNOTE_AUTH_TOKEN", "test_token")
        monkeypatch.setenv("EVERNOTE_BACKEND", "china")

        config = EvernoteConfig.from_env()
        assert config.backend == "china"

    def test_from_env_china_sandbox_backend(self, monkeypatch):
        """Test loading china:sandbox backend from environment."""
        monkeypatch.setenv("EVERNOTE_AUTH_TOKEN", "test_token")
        monkeypatch.setenv("EVERNOTE_BACKEND", "china:sandbox")

        config = EvernoteConfig.from_env()
        assert config.backend == "china:sandbox"

    def test_from_env_invalid_backend(self, monkeypatch):
        """Test that invalid backend raises ValueError."""
        monkeypatch.setenv("EVERNOTE_AUTH_TOKEN", "test_token")
        monkeypatch.setenv("EVERNOTE_BACKEND", "invalid")

        with pytest.raises(ValueError) as exc_info:
            EvernoteConfig.from_env()

        assert "Invalid backend" in str(exc_info.value)

    def test_from_env_custom_retry_count(self, monkeypatch):
        """Test loading custom retry count from environment."""
        monkeypatch.setenv("EVERNOTE_AUTH_TOKEN", "test_token")
        monkeypatch.setenv("EVERNOTE_RETRY_COUNT", "10")

        config = EvernoteConfig.from_env()
        assert config.network_retry_count == 10

    def test_from_env_use_system_ssl_ca_true(self, monkeypatch):
        """Test loading SSL CA setting when true."""
        monkeypatch.setenv("EVERNOTE_AUTH_TOKEN", "test_token")
        monkeypatch.setenv("EVERNOTE_USE_SYSTEM_SSL_CA", "true")

        config = EvernoteConfig.from_env()
        assert config.use_system_ssl_ca is True

    def test_from_env_use_system_ssl_ca_false(self, monkeypatch):
        """Test loading SSL CA setting when false."""
        monkeypatch.setenv("EVERNOTE_AUTH_TOKEN", "test_token")
        monkeypatch.setenv("EVERNOTE_USE_SYSTEM_SSL_CA", "false")

        config = EvernoteConfig.from_env()
        assert config.use_system_ssl_ca is False

    def test_from_env_use_system_ssl_ca_case_insensitive(self, monkeypatch):
        """Test that SSL CA setting is case insensitive."""
        monkeypatch.setenv("EVERNOTE_AUTH_TOKEN", "test_token")

        for value in ["True", "TRUE", "True", "1", "yes"]:
            monkeypatch.setenv("EVERNOTE_USE_SYSTEM_SSL_CA", value)
            config = EvernoteConfig.from_env()
            assert config.use_system_ssl_ca is (value.lower() == "true")

    def test_from_env_all_custom_settings(self, monkeypatch):
        """Test loading all custom settings from environment."""
        monkeypatch.setenv("EVERNOTE_AUTH_TOKEN", "custom_token")
        monkeypatch.setenv("EVERNOTE_BACKEND", "china")
        monkeypatch.setenv("EVERNOTE_RETRY_COUNT", "15")
        monkeypatch.setenv("EVERNOTE_USE_SYSTEM_SSL_CA", "true")

        config = EvernoteConfig.from_env()
        assert config.auth_token == "custom_token"
        assert config.backend == "china"
        assert config.network_retry_count == 15
        assert config.use_system_ssl_ca is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
