# 目录结构生成规则

生成 `## 目录结构` 时遵循以下规则：

1. **只显示目录，不显示文件**。
2. **默认显示 3 层**：显示当前目录及其下最多 2 层子目录。可通过 `--depth` 参数调整。
3. **排除 gitignore 目录**：读取 `.gitignore`，被忽略的目录（如 `node_modules/`、`.venv/`）不显示。
4. **排除隐藏目录**：以 `.` 开头的目录不显示。
5. **职责注释**：每个目录后加 `# 一句话职责说明`。
6. **条件生成**：若当前目录下没有需要显示的子目录，则不生成该章节。

## 输入

`tree-agent` 接收以下输入：

- `agents-guide tree --target <dir> --depth <N>` 返回的 JSON：
  ```json
  {
    "project_root": "...",
    "target_dir": "...",
    "directory_tree": [
      {"name": "skills", "rel_path": "skills", "depth": 1, "comment": "", "children": [...]}
    ],
    "ignored_patterns": [".venv/", "node_modules/"]
  }
  ```
- `--depth` 参数值。
- `.agents-guide.yaml` 中 `tree` 章节的 `exclude` 规则。

## 输出格式

只输出该章节内容，例如：

```markdown
## 目录结构

```text
yoing-skills/
├── docs/           # 项目文档
├── prompts/        # AI 行为与编码提示词
└── skills/         # 核心 skill
```
```

## 与 docs-agent 的边界

`tree-agent` 只负责按扫描结果和参数生成目录树，**不判断**是否过度展开。过度展开等跨章节一致性问题由 `review-agent` 处理。
