# Evernote MCP Server

Model Context Protocol (MCP) server for Evernote operations - enables AI assistants like Claude to interact with Evernote.

## Features

- **Notebook Operations**: Create, update, delete, and list notebooks
- **Note Operations**: Create, read, update, delete, copy, and move notes
- **Search**: Full-text search using Evernote's search syntax
- **Resources**: Direct access to notebooks and notes via MCP resources
- **Format Conversion**: ENML to text/markdown conversion

## Installation

### Using uv (Recommended)

```bash
uv tool install evernote-mcp
```

### Using pipx

```bash
pipx install evernote-mcp
```

### From source

```bash
git clone https://github.com/king/evernote-mcp.git
cd evernote-mcp
poetry install
```

## Configuration

### 1. Get Evernote Developer Token

Visit [Evernote Developer Token page](https://evernote.com/api/DeveloperToken.action) to obtain your authentication token.

### 2. Configure Environment Variables

Create a `.env` file or set environment variables:

```bash
export EVERNOTE_AUTH_TOKEN="your_token_here"
export EVERNOTE_BACKEND="evernote"  # or "china" for Yinxiang
```

### 3. Configure Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

For local development:

```json
{
  "mcpServers": {
    "evernote": {
      "command": "python",
      "args": ["-m", "evernote_mcp"],
      "cwd": "/path/to/evernote-mcp",
      "env": {
        "EVERNOTE_AUTH_TOKEN": "your_token_here"
      }
    }
  }
}
```

## Usage Examples

### With Claude Code

[Claude Code](https://claude.ai/code) is a CLI tool that provides an interactive terminal experience for coding tasks with Claude. You can use the Evernote MCP server with Claude Code to manage your Evernote notes while working on projects.

#### Installation

1. Install Claude Code:
```bash
npm install -g @anthropic/claude-code
```

2. Configure the MCP server by editing `~/.config/claude-code/config.json`:
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

#### Example Workflows

```bash
# Start Claude Code
claude-code

# Example conversations in Claude Code:
```

```
User: Create a note in my "Project Notes" notebook summarizing the current TODO items from src/todo.py

Claude: I'll read the TODO file and create a note for you.

[Reads src/todo.py, extracts TODOs]

[Uses create_note tool with extracted content]

Claude: I've created a note "TODO Summary" in your "Project Notes" notebook with 5 TODO items.
```

```
User: Search my Evernote for notes about "API design" and summarize the key points

Claude: Let me search for those notes and analyze them.

[Uses search_notes tool with "API design"]
[Gets note content for each result]
[Analyzes and summarizes]

Claude: Found 4 notes about API design. Key themes:
1. RESTful principles - emphasized in 3 notes
2. GraphQL considerations - mentioned in "API Architecture"
3. Rate limiting strategies - covered in "API Security"
```

```
User: Create a notebook called "Code Reviews" and add a note template for code review notes

Claude: I'll set that up for you.

[Uses create_notebook tool]
[Uses create_note tool with template content]

Claude: Created notebook "Code Reviews" with a template note containing:
- Review checklist
- Approval criteria
- Common issues to watch for
```

#### Common Use Cases with Claude Code

- **Documentation Sync**: Create Evernote notes from code comments or docstrings
- **Meeting Notes**: Create structured notes from project discussions
- **Task Tracking**: Sync TODO items between code and Evernote
- **Research Organization**: Save research findings and code snippets to Evernote
- **Code Review Documentation**: Document review outcomes in Evernote

### In Claude Desktop

```
User: Create a notebook called "Meeting Notes" in stack "Work"

Claude: I'll create that notebook for you.

[Uses create_notebook tool]

Claude: I've created the notebook "Meeting Notes" in the "Work" stack.

---

User: Find all notes about "project alpha"

Claude: Let me search for those notes.

[Uses search_notes tool]

Claude: I found 3 notes matching "project alpha":
1. "Project Alpha Kickoff" (updated 2024-01-15)
2. "Alpha Requirements" (updated 2024-01-20)
3. "Alpha Status Update" (updated 2024-01-25)

---

User: Create a note in "Meeting Notes" with title "Team Standup"

Claude: I'll create that note for you.

[Uses create_note tool]

Claude: I've created the note "Team Standup" in your "Meeting Notes" notebook.
```

## Available Tools

### Notebook Operations
- `create_notebook(name, stack)` - Create a new notebook
- `update_notebook(guid, name, stack)` - Update notebook properties
- `delete_notebook(guid)` - Delete a notebook
- `list_notebooks()` - List all notebooks
- `get_notebook(guid)` - Get notebook details

### Note Operations
- `create_note(title, content, notebook_guid, tags, format)` - Create a note
- `get_note(guid, output_format)` - Get note content (enml/text/markdown/json)
- `update_note(guid, title, content, format)` - Update a note
- `delete_note(guid)` - Move note to trash
- `expunge_note(guid)` - Permanently delete note
- `copy_note(guid, target_notebook_guid)` - Copy note to notebook
- `move_note(guid, target_notebook_guid)` - Move note to notebook
- `list_notes(notebook_guid, limit)` - List notes

### Search Operations
- `search_notes(query, notebook_guid, limit)` - Search notes
- `list_tags()` - List all tags

## Resources

- `file://notebooks` - List all notebooks
- `file://notebook/{guid}` - Access notebook metadata
- `file://note/{guid}` - Access note content (JSON)
- `file://note-text/{guid}` - Access note content as plain text
- `file://note-markdown/{guid}` - Access note content as Markdown

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EVERNOTE_AUTH_TOKEN` | Yes | - | Evernote developer token |
| `EVERNOTE_BACKEND` | No | `evernote` | API backend: `evernote`, `china`, `china:sandbox` |
| `EVERNOTE_RETRY_COUNT` | No | `5` | Network retry count |
| `EVERNOTE_USE_SYSTEM_SSL_CA` | No | `false` | Use system SSL CA certificates |

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run ruff check

# Format code
poetry run ruff format
```

## Dependencies

This project depends on `evernote-backup` for the Evernote API client:

```bash
pip install evernote-backup
```

## License

MIT License - see LICENSE file for details.
