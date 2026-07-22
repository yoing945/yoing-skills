# 待办计划

1. agents-guide 技能生成tree的depth参数能够在yaml中指定；docs章节也能设置md文件的遍历目录深度，而非仅仅只在AGENTS文档所在目录
2. 优化agents-guide技能，增加--update-docs {target}命令，自动查找指定文档上层对应的AGENTS文档并更新到文档导航章节，target为空则按规则重新生成该章节；增加--upate-tree {path} ，作用与前者同理
3. brainstorming 技能改为 my-brainstorming ，同时增加并改造superpowers的write-plans和执行计划技能
4. sync-skill技能优化：触发后自动提交并推送到远端，同样关联项目也自动提交并推送到远端，并且提交信息相同