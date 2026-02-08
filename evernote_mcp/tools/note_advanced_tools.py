"""MCP tools for advanced note operations."""
import logging
import json
from mcp.server.fastmcp import FastMCP

from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def register_note_advanced_tools(mcp: FastMCP, client):
    """Register advanced note-related MCP tools."""

    @mcp.tool()
    def get_note_content(guid: str) -> str:
        """
        Get just the ENML content of a note.

        Args:
            guid: Note GUID (required)

        Returns:
            JSON string with note ENML content
        """
        try:
            content = client.get_note_content(guid)
            result = {
                "success": True,
                "guid": guid,
                "content": content,
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_note_search_text(guid: str, note_only: bool = False,
                              tokenize_for_indexing: bool = False) -> str:
        """
        Get extracted plain text from a note for indexing.

        Args:
            guid: Note GUID (required)
            note_only: If true, only return text from the note content.
                       If false, also include text from resources (PDF, images).
            tokenize_for_indexing: If true, break text into clean tokens for indexing.
                                   If false, return raw text with punctuation.

        Returns:
            JSON string with extracted text
        """
        try:
            text = client.get_note_search_text(guid, note_only, tokenize_for_indexing)
            result = {
                "success": True,
                "guid": guid,
                "text": text,
                "note_only": note_only,
                "tokenized": tokenize_for_indexing,
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_note_tag_names(guid: str) -> str:
        """
        Get tag names for a note.

        Args:
            guid: Note GUID (required)

        Returns:
            JSON string with list of tag names
        """
        try:
            tag_names = client.get_note_tag_names(guid)
            result = {
                "success": True,
                "guid": guid,
                "tag_names": tag_names,
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def list_note_versions(note_guid: str) -> str:
        """
        List previous versions of a note (Premium only).

        Args:
            note_guid: Note GUID (required)

        Returns:
            JSON string with list of note versions
        """
        try:
            versions = client.list_note_versions(note_guid)
            result = {
                "success": True,
                "note_guid": note_guid,
                "versions": [
                    {
                        "update_sequence_num": v.updateSequenceNum,
                        "updated": v.updated,
                        "saved": v.saved,
                        "title": v.title,
                        "last_editor_id": getattr(v, 'lastEditorId', None),
                    }
                    for v in versions
                ],
                "count": len(versions),
            }
            logger.info(f"Listed {len(versions)} version(s) for note {note_guid}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_note_version(note_guid: str, update_sequence_num: int,
                         with_resources_data: bool = False,
                         with_resources_recognition: bool = False,
                         with_resources_alternate_data: bool = False) -> str:
        """
        Get a specific version of a note (Premium only).

        Args:
            note_guid: Note GUID (required)
            update_sequence_num: USN of the version to retrieve (required)
            with_resources_data: Include resource binary data
            with_resources_recognition: Include resource recognition data
            with_resources_alternate_data: Include resource alternate data

        Returns:
            JSON string with note version info
        """
        try:
            note = client.get_note_version(
                note_guid, update_sequence_num,
                with_resources_data, with_resources_recognition, with_resources_alternate_data
            )
            result = {
                "success": True,
                "guid": note.guid,
                "title": note.title,
                "content": note.content if hasattr(note, 'content') else None,
                "update_sequence_num": note.updateSequenceNum,
                "updated": note.updated,
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)
