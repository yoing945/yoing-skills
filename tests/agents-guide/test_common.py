import warnings

import pytest

from agents_guide.common import resolve_depth


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
