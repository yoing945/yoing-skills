from pathlib import Path


def find_project_root(target_dir: Path) -> Path:
    """从 target_dir 向上查找包含 .git 的目录；未找到则返回 target_dir 自身。"""
    current = target_dir.resolve()
    while True:
        if (current / ".git").is_dir():
            return current
        parent = current.parent
        if parent == current:
            return target_dir.resolve()
        current = parent


def normalize_rel_path(path: str) -> str:
    """规范化相对路径：去除 ./、多余斜杠和末尾斜杠；空字符串返回 '.'。"""
    parts = [p for p in path.replace("\\", "/").split("/") if p and p != "."]
    return "/".join(parts) if parts else "."
