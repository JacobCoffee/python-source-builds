"""Helper functions for the Python versions applet.

Parts borrowed from https://github.com/python/cpython-devcontainers/blob/main/cpython-ci/get_versions.py/ and Barry Warsaw
"""

import asyncio
import sqlite3
from contextlib import contextmanager
from datetime import UTC, date, datetime

import aiosqlite
import httpx
from litestar.config.app import AppConfig
from packaging import version as pkg_version
from structlog import get_logger

from app.applets.core.schemas import Version

logger = get_logger(__name__)

ACTIVE_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]
PRE_RELEASE = "3.14.0a0"
DATABASE_FILE = "python_versions.db"


@contextmanager
def get_db_connection() -> sqlite3.Connection:
    """Get a database connection.

    Yields:
        A database connection.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def initialize_database() -> None:
    """Initialize the database."""
    logger.debug("initializing database")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS python_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                major INTEGER,
                minor INTEGER,
                patch INTEGER,
                level TEXT,
                status TEXT,
                last_updated TIMESTAMP
            )
        """)


async def start_periodic_update() -> None:
    """Start the periodic update task."""
    logger.debug("starting periodic update task")
    task = asyncio.create_task(periodic_update())
    logger.debug("periodic update task created: %s", task)


async def periodic_update() -> None:
    """Periodically update the Python versions in the database."""
    while True:
        try:
            logger.debug("Running periodic update")
            await fetch_and_update_versions()
            logger.debug("Periodic update completed successfully")
        except Exception:
            logger.exception("Error in periodic update")
        finally:
            logger.debug("Sleeping for 24 hours before next update")
            await asyncio.sleep(24 * 60 * 60)


async def get_tags_from_github() -> list[dict]:
    """Get the Python tags from the GitHub API.

    Returns:
        list[dict]: A list of tags.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.github.com/repos/python/cpython/git/refs/tags",
                timeout=30.0,
                headers={"User-Agent": "Python-Versions-Applet"},
            )

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return []
        except httpx.RequestError as e:
            logger.exception("An error occurred while requesting %s", e.request.url)
            return []
        except Exception:
            logger.exception("An unexpected error occurred")
            return []


async def get_version_eols() -> dict[str, date]:
    """Get the Python version EOL dates from endoflife.date.

    Returns:
        dict[str, date]: A dictionary
    """
    async with httpx.AsyncClient() as client:
        response = await client.get("https://endoflife.date/api/python.json")
        response.raise_for_status()
        data = response.json()
        return {release["cycle"]: date.fromisoformat(release["eol"]) for release in data}


def get_version_from_tags(tags: list[dict]) -> list[pkg_version.Version]:
    """Get the Python versions from the GitHub tags.

    Args:
        tags (list[dict]): A list of tags from the GitHub API.

    Returns:
        list[pkg_version.Version]: A list of Version objects.
    """
    return [
        pkg_version.parse(item.get("ref").replace("refs/tags/v", ""))
        for item in tags
        if item.get("ref", "").startswith("refs/tags/v")
    ]


def get_latest_version(all_versions: list[pkg_version.Version]) -> dict[str, pkg_version.Version]:
    """Get the latest Python versions for each series.

    Args:
        all_versions (list[pkg_version.Version]): A list of Version objects.

    Returns:
        dict[str, pkg_version.Version]: A dictionary of the latest versions.
    """
    latest = {}
    for version in all_versions:
        series = f"{version.major}.{version.minor}"
        if series in latest and latest.get(series) < version or series not in latest:
            latest[series] = version
    return {key: value for key, value in latest.items() if key in ACTIVE_VERSIONS}


async def update_versions_in_db(versions: list[Version]) -> None:
    """Update the Python versions in the database.

    Args:
        versions (list[Version]): A list of Version objects to update.
    """
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.executemany(
            """
            INSERT OR REPLACE INTO python_versions
            (name, major, minor, patch, level, status, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            [(v.name, v.major, v.minor, v.patch, v.level, v.status, v.last_updated.isoformat()) for v in versions],
        )
        await db.commit()


async def get_versions_from_db() -> list[Version]:
    """Get the latest Python versions from the database.

    Returns:
        list[Version]: A list of Version objects.
    """
    async with aiosqlite.connect(DATABASE_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM python_versions
            ORDER BY major DESC, minor DESC, patch DESC
        """) as cursor:
            rows = await cursor.fetchall()
    return [
        Version(
            name=row["name"],
            major=row["major"],
            minor=row["minor"],
            patch=row["patch"],
            level=row["level"],
            status=row["status"],
            last_updated=datetime.fromisoformat(row["last_updated"]),
        )
        for row in rows
    ]


async def fetch_and_update_versions() -> None:
    """Fetch the latest Python versions from GitHub and update the database."""
    try:
        gh_response = await get_tags_from_github()
        all_versions = get_version_from_tags(gh_response)
        latest_versions = get_latest_version(all_versions)
        version_eols = await get_version_eols()

        today = datetime.now(tz=UTC).date()
        versions_to_update = []

        for key, value in latest_versions.items():
            if not value.is_prerelease:
                eol = version_eols.get(key)
                if eol is None or today <= eol:
                    status = "feature" if eol is None else "bugfix"
                    versions_to_update.append(
                        Version(
                            name=f"Python {value.major}.{value.minor}.{value.micro}",
                            major=value.major,
                            minor=value.minor,
                            patch=value.micro,
                            level="final",
                            status=status,
                            last_updated=datetime.now(UTC),
                        )
                    )

        # Add the pre-release version if specified
        if PRE_RELEASE:
            pre_version = pkg_version.parse(PRE_RELEASE)
            versions_to_update.append(
                Version(
                    name=f"Python {pre_version.major}.{pre_version.minor}.{pre_version.micro}",
                    major=pre_version.major,
                    minor=pre_version.minor,
                    patch=pre_version.micro,
                    level="alpha",
                    status="prerelease",
                    last_updated=datetime.now(UTC),
                )
            )

        logger.debug("Updating database with %s versions", len(versions_to_update))
        await update_versions_in_db(versions_to_update)
    except Exception:
        logger.exception("Error in fetch_and_update_versions")
        raise


async def get_python_versions() -> list[Version]:
    """Get the latest Python versions from the database or fetch them from GitHub if the database is empty or outdated.

    Returns:
        list[Version]: A list of Version objects.
    """
    db_versions = await get_versions_from_db()

    if not db_versions or (datetime.now(UTC) - db_versions[0].last_updated).days > 1:
        logger.info("fetching python versions")
        await fetch_and_update_versions()
        db_versions = await get_versions_from_db()

    return db_versions


def generate_app_config(app_config: AppConfig) -> AppConfig:
    """Configure the Python versions module.

    This function is used as an on_app_init handler for Litestar.

    Args:
        app_config: The Litestar AppConfig instance.

    Returns:
        AppConfig: The updated AppConfig instance.
    """
    initialize_database()
    app_config.on_startup.append(start_periodic_update)
    return app_config
