# agents-guide

为指定目录生成渐进式项目地图文档。

## 用法

```text
agents-guide [path] [options]
```

- 不带 `path`：在项目边界根目录生成/更新 `AGENTS.md`。
- 带 `path`：在指定目录生成/更新模块指南，并向上回写父级文档导航。

## 选项

```text
agents-guide --help                          # 显示帮助信息
agents-guide --dry-run [path]                # 预览生成结果，不写入文件
agents-guide --depth N [path]                # 通用深度参数（同时影响 tree 与 docs）
agents-guide --tree-depth N [path]           # 单独覆盖 tree 深度，默认 3
agents-guide --docs-depth N [path]           # 单独覆盖 docs 深度，默认 3
agents-guide --init-config [path]            # 复制 examples/.agents-guide.example.yaml 到目标目录，并重命名为 .agents-guide.yaml
agents-guide --init-config --dry-run [path]   # 预览配置模板，不创建文件
```

## 示例

```text
agents-guide              # 生成 AGENTS.md
agents-guide prompts      # 生成 prompts/AGENTS.md
agents-guide --dry-run src/payment  # 预览 src/payment/AGENTS.md
agents-guide --depth 2 src/payment  # 同时指定 tree 与 docs 的扫描深度
```

