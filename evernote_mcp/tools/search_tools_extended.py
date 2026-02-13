"""MCP tools for saved search operations."""
import logging
from typing import Optional
import json
from mcp.server.fastmcp import FastMCP

from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def serialize_scope(scope) -> Optional[dict]:
    """Convert SavedSearchScope to a serializable dict."""
    if scope is None:
        return None
    return {
        "include_account": getattr(scope, 'includeAccount', None),
        "include_personal_linked_notebooks": getattr(scope, 'includePersonalLinkedNotebooks', None),
        "include_business_linked_notebooks": getattr(scope, 'includeBusinessLinkedNotebooks', None),
    }


def register_search_tools_extended(mcp: FastMCP, client):
    """Register saved search-related MCP tools."""

    @mcp.tool()
    def list_searches() -> str:
        """
        List all saved searches in the Evernote account.

        Returns:
            JSON string with list of saved searches
        """
        try:
            searches = client.list_searches()

            result = {
                "success": True,
                "searches": [
                    {
                        "guid": s.guid,
                        "name": s.name,
                        "query": s.query,
                        "format": getattr(s, 'format', None),
                        "scope": serialize_scope(getattr(s, 'scope', None)),
                    }
                    for s in searches
                ]
            }
            logger.info(f"Listed {len(searches)} saved search(es)")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_search(guid: str) -> str:
        """
        Get saved search details by GUID.

        Args:
            guid: Saved search GUID

        Returns:
            JSON string with saved search details
        """
        try:
            search = client.get_search(guid)

            result = {
                "success": True,
                "guid": search.guid,
                "name": search.name,
                "query": search.query,
                "format": getattr(search, 'format', None),
                "scope": serialize_scope(getattr(search, 'scope', None)),
                "update_sequence_num": getattr(search, 'updateSequenceNum', None),
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def create_search(name: str, query: str) -> str:
        """
        Create a new saved search.

        Args:
            name: Search name (required)
            query: Evernote search query (required)

        Returns:
            JSON string with created search info including GUID
        """
        try:
            search = client.create_search(name, query)
            result = {
                "success": True,
                "guid": search.guid,
                "name": search.name,
                "query": search.query,
            }
            logger.info(f"Created saved search: {search.name} ({search.guid})")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def update_search(guid: str, name: Optional[str] = None,
                      query: Optional[str] = None) -> str:
        """
        Update an existing saved search.

        Args:
            guid: Saved search GUID (required)
            name: New search name (optional)
            query: New search query (optional)

        Returns:
            JSON string with updated search info
        """
        try:
            search = client.get_search(guid)
            if name:
                search.name = name
            if query:
                search.query = query

            usn = client.update_search(search)
            result = {
                "success": True,
                "guid": search.guid,
                "name": search.name,
                "query": search.query,
                "update_sequence_num": usn,
            }
            logger.info(f"Updated saved search: {search.name} ({search.guid})")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def expunge_search(guid: str) -> str:
        """
        Permanently delete a saved search.

        Args:
            guid: Saved search GUID to delete

        Returns:
            JSON string with operation result
        """
        try:
            usn = client.expunge_search(guid)
            result = {
                "success": True,
                "message": f"Saved search {guid} deleted",
                "update_sequence_num": usn,
            }
            logger.info(f"Deleted saved search: {guid}")
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)
