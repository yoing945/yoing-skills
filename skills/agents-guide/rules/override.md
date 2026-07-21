# 本地覆盖规则（`.agents-guide.yaml`）

每个目录可以包含一个 `.agents-guide.yaml` 文件，用于覆盖 `agents-guide` 生成 `AGENTS.md` 的默认规则。该文件是工具配置，**不纳入文档导航**。

## 文件格式

文件采用 YAML 格式，顶层按扫描阶段分为 `tree`（目录结构）和 `docs`（文档导航）两个可选键：

```yaml
# 目录结构（tree 扫描）
tree:
  include:
    - .agents/
    - src/core/
  exclude:
    - temp/

# 文档导航（docs 扫描）
docs:
  include:
    - CHANGELOG.md
    - assets/spec.xlsx
  exclude:
    - DRAFT.md
```

规则说明：

- `tree` / `docs` 均可省略；文件为空时，视为空配置，不修改生成结果。
- 每个键下使用 `include:` / `exclude:` 列表，两者均可省略。
- 路径相对于目标目录；目录建议以 `/` 结尾（实际存在的目录不加也能识别），文件直接写文件名或相对路径。
- `tree` 的规则传给 `agents-guide tree --include/--exclude`。
- `docs` 的规则传给 `agents-guide docs --include/--exclude`；`docs.include` 显式列出的文件可以是任意格式（如 `.xlsx`），脚本验证文件存在后纳入 leaf。

## 覆盖规则

`.agents-guide.yaml` 的优先级高于默认规则，即 **配置 > 默认**。

`.agents-guide.yaml` 不是 guide 文档，不计入“一个目录最多一份指引文档”的限制。

## 解析约定

`agents-guide` 命令通过 PyYAML 直接读取 `.agents-guide.yaml`，无需 LLM 介入：

- `tree` 对应 `## 目录结构` 生成阶段，其 `include` / `exclude` 传给 `agents-guide tree --include/--exclude`。
- `docs` 对应 `## 文档导航` 生成阶段，其 `include` / `exclude` 传给 `agents-guide docs --include/--exclude`。
- CLI 传入的 `--include` / `--exclude` 与 YAML 中的同类型列表合并；未提供时仅使用 YAML 配置。
- 键不存在或列表为空时，对应数组为 `[]`；文件为空或无法解析时，按空配置处理。

**规则优先级**：`include` > 默认排除规则 > `exclude` > `.gitignore`。

## 未来扩展

`.agents-guide.yaml` 的顶层可继续增加新键而不破坏现有结构，例如：

```yaml
settings:
  max_depth: 4
sections:
  - name: 关键约定
    source: prompts/CODING.md
```

当前实现只识别 `tree` 和 `docs`；新增键在需要时由会话或脚本扩展解释。
