"""Unit tests for reminder functionality."""

import json
from unittest.mock import MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.client import EvernoteMCPClient
from evernote_mcp.tools.reminder_tools import register_reminder_tools


class MockNote:
    def __init__(self, guid="test-guid", title="Test Note"):
        self.guid = guid
        self.title = title
        self.attributes = None


class MockNoteAttributes:
    def __init__(self):
        self.reminderTime = None
        self.reminderOrder = None
        self.reminderDoneTime = None


class TestReminderClientMethods:
    def test_set_reminder_creates_attributes(self):
        note = MockNote()
        note.attributes = None

        with patch.object(EvernoteMCPClient, "__init__", lambda x, **kwargs: None):
            with patch.object(
                EvernoteMCPClient, "note_store", new_callable=MagicMock
            ) as mock_store:
                client = EvernoteMCPClient()
                client.get_note = MagicMock(return_value=note)
                mock_store.updateNote.return_value = note

                client.set_reminder("test-guid", reminder_time=1704067200000)

                assert note.attributes is not None
                assert note.attributes.reminderTime == 1704067200000
                assert note.attributes.reminderOrder is not None

    def test_set_reminder_with_order(self):
        note = MockNote()
        note.attributes = MockNoteAttributes()

        with patch.object(EvernoteMCPClient, "__init__", lambda x, **kwargs: None):
            with patch.object(
                EvernoteMCPClient, "note_store", new_callable=MagicMock
            ) as mock_store:
                client = EvernoteMCPClient()
                client.get_note = MagicMock(return_value=note)
                mock_store.updateNote.return_value = note

                client.set_reminder(
                    "test-guid", reminder_time=1704067200000, reminder_order=100
                )

                assert note.attributes.reminderTime == 1704067200000
                assert note.attributes.reminderOrder == 100

    def test_complete_reminder(self):
        note = MockNote()
        note.attributes = MockNoteAttributes()
        note.attributes.reminderTime = 1704067200000

        with patch.object(EvernoteMCPClient, "__init__", lambda x, **kwargs: None):
            with patch.object(
                EvernoteMCPClient, "note_store", new_callable=MagicMock
            ) as mock_store:
                client = EvernoteMCPClient()
                client.get_note = MagicMock(return_value=note)
                mock_store.updateNote.return_value = note

                client.complete_reminder("test-guid", done_time=1704153600000)

                assert note.attributes.reminderDoneTime == 1704153600000

    def test_complete_reminder_auto_time(self):
        note = MockNote()
        note.attributes = MockNoteAttributes()

        with patch.object(EvernoteMCPClient, "__init__", lambda x, **kwargs: None):
            with patch.object(
                EvernoteMCPClient, "note_store", new_callable=MagicMock
            ) as mock_store:
                client = EvernoteMCPClient()
                client.get_note = MagicMock(return_value=note)
                mock_store.updateNote.return_value = note

                client.complete_reminder("test-guid")

                assert note.attributes.reminderDoneTime is not None

    def test_clear_reminder(self):
        note = MockNote()
        note.attributes = MockNoteAttributes()
        note.attributes.reminderTime = 1704067200000
        note.attributes.reminderOrder = 100
        note.attributes.reminderDoneTime = 1704153600000

        with patch.object(EvernoteMCPClient, "__init__", lambda x, **kwargs: None):
            with patch.object(
                EvernoteMCPClient, "note_store", new_callable=MagicMock
            ) as mock_store:
                client = EvernoteMCPClient()
                client.get_note = MagicMock(return_value=note)
                mock_store.updateNote.return_value = note

                client.clear_reminder("test-guid")

                assert note.attributes.reminderTime is None
                assert note.attributes.reminderDoneTime is None
                assert note.attributes.reminderOrder is None

    def test_find_reminders_with_completed(self):
        with patch.object(EvernoteMCPClient, "__init__", lambda x, **kwargs: None):
            with patch.object(
                EvernoteMCPClient, "note_store", new_callable=MagicMock
            ) as mock_store:
                client = EvernoteMCPClient()

                mock_result = MagicMock()
                mock_result.notes = []
                mock_store.findNotesMetadata.return_value = mock_result

                client.find_reminders(include_completed=True)

                call_args = mock_store.findNotesMetadata.call_args
                note_filter = call_args.kwargs["filter"]
                assert note_filter.words == "reminderTime:*"

    def test_find_reminders_without_completed(self):
        with patch.object(EvernoteMCPClient, "__init__", lambda x, **kwargs: None):
            with patch.object(
                EvernoteMCPClient, "note_store", new_callable=MagicMock
            ) as mock_store:
                client = EvernoteMCPClient()

                mock_result = MagicMock()
                mock_result.notes = []
                mock_store.findNotesMetadata.return_value = mock_result

                client.find_reminders(include_completed=False)

                call_args = mock_store.findNotesMetadata.call_args
                note_filter = call_args.kwargs["filter"]
                assert note_filter.words == "reminderTime:* -reminderDoneTime:*"


