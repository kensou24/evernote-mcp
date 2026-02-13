"""MCP tools for resource/attachment operations."""
import base64
import binascii
import json
import logging
from typing import Optional, Any

from mcp.server.fastmcp import FastMCP
from evernote.edam.type.ttypes import ResourceAttributes
from evernote_mcp.client import EvernoteMCPClient

from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def register_resource_tools(mcp: FastMCP, client: EvernoteMCPClient):
    """Register resource-related MCP tools."""

    @mcp.tool()
    def get_resource(
        guid: str,
        with_data: bool = False,
        with_recognition: bool = False,
        with_attributes: bool = True,
        with_alternate_data: bool = False
    ) -> str:
        """
        Get a resource by GUID.

        Args:
            guid: Resource GUID (required)
            with_data: Include binary data
            with_recognition: Include recognition data (OCR)
            with_attributes: Include resource attributes
            with_alternate_data: Include alternate data

        Returns:
            JSON string with resource info
        """
        try:
            resource = client.get_resource(
                guid,
                with_data=with_data,
                with_recognition=with_recognition,
                with_attributes=with_attributes,
                with_alternate_data=with_alternate_data,
            )
            result = {
                "success": True,
                "guid": resource.guid,
                "note_guid": resource.noteGuid,
                "mime": resource.mime,
                "width": getattr(resource, 'width', None),
                "height": getattr(resource, 'height', None),
                "duration": getattr(resource, 'duration', None),
                "active": getattr(resource, 'active', True),
                "attributes": None,
                "data_size": None,
                "recognition_size": None,
                "alternate_data_size": None,
            }

            if with_attributes and hasattr(resource, 'attributes') and resource.attributes:
                attr = resource.attributes
                result["attributes"] = {
                    "source_url": getattr(attr, 'sourceURL', None),
                    "timestamp": getattr(attr, 'timestamp', None),
                    "latitude": getattr(attr, 'latitude', None),
                    "longitude": getattr(attr, 'longitude', None),
                    "altitude": getattr(attr, 'altitude', None),
                    "camera_make": getattr(attr, 'cameraMake', None),
                    "camera_model": getattr(attr, 'cameraModel', None),
                    "file_name": getattr(attr, 'fileName', None),
                    "attachment": getattr(attr, 'attachment', None),
                }

            if with_data and hasattr(resource, 'data') and resource.data:
                result["data_size"] = len(resource.data.body) if resource.data.body else 0
                result["data_hash"] = resource.data.bodyHash.hex() if (hasattr(resource.data, 'bodyHash') and resource.data.bodyHash) else None

            if with_recognition and hasattr(resource, 'recognition') and resource.recognition:
                result["recognition_size"] = len(resource.recognition.body) if resource.recognition.body else 0

            if with_alternate_data and hasattr(resource, 'alternateData') and resource.alternateData:
                result["alternate_data_size"] = len(resource.alternateData.body) if resource.alternateData.body else 0

            logger.info(f"Retrieved resource: {guid}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_resource_data(guid: str, encode: bool = True) -> str:
        """
        Get resource binary data.

        Args:
            guid: Resource GUID (required)
            encode: Return base64 encoded data (default: true). Set to false for raw binary.

        Returns:
            JSON string with binary data (base64 encoded by default)
        """
        try:
            data = client.get_resource_data(guid)
            result = {
                "success": True,
                "guid": guid,
                "size": len(data),
                "data": base64.b64encode(data).decode('utf-8') if encode else None,
                "hash_hex": binascii.hexlify(data).decode('utf-8') if data else None,
            }
            if not encode:
                result["data_raw_preview"] = data[:100].hex() if len(data) > 0 else ""
                result["note"] = "Raw binary data not included in JSON (use encode=true for base64)"
            logger.info(f"Retrieved resource data: {guid}, size: {len(data)}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_resource_alternate_data(guid: str, encode: bool = True) -> str:
        """
        Get resource alternate data (e.g., PDF preview of an image).

        Args:
            guid: Resource GUID (required)
            encode: Return base64 encoded data (default: true)

        Returns:
            JSON string with alternate data
        """
        try:
            data = client.get_resource_alternate_data(guid)
            result = {
                "success": True,
                "guid": guid,
                "size": len(data),
                "data": base64.b64encode(data).decode('utf-8') if encode else None,
            }
            logger.info(f"Retrieved resource alternate data: {guid}, size: {len(data)}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_resource_attributes(guid: str) -> str:
        """
        Get resource attributes (metadata about the resource).

        Args:
            guid: Resource GUID (required)

        Returns:
            JSON string with resource attributes
        """
        try:
            attributes = client.get_resource_attributes(guid)
            result = {
                "success": True,
                "guid": guid,
                "source_url": getattr(attributes, 'sourceURL', None),
                "timestamp": getattr(attributes, 'timestamp', None),
                "latitude": getattr(attributes, 'latitude', None),
                "longitude": getattr(attributes, 'longitude', None),
                "altitude": getattr(attributes, 'altitude', None),
                "camera_make": getattr(attributes, 'cameraMake', None),
                "camera_model": getattr(attributes, 'cameraModel', None),
                "client_will_index": getattr(attributes, 'clientWillIndex', None),
                "reco_type": getattr(attributes, 'recoType', None),
                "file_name": getattr(attributes, 'fileName', None),
                "attachment": getattr(attributes, 'attachment', None),
                "application_data": getattr(attributes, 'applicationData', None),
            }
            logger.info(f"Retrieved resource attributes: {guid}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_resource_by_hash(
        note_guid: str,
        content_hash: str,
        with_data: bool = False,
        with_recognition: bool = False,
        with_attributes: bool = True,
        with_alternate_data: bool = False
    ) -> str:
        """
        Get resource by content hash (MD5 hex string).

        Args:
            note_guid: Note GUID containing the resource (required)
            content_hash: MD5 hash of resource content as hex string (required)
            with_data: Include binary data
            with_recognition: Include recognition data
            with_attributes: Include attributes
            with_alternate_data: Include alternate data

        Returns:
            JSON string with resource info
        """
        try:
            # Convert hex string to bytes
            hash_bytes = binascii.unhexlify(content_hash)
            resource = client.get_resource_by_hash(
                note_guid,
                hash_bytes,
                with_data=with_data,
                with_recognition=with_recognition,
                with_attributes=with_attributes,
                with_alternate_data=with_alternate_data,
            )
            result = {
                "success": True,
                "guid": resource.guid,
                "note_guid": resource.noteGuid,
                "mime": resource.mime,
            }
            if with_attributes and hasattr(resource, 'attributes') and resource.attributes:
                result["attributes"] = {
                    "file_name": getattr(resource.attributes, 'fileName', None),
                    "source_url": getattr(resource.attributes, 'sourceURL', None),
                }
            logger.info(f"Retrieved resource by hash: {content_hash[:8] if len(content_hash) >= 8 else content_hash}...")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except binascii.Error:
            return json.dumps({
                "success": False,
                "error": "Invalid content_hash format. Must be a hex string (e.g., '1a2b3c4d...')"
            }, indent=2)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_resource_recognition(guid: str, encode: bool = True) -> str:
        """
        Get resource recognition data (OCR/text recognition for images/PDFs).

        Args:
            guid: Resource GUID (required)
            encode: Return base64 encoded data (default: true)

        Returns:
            JSON string with recognition data
        """
        try:
            data = client.get_resource_recognition(guid)
            result = {
                "success": True,
                "guid": guid,
                "size": len(data),
                "data": base64.b64encode(data).decode('utf-8') if encode else None,
            }
            logger.info(f"Retrieved resource recognition: {guid}, size: {len(data)}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_resource_search_text(guid: str) -> str:
        """
        Get extracted search text from a resource.

        Args:
            guid: Resource GUID (required)

        Returns:
            JSON string with search text
        """
        try:
            text = client.get_resource_search_text(guid)
            result = {
                "success": True,
                "guid": guid,
                "text": text,
                "length": len(text) if text else 0,
            }
            logger.info(f"Retrieved resource search text: {guid}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def update_resource(
        guid: str,
        mime: Optional[str] = None,
        attributes: Optional[str] = None
    ) -> str:
        """
        Update an existing resource. Note: To update resource data, you must
        re-create the resource in the note.

        Args:
            guid: Resource GUID (required)
            mime: New MIME type (optional)
            attributes: JSON string of resource attributes to update (optional)

        Returns:
            JSON string with update result
        """
        try:
            resource = client.get_resource(guid, with_data=False, with_attributes=True)
            if mime:
                resource.mime = mime
            if attributes:
                attr_dict = json.loads(attributes)
                if not resource.attributes:
                    resource.attributes = ResourceAttributes()
                for key, value in attr_dict.items():
                    if hasattr(resource.attributes, key):
                        setattr(resource.attributes, key, value)
            update_sequence_num = client.update_resource(resource)
            result = {
                "success": True,
                "guid": guid,
                "update_sequence_num": update_sequence_num,
            }
            logger.info(f"Updated resource: {guid}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def set_resource_application_data_entry(guid: str, key: str, value: str) -> str:
        """
        Set application data entry for a resource.

        Args:
            guid: Resource GUID (required)
            key: Entry key (required, max 32 chars)
            value: Entry value (required, max 100 chars)

        Returns:
            JSON string with operation result
        """
        try:
            update_sequence_num = client.set_resource_application_data_entry(guid, key, value)
            result = {
                "success": True,
                "guid": guid,
                "key": key,
                "update_sequence_num": update_sequence_num,
            }
            logger.info(f"Set resource application data: {guid}, key: {key}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def unset_resource_application_data_entry(guid: str, key: str) -> str:
        """
        Remove application data entry from a resource.

        Args:
            guid: Resource GUID (required)
            key: Entry key to remove (required)

        Returns:
            JSON string with operation result
        """
        try:
            update_sequence_num = client.unset_resource_application_data_entry(guid, key)
            result = {
                "success": True,
                "guid": guid,
                "key": key,
                "update_sequence_num": update_sequence_num,
            }
            logger.info(f"Unset resource application data: {guid}, key: {key}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_resource_application_data(guid: str) -> str:
        """
        Get all application data for a resource.

        Args:
            guid: Resource GUID (required)

        Returns:
            JSON string with application data map
        """
        try:
            app_data = client.get_resource_application_data(guid)
            result = {
                "success": True,
                "guid": guid,
                "application_data": app_data if app_data else {},
            }
            logger.info(f"Retrieved resource application data: {guid}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_resource_application_data_entry(guid: str, key: str) -> str:
        """
        Get a specific application data entry from a resource.

        Args:
            guid: Resource GUID (required)
            key: Entry key (required)

        Returns:
            JSON string with entry value
        """
        try:
            value = client.get_resource_application_data_entry(guid, key)
            result = {
                "success": True,
                "guid": guid,
                "key": key,
                "value": value,
            }
            logger.info(f"Retrieved resource application data entry: {guid}, key: {key}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)
