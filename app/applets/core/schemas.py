"""Structures for the core applets."""

from datetime import datetime
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
    last_updated: datetime

    @property
    def full_version(self) -> str:
        """Return the full version string (major.minor.patch)."""
        return f"{self.major}.{self.minor}.{self.patch}"


class ScriptData(msgspec.Struct):
    """Schema for the script data."""

    selectedVersion: str = "3.13.0"
    prefixPath: str = "/opt/python/"
    installOSPackages: bool = False
    enableSpeedOptimization: bool = False
    enableSharedLibraries: bool = False
    useAllCPUs: bool = False
    runPostTest: bool = False
    updatePackages: bool = False
    addSoftLinks: bool = False
    disableGIL: bool = False
    enableJIT: bool = False
