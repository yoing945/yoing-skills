# agents-guide

为指定目录生成渐进式项目地图文档。

## 常用命令

```bash
agents-guide                  # 生成项目根 AGENTS.md
agents-guide prompts          # 生成 prompts/AGENTS.md
agents-guide --dry-run src/payment  # 预览生成结果
agents-guide sync             # 递归刷新范围内所有 AGENTS.md 的文档导航
agents-guide --init           # 创建配置模板（.agents.config.yaml 的 agents-guide 域）
```

## 文档

- `SKILL.md` — 完整规范与行为说明（含命令选项与示例）。

## 运行方式

扫描脚本入口为 `run.py`，第三方依赖（PyYAML、pathspec）已 vendor 进 `vendor/` 目录，无需安装环境：

```bash
python run.py tree --target <dir>   # 扫描目录结构
python run.py docs --target <dir>   # 发现 guide/leaf 文档
```

更新 vendor 依赖（重新生成整个 `vendor/` 目录）：

```bash
python -m pip install --target=vendor pyyaml pathspec
```
