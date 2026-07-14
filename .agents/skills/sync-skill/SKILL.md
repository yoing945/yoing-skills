---
name: sync-skill
description: 根据配置文件将本项目中指定的 skills、prompts 复制到目标工程目录，完全覆盖目标目录内容，确保目标与源完全一致。
---

# Skill 同步

读取本 skill 目录下的 YAML 配置文件，将指定的 skills 和 prompts 复制到目标工程目录。

## 依赖

见本 skill 目录下的 `pyproject.toml`。

当前依赖：

- Python 3
- PyYAML
- pathspec

## 初始化

在 skill 目录下创建虚拟环境，并根据 `pyproject.toml` 安装依赖。以下提供两种常用方式，任选其一：

**使用 uv：**

```bash
cd "{本skill目录}"
uv venv
uv pip install -e .
```

**使用 pip：**

```bash
cd "{本skill目录}"
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## 配置文件

本 skill 通过 YAML 文件指定同步参数。配置文件位于本 skill 目录下：

- 默认读取：`config.local.yaml`
- 示例参考：`config.example.yaml`

配置格式：

```yaml
config:
  target_path: "目标工程目录的绝对路径"
  skills:
    - skill-name-1
    - skill-name-2
  prompts:
    - PROMPT_NAME_1
    - PROMPT_NAME_2
```

配置项说明：

- `target_path`：目标工程目录的绝对路径
- `skills`：要同步的 skill 名称列表。脚本会按以下顺序查找源目录：
  1. 项目根目录 `skills/<skill-name>/`
  2. 项目根目录 `.agents/skills/<skill-name>/`
  找到后按原始相对路径复制到目标工程（例如 `.agents/skills/` 下的 skill 会同步到目标工程的 `.agents/skills/` 下）
- `prompts`：要同步的 prompt 文件名列表（不带 `.md` 后缀，对应本项目 `prompts/` 下的文件）

## 触发场景

- 需要根据配置将本仓库的 skill 同步到其他项目
- 需要根据配置将本仓库的 prompt 文件同步到其他项目
- 覆盖目标项目中已存在的同名 skill 或 prompt

## 执行前确认

执行前必须向用户确认：

1. 读取到的配置文件路径
2. 目标工程目录 `target_path`
3. 要同步的 skill 列表
4. 要同步的 prompt 列表
5. 覆盖策略（完全覆盖，目标目录中多余的文件将被删除）

## 执行步骤

1. 确认 `config.local.yaml` 配置正确
2. 按「初始化」步骤创建虚拟环境并安装依赖（首次或依赖变更时）
3. 执行脚本：
   - 使用 uv：`uv run python scripts/main.py`
   - 使用 pip（需先激活虚拟环境）：`python scripts/main.py`
4. 脚本会自动完成以下操作：
   - 读取 `config.local.yaml`
   - 按项目根目录 `.gitignore` 排除被忽略的文件
   - 删除并重新复制目标 skill 目录（保持源目录结构）
   - 覆盖目标 prompt 文件
   - 验证目标与源完全一致

## 验证

脚本执行完毕后会输出验证结果：

- `OK - all synced and verified`：同步成功且一致
- `FAILED:` 后列出不一致项：需要排查

## 注意事项

- 本 skill 执行完全覆盖，删除操作前需再次确认
- 同步时排除项目根目录 `.gitignore` 中匹配的文件
- skill 会保持原始目录结构同步（`skills/` 或 `.agents/skills/`）
- 配置文件中的 `prompts` 项不带 `.md` 后缀，执行时自动补全
- 仅同步配置文件中列出的 skill 和 prompt
- 不自动处理依赖关系
