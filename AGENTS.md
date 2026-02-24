# Evernote MCP Server - Knowledge Base

**Generated:** 2026-02-24
**Commit:** bf6290e
**Branch:** main

## OVERVIEW

Model Context Protocol (MCP) server enabling AI assistants (Claude) to interact with Evernote. Supports both International Evernote (evernote.com) and Yinxiang Biji (yinxiang.com). Python 3.10+, distributed via PyPI as `evernote-mcp`.

## STRUCTURE

```
evernote-mcp/
├── evernote_mcp/
│   ├── __main__.py          # Entry point - FastMCP server init
│   ├── client.py            # EvernoteMCPClient (wraps evernote-backup)
│   ├── config.py            # Env-based config (token, backend)
│   ├── tools/               # MCP tool implementations (8 modules)
│   ├── resources/           # MCP resource definitions (2 modules)
│   └── util/                # ENML converter, error handler
├── tests/                   # Empty - no tests yet
├── pyproject.toml           # Build config (poetry-core, uv package manager)
└── CLAUDE.md                # Project conventions
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new MCP tool | `evernote_mcp/tools/` | See `evernote_mcp/tools/AGENTS.md` |
| Modify API client | `evernote_mcp/client.py` | Inherits from `evernote_backup.EvernoteClient` |
| Error handling | `evernote_mcp/util/error_handler.py` | `handle_evernote_error()` |
| ENML conversion | `evernote_mcp/util/enml_converter.py` | text ↔ ENML ↔ markdown |
| Server startup | `evernote_mcp/__main__.py` | Registers all tools/resources |
| Configuration | `evernote_mcp/config.py` + `.env` | EVERNOTE_AUTH_TOKEN, EVERNOTE_BACKEND |

## CONVENTIONS

### Tool Pattern
```python
def register_xxx_tools(mcp: FastMCP, client):
    @mcp.tool()
    def tool_name(param: type) -> str:
        """One-line docstring."""
        try:
            # Implementation
            return json.dumps({"success": True, ...})
        except Exception as e:
            return json.dumps(handle_evernote_error(e))
```

### Naming
- Tool names: `snake_case` (e.g., `create_note`, `list_notebooks`)
- All tools return JSON strings
- Error responses include `{"success": False, "error": "..."}`

### Code Style
- Line length: 88 chars (ruff default, NOT 100 as CLAUDE.md states)
- Type hints required on all function signatures
- PEP 8, async/await for I/O

## ANTI-PATTERNS (THIS PROJECT)

| Rule | Severity |
|------|----------|
| NEVER log/expose `EVERNOTE_AUTH_TOKEN` | CRITICAL |
| NEVER skip dual backend testing (evernote + china) | HIGH |
| NEVER re-upload same version to PyPI | HIGH |
| ALWAYS use `handle_evernote_error()` in tools | MEDIUM |
| ALWAYS maintain README.md + README.zh-CN.md | MEDIUM |

## COMMANDS

```bash
# Development
uv sync                           # Install dependencies
uv run ruff check .               # Lint
uv run ruff check --fix .         # Auto-fix

# Build & Publish
uv build --out-dir dist/          # Build wheel + tarball
uv publish --token $TOKEN dist/*  # Publish to PyPI

# Run server
uvx evernote-mcp                  # Or: evernote-mcp
```

## ENVIRONMENT

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERNOTE_AUTH_TOKEN` | - | Required |
| `EVERNOTE_BACKEND` | `evernote` | `evernote` or `china` |
| `EVERNOTE_RETRY_COUNT` | 5 | Network retries |
| `EVERNOTE_USE_SYSTEM_SSL_CA` | false | Use system CA certs |

## NOTES

- **No tests**: `tests/` is empty despite pytest in dependencies
- **Package manager mix**: pyproject.toml uses poetry-core format but `uv` is the actual tool
- **GitLab CI**: Only AI-assisted review, no automated testing/linting
- **Imports in main()**: `__main__.py` imports inside function (minor deviation)
- **Dual README**: Maintain both English and Chinese versions
