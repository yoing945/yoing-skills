---
name: agents-context
description: 获取指定目录的上下文信息，为后续开发或修改建立精确上下文。
---

# 上下文获取

根据输入解析目标目录，读取该目录下的指南、文档和源码，并可选加载依赖目录的上下文，最终输出精炼的上下文摘要。

## 触发场景

- 用户首次在当前项目中发起对话
- 用户要求了解某个目录的架构、规范或上下文
- 用户要求了解某个具体目录的实现细节
- 当前任务涉及对特定目录的代码修改
- 用户问"这个项目是什么"、"xxx 是怎么实现的"等

## 命令接口

```text
agents-context [target] [options]
```

- **无 `target`**：获取当前工作目录的上下文。
- **`target` 是已存在的路径**（如 `skills/agents-guide`）：获取该目录的上下文。
- **`target` 是名称**（如 `agents-guide`）：先在当前目录 `AGENTS.md` 的 `## 文档导航` 中查找匹配项；找到则使用该条目指向的目录。未找到则按目录名搜索；仍无结果则报错或询问用户。

## 选项

| 选项 | 说明 |
|---|---|
| `-h`, `--help` | 显示帮助信息 |
| `--init-config [path]` | 在指定目录创建 `.agents-context.local.yaml` 模板；省略 `path` 时使用当前工作目录 |

AI 识别到 `-h` 或 `--help` 时，直接输出 `help.md` 内容并停止后续上下文获取逻辑。

`--init-config` 用于在指定目录生成依赖上下文配置文件模板；省略目录时使用当前工作目录。若目标目录的 `.agents-context.local.yaml` 已存在，提示用户并退出，不覆盖。

## 目标解析

`agents-context` 先把用户输入的 `target` 解析成一个具体目录，再基于该目录获取上下文。

### 解析规则

按以下顺序判断：

1. **无 `target`**：目标目录为当前工作目录。
2. **`target` 是已存在的路径**：目标目录就是该路径。
3. **`target` 是名称**：先在当前目录 `AGENTS.md` 的 `## 文档导航` 中查找名称匹配项；找到则使用该条目对应的目录。未找到则按目录名搜索；仍无结果则报错或询问用户。

### 解析示例

| 用户输入 | 解析结果 |
|---|---|
| `agents-context` | 当前工作目录 |
| `agents-context skills/agents-guide` | `skills/agents-guide` 目录 |
| `agents-context agents-guide` | 先在 `AGENTS.md` 的 `## 文档导航` 中查找 `agents-guide`；若匹配到对应条目，则使用该条目指向的目录 |
| `agents-context xxx` | 文档导航未匹配时，按目录名搜索 `xxx`；仍找不到则报错或询问用户 |

## 执行流程

1. **解析目标目录**：根据"目标解析"规则确定目标目录。
2. **读取目标目录内容**：
   - 按优先级查找并阅读指南文件：`AGENTS.md` → `README.md`。
   - 若存在子目录，概览目录结构。
   - 若存在源码文件，浏览核心源码文件（入口文件、主要逻辑文件、对外接口文件），了解目录的职责边界、关键类/函数和实现逻辑；优先阅读摘要性内容和核心接口，不陷入实现细节。
3. **加载依赖上下文文件**：查找 `.agents-context*.yaml` 文件，优先级：`.agents-context.local.yaml` > `.agents-context.yaml`。
4. **确认依赖加载**：若存在依赖条目，向用户展示列表，询问需要加载哪些（全部 / 部分 / 不加载）。
5. **并行获取依赖上下文**：仅对用户确认的依赖启动子 agent，执行简化版上下文获取（只读指南文件和目录文档）。
6. **整合输出上下文摘要**：根据已读取的目标目录内容以及已加载的依赖上下文，输出精炼的上下文摘要。

## 依赖上下文文件

查找 `.agents-context*.yaml` 文件，优先级：`.agents-context.local.yaml` > `.agents-context.yaml`。

文件采用 YAML 键值映射结构，以目录标识为键：

```yaml
project-alias:
  path: "<绝对或相对路径>"
  description: "<一句话描述>"
```

若文件不存在，跳过此步骤。

完整配置示例参见 [`examples/.agents-context.yaml.example`](examples/.agents-context.yaml.example)。

## 验证标准

- [ ] 已正确解析目标目录
- [ ] 已读取目标目录下的指南、文档和核心源码
- [ ] `-h` / `--help` 能正确输出帮助信息并停止执行
- [ ] `--init-config` 能在当前目录或指定目录生成 `.agents-context.local.yaml` 模板，且不覆盖已存在文件
- [ ] 若存在依赖，已向用户确认并仅加载指定依赖（或已跳过）
- [ ] 向用户提供了对应目标目录的上下文摘要
