import os
import platform
import shutil
import subprocess
import sys
from base64 import b64encode
from typing import Annotated, Literal

from typer import Argument, Exit, Option, Typer, echo

from tacklebox.utils import get_environment

app = Typer()


def _try_command(data: str, cmd: list[str], verbose: bool = False) -> bool:
    """Attempt to run a command using subprocess.

    Args:
        data (str): The data to send the process after it is invoked.
        cmd (list[str]): The command to invoke.
        verbose (bool, optional): Print some additional information during execution. Defaults to False.

    Returns:
        bool: Whether or not the command was successful.
    """
    if shutil.which(cmd[0]) is None:
        if verbose:
            echo(f"{cmd[0]} not found in PATH.", err=True)
        return False

    if cmd[0] == "clip.exe":
        encoder = "utf-16le"
    else:
        encoder = "utf-8"

    try:
        result = subprocess.run(
            cmd,
            input=data.encode(encoder),
            stdout=(None if verbose else subprocess.DEVNULL),
            stderr=(None if verbose else subprocess.DEVNULL),
            env=get_environment(),
            timeout=30,
        )
        if result.returncode == 0:
            if verbose:
                echo(f"Copied using {' '.join(cmd)}")
            return True
    except subprocess.TimeoutExpired:
        if verbose:
            echo(f"{cmd[0]} timed out", err=True)
    except OSError as e:
        if verbose:
            echo(f"{cmd[0]} execution failed: {e}", err=True)
    return False


def copy_with_tooling(data: str, copy_command: list[str] | None = None, verbose: bool = False) -> bool:
    """Attempt to copy the input data to the system clipboard using system tools.

    This function uses the following tools, and will try them in the order stated:
    - The content of the `copy_command` argument.
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
        - `clip.exe`

    Args:
        data (str): The data to copy to the system clipboard.
        copy_command (list[str] | None): A user-provided command to try before running anything else.
        verbose (bool, optional): Prints some extra information during execution. Defaults to False.

    Returns:
        bool: Whether or not copying was successful.
    """
    if copy_command:
        if success := _try_command(data, copy_command, verbose):
            return success

    system = platform.system().lower()

    tools: dict[str, list[list[str]]] = {
        "wayland": [["wl-copy"], ["copyq", "add", "-"]],
        "x11": [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"], ["copyq", "add", "-"]],
        "darwin": [["reattach-to-user-namespace", "pbcopy"], ["pbcopy"]],
        "windows": [["clip.exe"]],
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
                    echo("Detected Windows Subsystem for Linux.")
                commands.extend(tools["windows"])

            protocol: Literal["wayland", "x11"] | None = (
                "wayland" if "WAYLAND_DISPLAY" in get_environment() else ("x11" if "DISPLAY" in get_environment() else None)
            )
            if verbose:
                echo(f"Detected display protocol: {protocol}")

            match protocol:
                case "wayland":
                    commands.extend(tools["wayland"])
                case "x11":
                    commands.extend(tools["x11"])
                case _:
                    if verbose:
                        echo(
                            "Unknown display protocol: neither WAYLAND_DISPLAY nor DISPLAY set.",
                            err=True,
                        )
                    return False
        case "darwin":
            commands.extend(tools["darwin"])
        case "windows":
            commands.extend(tools["windows"])
        case _:
            if verbose:
                echo(f"No suitable clipboard tool found for platform '{system}'", err=True)
            return False

    for cmd in commands:
        if success := _try_command(data, cmd, verbose):
            return success
    return False


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


@app.command("clip")
def clipboard(
    data: Annotated[
        str | None,
        Argument(
            help="The data to copy to the clipboard. Reads from stdin if this is not provided.",
        ),
    ] = None,
    copy_command: Annotated[str | None, Option(..., "--copy-command", "-c", help="A command to try first instead of the hardcoded system defaults.")] = None,
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
    """Read from stdin and copy to the system clipboard using wl-copy or OSC 52."""
    if not data:
        data = sys.stdin.read()

    if not data:
        echo("No input received from stdin.", err=True)
        raise Exit(code=1)

    if verbose:
        echo(
            message="\n".join(
                (
                    f"Platform: {platform.system()}",
                    f"TERM: {os.environ.get('TERM')}",
                    f"TMUX: {'present' if 'TMUX' in os.environ else 'absent'}",
                    f"SCREEN: {'present' if os.environ.get('TERM', '').startswith('screen') else 'absent'}",
                )
            )
        )

    command = None
    if copy_command:
        command = copy_command.split(" ")

    if success := copy_with_tooling(data, command, verbose):
        return

    ssh = "SSH_CONNECTION" in os.environ

    if ssh or not success:
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


if __name__ == "__main__":
    app()
