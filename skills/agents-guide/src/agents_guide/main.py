import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from agents_guide.common import find_project_root
from agents_guide.docs import scan_docs
from agents_guide.tree import scan_tree


def _write_json(data: Dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv: Any = None) -> int:
    parser = argparse.ArgumentParser(prog="agents-guide")
    subparsers = parser.add_subparsers(dest="command")

    tree_parser = subparsers.add_parser("tree", help="扫描目录结构")
    tree_parser.add_argument("--target", required=True, type=Path)
    tree_parser.add_argument("--depth", type=int, default=3)

    docs_parser = subparsers.add_parser("docs", help="发现 guide/leaf 文档")
    docs_parser.add_argument("--target", required=True, type=Path)
    docs_parser.add_argument("--exclude", default=None)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"error: target directory does not exist: {target}", file=sys.stderr)
        return 1

    project_root = find_project_root(target)

    if args.command == "tree":
        data = scan_tree(target, args.depth, project_root)
    elif args.command == "docs":
        data = scan_docs(target, project_root, exclude=args.exclude)
    else:
        parser.print_help()
        return 1

    _write_json(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
