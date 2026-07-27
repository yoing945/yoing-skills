#!/usr/bin/env python3
import os
import shutil
import filecmp
from pathlib import Path
from typing import List

import pathspec


def load_gitignore(project_root: Path):
    """加载项目根目录的 .gitignore，返回 pathspec.PathSpec。"""
    gitignore_path = project_root / ".gitignore"
    patterns = []
    if gitignore_path.is_file():
        patterns = [
            line
            for line in gitignore_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    return pathspec.PathSpec.from_lines("gitignore", patterns)


def _make_ignore_func(spec, project_root: Path):
    """根据 .gitignore 生成 shutil.copytree 可用的 ignore 函数。"""

    def ignore_func(src, names):
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


def _resolve_skill_source(project_root: Path, skill: str) -> Path:
    """按优先级查找 skill 源目录。"""
    candidates = [
        project_root / "skills" / skill,
        project_root / ".agents" / "skills" / skill,
    ]
    for src in candidates:
        if src.is_dir():
            return src
    raise FileNotFoundError(
        f"source skill not found in skills/ or .agents/skills/: {skill}"
    )


def _get_relative_path(project_root: Path, src: Path) -> str:
    """返回源目录相对于项目根目录的路径。"""
    return src.relative_to(project_root).as_posix()


def sync_skills(project_root: Path, target_path: Path, skills: List[str], spec):
    """将 skills 复制到目标工程目录。"""
    ignore_func = _make_ignore_func(spec, project_root)
    for skill in skills:
        src = _resolve_skill_source(project_root, skill)
        rel_path = _get_relative_path(project_root, src)
        dst = target_path / rel_path

        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=ignore_func)
        print(f"skill synced: {skill} -> {rel_path}")


def sync_prompts(project_root: Path, target_path: Path, prompts: List[str]):
    """将 prompts 复制到目标工程目录。"""
    for prompt in prompts:
        src = project_root / "prompts" / f"{prompt}.md"
        dst = target_path / "prompts" / f"{prompt}.md"

        if not src.is_file():
            raise FileNotFoundError(f"source prompt not found: {src}")

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"prompt synced: {prompt}.md")


def verify(project_root: Path, target_path: Path, skills: List[str], prompts: List[str]):
    """校验目标工程目录与源目录是否完全一致。"""
    errors = []
    spec = load_gitignore(project_root)

    for skill in skills:
        src = _resolve_skill_source(project_root, skill)
        rel_path = _get_relative_path(project_root, src)
        dst = target_path / rel_path

        if not dst.is_dir():
            errors.append(f"skill missing in target: {skill}")
            continue

        for root, dirs, files in os.walk(src):
            rel_root_to_src = Path(root).relative_to(src).as_posix()

            dirs[:] = [
                d
                for d in dirs
                if not spec.match_file(
                    rel_path
                    + "/"
                    + (rel_root_to_src + "/" + d if rel_root_to_src != "." else d)
                    + "/"
                )
            ]

            for f in files:
                rel_file_to_src = (
                    rel_root_to_src + "/" + f if rel_root_to_src != "." else f
                )
                rel_file_to_project = rel_path + "/" + rel_file_to_src
                if spec.match_file(rel_file_to_project):
                    continue

                src_file = Path(root) / f
                dst_file = dst / rel_file_to_src

                if not dst_file.is_file():
                    errors.append(f"skill file missing in target: {skill}/{rel_file_to_src}")
                elif not filecmp.cmp(src_file, dst_file, shallow=False):
                    errors.append(f"skill file mismatch: {skill}/{rel_file_to_src}")

    for prompt in prompts:
        src = project_root / "prompts" / f"{prompt}.md"
        dst = target_path / "prompts" / f"{prompt}.md"
        if not dst.is_file() or not filecmp.cmp(src, dst, shallow=False):
            errors.append(f"prompt mismatch: {prompt}.md")

    return errors
