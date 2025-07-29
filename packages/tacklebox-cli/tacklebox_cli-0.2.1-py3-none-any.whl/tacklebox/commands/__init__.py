import platform

from typer import Typer
from zipline.cli.entrypoint import app as zipline

from .clipboard import app as clipboard
from .version import app as version

commands: list[Typer] = [clipboard, version, zipline]

if platform.system() == "Linux":
    from .spectacle import app as spectacle

    commands.append(spectacle)
