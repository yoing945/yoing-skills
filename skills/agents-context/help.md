# agents-context

获取指定目录的上下文信息。无 target 时获取当前工作目录的上下文，带 target 时获取对应目录的上下文。

## 用法

```text
agents-context [target] [options]
```

- 不带 `target`：获取当前工作目录的上下文。
- 带 `target`：获取指定目录的上下文；target 可以是路径或目录名称。

## 选项

```text
agents-context -h                          # 显示帮助信息
agents-context --help                      # 显示帮助信息
agents-context --init-config               # 在当前目录创建 .agents-context.local.yaml 模板
```

## 示例

```text
agents-context                             # 获取当前目录上下文
agents-context skills/agents-guide         # 按路径获取目录上下文
agents-context agents-guide                # 按名称获取目录上下文
agents-context --init-config               # 初始化依赖上下文配置文件
```

## 依赖上下文配置文件

文件优先级：`.agents-context.local.yaml` > `.agents-context.yaml`。

文件格式为 YAML 键值映射，以目录标识为键：

```yaml
darksun-skills:
  path: "E:\\workspace\\OtherProjects\\darksun-skills"
  description: "公司内部技能仓库"

shared-utils:
  path: "../shared-utils"
  description: "公共工具库"
```

完整示例参见 `examples/.agents-context.yaml.example`。
