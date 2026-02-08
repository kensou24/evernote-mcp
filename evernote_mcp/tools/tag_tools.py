"""MCP tools for tag operations."""
import logging
from typing import Optional
import json
from mcp.server.fastmcp import FastMCP

from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def register_tag_tools(mcp: FastMCP, client):
    """Register tag-related MCP tools."""

    @mcp.tool()
    def get_tag(guid: str) -> str:
        """
        Get tag details by GUID.

        Args:
            guid: Tag GUID

        Returns:
            JSON string with tag details
        """
        try:
            tag = client.get_tag(guid)
            result = {
                "success": True,
                "guid": tag.guid,
                "name": tag.name,
                "parent_guid": getattr(tag, 'parentGuid', None),
                "update_sequence_num": getattr(tag, 'updateSequenceNum', None),
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def create_tag(name: str, parent_guid: Optional[str] = None) -> str:
        """
        Create a new tag.

        Args:
            name: Tag name (required)
            parent_guid: Optional parent tag GUID for hierarchy

        Returns:
            JSON string with created tag info including GUID
        """
        try:
            tag = client.create_tag(name, parent_guid)
            result = {
                "success": True,
                "guid": tag.guid,
                "name": tag.name,
                "parent_guid": getattr(tag, 'parentGuid', None),
            }
            logger.info(f"Created tag: {tag.name} ({tag.guid})")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def update_tag(guid: str, name: Optional[str] = None,
                   parent_guid: Optional[str] = None) -> str:
        """
        Update an existing tag.

        Args:
            guid: Tag GUID (required)
            name: New tag name (optional)
            parent_guid: New parent tag GUID (optional)

        Returns:
            JSON string with updated tag info
        """
        try:
            tag = client.get_tag(guid)
            if name:
                tag.name = name
            if parent_guid is not None:
                tag.parentGuid = parent_guid if parent_guid else None

            usn = client.update_tag(tag)
            result = {
                "success": True,
                "guid": tag.guid,
                "name": tag.name,
                "update_sequence_num": usn,
            }
            logger.info(f"Updated tag: {tag.name} ({tag.guid})")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def expunge_tag(guid: str) -> str:
        """
        Permanently delete a tag.

        Args:
            guid: Tag GUID to delete

        Returns:
            JSON string with operation result
        """
        try:
            usn = client.expunge_tag(guid)
            result = {
                "success": True,
                "message": f"Tag {guid} deleted",
                "update_sequence_num": usn,
            }
            logger.info(f"Deleted tag: {guid}")
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def list_tags_by_notebook(notebook_guid: str) -> str:
        """
        List all tags used in a specific notebook.

        Args:
            notebook_guid: Notebook GUID

        Returns:
            JSON string with list of tags
        """
        try:
            tags = client.list_tags_by_notebook(notebook_guid)
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
            logger.info(f"Listed {len(tags)} tag(s) for notebook")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def untag_all(guid: str) -> str:
        """
        Remove a tag from all notes.

        Args:
            guid: Tag GUID to remove from all notes

        Returns:
            JSON string with operation result
        """
        try:
            tag = client.get_tag(guid)
            client.untag_all(guid)
            result = {
                "success": True,
                "message": f"Tag '{tag.name}' removed from all notes",
            }
            logger.info(f"Removed tag {guid} from all notes")
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)
