# 执行架构

`agents-guide` 通过 subagent 执行生成任务，以隔离当前对话上下文的干扰。

## 当前会话职责

- 解析用户输入的命令和参数。
- 确保 Python 扫描脚本可用：
  - 尝试运行 `agents-guide` 验证命令/Python 环境是否可用（不带参数时输出 argparse 默认帮助即表示可用）。
  - 若命令不可用（命令不存在或无法执行），在当前 skill 被加载的目录执行以下命令完成安装：
    ```bash
    python -m venv .venv
    .venv/Scripts/python -m pip install -e .   # Windows
    # .venv/bin/python -m pip install -e .     # Linux/macOS
    ```
- 当用户请求帮助时，直接读取 skill 目录下的 `help.md`。
- 启动主 subagent，传递必要参数：
  - 目标路径
  - 选项（`--dry-run`、`--depth` 等）
- 接收主 subagent 返回的执行摘要或 dry-run 内容。
- 向用户展示结果，不直接修改任何文件。

## 主 subagent 职责

主 subagent 按以下固定流程执行生成任务：

1. 确定目标目录和项目边界。
2. 调用内置 Python 扫描脚本获取目录结构和 guide/leaf 文档信息。
3. 读取 `agents.guide.override.md`，解析全局规则区和章节生成指令。
4. **并行派生** `tree-agent` 和 `docs-agent` 生成对应章节；必须等待两者都成功返回后才能进入合并步骤。
5. 合并两章结果，确保 Markdown 层级、frontmatter、链接格式一致。
6. 派生 `review-agent` 对合并后的 `AGENTS.md` 草案进行生成后自检；**在 `review-agent` 返回 `passed: true` 之前，禁止写入文件**。
7. 若目标目录不是项目根，更新父级 guide 文档的导航。
8. `--dry-run` 模式下返回生成内容；正常执行模式下，**仅当 review 通过后**才写入 `AGENTS.md`。
9. 返回执行摘要给当前会话。

## 强制约束与阶段门控

### 并行执行约束

- `tree-agent` 与 `docs-agent` 必须同时启动、独立执行。
- 主 subagent **必须等待两者都成功返回**，才能进入合并阶段。
- 若任一子 agent 失败或超时，主 subagent **立即终止流程**，不执行合并，向当前会话返回错误摘要。

### 合并门控

- 合并前，主 subagent 必须验证：
  - `tree-agent` 输出只包含 `## 目录结构` 章节。
  - `docs-agent` 输出只包含 `## 文档导航` 章节。
  - 两个输出的标题层级与目标 `AGENTS.md` 一致。
- 若输出格式异常，主 subagent 可尝试一次修复；修复失败则终止流程。

### Review 门控（HARD-GATE）

- **`review-agent` 未返回 `passed: true` 之前，主 subagent 禁止写入 `AGENTS.md`**。
- `--dry-run` 模式下，即使 review 未通过，也可以返回草案和问题列表供用户查看，但不得声称生成成功。

### 失败分支决策树

`review-agent` 返回 `passed: false` 时，主 subagent 按以下规则处理：

1. **可自动修复**：问题属于规则明确、修改范围确定的情况（如按规则裁剪目录树、删除多余空行）。
   - 主 subagent 执行修复。
   - 修复后重新派生 `review-agent` 审查。
   - 若连续自动修复 **3 次**后仍未通过，终止流程并返回当前问题列表。
2. **无法自动修复**：问题涉及语义判断、override 规则冲突、或需要用户决策。
   - 主 subagent **不得擅自写入**。
   - 向当前会话返回问题列表，由用户决定下一步。
3. **混合情况**：部分问题可自动修复，部分不可。
   - 先自动修复可修复部分。
   - 重新审查；若仍剩余不可修复问题，返回给用户。

### 写入前最终检查

在正常执行模式下写入 `AGENTS.md` 之前，主 subagent 必须确认：

- [ ] `tree-agent` 和 `docs-agent` 都已成功返回。
- [ ] 合并后的文档包含正确的 frontmatter。
- [ ] `review-agent` 返回 `passed: true`。
- [ ] 父级 guide 导航更新（如适用）。

## 子 subagent 职责与输入/输出契约

### tree-agent

**职责：** 生成 `## 目录结构` Markdown 内容。

**必须接收的上下文：**
- `agents-guide tree --target <dir> --depth <N>` 的完整 JSON 输出。
- `--depth` 参数值。
- `agents.guide.override.md` 全局规则区中的 `exclude` 规则（如存在）。
- `rules/tree-generation.md` 全文。

**禁止接收的上下文：**
- `docs-agent` 的输出。
- 完整的 `AGENTS.md` 草案。

**输出要求：**
- 仅该章节的 Markdown 字符串。
- 不包含 frontmatter、不包含 `#` 标题、不包含其他章节。

### docs-agent

**职责：** 生成 `## 文档导航` Markdown 内容，应用排序规则。

**必须接收的上下文：**
- `agents-guide docs --target <dir>` 的完整 JSON 输出。
- `agents.guide.override.md` 全局规则区中的 `include`/`exclude` 规则（如存在）。
- `rules/docs-navigation.md` 全文。

**禁止接收的上下文：**
- `tree-agent` 的输出。
- 完整的 `AGENTS.md` 草案。

**输出要求：**
- 仅该章节的 Markdown 字符串。
- 不包含 frontmatter、不包含 `#` 标题、不包含其他章节。

### review-agent

**职责：** 按检查清单审查合并后的 `AGENTS.md` 草案，输出 JSON 格式审查结果。

**必须接收的上下文：**
- 合并后的完整 `AGENTS.md` 草案。
- `agents-guide tree` 和 `agents-guide docs` 的原始 JSON。
- `rules/review-checklist.md` 全文。
- `agents.guide.override.md` 中的自定义规则（如存在）。

**禁止接收的上下文：**
- 子 agent 生成过程中的中间草稿。

**输出要求：**
- 必须返回 JSON，包含 `passed` 布尔字段和 `issues` 数组。
- 每个 issue 必须包含 `section`、`rule`、`problem`、`suggestion` 字段。
- 示例：
  ```json
  {
    "passed": false,
    "issues": [
      {
        "section": "## 目录结构",
        "rule": "子目录含 guide 文档时不再展开其内部",
        "problem": "skills/agents-guide/ 已包含 guide 文档，但仍展开到 examples/、src/",
        "suggestion": "将 skills/agents-guide/ 折叠为叶子节点，仅保留一层"
      }
    ]
  }
  ```

## 父级查找算法

生成 `src/auth/AGENTS.md` 时：

1. 取目标目录的父目录 `src/`。
2. 在 `src/` 下扫描所有 `.md` 文件。
3. 找到带 `agents-guide: true` 的文件，即父级 guide 文档。
4. 若找到多个，报错。
5. 若未找到，继续向上一级扫描，直到项目边界。
6. 在项目边界处仍未找到，说明没有父级 guide，停止。
