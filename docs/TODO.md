# 待办计划

1. ~~agents-guide 技能生成tree的depth参数能够在yaml中指定；docs章节也能设置md文件的遍历目录深度，而非仅仅只在AGENTS文档所在目录。如果存在用户输入的--depth，则优先使用用户输入，而非配置文件。改造docs的文档遍历规则（之前只在当前目录和docs中遍历），受--depth参数影响，收集所有遍历目录中的.md文档，注意同样受到gitignore规则影响。如果该目录有AGENTS，则停止往下找，说明有guide类型文档。~~ ✅
   - 剩余：增加 `--update-docs {target}` 命令，自动查找指定文档上层对应的 AGENTS 文档并更新到文档导航章节，target 为空则按规则重新生成该章节；增加 `--update-tree {path}`，作用与前者同理。
2. brainstorming 技能改为 my-brainstorming ，同时增加并改造superpowers的write-plans和执行计划技能
3. sync-skill技能优化：触发后自动提交并推送到远端，同样关联项目也自动提交并推送到远端，并且提交信息相同