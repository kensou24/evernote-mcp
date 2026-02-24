"""Integration tests for saved search tools."""

import json
from unittest.mock import MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.tools.search_tools_extended import (
    register_search_tools_extended,
    serialize_scope,
)


class MockSavedSearchScope:
    def __init__(
        self,
        include_account: bool = True,
        include_personal: bool = False,
        include_business: bool = False,
    ):
        self.includeAccount = include_account
        self.includePersonalLinkedNotebooks = include_personal
        self.includeBusinessLinkedNotebooks = include_business


class MockSavedSearch:
    def __init__(
        self,
        guid: str = "search-guid",
        name: str = "My Search",
        query: str = "tag:test",
    ):
        self.guid = guid
        self.name = name
        self.query = query
        self.format = None
        self.scope = None
        self.updateSequenceNum = 123


class TestSerializeScope:
    """Test serialize_scope function."""

    def test_serialize_none_scope(self):
        result = serialize_scope(None)
        assert result is None

    def test_serialize_full_scope(self):
        scope = MockSavedSearchScope(
            include_account=True,
            include_personal=True,
            include_business=True,
        )

        result = serialize_scope(scope)

        assert result is not None
        assert result["include_account"] is True
        assert result["include_personal_linked_notebooks"] is True
        assert result["include_business_linked_notebooks"] is True

    def test_serialize_partial_scope(self):
        scope = MockSavedSearchScope(
            include_account=True,
            include_personal=False,
            include_business=False,
        )

        result = serialize_scope(scope)

        assert result is not None
        assert result["include_account"] is True
        assert result["include_personal_linked_notebooks"] is False
        assert result["include_business_linked_notebooks"] is False

    def test_serialize_scope_with_missing_attributes(self):
        scope = MagicMock()
        # Delete the attributes to simulate missing data
        delattr(scope, 'includeAccount')
        delattr(scope, 'includePersonalLinkedNotebooks')
        delattr(scope, 'includeBusinessLinkedNotebooks')

        result = serialize_scope(scope)

        assert result is not None
        # getattr should return None for missing attributes
        assert result["include_account"] is None
        assert result["include_personal_linked_notebooks"] is None
        assert result["include_business_linked_notebooks"] is None


