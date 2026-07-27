# sync-skill

同步 skills 与 prompts 到目标工程目录。

## 用法

```text
sync-skill                      # 执行同步
sync-skill --dry-run            # 预览同步
sync-skill commit-push [options]  # 提交并推送目标工程
sync-skill --help / -h          # 显示本帮助
```

## sync

`sync-skill` 默认执行同步，将配置文件中指定的 skills 和 prompts 复制到目标工程，并校验一致性。

```text
sync-skill
sync-skill --dry-run
```

## commit-push

对目标工程执行 `git add/commit/pull --rebase/push`。默认以同步为前提：

- 未提供 `--message`：LLM 先执行同步，再检查目标工程变更并自动生成提交信息。
- 已提供 `--message`：跳过 LLM 总结步骤，直接使用指定提交信息。

| 选项 | 说明 |
|---|---|
| `--message TEXT`, `-m TEXT` | 提交信息。未提供时由 LLM 在同步后根据变更生成 |
| `--tag [TAG]` | 无值时自动递增目标仓库 patch tag；有值时使用指定 tag |
| `--dry-run` | 预览将要执行的 git 操作，不真正修改仓库 |

## 典型工作流

```text
# 方式一：一条命令，LLM 自动同步并生成提交信息
sync-skill commit-push

# 方式二：手动分步
sync-skill
sync-skill commit-push --message "sync agents-guide"
sync-skill commit-push --message "sync agents-guide" --tag
sync-skill commit-push --message "sync agents-guide" --tag v1.2.3
```
