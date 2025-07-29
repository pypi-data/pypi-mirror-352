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

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL if not verbose else None,
            stderr=subprocess.DEVNULL if not verbose else None,
            env=get_environment(),
        )
        process.communicate(input=data.encode("utf-8"))

        if process.returncode == 0:
            if verbose:
                echo(f"Copied using {' '.join(cmd)}")
            return True
    except Exception as e:
        if verbose:
            echo(f"{cmd[0]} failed: {e}", err=True)

    return False


def copy_with_tooling(data: str, verbose: bool = False) -> bool:
    """Attempt to copy the input data to the system clipboard using system tools.

    This function uses the following tools:
    - Linux (Wayland):
        - `wl-copy`
    - Linux (X11):
        - `xclip -selection -clipboard`
        - `xsel --clipboard --input`
    - MacOS:
        - `pbcopy`
    - Windows:
        - `clip`

    Args:
        data (str): The data to copy to the system clipboard.
        verbose (bool, optional): Prints some extra information during execution. Defaults to False.

    Returns:
        bool: Whether or not copying was successful.
    """
    system = platform.system()

    if system == "Linux":
        protocol: Literal["wayland", "x11"] | None = (
            "wayland" if "WAYLAND_DISPLAY" in get_environment() else ("x11" if "DISPLAY" in get_environment() else None)
        )

        if verbose:
            echo(f"Detected display protocol: {protocol}")

        if protocol == "wayland":
            if _try_command(data, ["wl-copy"], verbose):
                return True
        elif protocol == "x11":
            for tool in [
                ["xclip", "-selection", "clipboard"],
                ["xsel", "--clipboard", "--input"],
            ]:
                if _try_command(data, tool, verbose):
                    return True
        else:
            if verbose:
                echo(
                    "Unknown display protocol: neither WAYLAND_DISPLAY nor DISPLAY set.",
                    err=True,
                )
        return False

    elif system == "Darwin":
        return _try_command(data, ["pbcopy"], verbose)

    elif system == "Windows":
        return _try_command(data, ["clip"], verbose)

    if verbose:
        echo(f"No suitable clipboard tool found for platform {system}", err=True)
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
    verbose: Annotated[
        bool,
        Option(
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

    success = copy_with_tooling(data, verbose)
    if success:
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
