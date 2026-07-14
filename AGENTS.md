# yoing-skills

个人 AI skills 仓库。

## 文档索引

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目目标、目录结构、使用方式 |
| [prompts/CHAT.md](prompts/CHAT.md) | 适用于所有 AI 交互场景的通用准则 |
| [prompts/CODING.md](prompts/CODING.md) | 编码场景的行为准则与禁止事项 |
| [.agents/AGENTS_LOCAL.md](.agents/AGENTS_LOCAL.md) | .agents/ 目录的职责、结构与注意事项 |

## 项目结构

```
yoing-skills/
├── .agents/    # 项目级 AI 助手数据
├── skills/     # 核心 skill
│   ├── agents-guide/    # 生成项目与模块级 AI 助手指南
│   ├── brainstorming/   # 将想法转化为确认设计并生成设计文档
│   ├── confmirror/      # ConfMirror 配置备份/还原工具
│   ├── module-context/  # 深入了解具体模块的上下文、源码和依赖
│   ├── project-context/ # 快速获取项目架构、规范、记忆和约束
│   └── ssh-context/     # 读取 ~/.ssh/config 建立远程主机上下文
└── prompts/    # AI 行为与编码提示词
```
