#!/usr/bin/env python3
import re
from pathlib import Path
from typing import Optional

import git


def get_repo(repo_path: Path) -> git.Repo:
    """获取指定路径的 GitPython Repo 对象。"""
    try:
        return git.Repo(repo_path)
    except git.InvalidGitRepositoryError as exc:
        raise RuntimeError(f"not a git repository: {repo_path}") from exc


def has_changes(repo: git.Repo) -> bool:
    """判断工作区是否存在可提交的变更（含未跟踪文件）。"""
    return repo.is_dirty(untracked_files=True) or bool(repo.untracked_files)


def commit(repo: git.Repo, message: str) -> bool:
    """若存在变更则执行 add -A 并提交，返回是否实际创建了提交。"""
    if not has_changes(repo):
        return False
    repo.git.add("-A")
    repo.index.commit(message)
    return True


def pull_rebase(repo: git.Repo) -> None:
    """从 origin 拉取最新提交并使用 rebase 模式合并。"""
    if not repo.remotes:
        raise RuntimeError(f"no remote configured in {repo.working_dir}")
    branch = repo.active_branch.name
    repo.git.pull("origin", branch, "--rebase")


def push(repo: git.Repo) -> None:
    """将当前分支推送到 origin。"""
    if not repo.remotes:
        raise RuntimeError(f"no remote configured in {repo.working_dir}")
    branch = repo.active_branch.name
    repo.git.push("origin", branch)


def next_patch_tag(repo: git.Repo) -> str:
    """返回目标仓库下一个 patch 版本的 semver tag。"""
    pattern = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
    versions = []
    for tag in repo.tags:
        m = pattern.match(str(tag))
        if m:
            versions.append(tuple(int(x) for x in m.groups()))
    if not versions:
        return "v0.0.1"
    major, minor, patch = max(versions)
    return f"v{major}.{minor}.{patch + 1}"


def create_and_push_tag(repo: git.Repo, tag_name: Optional[str] = None) -> str:
    """在仓库中创建 tag 并推送到 origin（若配置了 origin）。"""
    name = tag_name or next_patch_tag(repo)
    repo.create_tag(name)
    if repo.remotes:
        repo.remotes.origin.push(name)
    return name
