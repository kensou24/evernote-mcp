"""Real API integration tests for Evernote MCP server.

These tests use real Evernote API credentials and make actual API calls.

Set environment variables:
    EVERNOTE_AUTH_TOKEN - Your Evernote developer token
    EVERNOTE_BACKEND - evernote, china, or china:sandbox (default: china)

Run tests:
    EVERNOTE_AUTH_TOKEN=xxx EVERNOTE_BACKEND=china uv run pytest tests/test_real_api.py -v
"""

import json
import os
import time

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.client import EvernoteMCPClient
from evernote_mcp.tools.notebook_tools import register_notebook_tools
from evernote_mcp.tools.note_tools import register_note_tools
from evernote_mcp.tools.tag_tools import register_tag_tools
from evernote_mcp.tools.search_tools import register_search_tools
from evernote_mcp.tools.search_tools_extended import register_search_tools_extended
from evernote_mcp.tools.resource_tools import register_resource_tools
from evernote_mcp.tools.note_advanced_tools import register_note_advanced_tools
from evernote_mcp.tools.sync_tools import register_sync_tools
from evernote_mcp.tools.reminder_tools import register_reminder_tools
from evernote_mcp.util.error_handler import handle_evernote_error


# Skip these tests unless explicitly enabled
pytestmark = pytest.mark.skipif(
    not os.getenv("EVERNOTE_AUTH_TOKEN"),
    reason="EVERNOTE_AUTH_TOKEN not set"
)


def _proper_enml(content: str) -> str:
    """Wrap content in proper ENML format."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
{content}
</en-note>"""


@pytest.fixture
def real_client() -> EvernoteMCPClient:
    """Create a real Evernote client using environment credentials."""
    token = os.getenv("EVERNOTE_AUTH_TOKEN")
    backend = os.getenv("EVERNOTE_BACKEND", "china")

    if not token:
        pytest.skip("EVERNOTE_AUTH_TOKEN not set")

    client = EvernoteMCPClient(auth_token=token, backend=backend)
    return client


@pytest.fixture
def mcp_server() -> FastMCP:
    """Create a FastMCP server for testing."""
    return FastMCP("test-evernote-mcp")


# ============================================================================
# Connection & Sync Tests
# ============================================================================

class TestConnectionAndSync:
    """Test basic connection and sync operations."""

    def test_authenticate_success(self, real_client: EvernoteMCPClient):
        """Test that we can successfully authenticate with Evernote."""
        assert real_client is not None
        assert real_client.user is not None
        print(f"Authenticated successfully, user type: {type(real_client.user)}")

    def test_get_sync_state(self, real_client: EvernoteMCPClient):
        """Test getting sync state from real API."""
        state = real_client.get_sync_state()
        assert state is not None
        assert hasattr(state, "currentTime")
        assert hasattr(state, "updateCount")
        print(f"Sync state: updateCount={state.updateCount}")


# ============================================================================
# Notebook Tools Tests
# ============================================================================

