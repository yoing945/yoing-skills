from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from agents_guide.gitignore import collect_gitignore_rules, is_ignored, merge_exclude_patterns


# ==================== 默认规则集 ====================

# 只扫描指定后缀的文件
DOC_SUFFIX = ".md"

# 默认额外扫描的目录（非递归），这些目录下的 .md 文件也作为 leaf 纳入
DEFAULT_INCLUDE_DOC_DIRS = {
    "docs",
}

# ==================== 实现 ====================


def _is_agents_md(path: Path) -> bool:
    """判断是否为 agents-guide 生成的 guide 文档。"""
    return path.is_file() and path.name.lower() == "agents.md"


def _load_meta(directory: Path) -> Dict[str, str]:
    """读取目录下的 .agents-guide.yaml，返回 meta 字典（若存在）。"""
    config_file = directory / ".agents-guide.yaml"
    if not config_file.is_file():
        return {}
    try:
        with config_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    meta = data.get("meta") or {}
    if isinstance(meta, dict):
        return {k: str(v) for k, v in meta.items() if v is not None}
    return {}


def _guide_name(directory: Path) -> str:
    """获取 guide 在导航中使用的名称：优先 .agents-guide.yaml 的 meta.name，否则用目录名。"""
    return _load_meta(directory).get("name") or directory.name


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
    include_files: set[str] = set()
    if include:
        for p in include:
            # 优先按文件系统实际类型判断文件/目录；不存在时回退到路径形态推断
            normalized = p.replace("\\", "/")
            stripped = normalized.rstrip("/")
            if normalized.endswith("/") or (target_dir / stripped).is_dir():
                include_dirs.add(stripped)
            elif "/" in normalized:
                include_files.add(normalized)
            else:
                include_names.add(normalized)

    guides: List[Dict[str, Any]] = []
    leafs: List[Dict[str, Any]] = []

    # 当前目录
    current_files = _scan_md_files(target_dir, project_root, spec, include_names)
    current_guide = next((f for f in current_files if _is_agents_md(f)), None)
    current_meta = _load_meta(target_dir)

    for f in current_files:
        rel = f.relative_to(target_dir).as_posix()
        if f.name in exclude_names:
            continue
        if f is current_guide:
            guides.append({
                "name": current_meta.get("name") or target_dir.name,
                "rel_path": rel,
                "source": "current",
                "meta": current_meta,
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
        sub_guide = next((f for f in sub_files if _is_agents_md(f)), None)
        if sub_guide:
            sub_meta = _load_meta(subdir)
            guides.append({
                "name": sub_meta.get("name") or subdir.name,
                "rel_path": sub_guide.relative_to(target_dir).as_posix(),
                "source": "subdirectory",
                "meta": sub_meta,
            })

    # include 显式列出的文件（含非 .md 文件）：验证存在后纳入 leaf
    discovered = {g["rel_path"] for g in guides} | {l["rel_path"] for l in leafs}
    for rel in sorted(include_names | include_files):
        if rel in discovered:
            continue
        f = target_dir / rel
        if not f.is_file():
            continue
        leafs.append({"name": f.stem, "rel_path": rel})

    # 排序
    guides.sort(key=lambda g: (0 if g["source"] == "current" else 1, g["name"]))
    leafs.sort(key=lambda l: l["name"])

    return {
        "project_root": str(project_root),
        "target_dir": str(target_dir),
        "guides": guides,
        "leafs": leafs,
        "config_exists": (target_dir / ".agents-guide.yaml").exists(),
    }
