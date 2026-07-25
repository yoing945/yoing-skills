from pathlib import Path
from typing import Any, Dict, List, Optional
from agents_guide.gitignore import collect_gitignore_rules, is_ignored, merge_exclude_patterns


# ==================== 默认规则集 ====================

# 默认排除的目录名（不显示在目录结构中）
DEFAULT_EXCLUDE_DIR_NAMES = {
    # 可根据需要添加，如 ".git", "node_modules" 等
}

# ==================== 实现 ====================


def scan_tree(
    target_dir: Path,
    depth: int,
    project_root: Path,
    exclude: Optional[List[str]] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """扫描 target_dir 下的目录结构，返回嵌套 JSON。"""
    target_dir = target_dir.resolve()
    project_root = project_root.resolve()
    spec, raw_patterns = collect_gitignore_rules(target_dir, project_root)

    if exclude:
        spec, raw_patterns = merge_exclude_patterns(spec, raw_patterns, exclude)

    include_dirs: set[str] = set()
    if include:
        for p in include:
            if "/" in p or "\\" in p:
                include_dirs.add(p.rstrip("/"))
            else:
                include_dirs.add(p)

    def walk(current: Path, current_depth: int) -> List[Dict[str, Any]]:
        if current_depth > depth:
            return []

        nodes: List[Dict[str, Any]] = []
        for entry in sorted(current.iterdir()):
            if not entry.is_dir():
                continue
            # include 的目录即使隐藏或属于默认排除也保留
            if entry.name in include_dirs:
                pass
            elif entry.name.startswith("."):
                continue
            elif entry.name in DEFAULT_EXCLUDE_DIR_NAMES:
                continue
            rel_to_project = entry.relative_to(project_root).as_posix()
            if is_ignored(rel_to_project, spec):
                continue
            rel_to_target = entry.relative_to(target_dir).as_posix()

            # 模块边界：目录包含 AGENTS.md 时作为叶子节点，不展开子目录
            children: List[Dict[str, Any]] = []
            if current_depth < depth and not (entry / "AGENTS.md").exists():
                children = walk(entry, current_depth + 1)

            nodes.append({
                "name": entry.name,
                "rel_path": rel_to_target,
                "depth": current_depth,
                "comment": "",
                "children": children,
            })
        return nodes

    return {
        "project_root": str(project_root),
        "target_dir": str(target_dir),
        "directory_tree": walk(target_dir, 1),
        "ignored_patterns": raw_patterns,
    }
