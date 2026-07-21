from pathlib import Path
from typing import List
import pathspec


def _read_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def collect_gitignore_rules(start_dir: Path, project_root: Path) -> tuple[pathspec.PathSpec, list[str]]:
    """收集 project_root 到 start_dir 路径上的所有 .gitignore 规则。

    返回 (PathSpec, raw_patterns)。
    """
    patterns: list[str] = []
    start_dir = start_dir.resolve()
    project_root = project_root.resolve()

    # project_root 的 .gitignore
    patterns.extend(_read_lines(project_root / ".gitignore"))

    # start_dir 相对于 project_root 的各级祖先（不含 project_root 本身）
    if start_dir != project_root:
        rel_parts = start_dir.relative_to(project_root).parts
        current = project_root
        for part in rel_parts:
            current = current / part
            prefix = current.relative_to(project_root).as_posix() + "/"
            for line in _read_lines(current / ".gitignore"):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                # 对嵌套 .gitignore 中的模式加前缀，保留 ! 否定前缀
                if stripped.startswith("!"):
                    patterns.append("!" + prefix + stripped[1:])
                else:
                    patterns.append(prefix + stripped)

    return pathspec.PathSpec.from_lines("gitignore", patterns), patterns


def is_ignored(rel_path: str, spec: pathspec.PathSpec) -> bool:
    """判断相对于 project_root 的路径是否被忽略。"""
    if not spec.patterns:
        return False
    if spec.match_file(rel_path):
        return True
    # 目录模式通常以 / 结尾，对目录路径也尝试带斜杠匹配
    return spec.match_file(rel_path + "/")


def merge_exclude_patterns(spec: pathspec.PathSpec, raw_patterns: list[str], extra_patterns: list[str]) -> tuple[pathspec.PathSpec, list[str]]:
    """将额外的排除模式合并到现有 PathSpec 中。"""
    if not extra_patterns:
        return spec, raw_patterns
    combined = raw_patterns + extra_patterns
    return pathspec.PathSpec.from_lines("gitignore", combined), combined
