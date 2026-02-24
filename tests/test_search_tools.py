"""Integration tests for search tools."""

import json
from unittest.mock import MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.tools.search_tools import register_search_tools


class MockNoteMetadata:
    def __init__(
        self,
        guid: str = "note-guid",
        title: str = "Test Note",
        notebook_guid: str = "nb-guid",
    ):
        self.guid = guid
        self.title = title
        self.notebookGuid = notebook_guid
        self.updated = 1704067200000
        self.created = 1704067200000


class MockNotesMetadataResult:
    def __init__(self, notes: list | None = None, total: int = 0):
        self.notes = notes or []
        self.totalNotes = total


class TestSearchTools:
    """Integration tests for search MCP tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()

        mock_note = MockNoteMetadata()
        mock_result = MockNotesMetadataResult(notes=[mock_note], total=1)
        mock.find_notes.return_value = mock_result

        mock_tag = MagicMock()
        mock_tag.guid = "tag-1"
        mock_tag.name = "test"
        mock_tag.parentGuid = None
        mock.list_tags.return_value = [mock_tag]

        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_search_notes_basic(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        search_tool = tools.get("search_notes")

        if search_tool:
            result = search_tool.fn(query="test query")
            data = json.loads(result)
            assert data["success"] is True
            assert data["query"] == "test query"
            assert data["count"] == 1
            assert len(data["notes"]) == 1

    def test_search_notes_with_notebook_filter(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        search_tool = tools.get("search_notes")

        if search_tool:
            result = search_tool.fn(query="test", notebook_guid="nb-guid")
            data = json.loads(result)
            assert data["success"] is True

            mock_client.find_notes.assert_called_once_with("test", "nb-guid", 100)

    def test_search_notes_with_custom_limit(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        search_tool = tools.get("search_notes")

        if search_tool:
            result = search_tool.fn(query="test", limit=50)
            data = json.loads(result)
            assert data["success"] is True

            mock_client.find_notes.assert_called_once_with("test", None, 50)

    def test_search_notes_returns_note_info(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        search_tool = tools.get("search_notes")

        if search_tool:
            result = search_tool.fn(query="test")
            data = json.loads(result)
            assert data["success"] is True

            note = data["notes"][0]
            assert note["guid"] == "note-guid"
            assert note["title"] == "Test Note"
            assert note["notebook_guid"] == "nb-guid"
            assert "updated" in note

    def test_search_notes_empty_result(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        mock_result = MockNotesMetadataResult(notes=[], total=0)
        mock_client.find_notes.return_value = mock_result

        tools = mcp._tool_manager._tools
        search_tool = tools.get("search_notes")

        if search_tool:
            result = search_tool.fn(query="nonexistent")
            data = json.loads(result)
            assert data["success"] is True
            assert data["total"] == 0
            assert data["count"] == 0
            assert len(data["notes"]) == 0

    def test_search_notes_multiple_results(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        note1 = MockNoteMetadata(guid="n1", title="Note 1")
        note2 = MockNoteMetadata(guid="n2", title="Note 2")
        mock_result = MockNotesMetadataResult(notes=[note1, note2], total=2)
        mock_client.find_notes.return_value = mock_result

        tools = mcp._tool_manager._tools
        search_tool = tools.get("search_notes")

        if search_tool:
            result = search_tool.fn(query="test")
            data = json.loads(result)
            assert data["success"] is True
            assert data["total"] == 2
            assert data["count"] == 2
            assert len(data["notes"]) == 2

    def test_list_tags(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_tags")

        if list_tool:
            result = list_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert "tags" in data
            assert len(data["tags"]) == 1
            assert data["tags"][0]["name"] == "test"

    def test_list_tags_multiple(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        tag1 = MagicMock()
        tag1.guid = "tag-1"
        tag1.name = "important"
        tag1.parentGuid = None

        tag2 = MagicMock()
        tag2.guid = "tag-2"
        tag2.name = "work"
        tag2.parentGuid = "tag-1"

        mock_client.list_tags.return_value = [tag1, tag2]

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_tags")

        if list_tool:
            result = list_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert len(data["tags"]) == 2
            assert data["tags"][0]["name"] == "important"
            assert data["tags"][1]["parent_guid"] == "tag-1"

    def test_list_tags_empty(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        mock_client.list_tags.return_value = []

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_tags")

        if list_tool:
            result = list_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert len(data["tags"]) == 0


class TestSearchToolsErrorHandling:
    """Test error handling in search tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        mock.find_notes.side_effect = Exception("Search failed")
        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_search_notes_handles_error(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        search_tool = tools.get("search_notes")

        if search_tool:
            result = search_tool.fn(query="test")
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data

    def test_list_tags_handles_error(self, mock_client, mcp):
        register_search_tools(mcp, mock_client)

        mock_client.list_tags.side_effect = Exception("Failed to list tags")

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_tags")

        if list_tool:
            result = list_tool.fn()
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
