"""Structures for the core applets."""

from typing import Literal

import msgspec


class Version(msgspec.Struct):
    """Python version schema."""

    name: str
    major: int
    minor: int
    patch: int
    level: Literal["alpha", "beta", "release-candidate", "final"]
    status: Literal["feature", "prerelease", "bugfix", "security", "end-of-life"]
