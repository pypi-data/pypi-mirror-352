import os


def get_environment() -> dict[str, str]:
    env = dict(os.environ)
    env["DIRENV_DISABLE"] = "1"
    return env
