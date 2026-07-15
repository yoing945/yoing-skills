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

可选参数：

```text
agents-guide --help                          # 显示帮助信息
agents-guide --dry-run [path]                # 预览生成结果，不写入文件
agents-guide --depth N [path]                # 控制 ## 目录结构 的索引深度，默认 3
agents-guide --init-override [path]          # 创建 agents.guide.override.md 模板
agents-guide --init-override --dry-run [path] # 预览 override 模板，不创建文件
```

示例：

```text
agents-guide              # 生成 AGENTS.md
agents-guide prompts      # 生成 prompts/AGENTS.md
agents-guide --dry-run src/payment  # 预览 src/payment/AGENTS.md
```

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

示例：

```text
project-a/                  # 包含 .git
├── AGENTS.md
└── submodules/
    └── project-b/          # 包含 .git
        ├── AGENTS.md
        └── src/
            └── auth/
```

- 在 `project-b` 内部运行 `agents-guide`：根为 `project-b/`，不会把 `project-a/AGENTS.md` 当作父级。
- 在 `project-b/src/auth` 运行 `agents-guide src/auth`：先向上找 `.git`，根为 `project-b/`。

## 指南文件命名

- 根指南：默认 `AGENTS.md`，位于项目边界根目录。
- 模块指南：默认 `AGENTS.md`，位于对应子目录。
- 用户可以自定义文件名，只要保留 frontmatter 标记即可。

## 生成流程

`agents-guide` 的实际生成工作由**主 subagent** 在干净上下文中独立完成。当前会话只负责解析命令、启动主 subagent、展示结果；所有文件扫描、override 解析、内容生成、父级导航更新和文件写入均由主 subagent 完成。

1. 确定目标目录。
2. 确定项目边界（Git 仓库根或目标目录自身）。
3. 检查目标目录下是否已存在 guide 文档：
   - 若存在，读取并准备更新。
   - 若不存在，按默认规则创建新文件 `AGENTS.md`。
4. 检查目标目录下是否存在 `agents.guide.override.md`：
   - 若存在，读取其内容。
   - 将文件开头到第一个 `##` 标题之前的内容作为**全局规则区**。
   - 将每个 `## 标题` 及其正文作为一个**章节生成指令**。
5. 使用统一模板生成内容，并应用 override 规则：
   - 解析全局规则区，识别 `include`/`exclude` 等覆盖规则，应用到默认生成过程。
   - 子目录按规则生成 `## 目录结构`，结合全局规则区的 `exclude`。
   - 当前目录下的 guide 和 leaf 文档按排序规则纳入 `## 文档导航`，结合全局规则区的 `include`/`exclude`。
   - 对每个章节生成指令，按 `## 标题` 定位到 `AGENTS.md`：同名章节替换内容，不存在则按 override 文件中的出现顺序追加到末尾。
6. 若目标目录不是项目根，向上查找父级 guide 文档并更新其文档导航。
7. 写入文件。

## 执行架构

`agents-guide` 通过 subagent 执行生成任务，以隔离当前对话上下文的干扰。

### 当前会话职责

- 解析用户输入的命令和参数。
- 启动主 subagent，传递必要参数：
  - 目标路径
  - 选项（`--dry-run`、`--depth` 等）
- 接收主 subagent 返回的执行摘要或 dry-run 内容。
- 向用户展示结果，不直接修改任何文件。

### 主 subagent 职责

主 subagent 拥有干净的上下文，不参考当前会话的历史对话。它负责：

1. 确定目标目录和项目边界。
2. 扫描目录结构、读取 `.gitignore`。
3. 读取 `agents.guide.override.md`，解析全局规则区和章节生成指令。
4. 识别当前目录下的 guide 和 leaf 文档。
5. 生成 `AGENTS.md` 内容。
6. 若目标目录不是项目根，更新父级 guide 文档的导航。
7. `--dry-run` 模式下返回生成内容；正常执行模式下直接写入 `AGENTS.md`。
8. 返回执行摘要给当前会话。

### 子 subagent 职责（可选）

当前 `agents-guide` 一次只处理一个目标目录，单目录内的扫描、override 解析、内容生成、父级导航更新都是紧密耦合的串行步骤，因此**通常不需要派生子 subagent**。

子 subagent 仅在以下扩展场景下使用：

- 未来支持一次性为多个目录批量生成 `AGENTS.md`。
- 未来支持递归为所有子目录生成 guide 文档。

