---
name: agents-guide
description: 为指定目录生成渐进式项目地图文档。不带路径时生成项目根 AGENTS.md；带路径时生成该目录下的模块指南，并自动更新父级文档导航。check-nav 子命令核验并修复文档导航的层级引用关系。
---

# 渐进式项目地图生成

为任意目标目录生成导航文档。

## 命令接口

```text
agents-guide [path] [options]
agents-guide check-nav [path] [--fix]
```

- 不带 `path`：在项目边界根目录生成/更新 `AGENTS.md`
- 带 `path`：在指定目录生成/更新模块指南，并向上回写父级文档导航
- `check-nav`：核验范围内所有 `AGENTS.md` 的文档导航层级引用，默认只报告差异，`--fix` 时修补（详见「索引核验」）

## 选项

| 选项 | 说明 |
|---|---|
| `-h`, `--help` | 基于本 SKILL.md 输出用法摘要 |
| `--dry-run [path]` | 预览生成结果，不写入文件 |
| `--fix` | 仅 `check-nav` 子命令：核验并写入修补（不带时只输出差异报告） |
| `--depth N [path]` | 通用深度参数（同时影响 tree 与 docs） |
| `--tree-depth N [path]` | 单独覆盖 tree 深度，默认 3 |
| `--docs-depth N [path]` | 单独覆盖 docs 深度，默认 3 |
| `--init [path]` | 在目标目录 `.agents.config.yaml` 中生成 `agents-guide` 域模板 |
| `--init-local [path]` | 在目标目录 `.agents.config.local.yaml` 中生成 `agents-guide` 域模板 |

`--init` / `--init-local` 遵循 `agents-config` 技能的初始化约定：只负责 `agents-guide` 域；文件已存在时不覆盖，已含该域则提示已配置，缺少则输出待追加的 YAML 片段。

init 最小模板：

```yaml
agents-guide:
  scan:
    include: []   # 强制纳入扫描的目录/文件
    exclude: []   # 排除的目录/文件
```

### 示例

```text
agents-guide              # 生成 AGENTS.md
agents-guide prompts      # 生成 prompts/AGENTS.md
agents-guide check-nav        # 核验整个项目的文档导航，输出差异报告
agents-guide check-nav src --fix  # 核验 src/ 范围并修补不一致条目
agents-guide --dry-run src/payment  # 预览 src/payment/AGENTS.md
agents-guide --depth 2 src/payment  # 同时指定 tree 与 docs 的扫描深度
```

## 文档类型

| 类型 | 识别规则 | 说明 |
|---|---|---|
| `guide` | 名为 `AGENTS.md` 的文件 | 属于项目地图体系的指引文档 |
| `leaf` | 其他普通 `.md` 文件 | 被 guide 文档索引的内容文档 |

guide 文档的位置决定其内容范围：

- 位于项目边界根目录 → 项目整体地图
- 位于任意子目录 → 该目录的局部地图

### 唯一性约束

同一目录下只能有一份 `AGENTS.md`。若发现多份（文件名大小写不同，如 `AGENTS.md` 与 `agents.md`），应报错或提示用户选择。

## 项目边界判定

从目标路径出发向上查找，遇到包含 `.git` 目录的目录即为项目边界。若一直未遇到 `.git` 目录，则以目标目录自身作为项目边界。

## 执行架构

### 会话职责

- 解析用户输入的命令和参数。
- 调用扫描脚本：`python <skill目录>/run.py tree|docs --target <dir> [options]`。依赖已 vendor 进技能目录（`vendor/`），无需安装环境；执行失败时报错并提示用户检查 Python 环境。
- 当用户请求帮助（`-h` / `--help`）时，基于本 SKILL.md 输出用法摘要。
- 调用 Python 扫描脚本获取目录结构和文档信息。
- 检查目标目录是否已存在 `AGENTS.md`：
  - 若存在，默认执行**增量更新**：保留 `## 目录结构`、`## 文档导航` 之外的自定义章节。
  - 若不存在，按空白模板生成新 guide。
  - **完全覆盖**（删除自定义章节）仅在用户显式声明时执行。
- 生成完整 `AGENTS.md`。
- 更新父级 guide 文档导航（如适用）。
- 写入文件或返回 dry-run 内容。

### 生成流程

