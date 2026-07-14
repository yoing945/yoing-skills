# yoing-skills

个人 AI skills 仓库。管理可直接加载给 AI 执行的工作流 skill 和通用参考规范。

## 文档索引

| 文档 | 路径 | 职责 |
|------|------|------|
| 项目说明 | [README.md](README.md) | 项目目标、目录结构、使用方式 |
| AI 基础行为准则 | [prompts/CHAT.md](prompts/CHAT.md) | 适用于所有 AI 交互场景的通用准则 |
| 编码行为准则 | [prompts/CODING.md](prompts/CODING.md) | 编码场景的行为准则与禁止事项 |

## 项目结构

```
yoing-skills/
├── skills/                  # 核心 skill
│   ├── brainstorming/       # 手动触发，将想法转化为确认设计并生成设计文档
│   ├── confmirror/          # ConfMirror 配置备份/还原工具 skill
│   ├── init-agents/         # 生成项目级 AI 助手指南（根目录 AGENTS.md）
│   ├── init-module-agents/  # 生成模块级 AI 助手指南（AGENTS_<模块名>.md）
│   ├── module-context/      # 深入了解项目中某个模块的文档、源码和依赖
│   ├── project-context/     # 快速获取项目架构、规范、记忆和约束
│   └── ssh-context/         # 读取 ~/.ssh/config 建立远程主机上下文
├── prompts/                 # AI 行为与编码提示词
```

## 编码规范

- **Skill 文件格式**：每个 skill 目录内必须包含 `SKILL.md`，顶部使用 YAML frontmatter（`name`、`description`）
- **命名**：skill 目录名即标识符，使用 kebab-case
- **语言**：文档使用中文，除非用户明确要求其他语言
- **内容边界**：skill 只包含 AI 执行所需的最小信息，不绑定特定平台或工具

