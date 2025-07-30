import asyncio
import configparser
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from enum import Enum, IntEnum
from pathlib import Path
from shutil import which
from typing import Annotated

from desktop_notifier import DEFAULT_SOUND, Attachment, DesktopNotifier, Urgency
from platformdirs import user_config_dir
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from typer import Exit, Option, Typer
from zipline.cli.commands._handling import handle_api_errors
from zipline.cli.commands.upload import _complete_format  # pyright: ignore[reportPrivateUsage]
from zipline.client import Client, FileData, NameFormat

from tacklebox import sync

if not platform.system() == "Linux":
    print("Spectacle is only supported on Linux.")
    raise Exit(code=1)

app = Typer()


class VideoFormat(IntEnum):
    """Because Spectacle is weird and doesn't just use file extensions for storing video formats 😭"""

    WEBM = 0
    MP4 = 2
    WEBP = 4
    GIF = 8

    @property
    def ext(self) -> str:
        return "." + self.__str__()

    def __str__(self) -> str:
        return self.name.lower()


def _read_spectacle_config() -> tuple[str, VideoFormat]:
    """Read the Spectacle config file and return the configured file formats."""
    path = Path(user_config_dir("spectaclerc"))
    if not path.exists():
        return "png", VideoFormat.WEBM

    config = configparser.ConfigParser()
    config.read(path)

    preferred_image_format = config.get("ImageSave", "preferredImageFormat", fallback="png").lower()

    preferred_video_format = VideoFormat(config.getint("VideoSave", "preferredVideoFormat", fallback=0))

    return preferred_image_format, preferred_video_format


class SpectacleMode(str, Enum):
    REGION = "region"
    DESKTOP = "desktop"
    MONITOR = "monitor"
    WINDOW = "window"
    ACTIVEWINDOW = "activewindow"
    TRANSIENT = "transient"

    @classmethod
    def complete_format(cls, incomplete: str) -> list[tuple[str, str] | str]:
        """Generate autocompletion strings for Typer."""
        completions: list[tuple[str, str] | str] = []
        for mode in SpectacleMode:
            if mode.value.startswith(incomplete):
                completions.append((mode, mode.completion_string) if mode.completion_string else mode)
        return completions

    @property
    def completion_string(self) -> str | None:
        argument = self.get_argument()
        record_argument = self.get_argument(True)

        completion_strings: dict[SpectacleMode, str] = {
            SpectacleMode.REGION: f"Capture a retangular region of the desktop. ({argument} | {record_argument})",
            SpectacleMode.DESKTOP: f"Capture the entire desktop (default). When recording, this will capture only the current monitor. ({argument} | {record_argument})",
            SpectacleMode.MONITOR: f"Capture the current monitor. ({argument} | {record_argument})",
            SpectacleMode.WINDOW: f"Capture the window currently under the cursor, including parents of pop-up menus. ({argument} | {record_argument})",
            SpectacleMode.ACTIVEWINDOW: f"Capture the currently selected window. ({argument} | {record_argument})",
            SpectacleMode.TRANSIENT: f"Capture the window currently under the cursor, excluding parents of pop-up menus. ({argument} | {record_argument})",
        }

        return completion_strings.get(self, None)

    def get_argument(self, record: bool = False) -> str:
        match self:
            case SpectacleMode.REGION:
                return "--record=region" if record else "--region"
            case SpectacleMode.DESKTOP:
                return "--record=screen" if record else "--fullscreen"
            case SpectacleMode.MONITOR:
                return "--record=screen" if record else "--current"
            case SpectacleMode.WINDOW:
                return "--record=window" if record else "--windowundercursor"
            case SpectacleMode.ACTIVEWINDOW:
                return "--record=window" if record else "--activewindow"
            case SpectacleMode.TRANSIENT:
                return "--record=window" if record else "--transientonly"


