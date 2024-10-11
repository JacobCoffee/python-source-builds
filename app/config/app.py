"""Configs and plugins settings for Litestar."""

import logging

from litestar.logging.config import LoggingConfig, StructLoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin
from litestar.template.config import TemplateConfig
from litestar_granian import GranianPlugin
from litestar_vite import ViteConfig, VitePlugin

from app.__metadata__ import __version__
from app.config.settings import get_settings
from app.utils import get_template_directories

settings = get_settings()

# --- Configs
vite_config = ViteConfig(
    bundle_dir=settings.vite.BUNDLE_DIR,
    resource_dir=settings.vite.RESOURCE_DIR,
    template_dir=settings.vite.TEMPLATE_DIR,
    use_server_lifespan=settings.vite.USE_SERVER_LIFESPAN,
    dev_mode=settings.vite.DEV_MODE,
    hot_reload=settings.vite.HOT_RELOAD,
    is_react=settings.vite.ENABLE_REACT_HELPERS,
    port=settings.vite.PORT,
    host=settings.vite.HOST,
)
log_config = StructlogConfig(
    structlog_logging_config=StructLoggingConfig(
        log_exceptions="always",
        standard_lib_logging_config=LoggingConfig(
            root={"level": logging.getLevelName(settings.log.LEVEL), "handlers": ["queue_listener"]},
            loggers={
                "granian.access": {
                    "propagate": False,
                    "level": settings.log.GRANIAN_ACCESS_LEVEL,
                    "handlers": ["queue_listener"],
                },
                "granian.error": {
                    "propagate": False,
                    "level": settings.log.GRANIAN_ERROR_LEVEL,
                    "handlers": ["queue_listener"],
                },
                "aiosqlite": {
                    "propagate": False,
                    "level": 30,
                    "handlers": ["queue_listener"],
                },
                "httpcore": {
                    "propagate": False,
                    "level": 30,
                    "handlers": ["queue_listener"],
                },
                "httpx": {
                    "propagate": False,
                    "level": 30,
                    "handlers": ["queue_listener"],
                },
            },
        ),
    ),
    middleware_logging_config=LoggingMiddlewareConfig(
        request_log_fields=["method", "path", "path_params", "query"],
        response_log_fields=["status_code"],
    ),
)
openapi_config = OpenAPIConfig(
    title=settings.app.NAME,
    version=__version__,
    path="/api",
    use_handler_docstrings=True,
    render_plugins=[
        ScalarRenderPlugin(
            version="latest",
            css_url="/static/scalar.css",
        )
    ],
)
template_config = TemplateConfig(
    directory=get_template_directories(),
    engine=settings.template.ENGINE,
)

# --- Plugin instances
structlog_plugin = StructlogPlugin(config=log_config)
vite_plugin = VitePlugin(config=vite_config)
granian_plugin = GranianPlugin()
