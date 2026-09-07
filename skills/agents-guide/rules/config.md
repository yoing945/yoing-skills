# 配置规则（`agents-guide` 域）

每个目录可以在 `.agents.config.yaml` / `.agents.config.local.yaml` 中包含一个 `agents-guide` 域，用于配置 `agents-guide` 生成 `AGENTS.md` 的规则。配置文件遵循 `agents-config` 技能约定：

- **目录级作用域**：只读目标目录的配置文件，不向上查找；文件位置即作用域。
- **覆盖语义（本技能自定义）**：`.agents.config.local.yaml` 中 `agents-guide` 域存在时，整域替换共享层，域内不做合并。

配置文件是工具配置，**不纳入文档导航**。

## 域格式

`agents-guide` 域下分为三个可选键：

- `scan`：`tree` 与 `docs` 的共同基础配置（depth/include/exclude）。
- `tree`：目录结构扫描阶段的 depth/include/exclude。
- `docs`：文档导航扫描阶段的 depth/include/exclude。

```yaml
agents-guide:
  # scan：tree 与 docs 的共同基础配置
  scan:
    depth: 3          # tree 和 docs 的共同默认深度
    include:
      - .agents/     # 两个 stage 都强制包含的目录/文件
    exclude:
      - tests/        # 两个 stage 都排除的目录/文件

  # tree：目录结构（## 目录结构）生成阶段的覆盖规则
  tree:
    depth: 3          # 目录结构展开深度，默认 3
    include:
      - .agents/     # 目录建议以 / 结尾；实际存在的目录不加也能识别
      - src/core/
    exclude:
      - temp/        # 被排除的目录不会出现在目录树中

  # docs：文档导航（## 文档导航）生成阶段的覆盖规则
  docs:
    depth: 3          # 文档扫描深度，默认 3
    include:
      - CHANGELOG.md          # 普通 md 文件
      - assets/spec.xlsx      # 非 md 文件也可显式纳入 leaf
    exclude:
      - DRAFT.md              # 被排除的文件不纳入文档导航
```

规则说明：

- `scan` / `tree` / `docs` 均可省略；`agents-guide` 域为空时，视为空配置，按默认值生成。
- `tree` / `docs` 下使用 `include:` / `exclude:` 列表，两者均可省略。
- 路径相对于目标目录；目录建议以 `/` 结尾（实际存在的目录不加也能识别），文件直接写文件名或相对路径。
- `tree` 的规则传给 `run.py tree --include/--exclude`。
- `docs` 的规则传给 `run.py docs --include/--exclude`；`docs.include` 显式列出的文件可以是任意格式（如 `.xlsx`），脚本验证文件存在后纳入 leaf。

## 覆盖规则

`agents-guide` 域的优先级高于默认规则，即 **配置 > 默认**。

`.agents.config.yaml` 不是 guide 文档，不计入"一个目录最多一份指引文档"的限制。

## 解析约定

`agents-guide` 命令通过 PyYAML 直接读取配置文件的 `agents-guide` 域，无需 LLM 介入：

- `scan` 为可选键。若存在，其 `depth` / `include` / `exclude` 作为 `tree` 和 `docs` 的共同基础。
- `tree.depth` / `docs.depth` 若存在则覆盖 `scan.depth`；否则继承 `scan.depth`。
- `tree.include` / `docs.include` 与 `scan.include` 合并；`tree.exclude` / `docs.exclude` 与 `scan.exclude` 合并。
- `tree` 对应 `## 目录结构` 生成阶段，其最终 `include` / `exclude` 传给 `run.py tree --include/--exclude`。
- `docs` 对应 `## 文档导航` 生成阶段，其最终 `include` / `exclude` 传给 `run.py docs --include/--exclude`。
- CLI 传入的 `--include` / `--exclude` 与 YAML 中的同类型列表合并；未提供时仅使用 YAML 配置。
- 无 `scan` 时，`tree` / `docs` 行为与之前完全一致。
- 键不存在或列表为空时，对应数组为 `[]`；`agents-guide` 域为空或无法解析时，按空配置处理。

**规则优先级**：`include` > 默认排除规则 > `exclude` > `.gitignore`。

## 未来扩展

`agents-guide` 域下可继续增加新键而不破坏现有结构，例如：

```yaml
agents-guide:
  settings:
    max_depth: 4
  sections:
    - name: 关键约定
      source: prompts/CODING.md
```

当前实现只识别 `tree` 和 `docs`；新增键在需要时由会话或脚本扩展解释。
