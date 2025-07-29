import os
import platform
import shutil
import subprocess
import sys
from base64 import b64encode
from enum import Enum
from typing import Annotated, Literal

from typer import Argument, Exit, Option, Typer, echo

from tacklebox.utils import get_environment

app = Typer()


class ClipboardMode(str, Enum):
    COPY = "Copied"
    PASTE = "Pasted"


def _try_command(mode: ClipboardMode, cmd: list[str], verbose: bool = False, data: str | None = None) -> tuple[bool, str | None]:
    """Attempt to run a command using subprocess.

    Args:
        mode (ClipboardMode): Determines some stdout stuff.
        cmd (list[str]): The command to invoke.
        verbose (bool, optional): Print some additional information during execution. Defaults to False.
        data (str, optional): The data to send the process after it is invoked.

    Returns:
        bool: Whether or not the command was successful.
    """
    if shutil.which(cmd[0]) is None:
        if verbose:
            echo(f"{cmd[0]} not found in PATH.", err=True)
        return False, None

    if cmd[0] == "clip.exe":
        encoder = "utf-16le"
    else:
        encoder = "utf-8"

    try:
        result = subprocess.run(
            cmd,
            input=data.encode(encoder) if data else None,
            stderr=None if verbose else subprocess.DEVNULL,
            env=get_environment(),
            timeout=30,
        )
        if result.returncode == 0:
            if verbose:
                echo(f"{mode.value} using {' '.join(cmd)}", err=True)
            return True, result.stdout.decode(encoder) if result.stdout else None
    except subprocess.TimeoutExpired:
        if verbose:
            echo(f"{cmd[0]} timed out", err=True)
    except OSError as e:
        if verbose:
            echo(f"{cmd[0]} execution failed: {e}", err=True)
    return False, None


