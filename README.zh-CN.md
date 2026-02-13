# Evernote MCP 服务器

[English](README.md) | [简体中文](README.zh-CN.md)

Evernote 的模型上下文协议（MCP）服务器——让 Claude Code 能够与您的 Evernote 笔记交互。

> **同时支持 [国际版 Evernote](https://evernote.com) 和 [印象笔记](https://yinxiang.com)**

## 功能特性

- **笔记本操作**（创建、读取、更新、删除、列表、获取默认笔记本）
- **笔记操作**（创建、读取、更新、删除、复制、移动、列表、版本管理）
- **标签管理**（创建、读取、更新、删除、列表、按笔记本查找）
- **保存的搜索**（创建、读取、更新、删除、列表）
- **资源/附件操作**（获取、更新、数据、属性、识别）
- **高级笔记功能**（获取内容、搜索文本、标签名称、笔记版本）
- **同步与工具**（同步状态、笔记计数、查找相关内容）
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

```
用户: 找到所有标有"重要"的笔记并按更新时间排序

Claude: 我会搜索带有该标签的笔记并排序。
[使用 search_notes 和 list_tags]
```

## 环境变量

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `EVERNOTE_AUTH_TOKEN` | - | 您的开发者令牌（必需） |
| `EVERNOTE_BACKEND` | `evernote` | `evernote`（国际版）或 `china`（印象笔记） |

## 可用工具

### 笔记本（6个工具）
- `create_notebook(name, stack)` - 创建新笔记本
- `list_notebooks()` - 列出所有笔记本
- `get_notebook(guid)` - 按 GUID 获取笔记本详情
- `update_notebook(guid, name, stack)` - 更新笔记本名称/笔记本组
- `expunge_notebook(guid)` - 永久删除笔记本
- `get_default_notebook()` - 获取新笔记的默认笔记本

### 笔记（8个工具）
- `create_note(title, content, notebook_guid, tags, format)` - 创建新笔记
- `get_note(guid, output_format)` - 获取笔记（enml/text/markdown/json）
- `update_note(guid, title, content, format)` - 更新笔记标题/内容
- `delete_note(guid)` - 移至回收站
- `expunge_note(guid)` - 永久删除笔记
- `copy_note(guid, target_notebook_guid)` - 复制笔记到另一个笔记本
- `move_note(guid, target_notebook_guid)` - 移动笔记到另一个笔记本
- `list_notes(notebook_guid, limit)` - 列出笔记本中的笔记

### 标签（7个工具）
- `list_tags()` - 列出所有标签
- `get_tag(guid)` - 按 GUID 获取标签详情
- `create_tag(name, parent_guid)` - 创建新标签
- `update_tag(guid, name, parent_guid)` - 更新标签名称/父标签
- `expunge_tag(guid)` - 永久删除标签
- `list_tags_by_notebook(notebook_guid)` - 列出特定笔记本中的标签
- `untag_all(guid)` - 从所有笔记中移除标签

### 保存的搜索（5个工具）
- `list_searches()` - 列出所有保存的搜索
- `get_search(guid)` - 按 GUID 获取保存的搜索
- `create_search(name, query)` - 创建新的保存搜索
- `update_search(guid, name, query)` - 更新保存的搜索
- `expunge_search(guid)` - 删除保存的搜索

### 高级笔记操作（5个工具）
- `get_note_content(guid)` - 仅获取 ENML 内容
- `get_note_search_text(guid, note_only, tokenize_for_indexing)` - 获取提取的纯文本
- `get_note_tag_names(guid)` - 获取笔记的标签名称
- `list_note_versions(note_guid)` - 列出历史版本（仅高级用户）
- `get_note_version(note_guid, update_sequence_num, ...)` - 获取特定版本（仅高级用户）

### 资源/附件（13个工具）
- `get_resource(guid, with_data, with_recognition, ...)` - 按 GUID 获取资源
- `get_resource_data(guid, encode)` - 获取资源二进制数据（base64）
- `get_resource_alternate_data(guid, encode)` - 获取备份数据（如 PDF 预览）
- `get_resource_attributes(guid)` - 获取资源元数据
- `get_resource_by_hash(note_guid, content_hash, ...)` - 按 MD5 哈希查找资源
- `get_resource_recognition(guid, encode)` - 获取 OCR/识别数据
- `get_resource_search_text(guid)` - 从资源获取提取的搜索文本
- `update_resource(guid, mime, attributes)` - 更新资源元数据
- `set_resource_application_data_entry(guid, key, value)` - 设置应用数据
- `unset_resource_application_data_entry(guid, key)` - 删除应用数据
- `get_resource_application_data(guid)` - 获取所有应用数据
- `get_resource_application_data_entry(guid, key)` - 获取特定应用数据条目

### 搜索与工具（4个工具）
- `search_notes(query, notebook_guid, limit)` - 使用 Evernote 查询语法搜索
- `get_sync_state()` - 获取同步状态信息
- `find_note_counts(query, with_trash)` - 获取每个笔记本/标签的笔记计数
- `find_related(note_guid, plain_text, max_notes, ...)` - 查找相关的笔记/标签/笔记本

## 许可证

MIT
