#!/usr/bin/env python3
import os
import sys
import shutil
import filecmp

import pathspec
import yaml


def load_gitignore(project_root):
    """加载项目根目录的 .gitignore，返回 pathspec.PathSpec。"""
    gitignore_path = os.path.join(project_root, ".gitignore")
    patterns = []
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            patterns = [line for line in f.read().splitlines() if line.strip()]
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


def make_ignore_func(spec, project_root):
    """根据 .gitignore 生成 shutil.copytree 可用的 ignore 函数。"""
    def ignore_func(src, names):
        ignored = set()
        for name in names:
            full_path = os.path.join(src, name)
            rel_path = os.path.relpath(full_path, project_root).replace(os.sep, "/")
            if spec.match_file(rel_path):
                ignored.add(name)
            elif os.path.isdir(full_path):
                # 目录模式常以 / 结尾，补 / 后再匹配一次
                if spec.match_file(rel_path + "/"):
                    ignored.add(name)
        return ignored
    return ignore_func


def get_skill_root():
    """获取 skill 根目录（脚本位于 scripts/ 子目录下）"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def get_project_root():
    """从 skill 根目录向上回溯到项目根目录（.agents/skills/skill-sync -> 根目录）"""
    skill_root = get_skill_root()
    return os.path.dirname(os.path.dirname(os.path.dirname(skill_root)))


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_skill_source(project_root, skill):
    """按优先级查找 skill 源目录。优先根目录 skills/，其次 .agents/skills/。"""
    candidates = [
        os.path.join(project_root, "skills", skill),
        os.path.join(project_root, ".agents", "skills", skill),
    ]
    for src in candidates:
        if os.path.isdir(src):
            return src
    raise FileNotFoundError(f"source skill not found in skills/ or .agents/skills/: {skill}")


def get_relative_path(project_root, src):
    """返回源目录相对于项目根目录的路径。"""
    return os.path.relpath(src, project_root).replace(os.sep, "/")


def sync_skills(project_root, target_path, skills, spec):
    ignore_func = make_ignore_func(spec, project_root)

    for skill in skills:
        src = resolve_skill_source(project_root, skill)
        rel_path = get_relative_path(project_root, src)
        dst = os.path.join(target_path, rel_path)

        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=ignore_func)
        print(f"skill synced: {skill} -> {rel_path}")


def sync_prompts(project_root, target_path, prompts):
    for prompt in prompts:
        src = os.path.join(project_root, "prompts", f"{prompt}.md")
        dst_dir = os.path.join(target_path, "prompts")
        dst = os.path.join(dst_dir, f"{prompt}.md")

        if not os.path.isfile(src):
            raise FileNotFoundError(f"source prompt not found: {src}")

        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"prompt synced: {prompt}.md")


def verify(project_root, target_path, skills, prompts):
    errors = []
    spec = load_gitignore(project_root)

    for skill in skills:
        src = resolve_skill_source(project_root, skill)
        rel_path = get_relative_path(project_root, src)
        dst = os.path.join(target_path, rel_path)

        if not os.path.isdir(dst):
            errors.append(f"skill missing in target: {skill}")
            continue

        for root, dirs, files in os.walk(src):
            rel_root = os.path.relpath(root, src).replace(os.sep, "/")

            # 排除被忽略的目录
            dirs[:] = [
                d for d in dirs
                if not spec.match_file(
                    (rel_root + "/" + d if rel_root != "." else d) + "/"
                )
            ]

            for f in files:
                rel_file = (rel_root + "/" + f if rel_root != "." else f)
                if spec.match_file(rel_file):
                    continue

                src_file = os.path.join(root, f)
                dst_file = os.path.join(dst, rel_file)

                if not os.path.isfile(dst_file):
                    errors.append(f"skill file missing in target: {skill}/{rel_file}")
                elif not filecmp.cmp(src_file, dst_file, shallow=False):
                    errors.append(f"skill file mismatch: {skill}/{rel_file}")

    for prompt in prompts:
        src = os.path.join(project_root, "prompts", f"{prompt}.md")
        dst = os.path.join(target_path, "prompts", f"{prompt}.md")
        if not os.path.isfile(dst) or not filecmp.cmp(src, dst, shallow=False):
            errors.append(f"prompt mismatch: {prompt}.md")

    return errors


def main():
    skill_root = get_skill_root()
    config_path = os.path.join(skill_root, "config.local.yaml")
    project_root = get_project_root()

    if not os.path.isfile(config_path):
        print(f"ERROR: config not found: {config_path}")
        sys.exit(1)

    config = load_config(config_path).get("config", {})
    target_path = config.get("target_path")
    skills = config.get("skills", [])
    prompts = config.get("prompts", [])

    if not target_path:
        print("ERROR: target_path is required in config")
        sys.exit(1)

    spec = load_gitignore(project_root)

    print(f"target_path: {target_path}")
    print(f"skills: {skills}")
    print(f"prompts: {prompts}")
    print()

    sync_skills(project_root, target_path, skills, spec)
    sync_prompts(project_root, target_path, prompts)

    print()
    print("verifying...")
    errors = verify(project_root, target_path, skills, prompts)

    if errors:
        print("FAILED:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    print("OK - all synced and verified")


if __name__ == "__main__":
    main()