class TestNotebookTools:
    """Test all notebook MCP tools with real API."""

    def test_list_notebooks_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test list_notebooks MCP tool."""
        register_notebook_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        list_tool = tools.get("list_notebooks")

        result = list_tool.fn()
        data = json.loads(result)
        assert data["success"] is True
        assert "notebooks" in data
        print(f"Found {len(data['notebooks'])} notebooks")

    def test_get_notebook_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_notebook MCP tool."""
        register_notebook_tools(mcp_server, real_client)

        # Get default notebook first
        default_nb = real_client.get_default_notebook()

        tools = mcp_server._tool_manager._tools
        get_tool = tools.get("get_notebook")

        result = get_tool.fn(guid=default_nb.guid)
        data = json.loads(result)
        assert data["success"] is True
        assert data["name"] == default_nb.name
        print(f"Got notebook: {data['name']}")

    def test_create_notebook_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test create_notebook MCP tool."""
        register_notebook_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        create_tool = tools.get("create_notebook")

        test_name = f"Test Notebook {int(time.time())}"

        result = create_tool.fn(name=test_name, stack="Test Stack")
        data = json.loads(result)
        assert data["success"] is True
        assert data["name"] == test_name
        assert data["stack"] == "Test Stack"

        # Clean up
        real_client.expunge_notebook(data["guid"])
        print(f"Created and deleted notebook: {test_name}")

    def test_update_notebook_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test update_notebook MCP tool."""
        register_notebook_tools(mcp_server, real_client)

        # Create a test notebook first
        notebook = real_client.create_notebook(f"Update Test {int(time.time())}")

        tools = mcp_server._tool_manager._tools
        update_tool = tools.get("update_notebook")

        new_name = f"Updated {int(time.time())}"
        result = update_tool.fn(guid=notebook.guid, name=new_name)
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_notebook(notebook.guid)
        print(f"Updated notebook to: {new_name}")

    def test_delete_notebook_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test delete_notebook MCP tool."""
        register_notebook_tools(mcp_server, real_client)

        # Create a test notebook first
        notebook = real_client.create_notebook(f"Delete Test {int(time.time())}")
        notebook_guid = notebook.guid

        tools = mcp_server._tool_manager._tools
        delete_tool = tools.get("delete_notebook")

        result = delete_tool.fn(guid=notebook_guid)
        data = json.loads(result)
        assert data["success"] is True
        print(f"Deleted notebook: {notebook_guid}")


# ============================================================================
# Note Tools Tests
# ============================================================================

class TestNoteTools:
    """Test all note MCP tools with real API."""

    def test_list_notes_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test list_notes MCP tool."""
        register_note_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        list_tool = tools.get("list_notes")

        default_nb = real_client.get_default_notebook()

        result = list_tool.fn(notebook_guid=default_nb.guid, limit=10)
        data = json.loads(result)
        assert data["success"] is True
        print(f"Listed {data['count']} notes")

    def test_get_note_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_note MCP tool."""
        register_note_tools(mcp_server, real_client)

        # Create a test note first
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Get Test Note",
            content=_proper_enml("<div>Content for get_note test</div>"),
            notebook_guid=default_nb.guid
        )

        tools = mcp_server._tool_manager._tools
        get_tool = tools.get("get_note")

        result = get_tool.fn(guid=note.guid)
        data = json.loads(result)
        assert data["success"] is True
        assert data["title"] == "Get Test Note"

        # Clean up
        real_client.expunge_note(note.guid)
        print("get_note tool test passed")

    def test_create_note_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test create_note MCP tool."""
        register_note_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        create_tool = tools.get("create_note")

        default_nb = real_client.get_default_notebook()
        test_title = f"Create Test {int(time.time())}"

        result = create_tool.fn(
            title=test_title,
            content="Test content",
            notebook_guid=default_nb.guid
        )
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_note(data["guid"])
        print(f"Created note: {test_title}")

    def test_update_note_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test update_note MCP tool."""
        register_note_tools(mcp_server, real_client)

        # Create a test note
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Update Test Note",
            content=_proper_enml("<div>Original content</div>"),
            notebook_guid=default_nb.guid
        )

        tools = mcp_server._tool_manager._tools
        update_tool = tools.get("update_note")

        new_title = f"Updated {int(time.time())}"
        result = update_tool.fn(guid=note.guid, title=new_title)
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_note(note.guid)
        print("update_note tool test passed")

    def test_delete_note_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test delete_note MCP tool."""
        register_note_tools(mcp_server, real_client)

        # Create a test note
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Delete Test Note",
            content=_proper_enml("<div>To be deleted</div>"),
            notebook_guid=default_nb.guid
        )
        note_guid = note.guid

        tools = mcp_server._tool_manager._tools
        delete_tool = tools.get("delete_note")

        result = delete_tool.fn(guid=note_guid)
        data = json.loads(result)
        assert data["success"] is True

        # Permanently delete
        real_client.expunge_note(note_guid)
        print("delete_note tool test passed")

    def test_copy_note_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test copy_note MCP tool."""
        register_note_tools(mcp_server, real_client)

        # Create a test notebook
        target_nb = real_client.create_notebook(f"Copy Target {int(time.time())}")

        # Create a test note
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Copy Test Note",
            content=_proper_enml("<div>To be copied</div>"),
            notebook_guid=default_nb.guid
        )

        tools = mcp_server._tool_manager._tools
        copy_tool = tools.get("copy_note")

        result = copy_tool.fn(guid=note.guid, target_notebook_guid=target_nb.guid)
        data = json.loads(result)
        assert data["success"] is True

        # Clean up both notes and notebook
        real_client.expunge_note(note.guid)
        real_client.expunge_note(data["guid"])
        real_client.expunge_notebook(target_nb.guid)
        print("copy_note tool test passed")


# ============================================================================
# Tag Tools Tests
# ============================================================================

class TestTagTools:
    """Test all tag MCP tools with real API."""

    def test_list_tags_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test list_tags MCP tool."""
        register_search_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        list_tool = tools.get("list_tags")

        if list_tool:
            result = list_tool.fn()
            data = json.loads(result)
            assert data["success"] is True
            print(f"Listed {len(data['tags'])} tags")

    def test_get_tag_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_tag MCP tool."""
        register_tag_tools(mcp_server, real_client)

        # Create a test tag first
        tag = real_client.create_tag(f"test-tag-{int(time.time())}")

        tools = mcp_server._tool_manager._tools
        get_tool = tools.get("get_tag")

        result = get_tool.fn(guid=tag.guid)
        data = json.loads(result)
        assert data["success"] is True
        assert data["name"] == tag.name

        # Clean up
        real_client.expunge_tag(tag.guid)
        print("get_tag tool test passed")

    def test_create_tag_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test create_tag MCP tool."""
        register_tag_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        create_tool = tools.get("create_tag")

        tag_name = f"test-create-{int(time.time())}"

        result = create_tool.fn(name=tag_name)
        data = json.loads(result)
        assert data["success"] is True
        assert data["name"] == tag_name

        # Clean up
        real_client.expunge_tag(data["guid"])
        print(f"Created tag: {tag_name}")

    def test_update_tag_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test update_tag MCP tool."""
        register_tag_tools(mcp_server, real_client)

        # Create a test tag
        tag = real_client.create_tag(f"test-update-{int(time.time())}")

        tools = mcp_server._tool_manager._tools
        update_tool = tools.get("update_tag")

        new_name = f"updated-{int(time.time())}"
        result = update_tool.fn(guid=tag.guid, name=new_name)
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_tag(tag.guid)
        print("update_tag tool test passed")

    def test_expunge_tag_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test expunge_tag MCP tool."""
        register_tag_tools(mcp_server, real_client)

        # Create a test tag
        tag = real_client.create_tag(f"test-expunge-{int(time.time())}")
        tag_guid = tag.guid

        tools = mcp_server._tool_manager._tools
        expunge_tool = tools.get("expunge_tag")

        result = expunge_tool.fn(guid=tag_guid)
        data = json.loads(result)
        assert data["success"] is True
        print("expunge_tag tool test passed")

    def test_list_tags_by_notebook_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test list_tags_by_notebook MCP tool."""
        register_tag_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        list_tool = tools.get("list_tags_by_notebook")

        default_nb = real_client.get_default_notebook()

        result = list_tool.fn(notebook_guid=default_nb.guid)
        data = json.loads(result)
        assert data["success"] is True
        print(f"Tags in default notebook: {len(data['tags'])}")

    def test_untag_all_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test untag_all MCP tool."""
        register_tag_tools(mcp_server, real_client)

        # Create a test tag
        tag = real_client.create_tag(f"test-untag-{int(time.time())}")

        # Create a test note with the tag
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Untag Test Note",
            content=_proper_enml("<div>Test content</div>"),
            notebook_guid=default_nb.guid,
            tag_guids=[tag.guid]
        )

        tools = mcp_server._tool_manager._tools
        untag_tool = tools.get("untag_all")

        result = untag_tool.fn(guid=tag.guid)
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_note(note.guid)
        real_client.expunge_tag(tag.guid)
        print("untag_all tool test passed")