class TestReminderTools:
    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_set_reminder_tool(self, mock_client, mcp):
        register_reminder_tools(mcp, mock_client)

        mock_note = MockNote()
        mock_note.attributes = MockNoteAttributes()
        mock_note.attributes.reminderTime = 1704067200000
        mock_note.attributes.reminderOrder = 100
        mock_client.set_reminder.return_value = mock_note

        tools = mcp._tool_manager._tools
        set_reminder_tool = tools.get("set_reminder")

        if set_reminder_tool:
            result = set_reminder_tool.fn(
                note_guid="test-guid", reminder_time=1704067200000, reminder_order=100
            )
            data = json.loads(result)
            assert data["success"] is True
            assert data["note_guid"] == "test-guid"
            assert data["reminder_time"] == 1704067200000

    def test_complete_reminder_tool(self, mock_client, mcp):
        register_reminder_tools(mcp, mock_client)

        mock_note = MockNote()
        mock_note.attributes = MockNoteAttributes()
        mock_note.attributes.reminderTime = 1704067200000
        mock_note.attributes.reminderDoneTime = 1704153600000
        mock_client.complete_reminder.return_value = mock_note

        tools = mcp._tool_manager._tools
        complete_tool = tools.get("complete_reminder")

        if complete_tool:
            result = complete_tool.fn(note_guid="test-guid", done_time=1704153600000)
            data = json.loads(result)
            assert data["success"] is True
            assert data["reminder_done_time"] == 1704153600000

    def test_clear_reminder_tool(self, mock_client, mcp):
        register_reminder_tools(mcp, mock_client)

        mock_note = MockNote()
        mock_client.clear_reminder.return_value = mock_note

        tools = mcp._tool_manager._tools
        clear_tool = tools.get("clear_reminder")

        if clear_tool:
            result = clear_tool.fn(note_guid="test-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["message"] == "Reminder cleared"

    def test_list_reminders_tool(self, mock_client, mcp):
        register_reminder_tools(mcp, mock_client)

        mock_result = MagicMock()
        mock_result.totalNotes = 2

        mock_note1 = MagicMock()
        mock_note1.guid = "note-1"
        mock_note1.title = "Reminder 1"
        mock_note1.notebookGuid = "nb-1"
        mock_note1.updated = 1704067200000
        mock_note1.attributes = MagicMock()
        mock_note1.attributes.reminderTime = 1704067200000
        mock_note1.attributes.reminderOrder = 100
        mock_note1.attributes.reminderDoneTime = None

        mock_result.notes = [mock_note1]
        mock_client.find_reminders.return_value = mock_result

        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_reminders")

        if list_tool:
            result = list_tool.fn(limit=10, include_completed=False)
            data = json.loads(result)
            assert data["success"] is True
            assert data["count"] == 1
            assert len(data["reminders"]) == 1

    def test_get_reminder_tool(self, mock_client, mcp):
        register_reminder_tools(mcp, mock_client)

        mock_note = MockNote()
        mock_note.attributes = MockNoteAttributes()
        mock_note.attributes.reminderTime = 1704067200000
        mock_note.attributes.reminderOrder = 100
        mock_client.get_note.return_value = mock_note

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_reminder")

        if get_tool:
            result = get_tool.fn(note_guid="test-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["has_reminder"] is True
            assert data["is_completed"] is False

    def test_get_reminder_tool_no_reminder(self, mock_client, mcp):
        register_reminder_tools(mcp, mock_client)

        mock_note = MockNote()
        mock_note.attributes = None
        mock_client.get_note.return_value = mock_note

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_reminder")

        if get_tool:
            result = get_tool.fn(note_guid="test-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["has_reminder"] is False
            assert data["is_completed"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
