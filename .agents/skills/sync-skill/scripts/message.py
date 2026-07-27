#!/usr/bin/env python3
import filecmp
import os
from pathlib import Path
from typing import List, Optional

from sync import _resolve_skill_source, load_gitignore


def _skill_has_changes(project_root: Path, target_path: Path, skill: str, spec) -> bool:
    """判断某个 skill 在源目录与目标目录之间是否存在差异。"""
    src = _resolve_skill_source(project_root, skill)
    rel_path = src.relative_to(project_root).as_posix()
    dst = target_path / rel_path

    if not dst.is_dir():
        return True

    for root, dirs, files in os.walk(src):
        rel_root = Path(root).relative_to(src).as_posix()
        dirs[:] = [
            d
            for d in dirs
            if not spec.match_file(
                (rel_root + "/" + d if rel_root != "." else d) + "/"
            )
        ]
        for f in files:
            rel_file = rel_root + "/" + f if rel_root != "." else f
            if spec.match_file(rel_file):
                continue
            src_file = Path(root) / f
            dst_file = dst / rel_file
            if not dst_file.is_file() or not filecmp.cmp(
                src_file, dst_file, shallow=False
            ):
                return True
    return False


def _prompt_has_changes(project_root: Path, target_path: Path, prompt: str) -> bool:
    """判断某个 prompt 在源目录与目标目录之间是否存在差异。"""
    src = project_root / "prompts" / f"{prompt}.md"
    dst = target_path / "prompts" / f"{prompt}.md"
    if not src.is_file():
        return False
    if not dst.is_file():
        return True
    return not filecmp.cmp(src, dst, shallow=False)


def generate_message(
    project_root: Path,
    target_path: Path,
    skills: List[str],
    prompts: List[str],
) -> Optional[str]:
    """根据本次同步的 skill/prompt 差异生成提交信息。

    若没有任何变更，返回 None。
    """
    spec = load_gitignore(project_root)

    changed_skills = [
        s for s in skills if _skill_has_changes(project_root, target_path, s, spec)
    ]
    changed_prompts = [
        p for p in prompts if _prompt_has_changes(project_root, target_path, p)
    ]

    parts = []
    if changed_skills:
        parts.append("sync skills: " + ", ".join(changed_skills))
    if changed_prompts:
        parts.append("sync prompts: " + ", ".join(changed_prompts))

    if not parts:
        return None
    return "; ".join(parts)
