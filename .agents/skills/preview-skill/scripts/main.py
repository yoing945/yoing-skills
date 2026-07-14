#!/usr/bin/env python3
"""Copy a skill from project skills/ to .agents/skills/test/ for isolated testing."""

import shutil
import sys
from pathlib import Path


def find_project_root(start: Path) -> Path:
    """向上查找项目根目录，以同时存在 skills/ 和 .agents/ 为判断依据。"""
    current = start.resolve()
    while current != current.parent:
        if (current / "skills").is_dir() and (current / ".agents").is_dir():
            return current
        current = current.parent
    raise RuntimeError("找不到项目根目录（未同时发现 skills/ 和 .agents/ 目录）")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/main.py <skill-name>")
        sys.exit(1)

    skill_name = sys.argv[1]
    project_root = find_project_root(Path(__file__).resolve().parent)
    source = project_root / "skills" / skill_name
    target = project_root / ".agents" / "skills" / "test" / skill_name

    if not source.exists():
        print(f"FAILED: 源 skill 不存在: {source}")
        sys.exit(1)

    if not (source / "SKILL.md").is_file():
        print(f"FAILED: 源目录缺少 SKILL.md: {source}")
        sys.exit(1)

    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        shutil.rmtree(target)

    shutil.copytree(source, target)

    if (target / "SKILL.md").is_file():
        print(f"OK - {skill_name} 已复制到 {target}")
    else:
        print("FAILED: 复制结果验证失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
