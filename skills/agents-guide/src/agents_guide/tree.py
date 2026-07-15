from pathlib import Path
from typing import Any, Dict, List
from agents_guide.gitignore import collect_gitignore_rules, is_ignored


def scan_tree(target_dir: Path, depth: int, project_root: Path) -> Dict[str, Any]:
    """扫描 target_dir 下的目录结构，返回嵌套 JSON。"""
    target_dir = target_dir.resolve()
    project_root = project_root.resolve()
    spec, raw_patterns = collect_gitignore_rules(target_dir, project_root)

    def walk(current: Path, current_depth: int) -> List[Dict[str, Any]]:
        if current_depth > depth:
            return []

        nodes: List[Dict[str, Any]] = []
        for entry in sorted(current.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name.startswith("."):
                continue
            rel_to_project = entry.relative_to(project_root).as_posix()
            if is_ignored(rel_to_project, spec):
                continue
            rel_to_target = entry.relative_to(target_dir).as_posix()
            children = walk(entry, current_depth + 1) if current_depth < depth else []
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