每个子 subagent 负责一个独立的目标目录，返回生成结果给主 subagent，由主 subagent 汇总。

### 上下文隔离原则

- 主 subagent 接收的 prompt 中明确说明：只基于提供的输入和项目文件执行，不参考任何外部对话上下文。
- 子 subagent 接收的 prompt 中同样明确说明上下文隔离要求。
- 当前会话在主 subagent 返回结果前，不向主 subagent 注入新的上下文或中途修改指令。

## 父级查找算法

生成 `src/auth/AGENTS.md` 时：

1. 取目标目录的父目录 `src/`。
2. 在 `src/` 下扫描所有 `.md` 文件。
3. 找到带 `agents-guide: true` 的文件，即父级 guide 文档。
4. 若找到多个，报错。
5. 若未找到，继续向上一级扫描，直到项目边界。
6. 在项目边界处仍未找到，说明没有父级 guide，停止。

## 目录结构生成规则

生成 `## 目录结构` 时遵循以下规则：

1. **只显示目录，不显示文件**。
2. **默认显示 3 层**：显示当前目录及其下最多 2 层子目录。可通过 `--depth` 参数调整。
3. **排除 gitignore 目录**：读取 `.gitignore`，被忽略的目录（如 `node_modules/`、`.venv/`）不显示。
4. **职责注释**：每个目录后加 `# 一句话职责说明`。
5. **条件生成**：若当前目录下没有需要显示的子目录，则不生成该章节。

## 文档导航

`## 文档导航` 表格列出当前目录下的 guide 和 leaf 文档：

| 名称 | 类型 | 说明 |
|---|---|---|
| [AI-Prompts](prompts/AGENTS.md) | guide | 定义 AI 行为与编码提示词 |
| [Skills](skills/AGENTS.md) | guide | 存放核心 skill |
| [CHAT](CHAT.md) | leaf | 说明通用 AI 交互准则 |

### 排序规则

1. **类型优先**：guide 文档排在 leaf 文档前面。
2. **同类型内按名称字母序**：guide 之间、leaf 之间分别按 `name` 或文件名排序。

### 纳入规则

- 当前目录下真实存在的 `.md` 文件。
- 排除当前正在生成的 guide 文档本身。
- 排除 `agents.guide.override.md`。
- 结合 `agents.guide.override.md` 全局规则区中的 `include`/`exclude`。

## 本地覆盖规则（`agents.guide.override.md`）

每个目录可以包含一个 `agents.guide.override.md` 文件，用于覆盖默认生成规则或按规则生成附加章节。该文件**不纳入文档导航**。

### 文件格式

```markdown
# 覆盖规则

排除目录 temp/。
强制将 README.md 纳入文档导航。

## 关键约定

根据 prompts/CODING.md 和 prompts/CHAT.md，总结本项目 AI 交互与编码的核心约定。

## 注意事项

列出 skill 目录下每个子目录的命名规范，以及新增 skill 时应遵循的步骤。
```

规则说明：

- 文件开头到第一个 `##` 标题之前的内容为**全局规则区**。
- 全局规则区可以包含一个 `#` 一级标题作为文件标题（如 `# 覆盖规则`），该标题仅用于说明，不参与章节定位。
- 每个 `## 标题` 及其正文为一个**章节生成指令**。
- 只识别 `##` 二级标题，不识别 `###` 等子标题。
- 如果全局规则区为空且没有 `##` 标题，视为空 override，不修改 `AGENTS.md`。

完整示例参见 [`examples/override.example.md`](examples/override.example.md)。

### 覆盖规则

| 来源 | 处理方式 |
|---|---|
| 全局规则区 | 自然语言描述的 `include`/`exclude` 等规则，优先级高于默认规则 |
| `## 标题` 章节生成指令 | 标题作为章节定位键，标题下的自然语言作为生成提示词，动态生成章节内容并替换或追加到 `AGENTS.md` |

`agents.guide.override.md` 不是 guide 文档，不计入“一个目录最多一份指引文档”的限制。

### 全局规则区

全局规则区使用自然语言表达覆盖规则，例如：

- "排除目录 temp/"
- "强制包含 README.md"
- "忽略 .agents/ 目录"

`agents-guide` 通过自然语言理解这些规则，并应用到默认生成过程中。规则优先级高于默认规则，即 **override > 默认**。

### 章节生成指令

每个 `## 标题` 及其正文是一个章节生成指令。标题下的自然语言不是最终文本，而是生成提示词。