# ============================================================================
# Search Tools Tests
# ============================================================================

class TestSearchTools:
    """Test all search MCP tools with real API."""

    def test_search_notes_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test search_notes MCP tool."""
        register_search_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        search_tool = tools.get("search_notes")

        result = search_tool.fn(query="", limit=5)
        data = json.loads(result)
        assert data["success"] is True
        print(f"Search found {data['count']} notes")


# ============================================================================
# Saved Search Tools Tests
# ============================================================================

class TestSavedSearchTools:
    """Test all saved search MCP tools with real API."""

    def test_list_searches_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test list_searches MCP tool."""
        register_search_tools_extended(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        list_tool = tools.get("list_searches")

        result = list_tool.fn()
        data = json.loads(result)
        assert data["success"] is True
        print(f"Found {len(data['searches'])} saved searches")

    def test_get_search_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_search MCP tool."""
        register_search_tools_extended(mcp_server, real_client)

        # Create a test saved search
        search = real_client.create_search(
            f"test-search-{int(time.time())}",
            "notebook:*"
        )

        tools = mcp_server._tool_manager._tools
        get_tool = tools.get("get_search")

        result = get_tool.fn(guid=search.guid)
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_search(search.guid)
        print("get_search tool test passed")

    def test_create_search_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test create_search MCP tool."""
        register_search_tools_extended(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        create_tool = tools.get("create_search")

        search_name = f"test-create-search-{int(time.time())}"

        result = create_tool.fn(name=search_name, query="tag:test")
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_search(data["guid"])
        print(f"Created saved search: {search_name}")

    def test_update_search_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test update_search MCP tool."""
        register_search_tools_extended(mcp_server, real_client)

        # Create a test saved search
        search = real_client.create_search(
            f"test-update-search-{int(time.time())}",
            "tag:test"
        )

        tools = mcp_server._tool_manager._tools
        update_tool = tools.get("update_search")

        new_query = "tag:updated"
        result = update_tool.fn(guid=search.guid, query=new_query)
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_search(search.guid)
        print("update_search tool test passed")

    def test_expunge_search_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test expunge_search MCP tool."""
        register_search_tools_extended(mcp_server, real_client)

        # Create a test saved search
        search = real_client.create_search(
            f"test-expunge-search-{int(time.time())}",
            "tag:test"
        )
        search_guid = search.guid

        tools = mcp_server._tool_manager._tools
        expunge_tool = tools.get("expunge_search")

        result = expunge_tool.fn(guid=search_guid)
        data = json.loads(result)
        assert data["success"] is True
        print("expunge_search tool test passed")


# ============================================================================
# Advanced Note Tools Tests
# ============================================================================

class TestNoteAdvancedTools:
    """Test all advanced note MCP tools with real API."""

    def test_get_note_content_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_note_content MCP tool."""
        register_note_advanced_tools(mcp_server, real_client)

        # Create a test note
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Content Test Note",
            content=_proper_enml("<div>Test content for get_note_content</div>"),
            notebook_guid=default_nb.guid
        )

        tools = mcp_server._tool_manager._tools
        get_content_tool = tools.get("get_note_content")

        result = get_content_tool.fn(guid=note.guid)
        data = json.loads(result)
        assert data["success"] is True
        assert "content" in data

        # Clean up
        real_client.expunge_note(note.guid)
        print("get_note_content tool test passed")

    def test_get_note_search_text_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_note_search_text MCP tool."""
        register_note_advanced_tools(mcp_server, real_client)

        # Create a test note
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Search Text Test Note",
            content=_proper_enml("<div>Searchable text content</div>"),
            notebook_guid=default_nb.guid
        )

        tools = mcp_server._tool_manager._tools
        get_text_tool = tools.get("get_note_search_text")

        result = get_text_tool.fn(guid=note.guid, note_only=True)
        data = json.loads(result)
        assert data["success"] is True
        assert "text" in data

        # Clean up
        real_client.expunge_note(note.guid)
        print("get_note_search_text tool test passed")

    def test_get_note_tag_names_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_note_tag_names MCP tool."""
        register_note_advanced_tools(mcp_server, real_client)

        # Create a test note with a tag
        default_nb = real_client.get_default_notebook()
        tag = real_client.create_tag(f"test-tag-names-{int(time.time())}")

        note = real_client.create_note(
            title="Tag Names Test Note",
            content=_proper_enml("<div>Test content</div>"),
            notebook_guid=default_nb.guid,
            tag_guids=[tag.guid]
        )

        tools = mcp_server._tool_manager._tools
        get_tag_names_tool = tools.get("get_note_tag_names")

        result = get_tag_names_tool.fn(guid=note.guid)
        data = json.loads(result)
        assert data["success"] is True
        assert "tag_names" in data

        # Clean up
        real_client.expunge_note(note.guid)
        real_client.expunge_tag(tag.guid)
        print("get_note_tag_names tool test passed")

    def test_list_note_versions_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test list_note_versions MCP tool (Premium only)."""
        register_note_advanced_tools(mcp_server, real_client)

        # Create a test note
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Versions Test Note",
            content=_proper_enml("<div>Test content</div>"),
            notebook_guid=default_nb.guid
        )

        tools = mcp_server._tool_manager._tools
        list_versions_tool = tools.get("list_note_versions")

        result = list_versions_tool.fn(note_guid=note.guid)
        data = json.loads(result)
        assert data["success"] is True
        # Note: Free accounts may not have version history
        print(f"Note versions: {data['count']}")

        # Clean up
        real_client.expunge_note(note.guid)
        print("list_note_versions tool test passed")


