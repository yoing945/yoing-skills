---
agents-guide: true
name: yoing-skills
description: 个人 AI skills 仓库
---

# yoing-skills

个人 AI skills 仓库。

## 目录结构

```text
yoing-skills/
├── .agents/              # AI 技能预览与测试工作区
│   ├── memory/           # 会话记忆
│   └── skills/           # 实验性 skill
├── docs/                 # 项目文档
├── prompts/              # AI 行为与编码提示词
└── skills/               # 核心 skill
    ├── agents-guide/     # 生成项目地图文档的 skill
    ├── brainstorming/    # 将想法转化为确认设计并生成设计文档
    ├── confmirror/       # ConfMirror 配置备份/还原工具 skill
    ├── module-context/   # 深入了解项目中某个具体模块的上下文
    ├── project-context/  # 快速获取项目架构、规范和工作方式
    └── ssh-context/      # 读取 ssh 配置并建立远程主机连接上下文
```

## 文档导航

| 名称 | 类型 | 说明 |
|---|---|---|
| [README](README.md) | leaf | 项目目标、目录结构、使用方式 |
