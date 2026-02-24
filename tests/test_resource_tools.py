"""Integration tests for resource tools."""

import json
import binascii
from unittest.mock import MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from evernote_mcp.tools.resource_tools import register_resource_tools


class MockResourceAttributes:
    def __init__(self):
        self.sourceURL = "https://example.com/image.png"
        self.timestamp = 1704067200000
        self.latitude = 37.7749
        self.longitude = -122.4194
        self.altitude = 100.0
        self.cameraMake = "Canon"
        self.cameraModel = "EOS R5"
        self.fileName = "photo.png"
        self.attachment = False


class MockResourceData:
    def __init__(self, data: bytes | None = None):
        self.body = data or b"fake image data"
        self.bodyHash = binascii.unhexlify("1a2b3c4d5e6f7890abcdef1234567890")


class MockResource:
    def __init__(self, guid: str = "res-guid"):
        self.guid = guid
        self.noteGuid = "note-guid"
        self.mime = "image/png"
        self.width = 1920
        self.height = 1080
        self.active = True
        self.data = MockResourceData()
        self.recognition = None
        self.alternateData = None
        self.attributes = MockResourceAttributes()


class TestResourceTools:
    """Integration tests for resource MCP tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        mock_resource = MockResource()
        mock.get_resource.return_value = mock_resource
        mock.get_resource_data.return_value = b"binary data"
        mock.get_resource_alternate_data.return_value = b"alternate data"
        mock.get_resource_attributes.return_value = MockResourceAttributes()
        mock.get_resource_by_hash.return_value = mock_resource
        mock.get_resource_recognition.return_value = b"ocr data"
        mock.get_resource_search_text.return_value = "searchable text from image"
        mock.update_resource.return_value = 123
        mock.set_resource_application_data_entry.return_value = 123
        mock.unset_resource_application_data_entry.return_value = 123
        mock.get_resource_application_data.return_value = {"key": "value"}
        mock.get_resource_application_data_entry.return_value = "value"
        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_get_resource_basic(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_resource")

        if get_tool:
            result = get_tool.fn(guid="res-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["mime"] == "image/png"
            assert data["note_guid"] == "note-guid"

    def test_get_resource_with_attributes(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_resource")

        if get_tool:
            result = get_tool.fn(guid="res-guid", with_attributes=True)
            data = json.loads(result)
            assert data["success"] is True
            assert data["attributes"] is not None
            assert data["attributes"]["file_name"] == "photo.png"
            assert data["attributes"]["camera_make"] == "Canon"

    def test_get_resource_with_data(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_resource")

        if get_tool:
            result = get_tool.fn(guid="res-guid", with_data=True)
            data = json.loads(result)
            assert data["success"] is True
            assert data["data_size"] is not None
            assert data["data_hash"] is not None

    def test_get_resource_with_recognition(self, mock_client, mcp):
        mock_resource = MockResource()
        mock_resource.recognition = MockResourceData(b"recognition data")
        mock_client.get_resource.return_value = mock_resource

        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_resource")

        if get_tool:
            result = get_tool.fn(guid="res-guid", with_recognition=True)
            data = json.loads(result)
            assert data["success"] is True
            assert data["recognition_size"] is not None

    def test_get_resource_with_alternate_data(self, mock_client, mcp):
        mock_resource = MockResource()
        mock_resource.alternateData = MockResourceData(b"alternate data")
        mock_client.get_resource.return_value = mock_resource

        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_resource")

        if get_tool:
            result = get_tool.fn(guid="res-guid", with_alternate_data=True)
            data = json.loads(result)
            assert data["success"] is True
            assert data["alternate_data_size"] is not None

    def test_get_resource_data(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_data_tool = tools.get("get_resource_data")

        if get_data_tool:
            result = get_data_tool.fn(guid="res-guid", encode=True)
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["size"] == len(b"binary data")
            assert "data" in data
            assert "hash_hex" in data

    def test_get_resource_data_not_encoded(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_data_tool = tools.get("get_resource_data")

        if get_data_tool:
            result = get_data_tool.fn(guid="res-guid", encode=False)
            data = json.loads(result)
            assert data["success"] is True
            assert data["data"] is None
            assert "data_raw_preview" in data
            assert "note" in data

    def test_get_resource_alternate_data(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_alt_tool = tools.get("get_resource_alternate_data")

        if get_alt_tool:
            result = get_alt_tool.fn(guid="res-guid", encode=True)
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["size"] == len(b"alternate data")
            assert "data" in data

    def test_get_resource_attributes(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_attr_tool = tools.get("get_resource_attributes")

        if get_attr_tool:
            result = get_attr_tool.fn(guid="res-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["source_url"] == "https://example.com/image.png"
            assert data["camera_make"] == "Canon"
            assert data["camera_model"] == "EOS R5"

    def test_get_resource_by_hash(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_by_hash_tool = tools.get("get_resource_by_hash")

        if get_by_hash_tool:
            hash_hex = "1a2b3c4d5e6f7890abcdef1234567890"
            result = get_by_hash_tool.fn(
                note_guid="note-guid",
                content_hash=hash_hex
            )
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["mime"] == "image/png"

    def test_get_resource_by_hash_invalid_hex(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_by_hash_tool = tools.get("get_resource_by_hash")

        if get_by_hash_tool:
            result = get_by_hash_tool.fn(
                note_guid="note-guid",
                content_hash="invalid-hex!!"
            )
            data = json.loads(result)
            assert data["success"] is False
            assert "Invalid content_hash format" in data["error"]

    def test_get_resource_recognition(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_recog_tool = tools.get("get_resource_recognition")

        if get_recog_tool:
            result = get_recog_tool.fn(guid="res-guid", encode=True)
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["size"] == len(b"ocr data")
            assert "data" in data

    def test_get_resource_search_text(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_text_tool = tools.get("get_resource_search_text")

        if get_text_tool:
            result = get_text_tool.fn(guid="res-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["text"] == "searchable text from image"
            assert data["length"] == len("searchable text from image")

    def test_update_resource(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_resource")

        if update_tool:
            result = update_tool.fn(guid="res-guid", mime="image/jpeg")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["update_sequence_num"] == 123

    def test_update_resource_with_attributes(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        update_tool = tools.get("update_resource")

        if update_tool:
            attrs = json.dumps({"fileName": "new-name.png"})
            result = update_tool.fn(guid="res-guid", attributes=attrs)
            data = json.loads(result)
            assert data["success"] is True

    def test_set_resource_application_data_entry(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        set_data_tool = tools.get("set_resource_application_data_entry")

        if set_data_tool:
            result = set_data_tool.fn(
                guid="res-guid",
                key="myKey",
                value="myValue"
            )
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["key"] == "myKey"
            assert data["update_sequence_num"] == 123

    def test_unset_resource_application_data_entry(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        unset_data_tool = tools.get("unset_resource_application_data_entry")

        if unset_data_tool:
            result = unset_data_tool.fn(guid="res-guid", key="myKey")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["key"] == "myKey"

    def test_get_resource_application_data(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_app_data_tool = tools.get("get_resource_application_data")

        if get_app_data_tool:
            result = get_app_data_tool.fn(guid="res-guid")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["application_data"] == {"key": "value"}

    def test_get_resource_application_data_entry(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_entry_tool = tools.get("get_resource_application_data_entry")

        if get_entry_tool:
            result = get_entry_tool.fn(guid="res-guid", key="myKey")
            data = json.loads(result)
            assert data["success"] is True
            assert data["guid"] == "res-guid"
            assert data["key"] == "myKey"
            assert data["value"] == "value"


class TestResourceToolsErrorHandling:
    """Test error handling in resource tools."""

    @pytest.fixture
    def mock_client(self):
        mock = MagicMock()
        mock.get_resource.side_effect = Exception("Resource not found")
        return mock

    @pytest.fixture
    def mcp(self):
        return FastMCP("test")

    def test_get_resource_handles_error(self, mock_client, mcp):
        register_resource_tools(mcp, mock_client)

        tools = mcp._tool_manager._tools
        get_tool = tools.get("get_resource")

        if get_tool:
            result = get_tool.fn(guid="invalid-guid")
            data = json.loads(result)
            assert data["success"] is False
            assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
