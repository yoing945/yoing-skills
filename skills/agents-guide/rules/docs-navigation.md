# 文档导航生成规则

`## 文档导航` 表格列出当前目录下的 guide 和 leaf 文档：

| 名称 | 类型 | 说明 |
|---|---|---|
| [README](README.md) | leaf | 项目目标、目录结构、使用方式 |

## 排序规则

1. **类型优先**：guide 文档排在 leaf 文档前面。
2. **guide 内部**：当前目录的 guide 排在直接子目录 guide 前面；同作用域内按 `name` 或文件名排序。
3. **leaf 内部**：按文件名排序。

## 纳入规则

- **guide**：当前目录下及直接子目录下真实存在的 guide 文档。
- **leaf**：当前目录下真实存在的普通 `.md` 文件。
- 排除当前正在生成的 guide 文档本身。
- 排除 `agents.guide.override.md`。
- 结合 `agents.guide.override.md` 全局规则区中的 `include`/`exclude`。

## 输入

`docs-agent` 接收以下输入：

- `agents-guide docs --target <dir>` 返回的 JSON：
  ```json
  {
    "project_root": "...",
    "target_dir": "...",
    "guides": [
      {"name": "Skills", "rel_path": "skills/AGENTS.md", "source": "subdirectory", "frontmatter": {...}}
    ],
    "leafs": [
      {"name": "README", "rel_path": "README.md"}
    ],
    "override_exists": false
  }
  ```
- `agents.guide.override.md` 全局规则区中的 `include`/`exclude` 规则。

## 输出格式

只输出该章节内容，例如：

```markdown
## 文档导航

| 名称 | 类型 | 说明 |
|---|---|---|
| [Skills](skills/AGENTS.md) | guide | 存放核心 skill |
| [README](README.md) | leaf | 项目目标、目录结构、使用方式 |
```
