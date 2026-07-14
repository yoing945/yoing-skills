---
name: preview-skill
description: 当需要预览或验证项目 skills/ 目录下的 skill 时，将其复制到 .agents/skills/test/ 目录进行隔离，避免影响已安装的 skill。
---

# Preview Skill

## 概述

将项目根目录 `skills/` 下的指定 skill 复制到 `.agents/skills/test/` 目录，用于在隔离环境中验证 skill 行为。

## 何时使用

- 新 skill 创建后，加载验证前
- 修改现有 skill 后，快速预览效果
- 不想把未验证的 skill 直接放入 `.agents/skills/` 正式目录

## 执行步骤

1. **确认目标 skill** — 用户指定 `skills/` 下的 skill 名称
2. **检查源目录** — 确认 `skills/<skill-name>/SKILL.md` 存在
3. **准备测试目录** — 确保 `.agents/skills/test/` 存在
4. **复制 skill** — 将 `skills/<skill-name>/` 完整复制到 `.agents/skills/test/<skill-name>/`
5. **验证复制结果** — 确认 `.agents/skills/test/<skill-name>/SKILL.md` 存在
6. **告知用户** — skill 已可用于测试加载

## 依赖

见本 skill 目录下的 `pyproject.toml`。

当前依赖：

- Python 3

## 初始化

在 skill 目录下创建虚拟环境，并根据 `pyproject.toml` 安装依赖。以下提供两种常用方式，任选其一：

**使用 uv：**

```bash
cd .agents/skills/preview-skill
uv venv
uv pip install -e .
```

**使用 pip：**

```bash
cd .agents/skills/preview-skill
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## 使用方法

```bash
cd .agents/skills/preview-skill
uv run python scripts/main.py <skill-name>
```

或使用 pip（需先激活虚拟环境）：

```bash
python scripts/main.py <skill-name>
```

## 注意事项

- 完全覆盖 `.agents/skills/test/` 下的同名 skill
- 不修改源 skill 目录
- 测试完成后建议清理 `.agents/skills/test/`
