from pathlib import Path

import pytest

from agents_guide.tree import scan_tree


def test_scan_tree_default_depth(tmp_path):
    # depth=1 时只返回当前目录的直接子目录
    child = tmp_path / "child"
    child.mkdir()
    result = scan_tree(tmp_path, depth=1, project_root=tmp_path)
    assert len(result["directory_tree"]) == 1
    assert result["directory_tree"][0]["name"] == "child"


def test_scan_tree_depth_limits_recursion(tmp_path):
    child = tmp_path / "child"
    child.mkdir()
    grandchild = child / "grandchild"
    grandchild.mkdir()

    result_depth1 = scan_tree(tmp_path, depth=1, project_root=tmp_path)
    child_node = result_depth1["directory_tree"][0]
    assert child_node["children"] == []

    result_depth2 = scan_tree(tmp_path, depth=2, project_root=tmp_path)
    child_node = result_depth2["directory_tree"][0]
    assert len(child_node["children"]) == 1
    assert child_node["children"][0]["name"] == "grandchild"


def test_scan_tree_stops_at_agents_md_boundary(tmp_path):
    child = tmp_path / "child"
    child.mkdir()
    (child / "AGENTS.md").write_text("# child")
    grandchild = child / "grandchild"
    grandchild.mkdir()

    result = scan_tree(tmp_path, depth=3, project_root=tmp_path)
    child_node = next(n for n in result["directory_tree"] if n["name"] == "child")
    assert child_node["children"] == []
