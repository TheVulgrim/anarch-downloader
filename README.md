# Anarch Downloader

A desktop video downloader built with Python, [yt-dlp](https://github.com/yt-dlp/yt-dlp), and `customtkinter`. Supports YouTube and 1000+ other sites, with live progress, quality selection, thumbnail preview/embedding, and a cancel button.

## Features

- Paste a URL, preview the thumbnail before downloading
- Choose video quality (Best / 1080p / 720p / 480p / Audio Only)
- Live progress bar with speed and ETA
- Choose your save folder
- Cancel an in-progress download
- Automatically embeds the thumbnail into the downloaded file
- Dark, card-based UI

## Project structure

```
gui.py             — UI, layout, threading, and queue handling
logic.py            — download logic (yt-dlp calls), independent of the GUI
requirements.txt
```

`logic.py` contains no GUI code — it just does the actual work and reports progress through callback functions. `gui.py` owns the window and supplies those callbacks.

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg

Required for merging separate video/audio streams and embedding thumbnails. Not a Python package — install via your system's package manager:

**Fedora / RHEL**
```bash
sudo dnf install ffmpeg
```

**Ubuntu / Debian**
```bash
sudo apt install ffmpeg
```

**macOS (Homebrew)**
```bash
brew install ffmpeg
```

**Windows**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add it to your PATH.

### 3. Run the app

```bash
python gui.py
```

### Optional touches

- **Background image** — the app looks for `Fallen.jpeg` in the project folder. It's not included in this repo (unclear image license), so the app runs fine without it, just with a plain dark background. Drop your own image named `Fallen.jpeg` in the project root for the full look.
- **Heading font** — the title uses a font called "Road Rage." If it isn't installed on your system, `customtkinter` silently falls back to a default font — nothing breaks either way.

## Known limitations

- Some sites use aggressive bot-detection and may intermittently fail or need a retry.
- Download speed depends on the source site's rate limiting, not just your connection.
