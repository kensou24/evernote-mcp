"""Integration tests for core MCP tools."""

from unittest.mock import MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.tools.notebook_tools import register_notebook_tools


class TestCoreToolsIntegration:
    """Integration tests for core MCP tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        mock_notebook_obj = MagicMock()
        mock_notebook_obj.guid = "test-notebook-guid"
        mock_notebook_obj.name = "Test Notebook"
        mock_notebook_obj.stack = "Test Stack"
        mock_notebook_obj.serviceCreated = 1704067200000
        mock_notebook_obj.serviceUpdated = 1704067200000
        mock_notebook_obj.defaultNotebook = False

        mock.create_notebook.return_value = mock_notebook_obj
        mock.get_notebook.return_value = mock_notebook_obj
        mock.listNotebooks.return_value = [mock_notebook_obj]

        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_create_and_list_notebook(self, mock_client, mcp):
        register_notebook_tools(mcp, mock_client)

        create_tool = mcp._tool_manager._tools.get("create_notebook")

        if create_tool:
            result = create_tool.fn(name="Test Notebook", stack="Test Stack")
            import json

            data = json.loads(result)
            assert data["success"] is True
            assert data["name"] == "Test Notebook"
            assert data["stack"] == "Test Stack"

        list_tool = mcp._tool_manager._tools.get("list_notebooks")

        if list_tool:
            result = list_tool.fn()
            import json

            data = json.loads(result)
            assert data["success"] is True
            assert "notebooks" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