`agents-guide` 在每次生成时：

1. 读取 `## 标题` 作为章节名称。
2. 将标题下的正文作为提示词，结合项目上下文生成章节内容。
3. 将生成的内容按标题定位到 `AGENTS.md`：
   - 若 `AGENTS.md` 已存在同名章节，替换其内容。
   - 若不存在，按 override 文件中的出现顺序追加到末尾。

标题比较时忽略大小写和首尾空格，但保留生成后的原始标题文本。

### 文件引用与上下文读取

override 中的自然语言可能引用项目文件，例如“根据 prompts/CODING.md 总结编码规范”。`agents-guide` 会扫描自然语言中符合文件路径或文件名的字符串，读取其内容作为生成上下文。若引用的文件不存在，则跳过该引用，在生成内容中说明未找到；不存在的引用不中断生成流程。

### 合并优先级

`agents.guide.override.md` 的规则优先级高于 agents-guide 默认规则。即：**override > 默认**。

## 内容模板

所有 guide 文档共用同一套模板。以下章节均按条件生成：

| 章节 | 生成条件 |
|---|---|
| `## 目录结构` | 当前目录下有子目录（排除 gitignore 目录） |
| `## 文档导航` | 当前目录下存在 guide 或 leaf 文档 |
| `## 关键约定` | 用户通过 `agents.guide.override.md` 的章节生成指令提供了生成提示，或手动编辑提供了内容 |

```markdown
---
agents-guide: true
name: <英文标识符>
description: <一句话中文描述>
---

# <标题>

<正文概述内容>

## 目录结构

~~~text
yoing-skills/
├── prompts/        # 定义 AI 行为与编码提示词
├── skills/         # 存放核心 skill
└── docs/           # 项目文档
~~~

## 文档导航

| 名称 | 类型 | 说明 |
|---|---|---|
| [AI-Prompts](prompts/AGENTS.md) | guide | 定义 AI 行为与编码提示词 |
| [Skills](skills/AGENTS.md) | guide | 存放核心 skill |
| [CHAT](CHAT.md) | leaf | 说明通用 AI 交互准则 |
| [CODING](CODING.md) | leaf | 说明编码场景行为准则 |

## 关键约定

- 命名规范。
- 使用方式。
```

### 根目录示例

位于根目录的 `AGENTS.md`，其 `# 标题` 下是项目整体概述，`## 目录结构` 展示顶层目录树，`## 文档导航` 列出顶层 guide 和根目录下的 leaf 文档（如有）。

### 子目录示例

位于 `prompts/AGENTS.md`，其 `# 标题` 下是 prompts 模块概述。`prompts/` 没有子目录但有 leaf 文档，因此只生成 `## 文档导航`，不生成 `## 目录结构`。

## 链接规则

| 关系 | 方向 | 维护方式 |
|---|---|---|
| guide → 子 guide / leaf | 单向 | guide 的“文档导航”链接到其下的子 guide 和 leaf 文档 |

子 guide 不需要显式声明父级。skill 生成子指南时，会自动向上扫描并更新父指南的“文档导航”。

## 检查清单

展示结果前，必须按以下清单自检。发现问题直接修复，无需重新向用户展示中间过程。

- [ ] **frontmatter 检查**：必须包含 `agents-guide: true`；`name`、`description` 按规则填写
- [ ] **章节检查**：只生成必要的章节，不强求三节；无用户明确要求时不写入技术栈、架构、编码规范、测试、依赖、注意事项等章节
- [ ] **目录结构检查**：只含目录，不含文件；排除 `.gitignore` 中忽略的目录和隐藏目录；深度符合 `--depth` 参数
- [ ] **文档导航检查**：包含当前目录下所有 guide 和 leaf（排除 override 文件和当前 guide 本身）；guide 在前、leaf 在后；同类型内按名称字母序
- [ ] **真实性检查**：文档导航中引用的文件真实存在
- [ ] **父级回写检查**（非根目录）：父级 guide 的文档导航中已正确添加当前目录条目，未重复添加
- [ ] **禁止内容检查**：无类设计、流程步骤、详细架构表格、源码级详细逻辑
- [ ] **override 检查**：若存在 `agents.guide.override.md`，全局规则区已正确解析并应用，`## 标题` 对应的章节已按标题定位或替换，无重复标题，引用的文件已尽量读取
- [ ] **subagent 执行检查**：生成工作由主 subagent 在干净上下文中独立完成，当前会话未中途注入额外上下文或修改指令
