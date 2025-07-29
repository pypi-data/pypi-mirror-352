# tacklebox-cli

tacklebox-cli offers a suite of useful CLI tools.

## Usage

### tacklebox clip

Cross-platform clipboard copying tool. Uses `wl-copy`, `xclip`, or `xsel` on Linux, `pbcopy` on MacOS, `clip` on Windows, and [OSC 52](https://www.reddit.com/r/vim/comments/k1ydpn/a_guide_on_how_to_copy_text_from_anywhere/) escape codes when operating over SSH or when no other tools are available.

```bash
echo "a" | tr -d '\n' | tacklebox clip
```

### tacklebox spectacle (Linux only)

Uses the [zipline.py](https://pypi.org/project/zipline-py/) CLI alongside KDE's [Spectacle](https://invent.kde.org/plasma/spectacle) application to take a screenshot or screen recording and automatically upload it to a [Zipline](https://github.com/diced/zipline) instance. This automatically reads Spectacle's configuration files to determine file formats.

```bash
tacklebox spectacle | tr -d '\n' | tacklebox clip

# or to record a video
tacklebox spectacle --record | tr -d '\n' | tacklebox clip
```

### tacklebox zipline

Wraps the [zipline.py](https://pypi.org/project/zipline-py/) CLI. See that project for documentation.
