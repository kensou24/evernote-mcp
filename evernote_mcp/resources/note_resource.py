"""MCP resources for notes."""
import logging
import json
from mcp.server.fastmcp import FastMCP
from evernote.edam.error.ttypes import EDAMNotFoundException

from evernote_mcp.util.enml_converter import enml_to_text, enml_to_markdown
from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def register_note_resources(mcp: FastMCP, client):
    """Register note resources."""

    @mcp.resource("note://{guid}")
    def get_note_content(guid: str) -> str:
        """
        Get full note content.

        URI format: note://{guid}

        Args:
            guid: Note GUID

        Returns:
            JSON string with note details including content
        """
        try:
            note = client.get_note(guid, with_content=True)
            result = {
                "guid": note.guid,
                "title": note.title,
                "content": note.content,
                "content_text": enml_to_text(note.content),
                "content_markdown": enml_to_markdown(note.content),
                "notebook_guid": note.notebookGuid,
                "created": note.created,
                "updated": note.updated,
                "active": note.active,
                "tag_guids": note.tagGuids or [],
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except EDAMNotFoundException:
            return json.dumps({"error": f"Note {guid} not found"}, indent=2)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.resource("note-text://{guid}")
    def get_note_text(guid: str) -> str:
        """
        Get note content as plain text.

        URI format: note-text://{guid}

        Args:
            guid: Note GUID

        Returns:
            Plain text content of the note
        """
        try:
            note = client.get_note(guid, with_content=True)
            text_content = enml_to_text(note.content)
            return f"# {note.title}\n\n{text_content}"
        except EDAMNotFoundException:
            return f"Error: Note {guid} not found"
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.resource("note-markdown://{guid}")
    def get_note_markdown(guid: str) -> str:
        """
        Get note content as Markdown.

        URI format: note-markdown://{guid}

        Args:
            guid: Note GUID

        Returns:
            Markdown formatted content of the note
        """
        try:
            note = client.get_note(guid, with_content=True)
            md_content = enml_to_markdown(note.content)
            return f"# {note.title}\n\n{md_content}"
        except EDAMNotFoundException:
            return f"Error: Note {guid} not found"
        except Exception as e:
            return f"Error: {str(e)}"
