"""MCP tools for note operations."""
import logging
from typing import Optional, List
import json
from mcp.server.fastmcp import FastMCP
from evernote.edam.error.ttypes import EDAMNotFoundException

from evernote_mcp.util.enml_converter import enml_to_text, enml_to_markdown, text_to_enml
from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def register_note_tools(mcp: FastMCP, client):
    """Register note-related MCP tools."""

    @mcp.tool()
    def create_note(
        title: str,
        content: str,
        notebook_guid: str,
        tags: Optional[List[str]] = None,
        format: str = "text"
    ) -> str:
        """
        Create a new note in Evernote.

        Args:
            title: Note title (required)
            content: Note content (required)
            notebook_guid: Target notebook GUID (required)
            tags: Optional list of tag names to assign
            format: Content format - 'text' (default) or 'enml'

        Returns:
            JSON string with created note info including GUID
        """
        try:
            # Convert content to ENML if needed
            enml_content = content if format == "enml" else text_to_enml(content)

            # Convert tag names to GUIDs if provided
            tag_guids = None
            if tags:
                all_tags = {t.name: t.guid for t in client.list_tags()}
                tag_guids = [all_tags.get(tag) for tag in tags if tag in all_tags]

            note = client.create_note(title, enml_content, notebook_guid, tag_guids)
            result = {
                "success": True,
                "guid": note.guid,
                "title": note.title,
                "notebook_guid": note.notebookGuid,
                "created": note.created,
            }
            logger.info(f"Created note: {note.title} ({note.guid})")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_note(guid: str, output_format: str = "enml") -> str:
        """
        Get note content and metadata.

        Args:
            guid: Note GUID (required)
            output_format: Output format - 'enml', 'text', 'markdown', or 'json' (default: enml)

        Returns:
            JSON string with note content and metadata
        """
        try:
            note = client.get_note(guid, with_content=True)

            if output_format == "json":
                result = {
                    "success": True,
                    "guid": note.guid,
                    "title": note.title,
                    "content": note.content,
                    "notebook_guid": note.notebookGuid,
                    "created": note.created,
                    "updated": note.updated,
                    "active": note.active,
                    "tag_guids": note.tagGuids or [],
                }
            elif output_format == "text":
                content_text = enml_to_text(note.content)
                result = {
                    "success": True,
                    "guid": note.guid,
                    "title": note.title,
                    "content": content_text,
                    "notebook_guid": note.notebookGuid,
                    "updated": note.updated,
                }
            elif output_format == "markdown":
                content_md = enml_to_markdown(note.content)
                result = {
                    "success": True,
                    "guid": note.guid,
                    "title": note.title,
                    "content": content_md,
                    "notebook_guid": note.notebookGuid,
                    "updated": note.updated,
                }
            else:  # enml
                result = {
                    "success": True,
                    "guid": note.guid,
                    "title": note.title,
                    "content": note.content,
                    "notebook_guid": note.notebookGuid,
                }

            return json.dumps(result, indent=2, ensure_ascii=False)
        except EDAMNotFoundException:
            return json.dumps({"success": False, "error": f"Note {guid} not found"}, indent=2)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def update_note(
        guid: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        format: str = "text"
    ) -> str:
        """
        Update an existing note.

        Args:
            guid: Note GUID (required)
            title: New title (optional)
            content: New content (optional)
            format: Content format - 'text' (default) or 'enml'

        Returns:
            JSON string with updated note info
        """
        try:
            note = client.get_note(guid, with_content=False)
            if title:
                note.title = title
            if content:
                enml_content = content if format == "enml" else text_to_enml(content)
                note.content = enml_content

            updated = client.update_note(note)
            result = {
                "success": True,
                "guid": updated.guid,
                "title": updated.title,
                "updated": updated.updated,
            }
            logger.info(f"Updated note: {updated.title} ({updated.guid})")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def delete_note(guid: str) -> str:
        """
        Move a note to trash.

        Args:
            guid: Note GUID to delete

        Returns:
            JSON string with operation result
        """
        try:
            note = client.delete_note(guid)
            result = {
                "success": True,
                "message": f"Note {guid} moved to trash",
                "title": note.title,
            }
            logger.info(f"Moved note to trash: {guid}")
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def expunge_note(guid: str) -> str:
        """
        Permanently delete a note.

        Args:
            guid: Note GUID to permanently delete

        Returns:
            JSON string with operation result
        """
        try:
            client.expunge_note(guid)
            result = {
                "success": True,
                "message": f"Note {guid} permanently deleted"
            }
            logger.info(f"Permanently deleted note: {guid}")
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def copy_note(guid: str, target_notebook_guid: str) -> str:
        """
        Copy a note to another notebook.

        Args:
            guid: Source note GUID
            target_notebook_guid: Destination notebook GUID

        Returns:
            JSON string with new note info
        """
        try:
            new_note = client.copy_note(guid, target_notebook_guid)
            result = {
                "success": True,
                "guid": new_note.guid,
                "title": new_note.title,
                "notebook_guid": new_note.notebookGuid,
            }
            logger.info(f"Copied note {guid} to {new_note.guid}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def move_note(guid: str, target_notebook_guid: str) -> str:
        """
        Move a note to another notebook.

        Args:
            guid: Note GUID to move
            target_notebook_guid: Destination notebook GUID

        Returns:
            JSON string with operation result
        """
        try:
            note = client.get_note(guid, with_content=False)
            old_notebook = note.notebookGuid
            note.notebookGuid = target_notebook_guid
            updated = client.update_note(note)

            result = {
                "success": True,
                "guid": updated.guid,
                "title": updated.title,
                "from_notebook_guid": old_notebook,
                "to_notebook_guid": updated.notebookGuid,
            }
            logger.info(f"Moved note {guid} from {old_notebook} to {target_notebook_guid}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def list_notes(notebook_guid: Optional[str] = None, limit: int = 100) -> str:
        """
        List notes in a notebook or all notes.

        Args:
            notebook_guid: Optional notebook GUID to filter
            limit: Maximum number of notes to return (default: 100)

        Returns:
            JSON string with list of notes
        """
        try:
            # Use empty search to list all notes
            query = "" if not notebook_guid else ""
            result = client.find_notes(query, notebook_guid, limit)

            notes_list = result.notes if hasattr(result, 'notes') else []
            notes_data = []
            for n in notes_list[:limit]:
                note_info = {
                    "guid": n.guid,
                    "title": n.title if hasattr(n, 'title') else "",
                    "notebook_guid": n.notebookGuid if hasattr(n, 'notebookGuid') else notebook_guid,
                }
                if hasattr(n, 'updated'):
                    note_info["updated"] = n.updated
                notes_data.append(note_info)

            response = {
                "success": True,
                "count": len(notes_data),
                "notes": notes_data,
            }
            return json.dumps(response, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)
