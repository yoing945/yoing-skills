# yoing-skills

个人 AI skills 仓库。

## 目录结构

```
yoing-skills/
├── skills/                  # 核心技能
│   ├── brainstorming/       # 手动触发，将想法转化为确认设计并生成设计文档
│   ├── confmirror/          # ConfMirror 配置备份/还原工具 skill
│   ├── init-agents/         # 生成项目根目录级 AI 助手指南（AGENTS.md）
│   ├── init-module-agents/  # 生成模块级 AI 助手指南（AGENTS_<模块名>.md）
│   ├── module-context/      # 深入了解项目中某个具体模块的上下文、源码和依赖
│   ├── project-context/     # 快速获取项目架构、规范、技术栈和工作方式
│   └── ssh-context/         # 读取 ~/.ssh/config，建立远程主机连接上下文
├── prompts/                 # AI 行为与编码提示词