# ============================================================================
# Sync Tools Tests
# ============================================================================

class TestSyncTools:
    """Test all sync/utility MCP tools with real API."""

    def test_get_sync_state_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_sync_state MCP tool."""
        register_sync_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        get_state_tool = tools.get("get_sync_state")

        result = get_state_tool.fn()
        data = json.loads(result)
        assert data["success"] is True
        assert "update_count" in data
        print(f"Sync state: {data['update_count']}")

    def test_get_default_notebook_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_default_notebook MCP tool."""
        register_sync_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        get_default_tool = tools.get("get_default_notebook")

        result = get_default_tool.fn()
        data = json.loads(result)
        assert data["success"] is True
        assert "name" in data
        print(f"Default notebook: {data['name']}")

    def test_find_note_counts_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test find_note_counts MCP tool."""
        register_sync_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        find_counts_tool = tools.get("find_note_counts")

        result = find_counts_tool.fn(query="")
        data = json.loads(result)
        assert data["success"] is True
        print(f"Note counts retrieved")

    def test_find_related_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test find_related MCP tool."""
        register_sync_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        find_related_tool = tools.get("find_related")

        # Test with plain text
        result = find_related_tool.fn(plain_text="test query")
        data = json.loads(result)
        assert data["success"] is True
        print(f"Related content found")


