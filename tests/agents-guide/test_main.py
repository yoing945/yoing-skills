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
