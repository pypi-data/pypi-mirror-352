import asyncio
import platform

from typer import Typer

from tacklebox.commands import commands

# fmt: off
if platform.system() == "Darwin":
    from rubicon.objc.eventloop import EventLoopPolicy  # pyright: ignore[reportMissingImports, reportUnknownVariableType]

    asyncio.set_event_loop_policy(EventLoopPolicy()) # pyright: ignore[reportUnknownArgumentType]

app = Typer(name="Tacklebox", pretty_exceptions_show_locals=False)


for typer_instance in commands:
    match typer_instance.info.name:
        case "zipline.py":
            app.add_typer(
                typer_instance,
                name="zipline",
                help="Interact with a remote Zipline instance using the zipline.py library's CLI.",
            )
        case _:
            app.add_typer(typer_instance)

if __name__ == "__main__":
    app()
