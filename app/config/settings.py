"""Application settings.

Secrets are consumed from env vars.
"""

from __future__ import annotations

import binascii
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Final

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.utils.module_loader import module_to_os_path

if TYPE_CHECKING:
    from litestar.data_extractors import RequestExtractorField, ResponseExtractorField

DEFAULT_MODULE_NAME = "app"
BASE_DIR: Final[Path] = module_to_os_path(DEFAULT_MODULE_NAME)

TRUE_VALUES = {"True", "true", "1", "yes", "Y", "T"}


@dataclass
class ViteSettings:
    """Server configurations."""

    DEV_MODE: bool = field(
        default_factory=lambda: os.getenv("VITE_DEV_MODE", "False") in TRUE_VALUES,
    )
    """Start ``vite`` development server."""
    USE_SERVER_LIFESPAN: bool = field(
        default_factory=lambda: os.getenv("VITE_USE_SERVER_LIFESPAN", "True") in TRUE_VALUES,
    )
    """Auto start and stop ``vite`` processes when running in development mode.."""
    HOST: str = field(default_factory=lambda: os.getenv("VITE_HOST", "0.0.0.0"))  # noqa: S104
    """The host the ``vite`` process will listen on.  Defaults to ``0.0.0.0``"""
    PORT: int = field(default_factory=lambda: int(os.getenv("VITE_PORT", "5173")))
    """The port to start vite on.  Default to ``5173``"""
    HOT_RELOAD: bool = field(
        default_factory=lambda: os.getenv("VITE_HOT_RELOAD", "True") in TRUE_VALUES,
    )
    """Start ``vite`` with HMR enabled."""
    ENABLE_REACT_HELPERS: bool = field(
        default_factory=lambda: os.getenv("VITE_ENABLE_REACT_HELPERS", "True") in TRUE_VALUES,
    )
    """Enable React support in HMR."""
    BUNDLE_DIR: Path = field(default_factory=lambda: Path(f"{BASE_DIR}/applets/core/public"))
    """Bundle directory"""
    RESOURCE_DIR: Path = field(default_factory=lambda: Path("resources"))
    """Resource directory"""
    TEMPLATE_DIR: Path = field(default_factory=lambda: Path(f"{BASE_DIR}/applets/core/templates"))
    """Template directory."""
    ASSET_URL: str = field(default_factory=lambda: os.getenv("ASSET_URL", "/static/"))
    """Base URL for assets"""

    @property
    def set_static_files(self) -> bool:
        """Serve static assets.

        Returns:
            bool: True if the asset URL is a relative path.
        """
        return self.ASSET_URL.startswith("/")


@dataclass
class ServerSettings:
    """Server configurations."""

    APP_LOC: str = "app.asgi:app"
    """Path to app executable, or factory."""
    APP_LOC_IS_FACTORY: bool = False
    """Indicate if APP_LOC points to an executable or factory."""
    HOST: str = field(default_factory=lambda: os.getenv("LITESTAR_HOST", "0.0.0.0"))  # noqa: S104
    """Server network host."""
    PORT: int = field(default_factory=lambda: int(os.getenv("LITESTAR_PORT", "8000")))
    """Server port."""
    KEEPALIVE: int = field(default_factory=lambda: int(os.getenv("LITESTAR_KEEPALIVE", "65")))
    """Seconds to hold connections open (65 is > AWS lb idle timeout)."""
    RELOAD: bool = field(
        default_factory=lambda: os.getenv("LITESTAR_RELOAD", "False") in TRUE_VALUES,
    )
    """Turn on hot reloading."""
    RELOAD_DIRS: list[str] = field(default_factory=lambda: [f"{BASE_DIR}"])
    """Directories to watch for reloading."""
    HTTP_WORKERS: int | None = field(
        default_factory=lambda: int(os.getenv("WEB_CONCURRENCY")) if os.getenv("WEB_CONCURRENCY") is not None else None,
        # type: ignore[arg-type]
    )
    """Number of HTTP Worker processes to be spawned by Uvicorn."""


@dataclass
class LogSettings:
    """Logger configuration."""

    # https://stackoverflow.com/a/1845097/6560549
    EXCLUDE_PATHS: str = r"\A(?!x)x"
    """Regex to exclude paths from logging."""
    HTTP_EVENT: str = "HTTP"
    """Log event name for logs from Litestar handlers."""
    INCLUDE_COMPRESSED_BODY: bool = False
    """Include ``body`` of compressed responses in log output."""
    LEVEL: int = field(default_factory=lambda: int(os.getenv("LOG_LEVEL", "10")))
    """Stdlib log levels.

    Only emit logs at this level, or higher.
    """
    OBFUSCATE_COOKIES: set[str] = field(default_factory=lambda: {"session"})
    """Request cookie keys to obfuscate."""
    OBFUSCATE_HEADERS: set[str] = field(default_factory=lambda: {"Authorization", "X-API-KEY"})
    """Request header keys to obfuscate."""
    REQUEST_FIELDS: list[RequestExtractorField] = field(
        default_factory=lambda: [
            "path",
            "method",
            "headers",
            "cookies",
            "query",
            "path_params",
            "body",
        ],
    )
    """Attributes of the `~litestar.connection.request.Request`_ to be logged."""
    RESPONSE_FIELDS: list[ResponseExtractorField] = field(
        default_factory=lambda: [
            "status_code",
            "cookies",
            "headers",
            "body",
        ],
    )
    """Attributes of the `~litestar.response.Response`_ to be logged."""
    GRANIAN_ACCESS_LEVEL: int = 30
    """Level to log uvicorn access logs."""
    GRANIAN_ERROR_LEVEL: int = 20
    """Level to log uvicorn error logs."""


@dataclass
class AppSettings:
    """Application configuration."""

    URL: str = field(default_factory=lambda: os.getenv("APP_URL", "http://localhost:8000"))
    """The frontend base URL"""
    DEBUG: bool = field(default_factory=lambda: os.getenv("LITESTAR_DEBUG", "False") in TRUE_VALUES)
    """Run ``Litestar`` with ``debug=True``."""
    SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", binascii.hexlify(os.urandom(32)).decode(encoding="utf-8")),
    )
    """Application secret key."""
    NAME: str = field(default_factory=lambda: "python-source-builder")
    """Application name."""


@dataclass
class TemplateSettings:
    """Configures Templating for the project."""

    ENGINE: type[JinjaTemplateEngine] = JinjaTemplateEngine
    """Template engine to use. (Jinja2 or Mako)"""


@dataclass
class Settings:
    """Application settings."""

    app: AppSettings = field(default_factory=AppSettings)
    template: TemplateSettings = field(default_factory=TemplateSettings)
    vite: ViteSettings = field(default_factory=ViteSettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    log: LogSettings = field(default_factory=LogSettings)

    @classmethod
    def from_env(cls, dotenv_filename: str = ".env") -> Settings:
        """Load settings from environment variables.

        Args:
            dotenv_filename (str): The name of the dotenv file to load.
                Assumes ``curdir`` but can pass the rest of the path.

        Returns:
            Settings: Application settings
        """
        # noinspection PyProtectedMember
        from litestar.cli._utils import console

        env_file = Path(f"{os.curdir}/{dotenv_filename}")
        if env_file.is_file():
            from dotenv import load_dotenv

            console.print(f"[yellow]Loading environment configuration from {dotenv_filename}[/]")

            load_dotenv(env_file, override=True)
        return Settings()


@lru_cache(maxsize=1, typed=True)
def get_settings() -> Settings:
    """Helper function to get settings from elsewhere.

    Returns:
        Settings: Application settings
    """
    return Settings.from_env()
