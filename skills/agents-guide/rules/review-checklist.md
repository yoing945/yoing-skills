# 生成后自检清单

`review-agent` 在合并后的完整 `AGENTS.md` 草案上执行以下检查。不重复 `tree-agent`/`docs-agent` 生成逻辑已保证的技术约束（如只含目录、排除 `.gitignore`、深度符合参数、文档导航排序等）。

## 跨章节一致性（核心）

- 若 `## 目录结构` 中某子目录被展开到内部，且 `## 文档导航` 中该子目录存在 guide 条目，则判定为过度展开。
- 反过来，若文档导航中某子目录有 guide，`## 目录结构` 中也应只显示该子目录本身，不显示其内部。
- **语义边界补充**：对于具有独立语义边界（如一个 skill、一个服务、一个模块）的子目录，即使未包含 guide 文档，也不应过度展开其内部实现细节（如 `examples/`、`src/`、`tests/`）。仅当这些内部目录对当前层级地图有明确说明价值时才保留。

## 语义质量

- 目录职责注释是否简洁、准确，不无谓重复路径字面名称。

## Override 规则生效

- 若 `agents.guide.override.md` 中声明了排除、强制展开、强制折叠等规则，检查生成结果是否遵守。

## 禁止内容

- 无类设计、流程步骤、详细架构表格、源码级详细逻辑。

## 输出格式

`review-agent` 必须输出 JSON：

```json
{
  "passed": false,
  "issues": [
    {
      "section": "## 目录结构",
      "rule": "子目录含 guide 文档时不再展开其内部",
      "problem": "skills/agents-guide/ 已包含 guide 文档，但仍展开到 examples/、src/",
      "suggestion": "将 skills/agents-guide/ 折叠为叶子节点，仅保留一层"
    }
  ]
}
```

- `passed`：`true` 表示全部检查通过；`false` 表示存在问题。
- `issues`：问题列表，每个问题包含触发规则的章节、规则名、问题描述、修复建议。
