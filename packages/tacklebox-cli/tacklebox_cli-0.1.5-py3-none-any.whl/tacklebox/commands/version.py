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
    """Shows versions of the tacklebox, typer, click, rich, and pyside6 packages."""
    versions: dict[str, str | None] = {
        "tacklebox": __version__,
        "typer": _get_package_version("typer"),
        "click": _get_package_version("click"),
        "rich": _get_package_version("rich"),
        "pyside6": _get_package_version("pyside6"),
    }

    output = "\n".join(
        f"[blue]{name}:[/blue] {f'[bright_cyan]{version}[/bright_cyan]' if version else '[bold red]Not available[/bold red]'}"
        for name, version in versions.items()
    )

    print(output)


if __name__ == "__main__":
    app()
