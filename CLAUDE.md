# Evernote MCP Server - Project Guidelines for Claude

This document provides context and conventions for Claude Code when working on this project.

## Project Overview

This is a Model Context Protocol (MCP) server that enables Claude Code to interact with Evernote. It supports both:
- **International Evernote** (evernote.com)
- **Yinxiang Biji** (印象笔记, yinxiang.com)

## Technology Stack

- **Language**: Python 3.13+
- **Package Manager**: uv (modern Python package manager)
- **Distribution**: Published as a PyPI package installable via `uvx evernote-mcp`
- **MCP SDK**: `@modelcontextprotocol/sdk-python`

## Project Structure

```
evernote-mcp/
├── evernote_mcp/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── client.py            # Evernote API client wrapper
│   ├── config.py            # Configuration handling
│   ├── resources/           # MCP resource definitions
│   ├── tools/               # MCP tool implementations
│   └── util/                # Utilities (ENML conversion, error handling)
├── tests/
└── pyproject.toml           # Project configuration and dependencies
```

## Coding Conventions

### Python Style
- Follow PEP 8 for code style
- Use type hints for all function signatures
- Use async/await for I/O operations where appropriate
- Maximum line length: 100 characters

### MCP Tools
- All tools are defined in `evernote_mcp/tools/`
- Each tool file should group related functionality
- Tools must have proper error handling with user-friendly messages
- Tool names use snake_case (e.g., `create_notebook`, `list_notes`)

### Error Handling
- Use custom exceptions from `evernote_mcp/util/error_handler.py`
- Always provide context in error messages (what operation failed, why)
- Never expose Evernote auth tokens in error messages or logs

### Documentation
- Keep README.md up to date with installation and configuration instructions
- Document all MCP tools with descriptions, parameters, and return values
- Maintain both English and Chinese (zh-CN) documentation

## Key Principles

1. **Security First**: Never log or expose `EVERNOTE_AUTH_TOKEN`
2. **Dual Backend Support**: Always test against both Evernote and Yinxiang Biji backends
3. **Type Safety**: Use Python type hints throughout
4. **Error Clarity**: Error messages should help users understand and fix issues
5. **MCP Compliance**: Follow MCP specification for tools, resources, and prompts

## Testing

When adding new features:
1. Test with both Evernote backends (`evernote` and `china`)
2. Verify error handling for invalid inputs
3. Check that ENML conversion handles edge cases
4. Ensure tool descriptions are clear and accurate

## Common Tasks

### Adding a New Tool

1. Create tool function in appropriate file under `evernote_mcp/tools/`
2. Add proper type hints and docstring
3. Register the tool in the MCP server setup
4. Update README.md with tool documentation
5. Test with both backends

### Updating Dependencies

1. Modify `pyproject.toml`
2. Test thoroughly with both Evernote backends
3. Ensure uv compatibility

### Documentation Updates

When changing functionality:
- Update README.md (English)
- Update README.zh-CN.md (Chinese)
- Update tool descriptions in code
