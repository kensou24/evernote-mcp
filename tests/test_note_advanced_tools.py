"""Integration tests for advanced note tools."""

import json
from unittest.mock import MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.tools.note_advanced_tools import register_note_advanced_tools


class MockNoteVersion:
    def __init__(
        self,
        usn: int = 1,
        updated: int = 1704067200000,
        title: str = "Old Title",
    ):
        self.updateSequenceNum = usn
        self.updated = updated
        self.saved = updated
        self.title = title


class TestNoteAdvancedTools:
    """Integration tests for advanced note MCP tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        mock.get_note_content.return_value = "<en-note><div>Content</div></en-note>"
        mock.get_note_search_text.return_value = "searchable text"
        mock.get_note_tag_names.return_value = ["tag1", "tag2", "important"]

        mock_version = MockNoteVersion()
        mock.list_note_versions.return_value = [mock_version]
        mock.get_note_version.return_value = MagicMock(
            guid="note-guid",
            title="Note v1",
            content="<en-note>Old content</en-note>",
            updateSequenceNum=1,
            updated=1704067200000,
        )

        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_get_note_content(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_content_tool = tools.get("get_note_content")

        if get_content_tool:
            result = get_content_tool.fn(guid="note-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "note-guid"
            assert data["content"] == "<en-note><div>Content</div></en-note>"

    def test_get_note_search_text_default(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_search_text_tool = tools.get("get_note_search_text")

        if get_search_text_tool:
            result = get_search_text_tool.fn(guid="note-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "note-guid"
            assert data["text"] == "searchable text"
            assert data["note_only"] is False
            assert data["tokenized"] is False

    def test_get_note_search_text_note_only(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_search_text_tool = tools.get("get_note_search_text")

        if get_search_text_tool:
            result = get_search_text_tool.fn(guid="note-guid", note_only=True)
            data = json.loads(result)
            assert data["success"] is True
            assert data["note_only"] is True

            mock_client.get_note_search_text.assert_called_once_with(
                "note-guid", True, False
            )

    def test_get_note_search_text_tokenized(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_search_text_tool = tools.get("get_note_search_text")

        if get_search_text_tool:
            result = get_search_text_tool.fn(
                guid="note-guid",
                tokenize_for_indexing=True
            )
            data = json.loads(result)
            assert data["success"] is True
            assert data["tokenized"] is True

            mock_client.get_note_search_text.assert_called_once_with(
                "note-guid", False, True
            )

    def test_get_note_search_text_all_options(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_search_text_tool = tools.get("get_note_search_text")

        if get_search_text_tool:
            result = get_search_text_tool.fn(
                guid="note-guid",
                note_only=True,
                tokenize_for_indexing=True
            )
            data = json.loads(result)
            assert data["success"] is True
            assert data["note_only"] is True
            assert data["tokenized"] is True

            mock_client.get_note_search_text.assert_called_once_with(
                "note-guid", True, True
            )

    def test_get_note_tag_names(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tags_tool = tools.get("get_note_tag_names")

        if get_tags_tool:
            result = get_tags_tool.fn(guid="note-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "note-guid"
            assert data["tag_names"] == ["tag1", "tag2", "important"]

    def test_get_note_tag_names_empty(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        mock_client.get_note_tag_names.return_value = []

        tools = mcp._tool_manager._tools
        get_tags_tool = tools.get("get_note_tag_names")

        if get_tags_tool:
            result = get_tags_tool.fn(guid="note-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["tag_names"] == []

    def test_list_note_versions(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        list_versions_tool = tools.get("list_note_versions")

        if list_versions_tool:
            result = list_versions_tool.fn(note_guid="note-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["note_guid"] == "note-guid"
            assert data["count"] == 1
            assert len(data["versions"]) == 1

            version = data["versions"][0]
            assert version["update_sequence_num"] == 1
            assert version["title"] == "Old Title"

    def test_list_note_versions_multiple(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        v1 = MockNoteVersion(usn=1, title="Version 1")
        v2 = MockNoteVersion(usn=2, title="Version 2")
        v3 = MockNoteVersion(usn=3, title="Version 3")
        mock_client.list_note_versions.return_value = [v1, v2, v3]

        tools = mcp._tool_manager._tools
        list_versions_tool = tools.get("list_note_versions")

        if list_versions_tool:
            result = list_versions_tool.fn(note_guid="note-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["count"] == 3
            assert len(data["versions"]) == 3

    def test_list_note_versions_empty(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        mock_client.list_note_versions.return_value = []

        tools = mcp._tool_manager._tools
        list_versions_tool = tools.get("list_note_versions")

        if list_versions_tool:
            result = list_versions_tool.fn(note_guid="note-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["count"] == 0
            assert len(data["versions"]) == 0

    def test_get_note_version(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_version_tool = tools.get("get_note_version")

        if get_version_tool:
            result = get_version_tool.fn(
                note_guid="note-guid",
                update_sequence_num=1
            )
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "note-guid"
            assert data["title"] == "Note v1"
            assert data["update_sequence_num"] == 1

    def test_get_note_version_with_resources(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_version_tool = tools.get("get_note_version")

        if get_version_tool:
            result = get_version_tool.fn(
                note_guid="note-guid",
                update_sequence_num=1,
                with_resources_data=True,
                with_resources_recognition=True,
                with_resources_alternate_data=True,
            )
            data = json.loads(result)
            assert data["success"] is True

            mock_client.get_note_version.assert_called_once()

    def test_get_note_version_with_content(self, mock_client, mcp):
        mock_note = MagicMock(
            guid="note-guid",
            title="Note v1",
            content="<en-note>Content</en-note>",
            updateSequenceNum=1,
            updated=1704067200000,
        )
        mock_client.get_note_version.return_value = mock_note

        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_version_tool = tools.get("get_note_version")

        if get_version_tool:
            result = get_version_tool.fn(
                note_guid="note-guid",
                update_sequence_num=1
            )
            data = json.loads(result)
            assert data["success"] is True
            assert data["content"] is not None


class TestNoteAdvancedToolsErrorHandling:
    """Test error handling in advanced note tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        mock.get_note_content.side_effect = Exception("Note not found")
        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_get_note_content_handles_error(self, mock_client, mcp):
        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_content_tool = tools.get("get_note_content")

        if get_content_tool:
            result = get_content_tool.fn(guid="invalid-guid")
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data

    def test_get_note_search_text_handles_error(self, mock_client, mcp):
        mock_client.get_note_search_text.side_effect = Exception("Search failed")

        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_search_text_tool = tools.get("get_note_search_text")

        if get_search_text_tool:
            result = get_search_text_tool.fn(guid="note-guid")
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data

    def test_list_note_versions_handles_error(self, mock_client, mcp):
        mock_client.list_note_versions.side_effect = Exception("Access denied")

        register_note_advanced_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        list_versions_tool = tools.get("list_note_versions")

        if list_versions_tool:
            result = list_versions_tool.fn(note_guid="note-guid")
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
