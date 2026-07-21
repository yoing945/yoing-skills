# 本地覆盖规则（`agents.guide.override.md`）

每个目录可以包含一个 `agents.guide.override.md` 文件，用于覆盖默认生成规则。该文件**不纳入文档导航**。

## 文件格式

文件由两个可选章节组成，分别对应 `tree` 和 `docs` 两次扫描：

```markdown
## 目录结构

include:
  - .agents/
  - src/core/

exclude:
  - temp/

## 文档导航

include:
  - CHANGELOG.md
  - assets/spec.xlsx

exclude:
  - DRAFT.md
```

规则说明：

- 两个章节均可省略；文件为空或没有任何章节时，视为空 override，不修改生成结果。
- 每个章节下使用 YAML 风格的 `include:` / `exclude:` 列表，两者均可省略。
- 路径相对于目标目录；目录建议以 `/` 结尾（实际存在的目录不加也能识别），文件直接写文件名或相对路径。
- `## 目录结构` 的规则传给 `agents-guide tree --include/--exclude`。
- `## 文档导航` 的规则传给 `agents-guide docs --include/--exclude`；include 显式列出的文件可以是任意格式（如 `.xlsx`），脚本验证文件存在后纳入 leaf。

## 覆盖规则

override 规则的优先级高于默认规则，即 **override > 默认**。

`agents.guide.override.md` 不是 guide 文档，不计入“一个目录最多一份指引文档”的限制。

## LLM 解析格式约束

当前会话读取 `agents.guide.override.md` 后，必须将其解析为结构化 JSON，格式如下：

```json
{
  "tree": {"include": [".agents/"], "exclude": ["temp/"]},
  "docs": {"include": ["CHANGELOG.md"], "exclude": ["DRAFT.md"]}
}
```

- `tree`：对应 `## 目录结构` 章节，传给 `agents-guide tree --include/--exclude`。
- `docs`：对应 `## 文档导航` 章节，传给 `agents-guide docs --include/--exclude`。
- 目录以 `/` 结尾（如 `temp/`、`.agents/`），文件直接写文件名或相对路径（如 `README.md`、`assets/spec.xlsx`）。
- 章节不存在或列表为空时，对应数组为 `[]`；文件为空或无法解析时，`tree` 和 `docs` 均为空 include/exclude。

**规则优先级**：`include` > 默认排除规则 > `exclude` > `.gitignore`。

LLM 解析结果必须是合法 JSON，不得包含额外解释文字。
