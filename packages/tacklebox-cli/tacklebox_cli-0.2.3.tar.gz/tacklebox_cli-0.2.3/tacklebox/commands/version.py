from importlib.metadata import version

from rich import print
from typer import Typer

from tacklebox import __version__

app = Typer()


def _get_package_version(package_name: str) -> str | None:
    """Safely retrieve package versions with error handling."""
    try:
        return version(package_name)
    except ImportError:
        return None


@app.command(name="version")
def show_versions() -> None:
    """Shows versions of the tacklebox, zipline-py, desktop-notifier, platformdirs, aiohttp, typer, click, and rich packages."""
    versions: dict[str, str | None] = {
        "tacklebox": __version__,
        "zipline-py": _get_package_version("zipline-py"),
        "desktop-notifier": _get_package_version("desktop-notifier"),
        "platformdirs": _get_package_version("platformdirs"),
        "aiohttp": _get_package_version("aiohttp"),
        "typer": _get_package_version("typer"),
        "click": _get_package_version("click"),
        "rich": _get_package_version("rich"),
    }

    output = "\n".join(
        f"[blue]{name}:[/blue] {f'[bright_cyan]{version}[/bright_cyan]' if version else '[bold red]Not available[/bold red]'}"
        for name, version in versions.items()
    )

    print(output)


if __name__ == "__main__":
    app()
