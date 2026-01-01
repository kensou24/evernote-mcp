"""MCP resources for notebooks."""
import logging
import json
from mcp.server.fastmcp import FastMCP

from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def register_notebook_resources(mcp: FastMCP, client):
    """Register notebook resources."""

    @mcp.resource("notebooks")
    def list_all_notebooks() -> str:
        """
        List all notebooks as a resource.

        Returns:
            JSON string with all notebooks
        """
        try:
            notebooks = client.list_notebooks()
            result = {
                "notebooks": [
                    {
                        "guid": nb.guid,
                        "name": nb.name,
                        "stack": nb.stack,
                        "created": nb.serviceCreated,
                        "updated": nb.serviceUpdated,
                        "default_notebook": getattr(nb, 'defaultNotebook', False),
                    }
                    for nb in notebooks
                ]
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)

    @mcp.resource("notebook://{guid}")
    def get_notebook_metadata(guid: str) -> str:
        """
        Get notebook metadata.

        URI format: notebook://{guid}

        Args:
            guid: Notebook GUID

        Returns:
            JSON string with notebook details
        """
        try:
            notebook = client.get_notebook(guid)
            result = {
                "guid": notebook.guid,
                "name": notebook.name,
                "stack": notebook.stack,
                "created": notebook.serviceCreated,
                "updated": notebook.serviceUpdated,
                "default_notebook": getattr(notebook, 'defaultNotebook', False),
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)
