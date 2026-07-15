#!/usr/bin/env python3
"""Copy a skill from project skills/ to .agents/skills/tests/ for isolated testing."""

import shutil
import sys
from pathlib import Path

import pathspec


def find_project_root(start: Path) -> Path:
    """向上查找项目根目录，以同时存在 skills/ 和 .agents/ 为判断依据。"""
    current = start.resolve()
    while current != current.parent:
        if (current / "skills").is_dir() and (current / ".agents").is_dir():
            return current
        current = current.parent
    raise RuntimeError("找不到项目根目录（未同时发现 skills/ 和 .agents/ 目录）")


def load_gitignore(project_root: Path) -> pathspec.PathSpec:
    """加载项目根目录的 .gitignore，返回 pathspec.PathSpec。"""
    gitignore_path = project_root / ".gitignore"
    patterns = []
    if gitignore_path.is_file():
        patterns = [
            line for line in gitignore_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


def make_ignore_func(spec: pathspec.PathSpec, project_root: Path):
    """根据 .gitignore 生成 shutil.copytree 可用的 ignore 函数。"""
    def ignore_func(src: str, names: list[str]) -> set[str]:
        ignored = set()
        for name in names:
            full_path = Path(src) / name
            rel_path = full_path.relative_to(project_root).as_posix()
            if spec.match_file(rel_path):
                ignored.add(name)
            elif full_path.is_dir() and spec.match_file(rel_path + "/"):
                ignored.add(name)
        return ignored
    return ignore_func


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/main.py <skill-name>")
        sys.exit(1)

    skill_name = sys.argv[1]
    project_root = find_project_root(Path(__file__).resolve().parent)
    source = project_root / "skills" / skill_name
    target = project_root / ".agents" / "skills" / "tests" / skill_name

    if not source.exists():
        print(f"FAILED: 源 skill 不存在: {source}")
        sys.exit(1)

    if not (source / "SKILL.md").is_file():
        print(f"FAILED: 源目录缺少 SKILL.md: {source}")
        sys.exit(1)

    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        shutil.rmtree(target)

    spec = load_gitignore(project_root)
    shutil.copytree(source, target, ignore=make_ignore_func(spec, project_root))

    if (target / "SKILL.md").is_file():
        print(f"OK - {skill_name} 已复制到 {target}")
    else:
        print("FAILED: 复制结果验证失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
