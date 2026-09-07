import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


CONFIG_NAME = ".agents.config.yaml"
LOCAL_CONFIG_NAME = ".agents.config.local.yaml"
GUIDE_DOMAIN = "agents-guide"


def read_yaml_file(config_file: Path) -> Dict[str, Any]:
    """读取 YAML 文件；文件缺失、解析失败或顶层非映射时返回空字典。"""
    if not config_file.is_file():
        return {}
    try:
        with config_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def load_guide_config(directory: Path) -> Dict[str, Any]:
    """读取目标目录 .agents.config*.yaml 中的 agents-guide 域。

    遵循 agents-config 约定：只在目标目录查找，不向上继承；
    本技能的覆盖语义：local 文件中 agents-guide 域存在时整域替换共享层。
    """
    shared = read_yaml_file(directory / CONFIG_NAME).get(GUIDE_DOMAIN)
    local = read_yaml_file(directory / LOCAL_CONFIG_NAME).get(GUIDE_DOMAIN)
    domain = local if local is not None else shared
    return domain if isinstance(domain, dict) else {}


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


def _resolve_section_config(
    scan_section: Any,
    stage_section: Any,
    default_depth: int,
) -> Dict[str, Any]:
    """将 scan 通用配置与 stage 特定配置合并。

    - depth: stage 存在则覆盖 scan，否则使用 scan，再否则使用 default_depth。
    - include / exclude: scan 与 stage 的列表合并。
    """
    scan_dict = scan_section if isinstance(scan_section, dict) else {}
    stage_dict = stage_section if isinstance(stage_section, dict) else {}

    scan_depth = scan_dict.get("depth")
    stage_depth = stage_dict.get("depth")
    depth = stage_depth if stage_depth is not None else (scan_depth if scan_depth is not None else default_depth)

    def collect(key: str) -> Optional[List[str]]:
        values: List[str] = []
        for section in (scan_dict, stage_dict):
            for item in section.get(key) or []:
                if item is not None:
                    values.append(str(item))
        return values or None

    return {
        "depth": depth,
        "include": collect("include"),
        "exclude": collect("exclude"),
    }


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
