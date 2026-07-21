# 本地覆盖规则（`agents.guide.override.md`）

每个目录可以包含一个 `agents.guide.override.md` 文件，用于覆盖默认生成规则。该文件**不纳入文档导航**。

## 文件格式

```markdown
# 覆盖规则

排除目录 temp/。
强制将 README.md 纳入文档导航。
```

规则说明：

- 文件开头到第一个 `##` 标题之前的内容为**全局规则区**。
- 全局规则区可以包含一个 `#` 一级标题作为文件标题（如 `# 覆盖规则`），该标题仅用于说明，不参与规则解析。
- 只识别全局规则区，不识别 `##` 等章节生成指令。
- 如果全局规则区为空且没有 `##` 标题，视为空 override，不修改 `AGENTS.md`。

## 覆盖规则

全局规则区使用自然语言表达 `include`/`exclude` 等规则，例如：

- "排除目录 temp/"
- "强制包含 README.md"
- "忽略 .agents/ 目录"

`agents-guide` 通过自然语言理解这些规则，并应用到默认生成过程中。规则优先级高于默认规则，即 **override > 默认**。

`agents.guide.override.md` 不是 guide 文档，不计入“一个目录最多一份指引文档”的限制。

## LLM 解析格式约束

当前会话读取 `agents.guide.override.md` 后，必须调用 LLM 将全局规则区解析为结构化 JSON，格式如下：

```json
{
  "exclude": ["temp/", "docs/", "README.md"],
  "include": [".agents/", "CHANGELOG.md"]
}
```

- `exclude`：需要排除的目录或文件列表，用于传给 `agents-guide tree/docs --exclude` 参数。
- `include`：需要强制包含的目录或文件列表，用于覆盖默认排除规则（如隐藏目录 `.agents/`、默认排除的文件名等）。
- 目录以 `/` 结尾（如 `temp/`、`.agents/`），文件直接写文件名（如 `README.md`）。
- 若全局规则区为空或无法解析，返回 `{"exclude": [], "include": []}`。

**规则优先级**：`include` > 默认排除规则 > `exclude` > `.gitignore`。

LLM 解析结果必须是合法 JSON，不得包含额外解释文字。
