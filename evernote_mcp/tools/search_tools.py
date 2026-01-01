"""MCP tools for search operations."""
import logging
from typing import Optional
import json
from mcp.server.fastmcp import FastMCP

from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def register_search_tools(mcp: FastMCP, client):
    """Register search-related MCP tools."""

    @mcp.tool()
    def search_notes(
        query: str,
        notebook_guid: Optional[str] = None,
        limit: int = 100
    ) -> str:
        """
        Search notes using Evernote's search syntax.

        Evernote search syntax examples:
        - 'intitle:meeting' - search in titles only
        - 'tag:important' - search by tag
        - 'created:20240101' - notes created on date
        - 'updated:day-7' - notes updated in last 7 days
        - 'notebook:My Notebook' - search in specific notebook
        - 'resource:application/pdf' - notes with PDFs
        - 'encryption:true' - encrypted notes

        Args:
            query: Evernote search query
            notebook_guid: Optional notebook GUID to limit search
            limit: Maximum number of results (default: 100)

        Returns:
            JSON string with search results
        """
        try:
            result = client.find_notes(query, notebook_guid, limit)
            notes_list = result.notes if hasattr(result, 'notes') else []

            notes_data = []
            for n in notes_list:
                note_info = {
                    "guid": n.guid,
                    "title": n.title if hasattr(n, 'title') else "",
                    "notebook_guid": n.notebookGuid if hasattr(n, 'notebookGuid') else None,
                }
                if hasattr(n, 'updated'):
                    note_info["updated"] = n.updated
                if hasattr(n, 'created'):
                    note_info["created"] = n.created
                notes_data.append(note_info)

            total = result.totalNotes if hasattr(result, 'totalNotes') else len(notes_list)

            response = {
                "success": True,
                "total": total,
                "count": len(notes_data),
                "query": query,
                "notes": notes_data,
            }
            logger.info(f"Search '{query}' found {total} note(s)")
            return json.dumps(response, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def list_tags() -> str:
        """
        List all tags in the Evernote account.

        Returns:
            JSON string with list of tags
        """
        try:
            tags = client.list_tags()
            result = {
                "success": True,
                "tags": [
                    {
                        "guid": t.guid,
                        "name": t.name,
                        "parent_guid": getattr(t, 'parentGuid', None),
                    }
                    for t in tags
                ]
            }
            logger.info(f"Listed {len(tags)} tag(s)")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)
