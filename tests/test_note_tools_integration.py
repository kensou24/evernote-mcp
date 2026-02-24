"""Integration tests for notebook tools."""

from unittest.mock import MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.tools.notebook_tools import register_notebook_tools


class TestNotebookToolsIntegration:
    """Integration tests for notebook MCP tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        # Create a notebook that can be configured per test
        def create_notebook_with_stack(name, stack=None):
            mock_nb = MagicMock()
            mock_nb.guid = "test-notebook-guid"
            mock_nb.name = name
            mock_nb.stack = stack
            mock_nb.serviceCreated = 1704067200000
            mock_nb.serviceUpdated = 1704067200000
            mock_nb.defaultNotebook = False
            return mock_nb

        mock.create_notebook.side_effect = create_notebook_with_stack

        # For get_notebook, return a default notebook
        mock_nb_default = MagicMock()
        mock_nb_default.guid = "test-notebook-guid"
        mock_nb_default.name = "Test Notebook"
        mock_nb_default.stack = None
        mock_nb_default.serviceCreated = 1704067200000
        mock_nb_default.serviceUpdated = 1704067200000
        mock_nb_default.defaultNotebook = False

        mock.get_notebook.return_value = mock_nb_default
        mock.update_notebook.return_value = 1
        # Setup listNotebooks (camelCase for Evernote API)
        mock.listNotebooks.return_value = [mock_nb_default]
        # Also setup list_notebooks (snake_case for client wrapper)
        mock.list_notebooks = lambda: mock.listNotebooks()
        mock.expungeNotebook.return_value = 1
        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_create_notebook_success(self, mock_client, mcp):
        register_notebook_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        create_tool = tools.get("create_notebook")

        if create_tool:
            result = create_tool.fn(name="Test Notebook", stack="Test Stack")
            import json

            data = json.loads(result)
            assert data["success"] is True
            assert data["name"] == "Test Notebook"
            assert data["stack"] == "Test Stack"
            assert "guid" in data

    def test_create_notebook_without_stack(self, mock_client, mcp):
        register_notebook_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        create_tool = tools.get("create_notebook")

        if create_tool:
            result = create_tool.fn(name="Test Notebook")
            import json

            data = json.loads(result)
            assert data["success"] is True
            assert data["name"] == "Test Notebook"
            assert data["stack"] is None

    def test_list_notebooks(self, mock_client, mcp):
        register_notebook_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_notebooks")

        if list_tool:
            result = list_tool.fn()
            import json

            data = json.loads(result)
            assert data["success"] is True
            assert "notebooks" in data
            assert len(data["notebooks"]) == 1
            assert data["notebooks"][0]["guid"] == "test-notebook-guid"

    def test_get_notebook(self, mock_client, mcp):
        register_notebook_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_notebook")

        if get_tool:
            result = get_tool.fn(guid="test-guid")
            import json

            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "test-notebook-guid"
            assert data["name"] == "Test Notebook"

    def test_update_notebook_name(self, mock_client, mcp):
        register_notebook_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_notebook")

        if update_tool:
            result = update_tool.fn(guid="test-guid", name="Updated Name")
            import json

            data = json.loads(result)
            assert data["success"] is True
            assert data["name"] == "Updated Name"

    def test_update_notebook_stack(self, mock_client, mcp):
        register_notebook_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_notebook")

        if update_tool:
            result = update_tool.fn(guid="test-guid", stack="New Stack")
            import json

            data = json.loads(result)
            assert data["success"] is True
            assert data["stack"] == "New Stack"

    def test_update_notebook_remove_stack(self, mock_client, mcp):
        register_notebook_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_notebook")

        if update_tool:
            result = update_tool.fn(guid="test-guid", stack="")
            import json

            data = json.loads(result)
            assert data["success"] is True
            assert data["stack"] is None

    def test_delete_notebook(self, mock_client, mcp):
        register_notebook_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        delete_tool = tools.get("delete_notebook")

        if delete_tool:
            result = delete_tool.fn(guid="test-guid")
            import json

            data = json.loads(result)
            assert data["success"] is True
            assert "message" in data
            assert "test-guid" in data["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
