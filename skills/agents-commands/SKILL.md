---
name: agents-commands
description: 读取当前目录下的技能配置文件，按规则选择并执行预定义的 LLM 命令集合。
---

# 命令集合执行器

根据当前目录下 `.agents.config.yaml` / `.agents.config.local.yaml` 中的 `agents-commands` 域，列出可用命令并按规则执行其中一条命令的 `command` 内容。

## 触发场景

- 用户调用 `agents-commands` 或 `agents-commands <命令名>`。
- 用户希望把常用的 LLM 提示词整理成可复用命令。
- 用户需要快速执行项目预定义的某个操作指令。

## 命令接口

```text
agents-commands [命令名] [options]
```

- **无 `命令名`**：按 default 规则处理，或列出命令让用户选择。
- **`命令名`**：直接执行匹配的命令。
- **`-h`, `--help`**：基于本 SKILL.md 输出用法摘要。
- **`--init [path]`**：在目标目录 `.agents.config.yaml` 中生成 `agents-commands` 域模板；默认当前目录。
- **`--init-local [path]`**：在目标目录 `.agents.config.local.yaml` 中生成 `agents-commands` 域模板；默认当前目录。

`--init` / `--init-local` 遵循 `agents-config` 技能的初始化约定：只负责 `agents-commands` 域；文件已存在时不覆盖，已含该域则提示已配置，缺少则输出待追加的 YAML 片段。

init 最小模板：

```yaml
agents-commands:
  - name: example
    description: 示例命令
    default: false
    command: |
      请在这里写入交给 LLM 执行的提示词。
```

目标目录固定为当前工作目录，不在命令参数中暴露目录路径。

## 配置（`agents-commands` 域）

配置文件与目录级作用域遵循 `agents-config` 技能约定：只读当前工作目录的 `.agents.config.yaml` / `.agents.config.local.yaml`，不向上查找。本技能的覆盖语义：local 中 `agents-commands` 域存在时**整域替换**共享层，不做合并。

`agents-commands` 域的值直接是命令列表：

```yaml
agents-commands:
  - name: review
    description: 审查当前代码
    default: false
    command: |
      请审查当前目录下的代码，关注潜在 bug、命名规范和可维护性。

  - name: test
    description: 生成测试计划
    default: true
    command: |
      请为当前项目生成一份测试计划，列出应覆盖的核心场景。
```

### 字段说明

| 字段 | 必填 | 说明 |
|---|---|---|
| `name` | 是 | 命令别名，调用时使用。同一域内应保持唯一。 |
| `command` | 是 | 要交给 LLM 执行的提示词/指令。 |
| `description` | 否 | 列表展示时说明命令用途。 |
| `default` | 否 | 布尔值，默认 `false`。是否为推荐默认命令。 |

## 执行流程

1. 确定目标目录为当前工作目录。
2. 按 `agents-config` 约定读取 `agents-commands` 域（local 整域替换）。
3. 若两个文件都不存在或都无 `agents-commands` 域，提示用户未找到配置，并建议运行 `--init` / `--init-local`。
4. 校验 `agents-commands` 域必须是命令列表；缺失或解析失败时报错。
5. 若用户提供了命令名：
   - 匹配到则执行该命令的 `command` 内容。
   - 未匹配到则列出所有可用命令并让用户重新选择。
6. 若用户未提供命令名：
   - 统计 `default: true` 的命令数量。
   - 若恰好 1 个，直接执行该命令。
   - 若 0 个或多个，进入列表选择模式。
7. 执行命令时，将对应 `command` 字段的内容作为 LLM 的下一条任务指令继续处理。

## 默认命令逻辑

- `default: true` 表示该命令是推荐默认执行项。
- 未指定命令名且仅有一个 `default: true` 时，自动执行，无需二次确认。
- 存在多个 `default: true` 或无 `default: true` 时，均进入列表选择模式，避免歧义和误操作。

## 列表选择交互

当需要用户选择时，在 Kimi 当前会话中以编号列表呈现：

```text
可用命令：
1. review - 审查当前代码
2. test - 生成测试计划（默认）

请回复要执行的命令编号或名称。
```

LLM 解析用户回复后执行对应命令。

## 错误处理

| 场景 | 行为 |
|---|---|
| 配置不存在（无文件或无 `agents-commands` 域） | 提示未找到配置，建议使用 `--init` / `--init-local` 生成模板。 |
| YAML 解析失败 | 报错并指出失败的文件路径。 |
| `agents-commands` 域不是列表或为空 | 报错并提示配置格式要求。 |
| 命令名未匹配 | 列出可用命令，等待用户重新选择。 |
| 多个 `default: true` | 列出命令让用户选择，不自动执行。 |

## 验证标准

- [ ] 已按约定正确读取 `agents-commands` 域（local 整域替换）。
- [ ] 未指定命令名且仅有一个 `default: true` 时自动执行。
- [ ] 多个/无 `default: true` 时列出命令让用户选择。
- [ ] 指定命令名时正确匹配并执行。
- [ ] `--init` / `--init-local` 生成模板且不覆盖已有配置。
- [ ] `-h`/`--help` 输出用法摘要。
