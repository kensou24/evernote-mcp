# Evernote MCP Server

[English](README.md) | [简体中文](README.zh-CN.md)

Model Context Protocol (MCP) server for Evernote - enables Claude Code to interact with your Evernote notes.

> **Supports both [International Evernote](https://evernote.com) and [Yinxiang Biji (印象笔记)](https://yinxiang.com)**

## Features

- **Notebook operations** (create, read, update, delete, list, get default)
- **Note operations** (create, read, update, delete, copy, move, list, versions)
- **Tag management** (create, read, update, delete, list, find by notebook)
- **Saved searches** (create, read, update, delete, list)
- **Resource/Attachment operations** (get, update, data, attributes, recognition)
- **Advanced note features** (get content, search text, tag names, note versions)
- **Sync & utilities** (sync state, note counts, find related content)
- Full-text search using Evernote's search syntax
- Multiple output formats (ENML, text, markdown, JSON)

## Installation

```bash
npm install -g @anthropic/claude-code
uvx evernote-mcp
```

## Configuration

### 1. Get Evernote Developer Token

**International Evernote**: https://evernote.com/api/DeveloperToken.action

**Yinxiang Biji (印象笔记)**: https://app.yinxiang.com/api/DeveloperToken.action

### 2. Configure Claude Code

Edit `~/.config/claude-code/config.json`:

**For International Evernote:**
```json
{
  "mcpServers": {
    "evernote": {
      "command": "uvx",
      "args": ["evernote-mcp"],
      "env": {
        "EVERNOTE_AUTH_TOKEN": "your_token_here",
        "EVERNOTE_BACKEND": "evernote"
      }
    }
  }
}
```

**For Yinxiang Biji (印象笔记):**
```json
{
  "mcpServers": {
    "evernote": {
      "command": "uvx",
      "args": ["evernote-mcp"],
      "env": {
        "EVERNOTE_AUTH_TOKEN": "your_token_here",
        "EVERNOTE_BACKEND": "china"
      }
    }
  }
}
```

## Usage Examples

```bash
claude-code
```

```
User: Create a note in my "Project Notes" notebook summarizing the current TODO items from src/todo.py

Claude: I'll read the TODO file and create a note for you.
[Creates note with extracted TODOs]
```

```
User: Search my Evernote for notes about "API design" and summarize the key points

Claude: Let me search for those notes and analyze them.
[Searches and summarizes findings]
```

```
User: Create a notebook called "Code Reviews" and add a note template

Claude: I'll set that up for you.
[Creates notebook and template note]
```

```
User: Find all notes tagged with "important" and list them by update time

Claude: I'll search for notes with that tag and sort them.
[Uses search_notes and list_tags]
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERNOTE_AUTH_TOKEN` | - | Your developer token (required) |
| `EVERNOTE_BACKEND` | `evernote` | `evernote` (International) or `china` (印象笔记) |

## Available Tools

### Notebooks (6 tools)
- `create_notebook(name, stack)` - Create a new notebook
- `list_notebooks()` - List all notebooks
- `get_notebook(guid)` - Get notebook details by GUID
- `update_notebook(guid, name, stack)` - Update notebook name/stack
- `expunge_notebook(guid)` - Permanently delete notebook
- `get_default_notebook()` - Get the default notebook for new notes

### Notes (8 tools)
- `create_note(title, content, notebook_guid, tags, format)` - Create a new note
- `get_note(guid, output_format)` - Get note (enml/text/markdown/json)
- `update_note(guid, title, content, format)` - Update note title/content
- `delete_note(guid)` - Move note to trash
- `expunge_note(guid)` - Permanently delete note
- `copy_note(guid, target_notebook_guid)` - Copy note to another notebook
- `move_note(guid, target_notebook_guid)` - Move note to another notebook
- `list_notes(notebook_guid, limit)` - List notes in notebook

### Tags (7 tools)
- `list_tags()` - List all tags
- `get_tag(guid)` - Get tag details by GUID
- `create_tag(name, parent_guid)` - Create a new tag
- `update_tag(guid, name, parent_guid)` - Update tag name/parent
- `expunge_tag(guid)` - Permanently delete tag
- `list_tags_by_notebook(notebook_guid)` - List tags in a specific notebook
- `untag_all(guid)` - Remove tag from all notes

### Saved Searches (5 tools)
- `list_searches()` - List all saved searches
- `get_search(guid)` - Get saved search by GUID
- `create_search(name, query)` - Create a new saved search
- `update_search(guid, name, query)` - Update saved search
- `expunge_search(guid)` - Delete saved search

### Advanced Note Operations (5 tools)
- `get_note_content(guid)` - Get ENML content only
- `get_note_search_text(guid, note_only, tokenize_for_indexing)` - Get extracted plain text
- `get_note_tag_names(guid)` - Get tag names for a note
- `list_note_versions(note_guid)` - List previous versions (Premium only)
- `get_note_version(note_guid, update_sequence_num, ...)` - Get specific version (Premium)

### Resources/Attachments (13 tools)
- `get_resource(guid, with_data, with_recognition, ...)` - Get resource by GUID
- `get_resource_data(guid, encode)` - Get resource binary data (base64)
- `get_resource_alternate_data(guid, encode)` - Get alternate data (e.g., PDF preview)
- `get_resource_attributes(guid)` - Get resource metadata
- `get_resource_by_hash(note_guid, content_hash, ...)` - Find resource by MD5 hash
- `get_resource_recognition(guid, encode)` - Get OCR/recognition data
- `get_resource_search_text(guid)` - Get extracted search text from resource
- `update_resource(guid, mime, attributes)` - Update resource metadata
- `set_resource_application_data_entry(guid, key, value)` - Set app data
- `unset_resource_application_data_entry(guid, key)` - Remove app data
- `get_resource_application_data(guid)` - Get all application data
- `get_resource_application_data_entry(guid, key)` - Get specific app data entry

### Search & Utilities (4 tools)
- `search_notes(query, notebook_guid, limit)` - Search using Evernote query syntax
- `get_sync_state()` - Get sync state information
- `find_note_counts(query, with_trash)` - Get note counts per notebook/tag
- `find_related(note_guid, plain_text, max_notes, ...)` - Find related notes/tags/notebooks

## License

MIT
