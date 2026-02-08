"""MCP tools for sync and utility operations."""
import logging
import json
from mcp.server.fastmcp import FastMCP
from evernote.edam.notestore.ttypes import RelatedQuery, RelatedResultSpec

from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def register_sync_tools(mcp: FastMCP, client):
    """Register sync and utility-related MCP tools."""

    @mcp.tool()
    def get_sync_state() -> str:
        """
        Get sync state information.

        Returns:
            JSON string with sync state including current time,
            update count, and upload usage
        """
        try:
            state = client.get_sync_state()
            result = {
                "success": True,
                "current_time": state.currentTime,
                "full_sync_before": state.fullSyncBefore,
                "update_count": state.updateCount,
                "uploaded": state.uploaded,
                "user_last_updated": state.userLastUpdated,
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_default_notebook() -> str:
        """
        Get the default notebook for new notes.

        Returns:
            JSON string with default notebook info
        """
        try:
            notebook = client.get_default_notebook()
            result = {
                "success": True,
                "guid": notebook.guid,
                "name": notebook.name,
                "stack": notebook.stack,
                "default_notebook": getattr(notebook, 'defaultNotebook', False),
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def find_note_counts(query: str = "", with_trash: bool = False) -> str:
        """
        Get note counts for each notebook and tag.

        Args:
            query: Evernote search query to filter notes (default: all notes)
            with_trash: If true, include trash count

        Returns:
            JSON string with note counts per notebook and tag
        """
        try:
            counts = client.find_note_counts(query, with_trash)

            # Convert notebook counts to dict for JSON serialization
            notebook_counts = {}
            if hasattr(counts, 'notebookCounts'):
                for guid, count in counts.notebookCounts.items():
                    notebook_counts[guid] = count

            # Convert tag counts to dict
            tag_counts = {}
            if hasattr(counts, 'tagCounts'):
                for guid, count in counts.tagCounts.items():
                    tag_counts[guid] = count

            result = {
                "success": True,
                "query": query,
                "notebook_counts": notebook_counts,
                "tag_counts": tag_counts,
                "trash_count": getattr(counts, 'trashCount', None),
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def find_related(note_guid: str = "", plain_text: str = "",
                     max_notes: int = 10, max_notebooks: int = 5,
                     max_tags: int = 10) -> str:
        """
        Find related entities (notes, notebooks, tags).

        Args:
            note_guid: GUID of an existing note to find related content for
            plain_text: Plain text to find related content for (alternative to note_guid)
            max_notes: Maximum number of related notes to return
            max_notebooks: Maximum number of related notebooks to return
            max_tags: Maximum number of related tags to return

        Returns:
            JSON string with related notes, notebooks, and tags
        """
        try:
            # Build the related query
            query = RelatedQuery()
            if note_guid:
                query.noteGuid = note_guid
            elif plain_text:
                query.plainText = plain_text
            else:
                return json.dumps({
                    "success": False,
                    "error": "Either note_guid or plain_text must be provided"
                }, indent=2)

            # Build the result spec
            result_spec = RelatedResultSpec()
            if max_notes > 0:
                result_spec.maxNotes = max_notes
            if max_notebooks > 0:
                result_spec.maxNotebooks = max_notebooks
            if max_tags > 0:
                result_spec.maxTags = max_tags

            # Find related content
            related = client.find_related(query, result_spec)

            # Extract results
            notes_data = []
            if hasattr(related, 'notes') and related.notes is not None:
                for note in related.notes:
                    notes_data.append({
                        "guid": note.guid,
                        "title": note.title,
                    })

            notebooks_data = []
            if hasattr(related, 'notebooks') and related.notebooks is not None:
                for nb in related.notebooks:
                    notebooks_data.append({
                        "guid": nb.guid,
                        "name": nb.name,
                    })

            tags_data = []
            if hasattr(related, 'tags') and related.tags is not None:
                for tag in related.tags:
                    tags_data.append({
                        "guid": tag.guid,
                        "name": tag.name,
                    })

            result = {
                "success": True,
                "notes": notes_data,
                "notebooks": notebooks_data,
                "tags": tags_data,
                "cache_key": getattr(related, 'cacheKey', None),
            }
            logger.info(f"Found related: {len(notes_data)} notes, {len(notebooks_data)} notebooks, {len(tags_data)} tags")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)
