---
name: agents-guide
description: 为指定目录生成渐进式项目地图文档。不带路径时生成项目根 AGENTS.md；带路径时生成该目录下的模块指南，并自动更新父级文档导航。sync 子命令递归刷新范围内所有 AGENTS.md 的文档导航，修复索引层级混乱。
---

# 渐进式项目地图生成

为任意目标目录生成导航文档。

## 命令接口

```text
agents-guide [path] [options]
agents-guide sync [path] [--dry-run]
```

- 不带 `path`：在项目边界根目录生成/更新 `AGENTS.md`
- 带 `path`：在指定目录生成/更新模块指南，并向上回写父级文档导航
- `sync`：递归刷新范围内所有 `AGENTS.md` 的文档导航章节，修复索引层级（详见「索引同步」）

## 选项

| 选项 | 说明 |
|---|---|
| `-h`, `--help` | 基于本 SKILL.md 输出用法摘要 |
| `--dry-run [path]` | 预览生成结果，不写入文件 |
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
agents-guide sync         # 递归刷新整个项目的文档导航
agents-guide sync src     # 只刷新 src/ 范围内的文档导航
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

## 索引同步（sync）

`sync` 子命令递归刷新范围内所有 `AGENTS.md` 的**文档导航**章节，修复文档变更导致的索引层级混乱。典型场景：子目录文档原本被根目录索引，后来中间新增了上层模块的 `AGENTS.md`，旧的越级条目残留，同一文档被多级重复索引。

### 执行流程

1. 确定起始目录：无 `path` 时为项目边界根目录。
2. 用 Glob 查找范围内所有 `AGENTS.md`，按目录深度**自底向上**排序（叶子优先，保证父级读取子文档标题时子文档已刷新）。
3. 对每个目录：
   - 调用 `python <skill目录>/run.py docs --target <dir>` 获取最新 guide/leaf 文档列表。
   - 按 [`docs-navigation`](rules/docs-navigation.md) 规则重新生成 `## 文档导航` 章节——只索引到下一个模块边界，越级、失效条目随之消失，新增文档补入。
   - **只替换该章节**，文档其余内容（含目录结构、自定义章节）一律不动。
4. 逐文档输出变更摘要：新增、移除、层级调整的条目。

### 约束

- `sync` 只处理已存在 `AGENTS.md` 的目录，不为缺失的目录生成新文档。
- `sync` 只刷新文档导航，不更新目录结构——目录结构变化频率低；若某目录变化频繁，说明它处于快速迭代期，应等稳定后再纳入 AGENTS 体系，而不是依赖 sync 反复修复。
- `--dry-run` 时只输出各文档的导航变更预览，不写入文件。

## 规则索引

| 名称 | 路径 |
|---|---|
| 目录结构生成规则 | [`tree-generation`](rules/tree-generation.md) |
| 文档导航生成规则 | [`docs-navigation`](rules/docs-navigation.md) |
| 配置规则 | [`config`](rules/config.md) |

## 检查清单

展示结果前，按以下清单自检：

- [ ] **更新模式检查**：目标目录已有 `AGENTS.md` 时，确认保留自定义章节；完全覆盖需用户明确声明
- [ ] **显示名称检查**：子目录导航条目的名称来自其子 `AGENTS.md` 标题，缺失时使用目录名；说明文字取正文第一段的精简版
- [ ] **章节检查**：只生成必要的章节，不强求三节；无用户明确要求时不写入技术栈、架构、编码规范、测试、依赖、注意事项等章节
- [ ] **真实性检查**：文档导航中引用的文件真实存在
- [ ] **父级回写检查**（非根目录）：父级 guide 的文档导航中已正确添加当前目录条目，未重复添加
- [ ] **sync 模式检查**：只重写各文档的 `## 文档导航` 章节；自底向上执行；不为缺失目录新建 `AGENTS.md`