class TestSavedSearchTools:
    """Integration tests for saved search MCP tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()

        def create_search_impl(name, query):
            return MockSavedSearch(name=name, query=query)

        mock_search = MockSavedSearch()
        mock.list_searches.return_value = [mock_search]
        mock.get_search.return_value = mock_search
        mock.create_search.side_effect = create_search_impl
        mock.update_search.return_value = 123
        mock.expunge_search.return_value = 123

        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_list_searches(self, mock_client, mcp):
        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_searches")

        if list_tool:
            result = list_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert "searches" in data
            assert len(data["searches"]) == 1
            assert data["searches"][0]["name"] == "My Search"
            assert data["searches"][0]["query"] == "tag:test"

    def test_list_searches_multiple(self, mock_client, mcp):
        search1 = MockSavedSearch(guid="s-1", name="Search 1", query="tag:important")
        search2 = MockSavedSearch(guid="s-2", name="Search 2", query="notebook:Work")
        mock_client.list_searches.return_value = [search1, search2]

        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_searches")

        if list_tool:
            result = list_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert len(data["searches"]) == 2
            assert data["searches"][0]["name"] == "Search 1"
            assert data["searches"][1]["name"] == "Search 2"

    def test_list_searches_empty(self, mock_client, mcp):
        mock_client.list_searches.return_value = []

        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_searches")

        if list_tool:
            result = list_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert len(data["searches"]) == 0

    def test_list_searches_with_scope(self, mock_client, mcp):
        search = MockSavedSearch()
        search.scope = MockSavedSearchScope()
        search.format = "user"
        mock_client.list_searches.return_value = [search]

        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_searches")

        if list_tool:
            result = list_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            assert data["searches"][0]["format"] == "user"
            assert data["searches"][0]["scope"] is not None
            assert data["searches"][0]["scope"]["include_account"] is True

    def test_get_search(self, mock_client, mcp):
        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_search")

        if get_tool:
            result = get_tool.fn(guid="search-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "search-guid"
            assert data["name"] == "My Search"
            assert data["query"] == "tag:test"

    def test_get_search_with_scope(self, mock_client, mcp):
        search = MockSavedSearch()
        search.scope = MockSavedSearchScope()
        search.updateSequenceNum = 456
        mock_client.get_search.return_value = search

        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_search")

        if get_tool:
            result = get_tool.fn(guid="search-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["update_sequence_num"] == 456
            assert data["scope"] is not None

    def test_create_search(self, mock_client, mcp):
        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        create_tool = tools.get("create_search")

        if create_tool:
            result = create_tool.fn(name="New Search", query="tag:new")
            data = json.loads(result)
            assert data["success"] is True
            assert data["name"] == "New Search"
            assert data["query"] == "tag:new"
            assert "guid" in data

            mock_client.create_search.assert_called_once_with("New Search", "tag:new")

    def test_update_search_name(self, mock_client, mcp):
        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_search")

        if update_tool:
            result = update_tool.fn(guid="search-guid", name="Updated Name")
            data = json.loads(result)
            assert data["success"] is True
            assert data["name"] == "Updated Name"
            assert data["update_sequence_num"] == 123

    def test_update_search_query(self, mock_client, mcp):
        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_search")

        if update_tool:
            result = update_tool.fn(guid="search-guid", query="tag:updated")
            data = json.loads(result)
            assert data["success"] is True
            assert data["query"] == "tag:updated"

    def test_update_search_both(self, mock_client, mcp):
        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_search")

        if update_tool:
            result = update_tool.fn(
                guid="search-guid",
                name="New Name",
                query="new query"
            )
            data = json.loads(result)
            assert data["success"] is True
            assert data["name"] == "New Name"
            assert data["query"] == "new query"

    def test_expunge_search(self, mock_client, mcp):
        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        expunge_tool = tools.get("expunge_search")

        if expunge_tool:
            result = expunge_tool.fn(guid="search-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert "search-guid deleted" in data["message"]
            assert data["update_sequence_num"] == 123

            mock_client.expunge_search.assert_called_once_with("search-guid")


class TestSavedSearchToolsErrorHandling:
    """Test error handling in saved search tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        mock.list_searches.side_effect = Exception("Failed to list")
        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_list_searches_handles_error(self, mock_client, mcp):
        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_searches")

        if list_tool:
            result = list_tool.fn()
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data

    def test_get_search_handles_error(self, mock_client, mcp):
        mock_client.list_searches.side_effect = None
        mock_client.get_search.side_effect = Exception("Search not found")

        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_search")

        if get_tool:
            result = get_tool.fn(guid="invalid-guid")
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data

    def test_create_search_handles_error(self, mock_client, mcp):
        mock_client.list_searches.side_effect = None
        mock_client.create_search.side_effect = Exception("Creation failed")

        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        create_tool = tools.get("create_search")

        if create_tool:
            result = create_tool.fn(name="Test", query="tag:test")
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data

    def test_update_search_handles_error(self, mock_client, mcp):
        mock_client.list_searches.side_effect = None
        mock_client.get_search.side_effect = Exception("Not found")

        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_search")

        if update_tool:
            result = update_tool.fn(guid="invalid-guid", name="New Name")
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data

    def test_expunge_search_handles_error(self, mock_client, mcp):
        mock_client.list_searches.side_effect = None
        mock_client.expunge_search.side_effect = Exception("Delete failed")

        register_search_tools_extended(mcp, mock_client)

        tools = mcp._tool_manager._tools
        expunge_tool = tools.get("expunge_search")

        if expunge_tool:
            result = expunge_tool.fn(guid="search-guid")
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
