import json
from pathlib import Path

from agents_guide.main import main


def test_tree_command_accepts_tree_depth(tmp_path, capsys):
    (tmp_path / "a").mkdir()
    code = main(["tree", "--target", str(tmp_path), "--tree-depth", "2"])
    captured = capsys.readouterr()
    assert code == 0
    assert "a" in captured.out


def test_docs_command_accepts_docs_depth(tmp_path, capsys):
    (tmp_path / "README.md").write_text("# readme")
    code = main(["docs", "--target", str(tmp_path), "--docs-depth", "1"])
    captured = capsys.readouterr()
    assert code == 0
    assert "README" in captured.out


def test_tree_uses_scan_depth_and_merged_rules(tmp_path, capsys):
    config = tmp_path / ".agents-guide.yaml"
    config.write_text(
        "scan:\n  depth: 2\n  include:\n    - .agents\n  exclude:\n    - temp\n",
        encoding="utf-8",
    )
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "AGENTS.md").write_text("# agents")
    (tmp_path / "temp").mkdir()
    (tmp_path / "src").mkdir()

    code = main(["tree", "--target", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 0
    data = json.loads(captured.out)
    names = {node["name"] for node in data["directory_tree"]}
    assert ".agents" in names
    assert "temp" not in names
    # depth=2 时 src 作为直接子目录应出现，但不继续展开
    assert "src" in names


def test_docs_stage_depth_overrides_scan_depth(tmp_path, capsys):
    config = tmp_path / ".agents-guide.yaml"
    config.write_text(
        "scan:\n  depth: 1\ndocs:\n  depth: 2\n",
        encoding="utf-8",
    )
    child = tmp_path / "child"
    child.mkdir()
    grandchild = child / "grandchild"
    grandchild.mkdir()
    (grandchild / "deep.md").write_text("# deep")

    code = main(["docs", "--target", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 0
    data = json.loads(captured.out)
    assert any(l["rel_path"] == "child/grandchild/deep.md" for l in data["leafs"])
