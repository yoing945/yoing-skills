import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from agents_guide.gitignore import collect_gitignore_rules, is_ignored, merge_exclude_patterns


# ==================== 默认规则集 ====================

# 只扫描指定后缀的文件
DOC_SUFFIX = ".md"

# 默认排除的文件名（不纳入文档导航）
DEFAULT_EXCLUDE_NAMES = {
    "agents.guide.override.md",
}

# 默认额外扫描的目录（非递归），这些目录下的 .md 文件也作为 leaf 纳入
DEFAULT_INCLUDE_DOC_DIRS = {
    "docs",
}

# ==================== 实现 ====================


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(content: str) -> Dict[str, str]:
    """轻量级 frontmatter 解析，仅支持简单 key: value 行。"""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}
    result: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def _is_guide(path: Path) -> bool:
    if not path.exists():
        return False
    fm = parse_frontmatter(path.read_text(encoding="utf-8"))
    return fm.get("agents-guide") == "true"


def _scan_md_files(
    directory: Path,
    project_root: Path,
    spec: Any,
    include_names: Optional[set[str]] = None,
) -> List[Path]:
    """扫描 directory 下非隐藏、非 gitignore 的 .md 文件。

    include_names: 若文件名在此集合中，即使以 . 开头也保留。
    """
    files: List[Path] = []
    if not directory.exists():
        return files
    include_names = include_names or set()
    for entry in sorted(directory.iterdir()):
        if not entry.is_file() or entry.suffix != DOC_SUFFIX:
            continue
        if entry.name.startswith(".") and entry.name not in include_names:
            continue
        rel_to_project = entry.relative_to(project_root).as_posix()
        if is_ignored(rel_to_project, spec):
            continue
        files.append(entry)
    return files


def scan_docs(
    target_dir: Path,
    project_root: Path,
    exclude: Optional[List[str]] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """发现 target_dir 下的 guide 与 leaf 文档。"""
    target_dir = target_dir.resolve()
    project_root = project_root.resolve()
    spec, raw_patterns = collect_gitignore_rules(target_dir, project_root)

    exclude_names: set[str] = set()
    if exclude:
        # 简单文件名直接加入排除集合，路径模式加入 gitignore spec
        simple_names = [p for p in exclude if "/" not in p and "\\" not in p]
        path_patterns = [p for p in exclude if "/" in p or "\\" in p]
        exclude_names.update(simple_names)
        if path_patterns:
            spec, raw_patterns = merge_exclude_patterns(spec, raw_patterns, path_patterns)

    include_names: set[str] = set()
    include_dirs: set[str] = set()
    if include:
        for p in include:
            if "/" in p or "\\" in p:
                include_dirs.add(p.rstrip("/"))
            else:
                include_names.add(p)

    # include 可覆盖默认排除的文件名
    default_exclude = DEFAULT_EXCLUDE_NAMES - include_names

    guides: List[Dict[str, Any]] = []
    leafs: List[Dict[str, Any]] = []

    # 当前目录
    current_files = _scan_md_files(target_dir, project_root, spec, include_names)
    guide_files = [f for f in current_files if f.name not in default_exclude and _is_guide(f)]
    if len(guide_files) > 1:
        raise ValueError(
            f"目录 {target_dir} 下发现多份 guide 文档："
            f"{[f.name for f in guide_files]}"
        )

    for f in current_files:
        rel = f.relative_to(target_dir).as_posix()
        if f.name in default_exclude:
            continue
        if f.name in exclude_names:
            continue
        if f in guide_files:
            fm = parse_frontmatter(f.read_text(encoding="utf-8"))
            name = fm.get("name") or (target_dir.name if f.parent == target_dir else f.stem)
            guides.append({
                "name": name,
                "rel_path": rel,
                "source": "current",
                "frontmatter": fm,
            })
        else:
            leafs.append({"name": f.stem, "rel_path": rel})

    # 默认额外扫描的目录（如 docs/），exclude 可覆盖
    for doc_dir_name in DEFAULT_INCLUDE_DOC_DIRS:
        if doc_dir_name in exclude_names:
            continue
        doc_dir = target_dir / doc_dir_name
        if not doc_dir.exists() or not doc_dir.is_dir():
            continue
        rel_to_project = doc_dir.relative_to(project_root).as_posix()
        if is_ignored(rel_to_project, spec):
            continue
        for f in _scan_md_files(doc_dir, project_root, spec, include_names):
            if f.name in default_exclude:
                continue
            if f.name in exclude_names:
                continue
            leafs.append({"name": f.stem, "rel_path": f.relative_to(target_dir).as_posix()})

    # 直接子目录
    for subdir in sorted(target_dir.iterdir()):
        if not subdir.is_dir():
            continue
        # include 的目录即使隐藏也保留
        if subdir.name.startswith(".") and subdir.name not in include_dirs:
            continue
        rel_to_project = subdir.relative_to(project_root).as_posix()
        if is_ignored(rel_to_project, spec):
            continue
        sub_files = _scan_md_files(subdir, project_root, spec, include_names)
        sub_guides = [f for f in sub_files if f.name not in default_exclude and _is_guide(f)]
        if len(sub_guides) > 1:
            raise ValueError(
                f"目录 {subdir} 下发现多份 guide 文档："
                f"{[f.name for f in sub_guides]}"
            )
        for f in sub_guides:
            fm = parse_frontmatter(f.read_text(encoding="utf-8"))
            guides.append({
                "name": fm.get("name") or subdir.name,
                "rel_path": f.relative_to(target_dir).as_posix(),
                "source": "subdirectory",
                "frontmatter": fm,
            })

    # 排序
    guides.sort(key=lambda g: (0 if g["source"] == "current" else 1, g["name"]))
    leafs.sort(key=lambda l: l["name"])

    return {
        "project_root": str(project_root),
        "target_dir": str(target_dir),
        "guides": guides,
        "leafs": leafs,
        "override_exists": (target_dir / "agents.guide.override.md").exists(),
    }
