"""Primitive test just to have something to discover."""

import pytest


def test_simple():
    """Stupid test function."""
    assert True
    assert 0.99 == pytest.approx(1, 0.1)
