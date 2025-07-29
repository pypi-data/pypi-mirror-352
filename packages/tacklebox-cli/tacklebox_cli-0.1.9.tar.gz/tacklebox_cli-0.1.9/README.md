# tacklebox-cli

[<img alt="Actions Status" src="https://c.csw.im/cswimr/tacklebox/badges/workflows/actions.yml/badge.svg?style=plastic">](https://c.csw.im/cswimr/tacklebox/actions?workflow=actions.yml)
[<img alt="PyPI - Version" src="https://img.shields.io/pypi/v/tacklebox-cli?style=plastic">](https://pypi.org/project/tacklebox-cli/)
[<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/tacklebox-cli?style=plastic">](https://pypi.org/project/tacklebox-cli/)
[<img alt="PyPI - License" src="https://img.shields.io/pypi/l/tacklebox-cli?style=plastic">](https://c.csw.im/cswimr/tacklebox/src/branch/main/LICENSE/)  
tacklebox-cli offers a suite of useful CLI tools.

## Usage

### tacklebox clip

Cross-platform clipboard copying tool. Uses `wl-copy`, `xclip`, or `xsel` on Linux, `pbcopy` on MacOS, `clip` on Windows, and [OSC 52](https://www.reddit.com/r/vim/comments/k1ydpn/a_guide_on_how_to_copy_text_from_anywhere/) escape codes when operating over SSH or when no other tools are available.

```bash
echo "a" | tr -d '\n' | tacklebox clip
```

### tacklebox spectacle (Linux only)

Uses the [zipline.py](https://pypi.org/project/zipline-py/) library alongside KDE's [Spectacle](https://invent.kde.org/plasma/spectacle) application to take a screenshot or screen recording and automatically upload it to a [Zipline](https://github.com/diced/zipline) instance. This automatically reads Spectacle's configuration files to determine file formats.

```bash
tacklebox spectacle | tr -d '\n' | tacklebox clip

# or to record a video
tacklebox spectacle --record | tr -d '\n' | tacklebox clip
```

### tacklebox zipline

Wraps the [zipline.py](https://pypi.org/project/zipline-py/) CLI. See the [zipline.py CLI documentation](https://ziplinepy.readthedocs.io/en/latest/cli.html) for more information.
