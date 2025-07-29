"""Unit tests for __version__.py."""

import bobleesj.utils


def test_package_version():
    """Ensure the package version is defined and not set to the initial
    placeholder."""
    assert hasattr(bobleesj.utils, "__version__")
    assert bobleesj.utils.__version__ != "0.0.0"