@app.command(name="spectacle")
@sync
async def spectacle(
    server_url: Annotated[
        str,
        Option(
            ...,
            "--server",
            "-s",
            help="Specify the URL to your Zipline instance.",
            envvar="ZIPLINE_SERVER",
            prompt=True,
        ),
    ],
    token: Annotated[
        str,
        Option(
            ...,
            "--token",
            "-t",
            help="Specify a token used for authentication against your chosen Zipline instance.",
            envvar="ZIPLINE_TOKEN",
            prompt=True,
            hide_input=True,
        ),
    ],
    print_object: Annotated[
        bool,
        Option(
            ...,
            "--object/--text",
            "-o/-O",
            default_factory=lambda: bool(sys.stdout.isatty()),
            help=(
                "Specify how to format the output. If --text (or piped), "
                "you'll get a link to the uploaded file; if --object (or on a TTY), "
                "you'll get the raw Python object."
            ),
            envvar="ZIPLINE_PRINT_OBJECT",
        ),
    ],
    mode: Annotated[
        SpectacleMode,
        Option(..., "--mode", "-M", help="Specify what mode Spectacle should be launched in.", autocompletion=SpectacleMode.complete_format),
    ] = SpectacleMode.DESKTOP,
    record: Annotated[
        bool, Option(..., "--record", "-r", help="Specify whether or not to record a video instead of taking a screenshot.")
    ] = False,
    format: Annotated[
        NameFormat | None,
        Option(
            ...,
            "--format",
            "-f",
            help="Specify what format Zipline should use to generate a link for this file.",
            autocompletion=_complete_format,
        ),
    ] = None,
    compression_percent: Annotated[
        int,
        Option(
            ...,
            "--compression-percent",
            "-c",
            help="Specify how much this file should be compressed.",
        ),
    ] = 0,
    expiry: Annotated[
        datetime | None,
        Option(
            ...,
            "--expiry",
            "-e",
            help=(
                "Specify when this file should expire.\n"
                "When this time expires, the file will be deleted from the Zipline instance.\n"
                "This argument uses your system's local timezone, not UTC dates."
            ),
        ),
    ] = None,
    password: Annotated[
        str | None,
        Option(
            ...,
            "--password",
            "-p",
            help="Specify a password for this file. Viewing this file from Zipline will then require having this password.",
        ),
    ] = None,
    max_views: Annotated[
        int | None,
        Option(
            ...,
            "--max-views",
            "-m",
            help="Specify how many times this file can be viewed before it will be automatically deleted.",
        ),
    ] = None,
    override_name: Annotated[
        str | None,
        Option(
            ...,
            "--name",
            "-n",
            help="Specify the name to give this file in Zipline. This overrides the --format option, if provided.",
        ),
    ] = None,
    folder: Annotated[
        str | None,
        Option(
            ...,
            "--folder",
            "-F",
            help="Specify what folder the file should be added to after it is uploaded.",
        ),
    ] = None,
    override_domain: Annotated[
        str | None,
        Option(
            ...,
            "--domain",
            "-d",
            help="Specify what domain should be used instead of the Zipline instance's core domain.",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        Option(
            ...,
            "--verbose",
            "-v",
            help="Specify whether or not the application should print tracebacks from exceptions to the console. If the application encounters an exception it doesn't expect, it will always be printed to the console regardless of this option.",
            envvar="ZIPLINE_VERBOSE",
        ),
    ] = False,
) -> None:
    """Take a screenshot or record a video using Spectacle, then upload it to a remote Zipline instance using zipline.py."""
    notifier = DesktopNotifier(app_name="Tacklebox - Spectacle")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="Setting up...", total=None)

        if not which("spectacle"):
            print("spectacle is not installed!")
            raise Exit(code=1)

        image_format, video_format = _read_spectacle_config()
        if record:
            ext = video_format.ext
        else:
            ext = "." + image_format

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        file_path = Path(temp_file.name)
        temp_file.close()

        command: list[str] = [
            "spectacle",
            "--nonotify",
            "--background",
            "--pointer",
            mode.get_argument(record),
            "--copy-image",
            "--output",
            str(file_path),
        ]

        proc = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            if file_path.exists():
                file_path.unlink(missing_ok=True)
            raise subprocess.CalledProcessError(proc.returncode or 1, command, output=stdout, stderr=stderr)

        if not file_path.stat().st_size:
            file_path.unlink(missing_ok=True)
            raise FileNotFoundError("The file was not created properly.")

        progress.update(task, description="Reading file...", total=None)
        file_data = FileData(data=file_path)

        progress.update(task, description="Uploading file...", total=None)
        async with Client(server_url, token) as client:
            try:
                uploaded_file = await client.upload_file(
                    payload=file_data,
                    compression_percent=compression_percent,
                    expiry=expiry.astimezone(tz=timezone.utc) if expiry else None,
                    format=format,
                    password=password,
                    max_views=max_views,
                    override_name=override_name,
                    override_domain=override_domain,
                    folder=folder,
                )
            except Exception as exception:
                handle_api_errors(exception, server_url, traceback=verbose)

        if print_object:
            print(uploaded_file)
        else:
            print(uploaded_file.files[0].url)

        await notifier.send(
            title="File Uploaded!",
            message=f"File successfully uploaded to {uploaded_file.files[0].url}",
            attachment=Attachment(path=file_path),
            urgency=Urgency.Low,
            timeout=5,
            sound=DEFAULT_SOUND,
        )

        file_path.unlink(missing_ok=True)


if __name__ == "__main__":
    app()
