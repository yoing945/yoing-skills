---
name: skill_testing
description: 本项目 skill 的测试工作流与目录规范
type: project
---

# Skill 测试工作流

**核心原则**：每个 skill 自己管理自己的虚拟环境与依赖；`tests/` 目录只存放测试脚本；运行测试时使用对应 skill 的虚拟环境。

## 目录结构

**优先规则**：如果被测试的 skill 目录本身已有 `tests/` 目录，或允许在 skill 目录内创建测试，则优先在 skill 目录本身的 `tests/` 中存放测试脚本。否则，放到项目根目录 `tests/<skill-name>/` 下。

```text
# 优先：skill 目录内测试
skills/<skill-name>/tests/
└── test_xxx.py

# 备选：项目根目录测试
tests/
└── <skill-name>/
    ├── __init__.py
    ├── test_xxx.py
    └── ...
```

示例（skill 目录内）：

```text
.agents/skills/sync-skill/
├── scripts/
└── tests/
    ├── conftest.py
    ├── test_sync.py
    └── test_main.py
```

示例（项目根目录）：

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
# 测试放在 skill 目录内时，在 skill 目录下运行
skills/<skill-name>/.venv/Scripts/python -m pytest tests/ -v

# 测试放在项目根目录时，使用该 skill 的 .venv 并指定测试路径
skills/<skill-name>/.venv/Scripts/python -m pytest tests/<skill-name> -v
```

> 不推荐在根目录创建统一虚拟环境运行所有 skill 测试。若确实需要一次性全量运行，可使用 `tox` / `nox` 等工具为每个 skill 创建隔离环境并逐个执行，避免依赖冲突。

## 为新 skill 添加测试

1. 在 skill 目录下创建 skill 专用 `.venv` 并安装依赖与 pytest：
   ```bash
   cd skills/<skill-name>          # 或 .agents/skills/<skill-name>
   python -m venv .venv
   .venv/Scripts/python -m pip install -e .
   .venv/Scripts/python -m pip install pytest
   ```
2. **优先**在 skill 目录内创建 `tests/` 目录，并添加测试文件；若不适合，再在项目根目录 `tests/<skill-name>/` 下创建。
3. 若测试放在项目根目录，需要在根目录 `pytest.ini` 的 `pythonpath` 中追加该 skill 的源码根目录。
4. 运行对应 skill 的 `.venv` 执行测试：
   ```bash
   # skill 目录内测试
   skills/<skill-name>/.venv/Scripts/python -m pytest tests/ -v

   # 项目根目录测试
   skills/<skill-name>/.venv/Scripts/python -m pytest tests/<skill-name> -v
   ```

## 测试位置权衡

- `skills/` 目录下的核心 skill 是同步给目标工程的源目录，测试代码若放在其中会随 skill 一起分发。因此核心 skill 优先使用项目根目录 `tests/<skill-name>/`。
- `.agents/skills/` 下的实验性 skill 以及不对外分发的 skill，测试可以放在 skill 目录本身的 `tests/` 内，便于与 skill 代码一起维护。
- 项目根目录 `.gitignore` 已包含 `**/tests`，因此 skill 目录内的 `tests/` 也不会被 git 跟踪；测试代码作为开发资产保留在项目仓库内，便于多机器协作开发。