def use_tooling(
    mode: ClipboardMode, command: list[str] | None = None, verbose: bool = False, data: str | None = None
) -> tuple[bool, str | None]:
    """Attempt to manipulate the system clipboard using system tools.

    This function uses the following tools, and will try them in the order stated:
    - The content of the `command` argument.
    - If `mode == ClipboardMode.COPY`:
        - Linux (Wayland):
            - `wl-copy`
            - `copyq add -`
        - Linux (X11):
            - `xclip -selection clipboard`
            - `xsel --clipboard --input`
            - `copyq add -`
        - MacOS:
            - `reattach-to-user-namespace pbcopy`
            - `pbcopy`
        - Windows:
            - `win32yank.exe -i`
            - `clip.exe`
    - If `mode == ClipboardMode.PASTE`:
        - Linux (Wayland):
            - `wl-paste --no-newline`
            - `copyq read 0`
        - Linux (X11):
            - `xclip -selection clipboard -o`
            - `xsel --clipboard --output`
            - `copyq read 0`
        - MacOS:
            - `reattach-to-user-namespace pbpaste`
            - `pbpaste`
        - Windows:
            - `win32yank.exe -o`

    Args:
        mode (ClipboardMode): Whether or not to copy or paste.
        command (list[str] | None): A user-provided command to try before running anything else.
        verbose (bool, optional): Prints some extra information during execution. Defaults to False.
        data (str, optional): The data to copy to the system clipboard, when `mode == ClipboardMode.COPY`.

    Returns:
        bool: Whether or not copying was successful.
        str: The content that was in the clipboard.
    """
    if command:
        if success := _try_command(mode, command, verbose, data):
            return success

    system = platform.system().lower()

    tools: dict[ClipboardMode, dict[str, list[list[str]]]] = {
        ClipboardMode.COPY: {
            "wayland": [["wl-copy"], ["copyq", "add", "-"]],
            "x11": [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"], ["copyq", "add", "-"]],
            "darwin": [["reattach-to-user-namespace", "pbcopy"], ["pbcopy"]],
            "windows": [["win32yank.exe", "-i"], ["clip.exe"]],
        },
        ClipboardMode.PASTE: {
            "wayland": [["wl-paste", "--no-newline"], ["copyq", "read", "0"]],
            "x11": [["xclip", "-selection", "clipboard", "-o"], ["xsel", "--clipboard", "--output"], ["copyq", "read", "0"]],
            "darwin": [["reattach-to-user-namespace", "pbpaste"], ["pbpaste"]],
            "windows": [["win32yank.exe", "-o"]],
        },
    }

    commands: list[list[str]] = []
    match system:
        case "linux":
            in_wsl = False
            try:
                with open("/proc/version", "r") as pv:
                    in_wsl = "microsoft" in pv.read().lower()
            except Exception:
                in_wsl = False

            if in_wsl:
                if verbose:
                    echo("Detected Windows Subsystem for Linux.", err=True)
                commands.extend(tools[mode]["windows"])

            protocol: Literal["wayland", "x11"] | None = (
                "wayland" if "WAYLAND_DISPLAY" in get_environment() else ("x11" if "DISPLAY" in get_environment() else None)
            )
            if verbose:
                echo(f"Detected display protocol: {protocol}", err=True)

            match protocol:
                case "wayland":
                    commands.extend(tools[mode]["wayland"])
                case "x11":
                    commands.extend(tools[mode]["x11"])
                case _:
                    if not in_wsl:
                        if verbose:
                            echo(
                                "Unknown display protocol: neither WAYLAND_DISPLAY nor DISPLAY set.",
                                err=True,
                            )
                        return False, None

        case "darwin":
            commands.extend(tools[mode]["darwin"])
        case "windows":
            commands.extend(tools[mode]["windows"])
        case _:
            if verbose:
                echo(f"No suitable clipboard tool known for platform '{system}'", err=True)
            return False, None

    if verbose:
        echo("\nAttempting commands:\n" + "\n".join(" ".join(cmd) for cmd in commands) + "\n", err=True)
    for cmd in commands:
        if (success := _try_command(mode, cmd, verbose, data))[0]:
            return success
    return False, None


def encode_osc52(data: str, verbose: bool = False) -> str:
    """Encode a string into an [OCS 52](https://www.reddit.com/r/vim/comments/k1ydpn/a_guide_on_how_to_copy_text_from_anywhere/) string, supporting tmux and screen as well.

    Args:
        data (str): The data to encode.
        verbose (bool, optional): Print additional information during execution. Defaults to False.

    Returns:
        str: The OSC 52 (& base64) encoded data.
    """
    b64_data = b64encode(data.encode("utf-8")).decode("ascii")
    osc_seq = f"\x1b]52;c;{b64_data}\x07"

    if "TMUX" in os.environ:
        if verbose:
            echo("Wrapping OSC 52 for tmux.")
        return f"\x1bPtmux;\x1b{osc_seq}\x1b\\"
    elif os.environ.get("TERM", "").startswith("screen"):
        if verbose:
            echo("Wrapping OSC 52 for screen.")
        return f"\x1bP{osc_seq}\x1b\\"
    else:
        if verbose:
            echo("Using plain OSC 52.")
        return osc_seq


def _maybe_print_environment_information(verbose: bool) -> None:
    if verbose:
        echo(
            (
                f"Platform: {platform.system()}\n"
                f"TERM: {os.environ.get('TERM')}\n"
                f"TMUX: {'present' if 'TMUX' in os.environ else 'absent'}\n"
                f"SCREEN: {'present' if os.environ.get('TERM', '').startswith('screen') else 'absent'}"
            ),
            err=True,
        )


@app.command("copy")
@app.command("clip", deprecated=True, hidden=True, epilog="Consider using `tacklebox copy` instead.")
def copy(
    data: Annotated[
        str | None,
        Argument(
            help="The data to copy to the clipboard. Reads from stdin if this is not provided.",
        ),
    ] = None,
    trim: Annotated[
        bool, Option(..., "--trim", "-t", help="Remove trailing newlines from the input before copying it to the clipboard.")
    ] = False,
    copy_command: Annotated[
        str | None, Option(..., "--copy-command", "-c", help="A command to try first instead of the hardcoded system defaults.")
    ] = None,
    verbose: Annotated[
        bool,
        Option(
            ...,
            "--verbose",
            "-v",
            help="Print some additional information during execution.",
        ),
    ] = False,
) -> None:
    """Copy to the system clipboard."""
    if not data:
        data = sys.stdin.read()

    if not data:
        echo("No input received from stdin.", err=True)
        raise Exit(code=1)

    if trim:
        data = data.rstrip("\r\n")

    _maybe_print_environment_information(verbose)

    command = None
    if copy_command:
        command = copy_command.split(" ")

    if use_tooling(ClipboardMode.COPY, command, verbose, data):
        return

    if verbose:
        echo("Clipboard tools failed; trying OSC 52...", err=True)

    osc = encode_osc52(data, verbose)
    try:
        with open("/dev/tty", "w") as tty:
            tty.write(osc)
        if verbose:
            echo("Copied using OSC 52.")
    except Exception as e:
        echo(f"OSC 52 failed: {e}", err=True)
        raise Exit(code=1)


@app.command("paste")
def paste(
    paste_command: Annotated[
        str | None, Option(..., "--paste-command", "-c", help="A command to try first instead of the hardcoded system defaults.")
    ] = None,
    trim: Annotated[bool, Option(..., "--trim", "-t", help="Remove trailing newlines from the clipboard entry before pasting it.")] = False,
    verbose: Annotated[
        bool,
        Option(
            ...,
            "--verbose",
            "-v",
            help=("Print some additional information during execution. This WILL mangle the output, so only use this for debugging."),
        ),
    ] = False,
) -> None:
    """Paste from the system clipboard."""
    _maybe_print_environment_information(verbose)

    command = None
    if paste_command:
        command = paste_command.split(" ")

    if (output := use_tooling(ClipboardMode.PASTE, command, verbose))[0]:
        string = output[1]
        if trim and string is not None:
            string = string.rstrip("\r\n")

        echo(string)
        return

    echo(f"Paste command failed!\n{output}", err=True)
    exit(code=1)


if __name__ == "__main__":
    app()
