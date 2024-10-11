"""i am root."""

import multiprocessing
import platform

from app import __main__, __metadata__, applets, asgi, config, utils

__all__ = ("applets", "config", "__main__", "__metadata__", "utils", "asgi")

if platform.system() == "Darwin":
    multiprocessing.set_start_method("fork", force=True)
