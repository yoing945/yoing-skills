"""agents-guide 入口：将 src/ 与 vendor/ 加入 sys.path 后调用 CLI。

用法：python run.py tree|docs --target <dir> [options]
依赖已 vendor 进 vendor/ 目录，无需安装环境。
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here / "vendor"))
sys.path.insert(0, str(_here / "src"))

from agents_guide.main import main

raise SystemExit(main())
