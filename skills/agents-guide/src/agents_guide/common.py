import warnings
from pathlib import Path
from typing import Optional


def resolve_depth(
    cli_specific: Optional[int],
    cli_common: Optional[int],
    yaml_value: Optional[int],
    default: int,
) -> int:
    """按优先级解析最终生效的 depth 值。

    优先级：CLI 专属参数 > CLI 通用参数 > YAML 配置 > 默认值。
    非法值（非正整数、非整数）回退到 1 或默认值，并输出警告。
    """
    raw: Optional[int] = None
    source = "default"
    if cli_specific is not None:
        raw = cli_specific
        source = "CLI"
    elif cli_common is not None:
        raw = cli_common
        source = "CLI"
    elif yaml_value is not None:
        raw = yaml_value
        source = "YAML"

    if raw is None:
        return default

    try:
        value = int(raw)
    except (TypeError, ValueError):
        warnings.warn(f"Invalid depth value from {source}: {raw!r}; using default {default}")
        return default

    if value <= 0:
        warnings.warn(f"Depth must be positive, got {value} from {source}; using 1")
        return 1

    return value


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
