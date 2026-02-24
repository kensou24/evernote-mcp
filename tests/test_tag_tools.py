"""Integration tests for tag tools."""

import json
from unittest.mock import MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.tools.tag_tools import register_tag_tools


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


class TestTagTools:
    """Integration tests for tag MCP tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        # Return a tag with the same name as requested
        def create_tag_impl(name, parent_guid=None):
            return MockTag(name=name, parent_guid=parent_guid)

        mock.get_tag.return_value = MockTag()
        mock.create_tag.side_effect = create_tag_impl
        mock.update_tag.return_value = 1
        mock.expunge_tag.return_value = 1
        mock.listTags.return_value = [MockTag()]
        mock.listTagsByNotebook.return_value = [MockTag()]
        # Also mock the snake_case version that the tools use
        mock.list_tags_by_notebook = lambda nb_guid: mock.listTagsByNotebook(nb_guid)
        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_get_tag_tool(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_tag")

        if get_tool:
            result = get_tool.fn(guid="test-tag-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "test-tag-guid"
            assert data["name"] == "test-tag"

    def test_get_tag_with_parent(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        mock_tag = MockTag(parent_guid="parent-guid")
        mock_client.get_tag.return_value = mock_tag

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_tag")

        if get_tool:
            result = get_tool.fn(guid="test-tag-guid")
            data = json.loads(result)
            assert data["parent_guid"] == "parent-guid"

    def test_create_tag_tool(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        create_tool = tools.get("create_tag")

        if create_tool:
            result = create_tool.fn(name="New Tag")
            data = json.loads(result)
            assert data["success"] is True
            assert data["name"] == "New Tag"
            assert "guid" in data

            # Verify client was called correctly
            mock_client.create_tag.assert_called_once_with("New Tag", None)

    def test_create_tag_with_parent(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        create_tool = tools.get("create_tag")

        if create_tool:
            result = create_tool.fn(name="Child Tag", parent_guid="parent-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["name"] == "Child Tag"

            mock_client.create_tag.assert_called_once_with("Child Tag", "parent-guid")

    def test_update_tag_name(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_tag")

        if update_tool:
            result = update_tool.fn(guid="tag-guid", name="Updated Name")
            data = json.loads(result)
            assert data["success"] is True
            assert data["name"] == "Updated Name"
            assert data["update_sequence_num"] == 1

    def test_update_tag_parent(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_tag")

        if update_tool:
            result = update_tool.fn(guid="tag-guid", parent_guid="new-parent")
            data = json.loads(result)
            assert data["success"] is True

    def test_update_tag_remove_parent(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_tag")

        if update_tool:
            result = update_tool.fn(guid="tag-guid", parent_guid="")
            data = json.loads(result)
            assert data["success"] is True

            # Verify parent was set to None
            call_args = mock_client.update_tag.call_args[0][0]
            assert call_args.parentGuid is None

    def test_expunge_tag_tool(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        expunge_tool = tools.get("expunge_tag")

        if expunge_tool:
            result = expunge_tool.fn(guid="tag-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert "tag-guid deleted" in data["message"]
            assert data["update_sequence_num"] == 1

    def test_list_tags_by_notebook(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_tags_by_notebook")

        if list_tool:
            result = list_tool.fn(notebook_guid="nb-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert "tags" in data
            assert len(data["tags"]) == 1
            assert data["tags"][0]["name"] == "test-tag"

    def test_list_tags_by_notebook_multiple_tags(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tag1 = MockTag(guid="tag-1", name="tag1")
        tag2 = MockTag(guid="tag-2", name="tag2")
        mock_client.listTagsByNotebook.return_value = [tag1, tag2]
        mock_client.list_tags_by_notebook = lambda nb_guid: mock_client.listTagsByNotebook(nb_guid)

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_tags_by_notebook")

        if list_tool:
            result = list_tool.fn(notebook_guid="nb-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert len(data["tags"]) == 2

    def test_untag_all_tool(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        untag_tool = tools.get("untag_all")

        if untag_tool:
            result = untag_tool.fn(guid="tag-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert "test-tag" in data["message"]
            assert "removed from all notes" in data["message"]

            mock_client.untag_all.assert_called_once_with("tag-guid")

    def test_untag_all_gets_tag_name(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        mock_tag = MockTag(name="My Tag")
        mock_client.get_tag.return_value = mock_tag

        tools = mcp._tool_manager._tools
        untag_tool = tools.get("untag_all")

        if untag_tool:
            result = untag_tool.fn(guid="tag-guid")
            data = json.loads(result)
            assert "My Tag" in data["message"]


class TestTagToolsErrorHandling:
    """Test error handling in tag tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        # Configure to raise exceptions for testing
        mock.get_tag.side_effect = Exception("Tag not found")
        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_get_tag_handles_error(self, mock_client, mcp):
        register_tag_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_tag")

        if get_tool:
            result = get_tool.fn(guid="invalid-guid")
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
