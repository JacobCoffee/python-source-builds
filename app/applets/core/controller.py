"""Core controller."""

from typing import Final

from litestar import Controller, get
from litestar.response import Template

from app.applets.core.schemas import Version

MINIMUM_PLAYERS: Final[int] = 2


class CoreController(Controller):
    """Houses all routes for core endpoints."""

    path = "/"

    @get("/")
    async def index(self) -> Template:
        """Render the index page.

        Returns:
            A Template response containing the index page.
        """
        return Template(
            template_name="index.html",
        )

    @get("/versions")
    async def list_versions(self) -> list[Version]:
        """List all players from the database.

        Returns:
            A Template response containing the list of players.
        """
        # return list_python_versions()
        return [
            Version(name="Python 3.8", major=3, minor=8, patch=0, level="final", status="end-of-life"),
            Version(name="Python 3.13", major=3, minor=13, patch=0, level="final", status="feature"),
            Version(name="Python 3.14", major=3, minor=14, patch=0, level="alpha", status="prerelease"),
        ]
