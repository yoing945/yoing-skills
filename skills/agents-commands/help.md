# agents-commands 帮助

## 用法

```text
agents-commands [命令名]
agents-commands --init-config [path]
agents-commands -h | --help
```

## 说明

读取当前目录下的 `.agents.commands*.yaml`，列出并执行预定义命令。

- `.agents.commands.local.yaml` 优先级高于 `.agents.commands.yaml`。
- 若存在且仅存在一个 `default: true` 的命令，未指定命令名时将自动执行。
- 否则将列出所有可用命令，等待用户选择。

## 示例

```text
agents-commands          # 执行默认命令或列出命令
agents-commands review   # 执行 review 命令
agents-commands --init-config
```
