import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from agents_guide.common import find_project_root
from agents_guide.docs import scan_docs
from agents_guide.tree import scan_tree


CONFIG_NAME = ".agents-guide.yaml"


def _write_json(data: Dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _load_config(target_dir: Path) -> Dict[str, Any]:
    """读取目标目录下的 .agents-guide.yaml 配置。"""
    config_file = target_dir / CONFIG_NAME
    if not config_file.is_file():
        return {}
    try:
        with config_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _merge_section_args(
    cli_include: List[str],
    cli_exclude: List[str],
    section: Dict[str, Any],
) -> tuple[Optional[List[str]], Optional[List[str]]]:
    """合并 .agents-guide.yaml 中的 include/exclude 与 CLI 参数。"""
    include: List[str] = []
    exclude: List[str] = []
    if isinstance(section, dict):
        include.extend(str(item) for item in section.get("include") or [] if item is not None)
        exclude.extend(str(item) for item in section.get("exclude") or [] if item is not None)
    include.extend(cli_include)
    exclude.extend(cli_exclude)
    return (include or None), (exclude or None)


def main(argv: Any = None) -> int:
    parser = argparse.ArgumentParser(prog="agents-guide")
    subparsers = parser.add_subparsers(dest="command")

    tree_parser = subparsers.add_parser("tree", help="扫描目录结构")
    tree_parser.add_argument("--target", required=True, type=Path)
    tree_parser.add_argument("--depth", type=int, default=3)
    tree_parser.add_argument("--exclude", action="append", default=[], help="排除目录/文件，可多次指定")
    tree_parser.add_argument("--include", action="append", default=[], help="强制包含目录/文件，可多次指定")

    docs_parser = subparsers.add_parser("docs", help="发现 guide/leaf 文档")
    docs_parser.add_argument("--target", required=True, type=Path)
    docs_parser.add_argument("--exclude", action="append", default=[], help="排除目录/文件，可多次指定")
    docs_parser.add_argument("--include", action="append", default=[], help="强制包含目录/文件，可多次指定")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"error: target directory does not exist: {target}", file=sys.stderr)
        return 1

    project_root = find_project_root(target)
    config = _load_config(target)

    if args.command == "tree":
        include, exclude = _merge_section_args(args.include, args.exclude, config.get("tree", {}))
        data = scan_tree(target, args.depth, project_root, exclude=exclude, include=include)
    elif args.command == "docs":
        include, exclude = _merge_section_args(args.include, args.exclude, config.get("docs", {}))
        data = scan_docs(target, project_root, exclude=exclude, include=include)
    else:
        parser.print_help()
        return 1

    _write_json(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
