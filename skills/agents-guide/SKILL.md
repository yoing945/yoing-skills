---
name: agents-guide
description: 为指定目录生成渐进式项目地图文档。不带路径时生成项目根 AGENTS.md；带路径时生成该目录下的模块指南，并自动更新父级文档导航。
---

# 渐进式项目地图生成

为任意目标目录生成导航文档。

## 命令接口

```text
agents-guide [path] [options]
```

- 不带 `path`：在项目边界根目录生成/更新 `AGENTS.md`
- 带 `path`：在指定目录生成/更新模块指南，并向上回写父级文档导航

完整命令帮助、选项和示例参见 [`help.md`](help.md)。

## 文档类型

| 类型 | 识别规则 | 说明 |
|---|---|---|
| `guide` | 带 `agents-guide: true` frontmatter 的 `.md` 文件 | 属于项目地图体系的指引文档 |
| `leaf` | 未带 `agents-guide: true` 的普通 `.md` 文件 | 被 guide 文档索引的内容文档 |

guide 文档的位置决定其内容范围：

- 位于项目边界根目录 → 项目整体地图
- 位于任意子目录 → 该目录的局部地图

### frontmatter 标记

所有 guide 文档头部必须包含 `agents-guide: true`，`name` 和 `description` 为可选字段：

```markdown
---
agents-guide: true
name: <英文标识符>
description: <一句话中文描述>
---
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `agents-guide` | 是 | 标记是否为指引文档 |
| `name` | 否 | 英文标识符，用于文档导航的链接文本；为空时默认使用目录名 |
| `description` | 否 | 一句话中文描述，用于文档导航的说明列 |

### 唯一性约束

同一目录下最多只能存在一份 guide 文档。若扫描到多份带 `agents-guide: true` 的 `.md` 文件，应报错或提示用户选择。

## 项目边界判定

从目标路径出发向上查找，遇到包含 `.git` 目录的目录即为项目边界。若一直未遇到 `.git` 目录，则以目标目录自身作为项目边界。

## 生成流程

`agents-guide` 的实际生成工作由**主 subagent** 在干净上下文中独立完成。当前会话只负责解析命令、启动主 subagent、展示结果；所有文件扫描、override 解析、内容生成、父级导航更新和文件写入均由主 subagent 完成。

1. 确定目标目录。
2. 确定项目边界（Git 仓库根或目标目录自身）。
3. 检查目标目录下是否已存在 guide 文档：
   - 若存在，读取并准备更新。
   - 若不存在，按默认规则创建新文件 `AGENTS.md`。
4. 读取 `agents.guide.override.md`（如存在）：
   - 将文件开头到第一个 `##` 标题之前的内容作为**全局规则区**。
   - 将每个 `## 标题` 及其正文作为一个**章节生成指令**。
5. 并行派生子 subagent 生成章节：
   - `tree-agent` 基于 `agents-guide tree` 输出生成 `## 目录结构`。
   - `docs-agent` 基于 `agents-guide docs` 输出生成 `## 文档导航`。
6. 主 subagent 合并两章结果，确保 Markdown 层级、frontmatter、链接格式一致。
7. 派生 `review-agent` 对合并后的 `AGENTS.md` 草案进行生成后自检。
8. 若目标目录不是项目根，向上查找父级 guide 文档并更新其文档导航。
9. 写入文件。

## 执行架构

详见 [`rules/architecture.md`](rules/architecture.md)。

## 目录结构生成规则

详见 [`rules/tree-generation.md`](rules/tree-generation.md)。

## 文档导航生成规则

详见 [`rules/docs-navigation.md`](rules/docs-navigation.md)。

## 本地覆盖规则

详见 [`rules/override.md`](rules/override.md)。

## 生成后自检

详见 [`rules/review-checklist.md`](rules/review-checklist.md)。

## 链接规则

| 关系 | 方向 | 维护方式 |
|---|---|---|
| guide → 子 guide / leaf | 单向 | guide 的“文档导航”链接到其下的子 guide 和 leaf 文档 |

子 guide 不需要显式声明父级。skill 生成子指南时，会自动向上扫描并更新父指南的“文档导航”。

## 检查清单

展示结果前，必须按 `rules/review-checklist.md` 自检。

- [ ] **frontmatter 检查**：必须包含 `agents-guide: true`；`name`、`description` 按规则填写
- [ ] **章节检查**：只生成必要的章节，不强求三节；无用户明确要求时不写入技术栈、架构、编码规范、测试、依赖、注意事项等章节
- [ ] **真实性检查**：文档导航中引用的文件真实存在
- [ ] **父级回写检查**（非根目录）：父级 guide 的文档导航中已正确添加当前目录条目，未重复添加
- [ ] **subagent 执行检查**：生成工作由主 subagent独立完成，当前会话未中途注入额外上下文或修改指令
