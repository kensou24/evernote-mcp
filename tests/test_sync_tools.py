"""Integration tests for sync tools."""

import json
from unittest.mock import MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.tools.sync_tools import register_sync_tools


class MockSyncState:
    def __init__(self):
        self.currentTime = 1704067200000
        self.fullSyncBefore = 1704153600000
        self.updateCount = 12345
        self.uploaded = 1024000
        self.userLastUpdated = 1704067200000


class MockNotebook:
    def __init__(
        self,
        guid: str = "default-nb-guid",
        name: str = "Default Notebook",
    ):
        self.guid = guid
        self.name = name
        self.stack = None
        self.defaultNotebook = True


class MockNoteCounts:
    def __init__(self):
        self.notebookCounts = {"nb-1": 10, "nb-2": 5}
        self.tagCounts = {"tag-1": 8, "tag-2": 3}
        self.trashCount = 2


class TestSyncTools:
    """Integration tests for sync and utility MCP tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()

        mock_state = MockSyncState()
        mock.get_sync_state.return_value = mock_state

        mock_nb = MockNotebook()
        mock.get_default_notebook.return_value = mock_nb

        mock_counts = MockNoteCounts()
        mock.find_note_counts.return_value = mock_counts

        mock_related = MagicMock()
        mock_related.notes = []
        mock_related.notebooks = []
        mock_related.tags = []
        mock_related.cacheKey = "cache-key-123"
        mock.find_related.return_value = mock_related

        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_get_sync_state(self, mock_client, mcp):
        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_state_tool = tools.get("get_sync_state")

        if get_state_tool:
            result = get_state_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert data["current_time"] == 1704067200000
            assert data["full_sync_before"] == 1704153600000
            assert data["update_count"] == 12345
            assert data["uploaded"] == 1024000
            assert data["user_last_updated"] == 1704067200000

    def test_get_default_notebook(self, mock_client, mcp):
        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_default_tool = tools.get("get_default_notebook")

        if get_default_tool:
            result = get_default_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "default-nb-guid"
            assert data["name"] == "Default Notebook"
            assert data["default_notebook"] is True
            assert data["stack"] is None

    def test_get_default_notebook_with_stack(self, mock_client, mcp):
        mock_nb = MockNotebook()
        mock_nb.stack = "Personal"
        mock_nb.defaultNotebook = False
        mock_client.get_default_notebook.return_value = mock_nb

        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_default_tool = tools.get("get_default_notebook")

        if get_default_tool:
            result = get_default_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert data["stack"] == "Personal"
            assert data["default_notebook"] is False

    def test_find_note_counts_default(self, mock_client, mcp):
        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        find_counts_tool = tools.get("find_note_counts")

        if find_counts_tool:
            result = find_counts_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert data["query"] == ""
            assert data["notebook_counts"] == {"nb-1": 10, "nb-2": 5}
            assert data["tag_counts"] == {"tag-1": 8, "tag-2": 3}
            assert data["trash_count"] == 2

    def test_find_note_counts_with_query(self, mock_client, mcp):
        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        find_counts_tool = tools.get("find_note_counts")

        if find_counts_tool:
            result = find_counts_tool.fn(query="tag:important")
            data = json.loads(result)
            assert data["success"] is True
            assert data["query"] == "tag:important"

            # Verify the client was called correctly
            mock_client.find_note_counts.assert_called_once()

    def test_find_note_counts_with_trash(self, mock_client, mcp):
        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        find_counts_tool = tools.get("find_note_counts")

        if find_counts_tool:
            result = find_counts_tool.fn(with_trash=True)
            data = json.loads(result)
            assert data["success"] is True
            assert data["trash_count"] == 2

    def test_find_related_by_note_guid(self, mock_client, mcp):
        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        find_related_tool = tools.get("find_related")

        if find_related_tool:
            result = find_related_tool.fn(note_guid="note-guid-123")
            data = json.loads(result)
            assert data["success"] is True
            assert "notes" in data
            assert "notebooks" in data
            assert "tags" in data
            assert data["cache_key"] == "cache-key-123"

    def test_find_related_by_plain_text(self, mock_client, mcp):
        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        find_related_tool = tools.get("find_related")

        if find_related_tool:
            result = find_related_tool.fn(plain_text="search for similar content")
            data = json.loads(result)
            assert data["success"] is True

    def test_find_related_with_limits(self, mock_client, mcp):
        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        find_related_tool = tools.get("find_related")

        if find_related_tool:
            result = find_related_tool.fn(
                plain_text="test",
                max_notes=5,
                max_notebooks=2,
                max_tags=3,
            )
            data = json.loads(result)
            assert data["success"] is True

    def test_find_related_with_results(self, mock_client, mcp):
        # Set up related content
        mock_note = MagicMock()
        mock_note.guid = "related-note-1"
        mock_note.title = "Related Note"

        mock_nb = MagicMock()
        mock_nb.guid = "related-nb-1"
        mock_nb.name = "Related Notebook"

        mock_tag = MagicMock()
        mock_tag.guid = "related-tag-1"
        mock_tag.name = "related-tag"

        mock_related = MagicMock()
        mock_related.notes = [mock_note]
        mock_related.notebooks = [mock_nb]
        mock_related.tags = [mock_tag]
        mock_related.cacheKey = "cache-456"
        mock_client.find_related.return_value = mock_related

        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        find_related_tool = tools.get("find_related")

        if find_related_tool:
            result = find_related_tool.fn(note_guid="note-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert len(data["notes"]) == 1
            assert data["notes"][0]["title"] == "Related Note"
            assert len(data["notebooks"]) == 1
            assert data["notebooks"][0]["name"] == "Related Notebook"
            assert len(data["tags"]) == 1
            assert data["tags"][0]["name"] == "related-tag"

    def test_find_related_missing_params(self, mock_client, mcp):
        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        find_related_tool = tools.get("find_related")

        if find_related_tool:
            # Call without note_guid or plain_text
            result = find_related_tool.fn()
            data = json.loads(result)
            assert data["success"] is False
            assert "Either note_guid or plain_text must be provided" in data["error"]


class TestSyncToolsErrorHandling:
    """Test error handling in sync tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        mock.get_sync_state.side_effect = Exception("Sync failed")
        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_get_sync_state_handles_error(self, mock_client, mcp):
        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_state_tool = tools.get("get_sync_state")

        if get_state_tool:
            result = get_state_tool.fn()
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data

    def test_get_default_notebook_handles_error(self, mock_client, mcp):
        mock_client.get_default_notebook.side_effect = Exception("Not found")

        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_default_tool = tools.get("get_default_notebook")

        if get_default_tool:
            result = get_default_tool.fn()
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data

    def test_find_note_counts_handles_error(self, mock_client, mcp):
        mock_client.find_note_counts.side_effect = Exception("Query failed")

        register_sync_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        find_counts_tool = tools.get("find_note_counts")

        if find_counts_tool:
            result = find_counts_tool.fn()
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
