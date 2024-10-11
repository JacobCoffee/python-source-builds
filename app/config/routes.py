"""Ingestion point for all app routes, to be sent into the Litestar app instance."""

from litestar.types import ControllerRouterHandler

from app.applets.core.controller import CoreController

__all__ = ("route_handlers",)

route_handlers: list[ControllerRouterHandler] = [CoreController]
