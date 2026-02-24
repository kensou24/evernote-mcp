"""Pytest configuration and shared fixtures for Evernote MCP tests."""

import json
from unittest.mock import MagicMock, patch
from typing import Generator

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.client import EvernoteMCPClient
from evernote_mcp.config import EvernoteConfig


# Mock classes for Evernote types
class MockNotebook:
    def __init__(
        self,
        guid: str = "test-notebook-guid",
        name: str = "Test Notebook",
        stack: str | None = None,
    ):
        self.guid = guid
        self.name = name
        self.stack = stack
        self.serviceCreated = 1704067200000
        self.serviceUpdated = 1704067200000
        self.defaultNotebook = False


class MockNote:
    def __init__(
        self,
        guid: str = "test-note-guid",
        title: str = "Test Note",
        notebook_guid: str = "test-notebook-guid",
    ):
        self.guid = guid
        self.title = title
        self.content = "<en-note><div>Test content</div></en-note>"
        self.notebookGuid = notebook_guid
        self.active = True
        self.tagGuids = []
        self.attributes = None
        self.created = 1704067200000
        self.updated = 1704067200000


class MockNoteAttributes:
    def __init__(self):
        self.reminderTime = None
        self.reminderOrder = None
        self.reminderDoneTime = None


class MockTag:
    def __init__(
        self,
        guid: str = "test-tag-guid",
        name: str = "test-tag",
        parent_guid: str | None = None,
    ):
        self.guid = guid
        self.name = name
        self.parentGuid = parent_guid


class MockSavedSearch:
    def __init__(
        self,
        guid: str = "test-search-guid",
        name: str = "Test Search",
        query: str = "test",
    ):
        self.guid = guid
        self.name = name
        self.query = query
        self.updateSequenceNum = 1


class MockResource:
    def __init__(self, guid: str = "test-resource-guid"):
        self.guid = guid
        self.mime = "image/png"
        self.data = MagicMock()
        self.data.body = b"fake image data"
        self.data.size = len(b"fake image data")
        self.attributes = MagicMock()
        self.attributes.fileName = "test.png"
        self.attributes.sourceURL = None


class MockNotesMetadataResult:
    def __init__(self, total_notes: int = 0, notes: list | None = None):
        self.totalNotes = total_notes
        self.startIndex = 0
        self.notes = notes or []


# Fixtures
@pytest.fixture
def mock_notebook() -> MockNotebook:
    """Create a mock Notebook object."""
    return MockNotebook()


@pytest.fixture
def mock_note() -> MockNote:
    """Create a mock Note object."""
    return MockNote()


@pytest.fixture
def mock_tag() -> MockTag:
    """Create a mock Tag object."""
    return MockTag()


@pytest.fixture
def mock_saved_search() -> MockSavedSearch:
    """Create a mock SavedSearch object."""
    return MockSavedSearch()


@pytest.fixture
def mock_resource() -> MockResource:
    """Create a mock Resource object."""
    return MockResource()


@pytest.fixture
def mock_note_attributes() -> MockNoteAttributes:
    """Create a mock NoteAttributes object."""
    return MockNoteAttributes()


@pytest.fixture
def mock_client() -> Generator[EvernoteMCPClient, None, None]:
    """Create a mock EvernoteMCPClient with mocked note_store."""
    with patch.object(EvernoteMCPClient, "__init__", lambda self, **kwargs: None):
        client = EvernoteMCPClient()
        client.note_store = MagicMock()
        client.user = MagicMock()
        client.user.username = "test_user"
        yield client


@pytest.fixture
def mcp_server() -> FastMCP:
    """Create a FastMCP server instance for testing."""
    return FastMCP("test-evernote-mcp")


@pytest.fixture
def sample_enml() -> str:
    """Sample ENML content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
<div><b>Bold text</b> and <i>italic</i></div>
<div>Regular paragraph</div>
<div><en-todo/></div>
<div><en-todo checked="true"/></div>
</en-note>"""


@pytest.fixture
def sample_text() -> str:
    """Sample plain text for testing."""
    return """Bold text and italic
Regular paragraph"""


# Environment variable fixtures
@pytest.fixture
def mock_env_token(monkeypatch) -> None:
    """Set up mock EVERNOTE_AUTH_TOKEN environment variable."""
    monkeypatch.setenv("EVERNOTE_AUTH_TOKEN", "test_auth_token")
    monkeypatch.setenv("EVERNOTE_BACKEND", "evernote")


@pytest.fixture
def mock_env_china_token(monkeypatch) -> None:
    """Set up mock environment variables for China backend."""
    monkeypatch.setenv("EVERNOTE_AUTH_TOKEN", "test_china_token")
    monkeypatch.setenv("EVERNOTE_BACKEND", "china")


# Helper functions
def parse_json_response(response: str) -> dict:
    """Parse JSON response from MCP tools."""
    return json.loads(response)


def assert_success_response(response: str) -> dict:
    """Assert that response is a success and return parsed data."""
    data = parse_json_response(response)
    assert data.get("success") is True, f"Expected success, got: {data}"
    return data


def assert_error_response(response: str, error_contains: str | None = None) -> dict:
    """Assert that response is an error and return parsed data."""
    data = parse_json_response(response)
    assert data.get("success") is False, f"Expected error, got: {data}"
    if error_contains:
        assert error_contains in data.get("error", ""), (
            f"Expected error containing '{error_contains}', got: {data.get('error')}"
        )
    return data
