"""MCP tools for notebook operations."""
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
from evernote.edam.error.ttypes import EDAMUserException, EDAMSystemException
from evernote.edam.type.ttypes import Notebook

from evernote_mcp.util.error_handler import handle_evernote_error

logger = logging.getLogger(__name__)


def register_notebook_tools(mcp: FastMCP, client):
    """Register notebook-related MCP tools."""

    @mcp.tool()
    def create_notebook(name: str, stack: Optional[str] = None) -> str:
        """
        Create a new Evernote notebook.

        Args:
            name: Notebook name (required)
            stack: Optional stack name to group notebook

        Returns:
            JSON string with created notebook info including GUID
        """
        try:
            notebook = client.create_notebook(name, stack)
            result = {
                "success": True,
                "guid": notebook.guid,
                "name": notebook.name,
                "stack": notebook.stack,
                "created": notebook.serviceCreated,
            }
            logger.info(f"Created notebook: {notebook.name} ({notebook.guid})")
            return __import__("json").dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return __import__("json").dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def update_notebook(
        guid: str,
        name: Optional[str] = None,
        stack: Optional[str] = None
    ) -> str:
        """
        Update an existing notebook.

        Args:
            guid: Notebook GUID (required)
            name: New notebook name (optional)
            stack: New stack name (optional, use empty string to remove)

        Returns:
            JSON string with updated notebook info
        """
        try:
            notebook = client.get_notebook(guid)
            if name:
                notebook.name = name
            if stack is not None:
                notebook.stack = stack if stack else None

            updated = client.update_notebook(notebook)
            result = {
                "success": True,
                "guid": updated.guid,
                "name": updated.name,
                "stack": updated.stack,
                "updated": updated.serviceUpdated,
            }
            logger.info(f"Updated notebook: {updated.name} ({updated.guid})")
            return __import__("json").dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return __import__("json").dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def delete_notebook(guid: str) -> str:
        """
        Delete a notebook (moves notes to trash, permanently deletes notebook).

        Args:
            guid: Notebook GUID to delete

        Returns:
            JSON string with operation result
        """
        try:
            client.expunge_notebook(guid)
            result = {
                "success": True,
                "message": f"Notebook {guid} deleted"
            }
            logger.info(f"Deleted notebook: {guid}")
            return __import__("json").dumps(result, indent=2)
        except Exception as e:
            return __import__("json").dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def list_notebooks() -> str:
        """
        List all notebooks in the Evernote account.

        Returns:
            JSON string with array of notebooks including GUID, name, stack
        """
        try:
            notebooks = client.list_notebooks()
            result = {
                "success": True,
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
            logger.info(f"Listed {len(notebooks)} notebook(s)")
            return __import__("json").dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return __import__("json").dumps(handle_evernote_error(e), indent=2)

    @mcp.tool()
    def get_notebook(guid: str) -> str:
        """
        Get notebook details by GUID.

        Args:
            guid: Notebook GUID

        Returns:
            JSON string with notebook details
        """
        try:
            notebook = client.get_notebook(guid)
            result = {
                "success": True,
                "guid": notebook.guid,
                "name": notebook.name,
                "stack": notebook.stack,
                "created": notebook.serviceCreated,
                "updated": notebook.serviceUpdated,
                "default_notebook": getattr(notebook, 'defaultNotebook', False),
            }
            return __import__("json").dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            return __import__("json").dumps(handle_evernote_error(e), indent=2)
