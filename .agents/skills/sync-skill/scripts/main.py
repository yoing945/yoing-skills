#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

import yaml

from gitops import commit, create_and_push_tag, get_repo, pull_rebase, push
from sync import load_gitignore, sync_prompts, sync_skills, verify


def get_skill_root() -> Path:
    """获取 skill 根目录（脚本位于 scripts/ 子目录下）。"""
    return Path(__file__).resolve().parent.parent


def get_project_root(skill_root: Path) -> Path:
    """从 skill 根目录向上回溯到项目根目录。"""
    return skill_root.parent.parent.parent


def _load_config(config_path: Path):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("config", {})


def _load_project_and_target(skill_root: Path):
    config_path = skill_root / "config.local.yaml"
    if not config_path.is_file():
        print(f"ERROR: config not found: {config_path}")
        sys.exit(1)

    config = _load_config(config_path)
    target_path_str = config.get("target_path")
    if not target_path_str:
        print("ERROR: target_path is required in config")
        sys.exit(1)

    project_root = get_project_root(skill_root)
    target_path = Path(target_path_str)
    skills = config.get("skills", [])
    prompts = config.get("prompts", [])
    return project_root, target_path, skills, prompts


def _do_sync(project_root: Path, target_path: Path, skills, prompts) -> bool:
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
        return False

    print("OK - all synced and verified")
    return True


def _do_commit_push(target_path: Path, message: str, tag: str | bool | None) -> int:
    if not message:
        print("ERROR: --message is required for commit-push")
        return 1

    repo = get_repo(target_path)

    if not commit(repo, message):
        print("no changes to commit in target project")
        return 0

    pull_rebase(repo)
    push(repo)
    print("target project pushed")

    if tag is not None:
        tag_name = create_and_push_tag(repo, tag if isinstance(tag, str) else None)
        print(f"tag created: {tag_name}")

    return 0


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    skill_root = get_skill_root()

    parser = argparse.ArgumentParser(prog="sync-skill")
    parser.add_argument("--dry-run", action="store_true", help="dry run for sync")

    subparsers = parser.add_subparsers(dest="command")

    cp_parser = subparsers.add_parser("commit-push", help="commit and push target project")
    cp_parser.add_argument("--message", "-m", required=True, help="commit message")
    cp_parser.add_argument(
        "--tag",
        nargs="?",
        const=True,
        default=None,
        help="create tag in target repo (auto-increment if no value)",
    )
    cp_parser.add_argument("--dry-run", action="store_true", help="dry run")

    args = parser.parse_args(argv)

    project_root, target_path, skills, prompts = _load_project_and_target(skill_root)

    if args.command == "commit-push":
        if args.dry_run:
            print("dry-run: would commit and push target project")
            return 0
        return _do_commit_push(target_path, args.message, args.tag)

    # 默认行为：执行同步
    if args.dry_run:
        print("dry-run: would sync skills and prompts")
        return 0
    return 0 if _do_sync(project_root, target_path, skills, prompts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
