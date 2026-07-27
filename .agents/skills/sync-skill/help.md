# sync-skill

同步 skills 与 prompts 到目标工程目录。

## 用法

```text
sync-skill sync                # 执行同步
sync-skill commit-push [options]  # 提交并推送目标工程
sync-skill --help / -h         # 显示本帮助
```

## sync

将配置文件中指定的 skills 和 prompts 复制到目标工程，并校验一致性。

```text
sync-skill sync
sync-skill sync --dry-run
```

## commit-push

对目标工程执行 `git add/commit/pull --rebase/push`。执行前需由 LLM 检查目标工程变更并生成提交信息。

| 选项 | 说明 |
|---|---|
| `--message TEXT`, `-m TEXT` | 提交信息（必填） |
| `--tag [TAG]` | 无值时自动递增目标仓库 patch tag；有值时使用指定 tag |
| `--dry-run` | 预览将要执行的 git 操作，不真正修改仓库 |

## 典型工作流

```text
sync-skill sync
# LLM 检查目标工程变更并生成提交信息
sync-skill commit-push --message "sync agents-guide"
sync-skill commit-push --message "sync agents-guide" --tag
sync-skill commit-push --message "sync agents-guide" --tag v1.2.3
```
