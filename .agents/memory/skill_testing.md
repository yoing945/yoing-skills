---
name: skill_testing
description: 本项目 skill 的测试工作流与目录规范
type: project
---

# Skill 测试工作流

**核心原则**：每个 skill 自己管理自己的虚拟环境与依赖；`tests/` 目录只存放测试脚本；运行测试时使用对应 skill 的虚拟环境。

## 目录结构

测试脚本统一放在项目根目录 `tests/` 下，按 skill 名称分子目录，避免污染 `skills/` 目录（`skills/` 是同步给用户的 skill 源目录）。

```text
tests/
└── <skill-name>/
    ├── __init__.py
    ├── test_xxx.py
    └── ...
```

示例：

```text
tests/
└── agents-guide/
    ├── __init__.py
    ├── test_common.py
    ├── test_tree.py
    ├── test_docs.py
    └── test_main.py
```

## 环境与依赖

每个 skill 的依赖定义在 `skills/<skill-name>/pyproject.toml` 中。**推荐为每个 skill 维护独立的虚拟环境**，避免 skill 之间的依赖版本冲突。

```text
skills/
└── agents-guide/
    ├── .venv/              # skill 专用虚拟环境
    ├── pyproject.toml      # skill 依赖声明
    └── src/
        └── agents_guide/
```

初始化 skill 测试环境：

```bash
cd skills/agents-guide
python -m venv .venv
.venv/Scripts/python -m pip install -e .
.venv/Scripts/python -m pip install pytest
```

## pytest 配置

根目录 `pytest.ini` 配置 `pythonpath`，列出各 skill 的源码根目录，使测试脚本能够导入被测包：

```ini
[pytest]
pythonpath =
    skills/agents-guide/src
    skills/<another-skill>/src
```

每个 skill 的源码应在 `skills/<skill-name>/src/<package_name>/` 下。

## 运行测试

```bash
# 运行单个 skill 的测试（使用该 skill 的 .venv）
skills/agents-guide/.venv/Scripts/python -m pytest tests/agents-guide -v

# 运行单个测试文件
skills/agents-guide/.venv/Scripts/python -m pytest tests/agents-guide/test_tree.py -v
```

> 不推荐在根目录创建统一虚拟环境运行所有 skill 测试。若确实需要一次性全量运行，可使用 `tox` / `nox` 等工具为每个 skill 创建隔离环境并逐个执行，避免依赖冲突。

## 为新 skill 添加测试

1. 在 `skills/<skill-name>/` 下创建 skill 专用 `.venv` 并安装依赖与 pytest：
   ```bash
   cd skills/<skill-name>
   python -m venv .venv
   .venv/Scripts/python -m pip install -e .
   .venv/Scripts/python -m pip install pytest
   ```
2. 在 `tests/<skill-name>/` 下创建 `__init__.py` 和测试文件。
3. 在根目录 `pytest.ini` 的 `pythonpath` 中追加该 skill 的 `src` 目录。
4. 运行 `skills/<skill-name>/.venv/Scripts/python -m pytest tests/<skill-name> -v` 验证。

## 为什么测试不放 skill 包内

- `skills/` 目录是同步给目标工程的 skill 源目录，测试代码不应随 skill 一起分发。
- 项目根目录 `.gitignore` 已包含 `**/tests`，因此根目录 `tests/` 不会被 git 跟踪；但测试代码作为开发资产保留在项目仓库内，便于多机器协作开发。
