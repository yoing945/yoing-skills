import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from agents_guide.gitignore import collect_gitignore_rules, is_ignored


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


def _scan_md_files(directory: Path, project_root: Path, spec: Any) -> List[Path]:
    """扫描 directory 下非隐藏、非 gitignore 的 .md 文件。"""
    files: List[Path] = []
    if not directory.exists():
        return files
    for entry in sorted(directory.iterdir()):
        if not entry.is_file() or entry.suffix != ".md":
            continue
        if entry.name.startswith("."):
            continue
        rel_to_project = entry.relative_to(project_root).as_posix()
        if is_ignored(rel_to_project, spec):
            continue
        files.append(entry)
    return files


def scan_docs(
    target_dir: Path,
    project_root: Path,
    exclude: Optional[str] = None,
) -> Dict[str, Any]:
    """发现 target_dir 下的 guide 与 leaf 文档。"""
    target_dir = target_dir.resolve()
    project_root = project_root.resolve()
    spec, _ = collect_gitignore_rules(target_dir, project_root)
    exclude_path = Path(exclude) if exclude else None

    guides: List[Dict[str, Any]] = []
    leafs: List[Dict[str, Any]] = []

    # 当前目录
    current_files = _scan_md_files(target_dir, project_root, spec)
    guide_files = [f for f in current_files if f.name != "agents.guide.override.md" and _is_guide(f)]
    if len(guide_files) > 1:
        raise ValueError(
            f"目录 {target_dir} 下发现多份 guide 文档："
            f"{[f.name for f in guide_files]}"
        )

    for f in current_files:
        rel = f.relative_to(target_dir).as_posix()
        if f.name == "agents.guide.override.md":
            continue
        if exclude_path and f.name == exclude_path.name:
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

    # 直接子目录
    for subdir in sorted(target_dir.iterdir()):
        if not subdir.is_dir() or subdir.name.startswith("."):
            continue
        rel_to_project = subdir.relative_to(project_root).as_posix()
        if is_ignored(rel_to_project, spec):
            continue
        sub_files = _scan_md_files(subdir, project_root, spec)
        sub_guides = [f for f in sub_files if f.name != "agents.guide.override.md" and _is_guide(f)]
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
