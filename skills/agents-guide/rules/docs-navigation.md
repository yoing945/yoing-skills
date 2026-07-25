# 文档导航生成规则

`## 文档导航` 表格列出当前目录下的 guide 与 leaf 文档。guide 文档固定为 `AGENTS.md`，其他 `.md` 文件为 leaf，因此表格不再单独显示类型列。

| 名称 | 说明 |
|---|---|
| [README](README.md) | 项目目标、目录结构、使用方式 |

## 排序规则

1. **类型优先**：guide 文档排在 leaf 文档前面。
2. **guide 内部**：当前目录的 guide 排在直接子目录 guide 前面；同作用域内按 `meta.name`、目录名或文件名排序。
3. **leaf 内部**：按文件名排序。

## 纳入规则

- **guide**：当前目录下及子目录下真实存在的 `AGENTS.md`，但当前目录自身的 `AGENTS.md` 除外。
- **leaf**：当前目录及子目录下真实存在的普通 `.md` 文件；子模块边界目录内的其他 `.md` 不纳入。
- 排除当前正在生成的 guide 文档本身。
- 排除 `.agents-guide.yaml`。
- 结合 `.agents-guide.yaml` 中 `docs` 章节的 `include`/`exclude`。

## 模块边界

子目录若包含 `AGENTS.md`，视为子模块 guide，收录后不再向该目录内部继续扫描。

## 输入

`docs-agent` 接收以下输入：

- `agents-guide docs --target <dir>` 返回的 JSON：
  ```json
  {
    "project_root": "...",
    "target_dir": "...",
    "current_meta": {"name": "...", "description": "..."},
    "guides": [
      {"name": "Skills", "rel_path": "skills/AGENTS.md", "source": "subdirectory", "meta": {}}
    ],
    "leafs": [
      {"name": "README", "rel_path": "README.md"}
    ],
    "config_exists": false
  }
  ```
- `--depth` / `--docs-depth` 参数值。
- `.agents-guide.yaml` 中 `docs` 章节的 `depth` / `include` / `exclude` 规则。

### 深度覆盖优先级

`--docs-depth` > `--depth` > `docs.depth`（YAML）> 默认值 3。

## 输出格式

只输出该章节内容，例如：

```markdown
## 文档导航

| 名称 | 说明 |
|---|---|
| [Skills](skills/AGENTS.md) | 存放核心 skill |
| [README](README.md) | 项目目标、目录结构、使用方式 |
```
