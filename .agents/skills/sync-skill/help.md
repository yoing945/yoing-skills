# sync-skill

同步 skills 与 prompts 到目标工程目录。

## 用法

```text
sync-skill                  # 默认执行同步
sync-skill --help / -h      # 显示本帮助
sync-skill commit-push [options]
```

## commit-push 选项

| 选项 | 说明 |
|---|---|
| `--message TEXT`, `-m TEXT` | 覆盖自动生成的提交信息 |
| `--tag [TAG]` | 无值时自动递增目标仓库 patch tag；有值时使用指定 tag |
| `--dry-run` | 预览将要执行的 git 操作，不真正修改仓库 |
| `--yes`, `--non-interactive` | 跳过交互确认 |

## 示例

```text
sync-skill
sync-skill commit-push
sync-skill commit-push --message "sync agents-guide"
sync-skill commit-push --tag
sync-skill commit-push --tag v1.2.3
```
