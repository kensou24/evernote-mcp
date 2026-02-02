# Evernote MCP 服务器

[English](README.md) | [简体中文](README.zh-CN.md)

Evernote 的模型上下文协议（MCP）服务器——让 Claude Code 能够与您的 Evernote 笔记交互。

> **同时支持 [国际版 Evernote](https://evernote.com) 和 [印象笔记](https://yinxiang.com)**

## 功能特性

- 笔记本操作（创建、更新、删除、列表）
- 笔记操作（创建、读取、更新、删除、复制、移动）
- 使用 Evernote 搜索语法进行全文搜索
- 多种输出格式（ENML、纯文本、Markdown、JSON）

## 安装

```bash
npm install -g @anthropic/claude-code
uvx evernote-mcp
```

## 配置

### 1. 获取 Evernote 开发者令牌

**国际版 Evernote**: https://evernote.com/api/DeveloperToken.action

**印象笔记**: https://app.yinxiang.com/api/DeveloperToken.action

### 2. 配置 Claude Code

编辑 `~/.config/claude-code/config.json`：

**国际版 Evernote:**
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

**印象笔记:**
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

## 使用示例

```bash
claude-code
```

```
用户: 在我的"项目笔记"笔记本中创建一条笔记，总结 src/todo.py 中的当前待办事项

Claude: 我会读取 TODO 文件并为您创建笔记。
[创建包含提取的待办事项的笔记]
```

```
用户: 在我的 Evernote 中搜索关于"API 设计"的笔记并总结要点

Claude: 让我搜索这些笔记并分析它们。
[搜索并总结发现]
```

```
用户: 创建一个名为"代码评审"的笔记本并添加笔记模板

Claude: 我会为您设置。
[创建笔记本和模板笔记]
```

## 环境变量

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `EVERNOTE_AUTH_TOKEN` | - | 您的开发者令牌（必需） |
| `EVERNOTE_BACKEND` | `evernote` | `evernote`（国际版）或 `china`（印象笔记） |

## 可用工具

### 笔记本
- `create_notebook(name, stack)` - 创建笔记本
- `list_notebooks()` - 列出所有笔记本
- `get_notebook(guid)` - 获取笔记本详情
- `update_notebook(guid, name, stack)` - 更新笔记本
- `delete_notebook(guid)` - 删除笔记本

### 笔记
- `create_note(title, content, notebook_guid, tags)` - 创建笔记
- `get_note(guid, output_format)` - 获取笔记（enml/text/markdown/json）
- `update_note(guid, title, content)` - 更新笔记
- `delete_note(guid)` - 移至回收站
- `copy_note(guid, target_notebook_guid)` - 复制笔记
- `move_note(guid, target_notebook_guid)` - 移动笔记
- `list_notes(notebook_guid, limit)` - 列出笔记

### 搜索
- `search_notes(query, notebook_guid)` - 搜索笔记
- `list_tags()` - 列出所有标签

## 许可证

MIT