# ============================================================================
# Reminder Tools Tests
# ============================================================================

class TestReminderTools:
    """Test all reminder MCP tools with real API."""

    def test_set_reminder_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test set_reminder MCP tool."""
        register_reminder_tools(mcp_server, real_client)

        # Create a test note
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Reminder Test Note",
            content=_proper_enml("<div>Test content with reminder</div>"),
            notebook_guid=default_nb.guid
        )

        tools = mcp_server._tool_manager._tools
        set_reminder_tool = tools.get("set_reminder")

        # Set reminder for tomorrow
        import time
        tomorrow = int((time.time() + 86400) * 1000)

        result = set_reminder_tool.fn(
            note_guid=note.guid,
            reminder_time=tomorrow
        )
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_note(note.guid)
        print("set_reminder tool test passed")

    def test_complete_reminder_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test complete_reminder MCP tool."""
        register_reminder_tools(mcp_server, real_client)

        # Create a test note with reminder
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Complete Reminder Test",
            content=_proper_enml("<div>Test</div>"),
            notebook_guid=default_nb.guid
        )

        # Set reminder first
        import time
        tomorrow = int((time.time() + 86400) * 1000)
        real_client.set_reminder(note.guid, tomorrow)

        tools = mcp_server._tool_manager._tools
        complete_tool = tools.get("complete_reminder")

        result = complete_tool.fn(note_guid=note.guid)
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_note(note.guid)
        print("complete_reminder tool test passed")

    def test_clear_reminder_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test clear_reminder MCP tool."""
        register_reminder_tools(mcp_server, real_client)

        # Create a test note with reminder
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Clear Reminder Test",
            content=_proper_enml("<div>Test</div>"),
            notebook_guid=default_nb.guid
        )

        # Set reminder first
        import time
        tomorrow = int((time.time() + 86400) * 1000)
        real_client.set_reminder(note.guid, tomorrow)

        tools = mcp_server._tool_manager._tools
        clear_tool = tools.get("clear_reminder")

        result = clear_tool.fn(note_guid=note.guid)
        data = json.loads(result)
        assert data["success"] is True

        # Clean up
        real_client.expunge_note(note.guid)
        print("clear_reminder tool test passed")

    def test_list_reminders_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test list_reminders MCP tool."""
        register_reminder_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        list_tool = tools.get("list_reminders")

        result = list_tool.fn(limit=10, include_completed=False)
        data = json.loads(result)
        assert data["success"] is True
        print(f"Active reminders: {data['count']}")

    def test_get_reminder_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_reminder MCP tool."""
        register_reminder_tools(mcp_server, real_client)

        # Create a note and set reminder
        default_nb = real_client.get_default_notebook()
        note = real_client.create_note(
            title="Get Reminder Test",
            content=_proper_enml("<div>Test</div>"),
            notebook_guid=default_nb.guid
        )

        import time
        tomorrow = int((time.time() + 86400) * 1000)
        real_client.set_reminder(note.guid, tomorrow)

        tools = mcp_server._tool_manager._tools
        get_reminder_tool = tools.get("get_reminder")

        result = get_reminder_tool.fn(note_guid=note.guid)
        data = json.loads(result)
        assert data["success"] is True
        assert data["has_reminder"] is True

        # Clean up
        real_client.expunge_note(note.guid)
        print("get_reminder tool test passed")


# ============================================================================
# Resource Tools Tests
# ============================================================================

class TestResourceTools:
    """Test resource MCP tools with real API."""

    def test_get_resource_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_resource MCP tool."""
        register_resource_tools(mcp_server, real_client)

        # Create a test note with an image (resource)
        # For now, we'll test that the tool is available and handles errors gracefully
        tools = mcp_server._tool_manager._tools
        get_resource_tool = tools.get("get_resource")

        if get_resource_tool:
            # Test with invalid GUID - should return error
            result = get_resource_tool.fn(guid="invalid-guid")
            data = json.loads(result)
            assert data["success"] is False
            print("get_resource tool handles errors correctly")

    def test_get_resource_attributes_tool(self, mcp_server: FastMCP, real_client: EvernoteMCPClient):
        """Test get_resource_attributes MCP tool."""
        register_resource_tools(mcp_server, real_client)

        tools = mcp_server._tool_manager._tools
        get_attrs_tool = tools.get("get_resource_attributes")

        if get_attrs_tool:
            # Test with invalid GUID
            result = get_attrs_tool.fn(guid="invalid-guid")
            data = json.loads(result)
            assert data["success"] is False
            print("get_resource_attributes tool handles errors correctly")


# ============================================================================
# Summary
# ============================================================================

if __name__ == "__main__":
    import sys
    pytest.main([__file__, "-v", "-s"] + sys.argv[1:])
