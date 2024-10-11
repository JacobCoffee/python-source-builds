"""Core controller."""

from litestar import Controller, Request, get, post
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.response import Template
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.shell import BashLexer
from structlog import get_logger

from app.applets.core.helpers import get_versions_from_db
from app.applets.core.schemas import ScriptData, Version

logger = get_logger(__name__)


class CoreController(Controller):
    """Houses all routes for core endpoints."""

    path = "/"

    @get("/", include_in_schema=False)
    async def index(self) -> Template:
        """Render the index page.

        Returns:
            Template: Index page.
        """
        python_versions = await get_versions_from_db()
        return Template(template_name="index.html", context={"python_versions": python_versions})

    @get("/api/versions")
    async def list_versions(self) -> list[Version]:
        """List all versions available in the database.

        Returns:
            list[Version]: List of all players.
        """
        return await get_versions_from_db()

    @post("/api/generate-script")
    async def generate_script(self, request: Request, script_data: ScriptData) -> HTMXTemplate :
        """Generate a script based on the provided data and apply Pygments highlighting.

        TODO: use multipart body instead of raw dogging the request and parsing...

        Args:
            request (Request): The incoming request.

        Returns:
            HTMXTemplate: The highlighted script.
        """
        form_data = await request.form()
        processed_data = {}

        for field_name in ScriptData.__annotations__:
            value = form_data.get(field_name)
            if value is not None:
                processed_data[field_name] = (
                    value == "on"
                    if isinstance(getattr(ScriptData, field_name, None), bool)
                    or field_name
                    in [
                        "installOSPackages",
                        "enableSpeedOptimization",
                        "enableSharedLibraries",
                        "useAllCPUs",
                        "runPostTest",
                        "updatePackages",
                        "addSoftLinks",
                    ]
                    else value
                )
            elif isinstance(getattr(ScriptData, field_name, None), bool) or field_name in [
                "installOSPackages",
                "enableSpeedOptimization",
                "enableSharedLibraries",
                "useAllCPUs",
                "runPostTest",
                "updatePackages",
                "addSoftLinks",
            ]:
                processed_data[field_name] = False
            else:
                # Use default value for other fields
                processed_data[field_name] = getattr(ScriptData, field_name)

        script_data = ScriptData(**processed_data)
        script_content = request.app.template_engine.get_template("partials/script.html").render(
            script_data=script_data
        )

        # Apply Pygments highlighting
        highlighted_script_with_lines = highlight(
            script_content, BashLexer(), HtmlFormatter(linenos=True, cssclass="source")
        )
        highlighted_script_for_copy = highlight(
            script_content, BashLexer(), HtmlFormatter(linenos=False, cssclass="source-no-lines")
        )
        pygments_css = HtmlFormatter(style="friendly").get_style_defs(".source")

        return HTMXTemplate(
            template_name="partials/highlighted_script.html",
            context={
                "highlighted_script": highlighted_script_with_lines,
                "highlighted_script_for_copy": highlighted_script_for_copy,
                "pygments_css": pygments_css,
            },
        )
