# Evernote MCP Server

[English](README.md) | [简体中文](README.zh-CN.md)

Model Context Protocol (MCP) server for Evernote - enables Claude Code to interact with your Evernote notes.

> **Supports both [International Evernote](https://evernote.com) and [Yinxiang Biji (印象笔记)](https://yinxiang.com)**

## Features

- Notebook operations (create, update, delete, list)
- Note operations (create, read, update, delete, copy, move)
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

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERNOTE_AUTH_TOKEN` | - | Your developer token (required) |
| `EVERNOTE_BACKEND` | `evernote` | `evernote` (International) or `china` (印象笔记) |

## Available Tools

### Notebooks
- `create_notebook(name, stack)` - Create notebook
- `list_notebooks()` - List all notebooks
- `get_notebook(guid)` - Get notebook details
- `update_notebook(guid, name, stack)` - Update notebook
- `delete_notebook(guid)` - Delete notebook

### Notes
- `create_note(title, content, notebook_guid, tags)` - Create note
- `get_note(guid, output_format)` - Get note (enml/text/markdown/json)
- `update_note(guid, title, content)` - Update note
- `delete_note(guid)` - Move to trash
- `copy_note(guid, target_notebook_guid)` - Copy note
- `move_note(guid, target_notebook_guid)` - Move note
- `list_notes(notebook_guid, limit)` - List notes

### Search
- `search_notes(query, notebook_guid)` - Search notes
- `list_tags()` - List all tags

## License

MIT
