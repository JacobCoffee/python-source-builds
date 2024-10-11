"""App factory for creating a new app instance."""

from litestar import Litestar

__all__ = ("app_factory",)


def app_factory() -> Litestar:
    """Construct app with some defaults."""
    from litestar import Litestar

    from app.config.app import granian_plugin, openapi_config, structlog_plugin, template_config, vite_plugin
    from app.config.routes import route_handlers

    return Litestar(
        # - Config
        plugins=[structlog_plugin, granian_plugin, vite_plugin],
        openapi_config=openapi_config,
        template_config=template_config,
        # - Core
        route_handlers=route_handlers,
        # - Hooks
        on_app_init=[],
    )


app = app_factory()
