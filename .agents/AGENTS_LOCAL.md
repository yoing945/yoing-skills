# .agents 模块指南

## 模块概述

`.agents/` 存放 AI 助手在本地的运行时数据，包括项目级记忆文件和用户目录 skill 副本。

## 文档索引

| 文档 | 路径 | 职责 |
|------|------|------|
| 父上下文 | [../AGENTS.md](../AGENTS.md) | 项目级 AI 助手指南 |
| 记忆索引 | [memory/MEMORY.md](memory/MEMORY.md) | 项目级记忆文件索引 |

## 模块结构

```
.agents/
├── memory/              # 项目级记忆文件
└── skills/              # 用户目录 skill 副本
    └── sync-skill/      # skill 同步工具
```
