# MCP Tools Module

**Generated:** 2026-02-24

## OVERVIEW

All MCP tool implementations for Evernote operations. Each file exports a `register_*_tools(mcp, client)` function called from `__main__.py`.

## STRUCTURE

```
tools/
├── notebook_tools.py      # Notebook CRUD (6 tools)
├── note_tools.py          # Note CRUD + copy/move/list (8 tools)
├── note_advanced_tools.py # Content, versions, tag names (5 tools)
├── tag_tools.py           # Tag CRUD + untag_all (7 tools)
├── search_tools.py        # Saved searches CRUD (5 tools)
├── search_tools_extended.py # Full-text search, find_related (4 tools)
└── sync_tools.py          # Sync state, note counts (4 tools)
```

## WHERE TO LOOK

| Tool Type | File | Key Functions |
|-----------|------|---------------|
| Create/read/update/delete notebooks | `notebook_tools.py` | `create_notebook`, `get_notebook`, `update_notebook`, `expunge_notebook` |
| Create/read/update/delete notes | `note_tools.py` | `create_note`, `get_note`, `update_note`, `delete_note`, `expunge_note`, `copy_note`, `move_note`, `list_notes` |
| Note content/versions | `note_advanced_tools.py` | `get_note_content`, `get_note_search_text`, `get_note_tag_names`, `list_note_versions`, `get_note_version` |
| Tag operations | `tag_tools.py` | `create_tag`, `get_tag`, `update_tag`, `expunge_tag`, `list_tags`, `list_tags_by_notebook`, `untag_all` |
| Saved searches | `search_tools.py` | `create_search`, `get_search`, `update_search`, `expunge_search`, `list_searches` |
| Full-text search | `search_tools_extended.py` | `search_notes`, `get_sync_state`, `find_note_counts`, `find_related` |
| Sync utilities | `sync_tools.py` | `get_sync_state`, `get_default_notebook`, `find_note_counts`, `find_related` |

## CONVENTIONS

### Registration Pattern
```python
def register_xxx_tools(mcp: FastMCP, client):
    @mcp.tool()
    def tool_name(param: type) -> str:
        """Docstring for MCP tool registry."""
        try:
            result = client.operation(...)
            return json.dumps({"success": True, ...}, indent=2, ensure_ascii=False)
        except Exception as e:
            return json.dumps(handle_evernote_error(e), indent=2)
```

### Parameter Patterns
- All GUID params: `guid: str`
- Optional params: `Optional[type] = None`
- Format params: `format: str = "text"` (text/enml/markdown)
- Limit params: `limit: int = 100`

### Return Format
- Always `str` (JSON-encoded)
- Success: `{"success": True, ...data}`
- Error: `{"success": False, "error": "message"}`

## ANTI-PATTERNS (THIS MODULE)

| Rule | Notes |
|------|-------|
| NEVER expose auth tokens | Check error messages before returning |
| NEVER skip `handle_evernote_error()` | All tools must use it in except block |
| NEVER use `as any` or `@ts-ignore` | Type safety required |

## NOTES

- **Most complex file**: `note_tools.py` (298 lines, 8 tools)
- **Evernote search syntax**: See `search_notes` for query examples (intitle:, tag:, created:, etc.)
- **Premium features**: `list_note_versions`, `get_note_version` require Evernote Premium
- **ENML conversion**: Uses `util/enml_converter.py` for text/markdown ↔ ENML
