import warnings

import pytest

from agents_guide.common import _resolve_section_config, resolve_depth


def test_resolve_section_config_uses_stage_depth_over_scan():
    result = _resolve_section_config(
        {"depth": 2, "include": ["a"], "exclude": ["b"]},
        {"depth": 5, "include": ["c"], "exclude": ["d"]},
        default_depth=3,
    )
    assert result["depth"] == 5
    assert result["include"] == ["a", "c"]
    assert result["exclude"] == ["b", "d"]


def test_resolve_section_config_inherits_scan_depth_when_stage_missing():
    result = _resolve_section_config(
        {"depth": 2},
        {},
        default_depth=3,
    )
    assert result["depth"] == 2
    assert result["include"] is None
    assert result["exclude"] is None


def test_resolve_section_config_uses_default_when_both_missing_depth():
    result = _resolve_section_config({}, {}, default_depth=3)
    assert result["depth"] == 3


def test_resolve_section_config_handles_none_sections():
    result = _resolve_section_config(None, None, default_depth=3)
    assert result["depth"] == 3
    assert result["include"] is None
    assert result["exclude"] is None


def test_resolve_section_config_skips_none_items():
    result = _resolve_section_config(
        {"include": ["a", None, "b"], "exclude": [None]},
        {"include": ["c"]},
        default_depth=3,
    )
    assert result["include"] == ["a", "b", "c"]
    assert result["exclude"] is None


def test_resolve_depth_returns_cli_specific_first():
    assert resolve_depth(cli_specific=5, cli_common=3, yaml_value=2, default=1) == 5


def test_resolve_depth_returns_cli_common_when_no_specific():
    assert resolve_depth(cli_specific=None, cli_common=3, yaml_value=2, default=1) == 3


def test_resolve_depth_returns_yaml_when_no_cli():
    assert resolve_depth(cli_specific=None, cli_common=None, yaml_value=2, default=1) == 2


def test_resolve_depth_returns_default_when_nothing_else():
    assert resolve_depth(cli_specific=None, cli_common=None, yaml_value=None, default=1) == 1


def test_resolve_depth_clamps_zero_to_one():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = resolve_depth(cli_specific=0, cli_common=None, yaml_value=None, default=3)
        assert result == 1
        assert len(w) == 1
        assert "Depth must be positive" in str(w[0].message)


def test_resolve_depth_clamps_negative_to_one():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = resolve_depth(cli_specific=-2, cli_common=None, yaml_value=None, default=3)
        assert result == 1
        assert len(w) == 1


def test_resolve_depth_falls_back_for_invalid_type():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = resolve_depth(cli_specific="abc", cli_common=None, yaml_value=None, default=3)
        assert result == 3
        assert len(w) == 1
        assert "Invalid depth value" in str(w[0].message)