1. 确定目标目录和项目边界。
2. Python 扫描脚本按 `agents-config` 约定读取目标目录 `.agents.config.yaml` / `.agents.config.local.yaml` 的 `agents-guide` 域（如存在，local 整域替换），按 `tree` / `docs` 键解析为 `depth` / `include` / `exclude` 配置，并与 CLI 参数合并（详见 [`rules/config.md`](rules/config.md)）。
3. 调用 `python <skill目录>/run.py tree --target <dir> --depth <N> --tree-depth <N> --exclude <目录1> --include <目录2> ...` 获取目录结构 JSON。
4. 调用 `python <skill目录>/run.py docs --target <dir> --depth <N> --docs-depth <N> --exclude <文件1> --include <文件2> ...` 获取 guide/leaf 文档 JSON。
5. 检查目标目录是否已有 `AGENTS.md`：
   - 若有，读取并解析现有 `AGENTS.md`，保留 `## 目录结构`、`## 文档导航` 之外的自定义章节。
   - 若无，使用空白模板。
6. 调用一次 LLM，传入：
   - 目录树 JSON
   - 文档列表 JSON
   - 需要保留的现有内容（如适用）
   - 生成规则（概述、目录结构、文档导航的要求）
7. 返回完整 `AGENTS.md` 内容。
8. 做基础格式检查（必要章节存在）。
9. `--dry-run` 模式下返回生成内容；正常执行模式下写入 `AGENTS.md`。
10. 若目标目录不是项目根，更新父级 guide 文档的导航。

### 父级查找算法

生成 `src/auth/AGENTS.md` 时：

1. 取目标目录的父目录 `src/`。
2. 在 `src/` 下扫描名为 `AGENTS.md` 的文件。
3. 找到即父级 guide 文档。
4. 若未找到，继续向上一级扫描，直到项目边界。
5. 在项目边界处仍未找到，说明没有父级 guide，停止。

回写条目时，子目录 guide 的显示名称读取其子目录 `AGENTS.md` 的标题（H1）；读取失败时使用目录名。说明文字读取该子目录 `AGENTS.md` 正文第一段，若内容较多则自行精简为简短说明。

## 索引核验（check-nav）

`check-nav` 子命令核验范围内所有 `AGENTS.md` 的**文档导航**章节与模块层级是否一致，修复越级、失效、重复等索引问题。典型场景：子目录文档原本被根目录索引，后来中间新增了上层模块的 `AGENTS.md`，旧的越级条目残留，同一文档被多级重复索引。

它是对现有索引的核验与修补：沿导航链接逐层递进核验，只修补不一致的条目，保留现有名称与说明文字，不重新生成内容，不分析文档内容。默认只输出差异报告，`--fix` 时写入修补。核验范围完全由文档引用决定，不做引用之外的探测；从未被引用的文档不在范围内。

详细执行流程与约束见 [`check-nav`](rules/check-nav.md) 规则。

## 规则索引

| 名称 | 路径 |
|---|---|
| 目录结构生成规则 | [`tree-generation`](rules/tree-generation.md) |
| 文档导航生成规则 | [`docs-navigation`](rules/docs-navigation.md) |
| 索引核验规则 | [`check-nav`](rules/check-nav.md) |
| 配置规则 | [`config`](rules/config.md) |

## 检查清单

展示结果前，按以下清单自检：

- [ ] **更新模式检查**：目标目录已有 `AGENTS.md` 时，确认保留自定义章节；完全覆盖需用户明确声明
- [ ] **显示名称检查**：子目录导航条目的名称来自其子 `AGENTS.md` 标题，缺失时使用目录名；说明文字取正文第一段的精简版
- [ ] **章节检查**：只生成必要的章节，不强求三节；无用户明确要求时不写入技术栈、架构、编码规范、测试、依赖、注意事项等章节
- [ ] **真实性检查**：文档导航中引用的文件真实存在
- [ ] **父级回写检查**（非根目录）：父级 guide 的文档导航中已正确添加当前目录条目，未重复添加
- [ ] **check-nav 模式检查**：只核验/修补导航章节的不一致条目，保留现有名称与说明；严格沿文档引用递进，未发起任何不带具体路径的 Glob/Grep 调用；默认不写文件，仅 `--fix` 时写入；不为缺失目录新建 `AGENTS.md`
