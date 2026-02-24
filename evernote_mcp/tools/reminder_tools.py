"""MCP tools for reminder operations."""

import json
import logging

from mcp.server.fastmcp import FastMCP

from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def register_reminder_tools(mcp: FastMCP, client):
    """Register reminder-related MCP tools."""

    @mcp.tool()
    def set_reminder(
        note_guid: str,
        reminder_time: int | None = None,
        reminder_order: int | None = None,
    ) -> str:
        """
        Set a reminder on a note.

        Args:
            note_guid: Note GUID (required)
            reminder_time: Reminder time as Unix timestamp in milliseconds.
                          If None, clears the reminder time (but keeps order).
                          Example: 1704067200000 for 2024-01-01 00:00:00 UTC
            reminder_order: Optional order for sorting (auto-generated if None)

        Returns:
            JSON string with updated note info
        """
        try:
            note = client.set_reminder(note_guid, reminder_time, reminder_order)
            result = {
                "success": True,
                "note_guid": note.guid,
                "title": note.title,
                "reminder_time": note.attributes.reminderTime
                if note.attributes
                else None,
                "reminder_order": note.attributes.reminderOrder
                if note.attributes
                else None,
            }
            logger.info(f"Set reminder on note {note_guid}: {reminder_time}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def complete_reminder(note_guid: str, done_time: int | None = None) -> str:
        """
        Mark a reminder as completed.

        Args:
            note_guid: Note GUID (required)
            done_time: Completion time as Unix timestamp in milliseconds.
                      If None, uses current time.

        Returns:
            JSON string with updated note info
        """
        try:
            note = client.complete_reminder(note_guid, done_time)
            result = {
                "success": True,
                "note_guid": note.guid,
                "title": note.title,
                "reminder_time": note.attributes.reminderTime
                if note.attributes
                else None,
                "reminder_done_time": note.attributes.reminderDoneTime
                if note.attributes
                else None,
            }
            logger.info(f"Completed reminder on note {note_guid}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def clear_reminder(note_guid: str) -> str:
        """
        Clear all reminder fields from a note.

        Args:
            note_guid: Note GUID (required)

        Returns:
            JSON string with operation result
        """
        try:
            note = client.clear_reminder(note_guid)
            result = {
                "success": True,
                "note_guid": note.guid,
                "title": note.title,
                "message": "Reminder cleared",
            }
            logger.info(f"Cleared reminder from note {note_guid}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def list_reminders(
        notebook_guid: str | None = None,
        limit: int = 100,
        include_completed: bool = False,
    ) -> str:
        """
        List notes with reminders.

        Args:
            notebook_guid: Optional notebook GUID to filter
            limit: Maximum number of results (default: 100)
            include_completed: Include completed reminders (default: false)

        Returns:
            JSON string with list of notes with reminders
        """
        try:
            result = client.find_reminders(notebook_guid, limit, include_completed)
            notes_list = result.notes if hasattr(result, "notes") else []

            reminders_data = []
            for n in notes_list[:limit]:
                reminder_info = {
                    "guid": n.guid,
                    "title": n.title if hasattr(n, "title") else "",
                    "notebook_guid": n.notebookGuid
                    if hasattr(n, "notebookGuid")
                    else None,
                    "updated": n.updated if hasattr(n, "updated") else None,
                }

                # Extract reminder attributes
                if hasattr(n, "attributes") and n.attributes:
                    reminder_info["reminder_time"] = getattr(
                        n.attributes, "reminderTime", None
                    )
                    reminder_info["reminder_order"] = getattr(
                        n.attributes, "reminderOrder", None
                    )
                    reminder_info["reminder_done_time"] = getattr(
                        n.attributes, "reminderDoneTime", None
                    )

                reminders_data.append(reminder_info)

            response = {
                "success": True,
                "total": result.totalNotes
                if hasattr(result, "totalNotes")
                else len(notes_list),
                "count": len(reminders_data),
                "include_completed": include_completed,
                "reminders": reminders_data,
            }
            logger.info(f"Listed {len(reminders_data)} reminder(s)")
            return json.dumps(response, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_reminder(note_guid: str) -> str:
        """
        Get reminder information for a specific note.

        Args:
            note_guid: Note GUID (required)

        Returns:
            JSON string with reminder details
        """
        try:
            note = client.get_note(note_guid, with_content=False)

            result = {
                "success": True,
                "note_guid": note.guid,
                "title": note.title,
                "has_reminder": False,
                "reminder_time": None,
                "reminder_order": None,
                "reminder_done_time": None,
                "is_completed": False,
            }

            if note.attributes:
                reminder_time = getattr(note.attributes, "reminderTime", None)
                reminder_order = getattr(note.attributes, "reminderOrder", None)
                reminder_done_time = getattr(note.attributes, "reminderDoneTime", None)

                result["reminder_time"] = reminder_time
                result["reminder_order"] = reminder_order
                result["reminder_done_time"] = reminder_done_time
                result["has_reminder"] = (
                    reminder_time is not None or reminder_order is not None
                )
                result["is_completed"] = reminder_done_time is not None

            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)
