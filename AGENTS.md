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
    ├── agents-context/   # 目录上下文统一获取
    ├── agents-guide/     # 生成项目地图文档的 skill
    ├── brainstorming/    # 将想法转化为确认设计并生成设计文档
    ├── confmirror/       # ConfMirror 配置备份/还原工具 skill
    └── ssh-context/      # 读取 ssh 配置并建立远程主机连接上下文
```

## 文档导航

| 名称 | 说明 |
|---|---|
| [项目级agent](.agents/AGENTS.md) | AI 助手运行时数据，包括项目级记忆与实验性 skill |
| [prompts](prompts/AGENTS.md) | AI 行为与编码提示词 |
| [README](README.md) | 项目目标与主要技能 |
