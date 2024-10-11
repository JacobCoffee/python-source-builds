"""Root module for the app."""

import multiprocessing
import platform

if platform.system() == "Darwin":
    multiprocessing.set_start_method("fork", force=True)

from app import __metadata__

__all__ = ("__metadata__",)
