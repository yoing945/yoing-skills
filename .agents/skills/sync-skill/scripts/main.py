#!/usr/bin/env python3
import os
import sys
import shutil
import filecmp

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


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


def sync_skills(project_root, target_path, skills):
    for skill in skills:
        src = os.path.join(project_root, "skills", skill)
        dst = os.path.join(target_path, "skills", skill)

        if not os.path.isdir(src):
            raise FileNotFoundError(f"source skill not found: {src}")

        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"skill synced: {skill}")


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

    for skill in skills:
        src = os.path.join(project_root, "skills", skill)
        dst = os.path.join(target_path, "skills", skill)
        cmp = filecmp.dircmp(src, dst)
        if cmp.left_only or cmp.right_only or cmp.diff_files:
            errors.append(f"skill mismatch: {skill}")

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

    print(f"target_path: {target_path}")
    print(f"skills: {skills}")
    print(f"prompts: {prompts}")
    print()

    sync_skills(project_root, target_path, skills)
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
