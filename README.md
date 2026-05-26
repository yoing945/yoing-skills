# yoing-skills

个人 AI skills 仓库。

## 目录结构

| 目录 | 用途 |
|------|------|
| `skills/` | 核心技能 |
| `references/` | 通用规范与参考资料 |
| `spec/` | 本仓库的设计规范 |

## 使用方式

所有 skill 均为纯文本 `SKILL.md`，任何支持文件读取的 AI 平台均可手动加载。

| 平台 | 加载方式 |
|------|---------|
| Claude Code | `/load skills/<name>/SKILL.md` 或复制内容到对话 |
| Claude.ai Projects | 上传 skill 文件到项目知识库 |
| ChatGPT / Gemini / Cursor 等 | 复制内容作为 system prompt 或对话上下文 |

## 设计规范

详见 [spec/CONVENTIONS.md](spec/CONVENTIONS.md)。
