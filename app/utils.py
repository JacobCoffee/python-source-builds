"""App-wide utilities."""

from pathlib import Path


def get_template_directories() -> list[str]:
    """Recurses throughout the app structure to find directories named "templates".

    Returns:
        list[str]: List of template directories.
    """
    current_dir = Path(__file__).parent
    template_dirs = list(current_dir.rglob("templates"))
    return [str(template_dir) for template_dir in template_dirs]
