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

## 执行架构

### 会话职责

- 解析用户输入的命令和参数。
- 确保 Python 扫描脚本可用：
  - 尝试运行 `agents-guide` 验证命令/Python 环境是否可用（不带参数时输出 argparse 默认帮助即表示可用）。
  - 若命令不可用（命令不存在或无法执行），在当前 skill 被加载的目录执行以下命令完成安装：
    ```bash
    python -m venv .venv
    .venv/Scripts/python -m pip install -e .   # Windows
    # .venv/bin/python -m pip install -e .     # Linux/macOS
    ```
- 当用户请求帮助时，直接读取 skill 目录下的 `help.md`。
- 读取 `agents.guide.override.md`（如存在），解析 `## 目录结构` / `## 文档导航` 章节，分别提取 tree/docs 所需的 include/exclude 列表。
- 调用 Python 扫描脚本获取目录结构和文档信息（传入排除列表）。
- 生成完整 `AGENTS.md`。
- 更新父级 guide 文档导航（如适用）。
- 写入文件或返回 dry-run 内容。

### 生成流程

1. 确定目标目录和项目边界。
2. 读取 `agents.guide.override.md`（如存在），按章节解析为 `tree` / `docs` 两组 `include` / `exclude` 数组（详见 [`rules/override.md`](rules/override.md)）。
3. 调用 `agents-guide tree --target <dir> --depth <N> --exclude <目录1> --include <目录2> ...`（参数来自 `## 目录结构` 章节）获取目录结构 JSON。
4. 调用 `agents-guide docs --target <dir> --exclude <文件1> --include <文件2> ...`（参数来自 `## 文档导航` 章节）获取 guide/leaf 文档 JSON。
5. 调用一次 LLM，传入：
   - 目录树 JSON
   - 文档列表 JSON
   - override 的 include/exclude 规则
   - 生成规则（概述、目录结构、文档导航的要求）
6. 返回完整 `AGENTS.md` 内容。
7. 做基础格式检查（frontmatter 存在、必要章节存在）。
8. `--dry-run` 模式下返回生成内容；正常执行模式下写入 `AGENTS.md`。
9. 若目标目录不是项目根，更新父级 guide 文档的导航。

### 父级查找算法

生成 `src/auth/AGENTS.md` 时：

1. 取目标目录的父目录 `src/`。
2. 在 `src/` 下扫描所有 `.md` 文件。
3. 找到带 `agents-guide: true` 的文件，即父级 guide 文档。
4. 若找到多个，报错。
5. 若未找到，继续向上一级扫描，直到项目边界。
6. 在项目边界处仍未找到，说明没有父级 guide，停止。

## 规则索引

| 名称 | 路径 |
|---|---|
| 目录结构生成规则 | [`tree-generation`](rules/tree-generation.md) |
| 文档导航生成规则 | [`docs-navigation`](rules/docs-navigation.md) |
| 本地覆盖规则 | [`override`](rules/override.md) |

## 检查清单

展示结果前，按以下清单自检：

- [ ] **frontmatter 检查**：必须包含 `agents-guide: true`；`name`、`description` 按规则填写
- [ ] **章节检查**：只生成必要的章节，不强求三节；无用户明确要求时不写入技术栈、架构、编码规范、测试、依赖、注意事项等章节
- [ ] **真实性检查**：文档导航中引用的文件真实存在
- [ ] **父级回写检查**（非根目录）：父级 guide 的文档导航中已正确添加当前目录条目，未重复添加
