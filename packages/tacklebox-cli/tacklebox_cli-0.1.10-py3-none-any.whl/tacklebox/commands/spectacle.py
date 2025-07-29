import asyncio
import configparser
import platform
import subprocess
import tempfile
from enum import IntEnum
from pathlib import Path
from shutil import which
from typing import Annotated

from desktop_notifier import DEFAULT_SOUND, Attachment, DesktopNotifier, Urgency
from platformdirs import user_config_dir
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from typer import Exit, Option, Typer
from zipline.cli.commands._handling import handle_api_errors
from zipline.client import Client
from zipline.models import FileData

from tacklebox import sync

if not platform.system() == "Linux":
    print("Spectacle is only supported on Linux.")
    raise Exit(code=1)

app = Typer()


class VideoFormats(IntEnum):
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


def _read_spectacle_config() -> tuple[str, VideoFormats]:
    """Read the Spectacle config file and return the configured file formats."""
    path = Path(user_config_dir("spectaclerc"))
    if not path.exists():
        return "png", VideoFormats.WEBM

    config = configparser.ConfigParser()
    config.read(path)

    preferred_image_format = config.get("ImageSave", "preferredImageFormat", fallback="png").lower()

    preferred_video_format = VideoFormats(config.getint("VideoSave", "preferredVideoFormat", fallback=0))

    return preferred_image_format, preferred_video_format


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
    record: Annotated[bool, Option(..., "--record", help="Record a video instead of taking a screenshot.")] = False,
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

        command: list[str] = ["spectacle", "--nonotify", "--background", "--pointer", "--copy-image", "--output", str(file_path)]

        if record:
            command.append("--record=region")
        else:
            command.append("--region")

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
        file_data = FileData(
            data=file_path,
        )

        progress.update(task, description="Uploading file...", total=None)
        async with Client(server_url, token) as client:
            try:
                uploaded_file = await client.upload_file(
                    payload=file_data,
                    text_only=True,
                )
            except Exception as exception:
                handle_api_errors(exception, server_url)

        print(uploaded_file)

        await notifier.send(
            title="File Uploaded!",
            message=f"File successfully uploaded to {uploaded_file}",
            attachment=Attachment(path=file_path),
            urgency=Urgency.Low,
            timeout=5,
            sound=DEFAULT_SOUND,
        )

        file_path.unlink(missing_ok=True)


if __name__ == "__main__":
    app()
