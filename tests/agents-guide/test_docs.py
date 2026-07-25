from pathlib import Path

import pytest

from agents_guide.docs import scan_docs


def test_scan_docs_returns_current_meta_not_current_guide(tmp_path):
    (tmp_path / ".agents-guide.yaml").write_text("meta:\n  name: current-module\n")
    (tmp_path / "AGENTS.md").write_text("# current")
    (tmp_path / "README.md").write_text("# readme")

    result = scan_docs(tmp_path, depth=3, project_root=tmp_path)
    assert result["current_meta"].get("name") == "current-module"
    assert not any(g["rel_path"] == "AGENTS.md" for g in result["guides"])
    assert any(l["rel_path"] == "README.md" for l in result["leafs"])


def test_scan_docs_stops_at_child_agents_md_boundary(tmp_path):
    child = tmp_path / "child"
    child.mkdir()
    (child / "AGENTS.md").write_text("# child")
    (child / "extra.md").write_text("# extra")
    grandchild = child / "grandchild"
    grandchild.mkdir()
    (grandchild / "deep.md").write_text("# deep")

    result = scan_docs(tmp_path, depth=3, project_root=tmp_path)
    assert any(g["rel_path"] == "child/AGENTS.md" for g in result["guides"])
    assert not any(l["rel_path"] == "child/extra.md" for l in result["leafs"])
    assert not any(l["rel_path"] == "child/grandchild/deep.md" for l in result["leafs"])


def test_scan_docs_depth_limits_recursion(tmp_path):
    child = tmp_path / "child"
    child.mkdir()
    grandchild = child / "grandchild"
    grandchild.mkdir()
    (grandchild / "deep.md").write_text("# deep")

    result_depth1 = scan_docs(tmp_path, depth=1, project_root=tmp_path)
    assert not any(l["rel_path"] == "child/grandchild/deep.md" for l in result_depth1["leafs"])

    result_depth3 = scan_docs(tmp_path, depth=3, project_root=tmp_path)
    assert any(l["rel_path"] == "child/grandchild/deep.md" for l in result_depth3["leafs"])


def test_scan_docs_current_guide_not_in_leafs(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# current")
    result = scan_docs(tmp_path, depth=3, project_root=tmp_path)
    assert not any(l["rel_path"] == "AGENTS.md" for l in result["leafs"])
