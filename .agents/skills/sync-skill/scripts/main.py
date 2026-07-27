#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

import yaml

from gitops import commit, create_and_push_tag, get_repo, pull_rebase, push
from message import generate_message
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


def _do_commit_push(project_root: Path, target_path: Path, skills, prompts, args) -> int:
    if args.dry_run:
        print("dry-run: would sync, commit, and push")
        return 0

    message = args.message
    if not message:
        message = generate_message(project_root, target_path, skills, prompts)

    if not message:
        print("no changes to commit")
        return 0

    for label, repo_path in [("source", project_root), ("target", target_path)]:
        print(f"\ncommitting {label}: {repo_path}")
        repo = get_repo(repo_path)
        committed = commit(repo, message)
        if committed:
            pull_rebase(repo)
            push(repo)
            print(f"{label} pushed")
        else:
            print(f"{label} has no changes, skipped")

    if args.tag is not False:
        print(f"\ncreating tag in target: {target_path}")
        target_repo = get_repo(target_path)
        tag_name = create_and_push_tag(target_repo, args.tag if isinstance(args.tag, str) else None)
        print(f"tag created: {tag_name}")

    return 0


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    skill_root = get_skill_root()

    parser = argparse.ArgumentParser(prog="sync-skill")
    subparsers = parser.add_subparsers(dest="command")

    cp_parser = subparsers.add_parser("commit-push", help="sync, commit and push")
    cp_parser.add_argument("--message", "-m", default=None, help="commit message")
    cp_parser.add_argument(
        "--tag",
        nargs="?",
        const=True,
        default=False,
        help="create tag in target repo (auto-increment if no value)",
    )
    cp_parser.add_argument("--dry-run", action="store_true", help="dry run")
    cp_parser.add_argument(
        "--yes",
        "--non-interactive",
        action="store_true",
        help="skip interactive confirmation",
    )

    args = parser.parse_args(argv)

    config_path = skill_root / "config.local.yaml"
    if not config_path.is_file():
        print(f"ERROR: config not found: {config_path}")
        return 1

    config = _load_config(config_path)
    target_path_str = config.get("target_path")
    if not target_path_str:
        print("ERROR: target_path is required in config")
        return 1

    target_path = Path(target_path_str)
    skills = config.get("skills", [])
    prompts = config.get("prompts", [])

    project_root = get_project_root(skill_root)

    if args.command == "commit-push":
        if args.dry_run:
            print("dry-run: would sync, commit, and push")
            return 0
        if not _do_sync(project_root, target_path, skills, prompts):
            return 1
        return _do_commit_push(project_root, target_path, skills, prompts, args)

    # 默认行为：执行同步
    if not _do_sync(project_root, target_path, skills, prompts):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
