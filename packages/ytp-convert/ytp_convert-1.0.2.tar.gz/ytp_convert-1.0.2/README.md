# 🎵 ytp-convert

[![PyPI version](https://badge.fury.io/py/ytp-convert.svg)](https://pypi.org/project/ytp-convert/)

**ytp-convert** is a Python-based command-line tool that downloads entire YouTube playlist and combines the content into a single media file.

Enjoy listening to your favorite playlists as one contiguous audio file, and skip advertisements. 

---

## 🚀 Features

- Downloads entire **YouTube playlists**
- Merges all tracks into one file
- Cross-platform (Windows, macOS, Linux)
- Built with `yt-dlp`, `pydub`, and `ffmpeg`

---

## 📦 Installation

Installation of Python is required.  You can install the tool from [PyPI](https://pypi.org/project/ytp-convert/)

```bash
pip install ytp-convert
```

⚠️ ffmpeg is required — see below.

## Usage

| Option             | Description                                              |
| ------------------ | -------------------------------------------------------- |
| `url` (positional) | The YouTube playlist URL                                 |
| `-o`, `--output`   | Output filename (must end in `.mp3`) |
| `-f`, `--force`    | Whether to skip or abort on failed video downloads       |

```bash
ytp-convert "https://youtube.com/playlist?list=..." -o my_playlist.mp3
```

For more help, use
```
ytp-convert --help
```

## 🔧 System Requirement: ffmpeg

pydub requires ffmpeg to process audio streams.

### macOS
```bash
brew install ffmpeg
```

### Ubuntu / Debian
```bash
sudo apt install ffmpeg
```

### Windows
Download from ffmpeg.org

Add the bin/ folder to your system PATH

