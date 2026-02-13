"""Evernote MCP server - main entry point."""
import logging
import sys

# Configure logging to stderr (important for stdio MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


def main():
    """Start the Evernote MCP server."""
    from mcp.server.fastmcp import FastMCP

    from evernote_mcp.config import EvernoteConfig
    from evernote_mcp.client import EvernoteMCPClient
    from evernote_mcp.tools.notebook_tools import register_notebook_tools
    from evernote_mcp.tools.note_tools import register_note_tools
    from evernote_mcp.tools.search_tools import register_search_tools
    from evernote_mcp.tools.tag_tools import register_tag_tools
    from evernote_mcp.tools.search_tools_extended import register_search_tools_extended
    from evernote_mcp.tools.note_advanced_tools import register_note_advanced_tools
    from evernote_mcp.tools.sync_tools import register_sync_tools
    from evernote_mcp.tools.resource_tools import register_resource_tools
    from evernote_mcp.resources.notebook_resource import register_notebook_resources
    from evernote_mcp.resources.note_resource import register_note_resources

    # Load configuration from environment
    try:
        config = EvernoteConfig.from_env()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize Evernote client
    try:
        client = EvernoteMCPClient(
            auth_token=config.auth_token,
            backend=config.backend,
            network_retry_count=config.network_retry_count,
            use_system_ssl_ca=config.use_system_ssl_ca,
        )
    except Exception as e:
        logger.error(f"Failed to initialize Evernote client: {e}")
        sys.exit(1)

    # Create FastMCP server
    mcp = FastMCP("evernote-mcp")

    # Register all tools
    register_notebook_tools(mcp, client)
    register_note_tools(mcp, client)
    register_search_tools(mcp, client)
    register_tag_tools(mcp, client)
    register_search_tools_extended(mcp, client)
    register_note_advanced_tools(mcp, client)
    register_sync_tools(mcp, client)
    register_resource_tools(mcp, client)

    # Register all resources
    register_notebook_resources(mcp, client)
    register_note_resources(mcp, client)

    # Run the server
    logger.info("Starting Evernote MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
