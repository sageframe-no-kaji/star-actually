"""Skeleton suite: the package imports and declares a version."""

import re

import star_actually


def test_version_is_declared() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", star_actually.__version__)
