# tacklebox-cli

[<img alt="Actions Status" src="https://c.csw.im/cswimr/tacklebox/badges/workflows/actions.yml/badge.svg?style=plastic">](https://c.csw.im/cswimr/tacklebox/actions?workflow=actions.yml)
[<img alt="PyPI - Version" src="https://img.shields.io/pypi/v/tacklebox-cli?style=plastic">](https://pypi.org/project/tacklebox-cli/)
[<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/tacklebox-cli?style=plastic">](https://pypi.org/project/tacklebox-cli/)
[<img alt="PyPI - License" src="https://img.shields.io/pypi/l/tacklebox-cli?style=plastic">](https://c.csw.im/cswimr/tacklebox/src/branch/main/LICENSE/)  
tacklebox-cli offers a suite of useful CLI tools.

## Usage

### tacklebox copy / paste

Cross-platform clipboard management tool. Uses system tools such as `wl-copy` on Linux Wayland or `clip.exe` on Windows, and [OSC 52](https://www.reddit.com/r/vim/comments/k1ydpn/a_guide_on_how_to_copy_text_from_anywhere/) escape codes when **copying** over SSH or when no other tools are available. See [`copy_with_tooling()`](https://c.csw.im/cswimr/tacklebox/src/branch/main/tacklebox/commands/clipboard.py) for all supported tools.

```bash
$ echo "a" | tacklebox copy --trim && tacklebox paste
a
```

### tacklebox spectacle (Linux only)

Uses the [zipline.py](https://pypi.org/project/zipline-py/) library alongside KDE's [Spectacle](https://invent.kde.org/plasma/spectacle) application to take a screenshot or screen recording and automatically upload it to a [Zipline](https://github.com/diced/zipline) instance. This automatically reads Spectacle's configuration files to determine file formats.

```bash
$ tacklebox spectacle --mode region \ 
    --server "https://zipline.example.com" \ 
    --token "$(cat /file/containing/zipline/token)" \ 
    | tacklebox copy --trim

# or to record a video
$ tacklebox spectacle --mode region --record \ 
    --server "https://zipline.example.com" \ 
    --token "$(cat /file/containing/zipline/token)" \ 
    | tacklebox copy --trim
```

### tacklebox zipline

Wraps the [zipline.py](https://pypi.org/project/zipline-py/) CLI. See the [zipline.py CLI documentation](https://ziplinepy.readthedocs.io/en/latest/cli.html) for more information.
