"""
Core download logic — no GUI code here.
Talks to yt-dlp and reports progress through callback functions
supplied by the caller (gui.py).
"""

import os
import yt_dlp
import requests
from PIL import Image
from io import BytesIO


def build_options(save_folder, progress_hook, postprocessor_hook, format_str="bestvideo+bestaudio/best"):
    return {
        "progress_hooks": [progress_hook],
        "postprocessor_hooks": [postprocessor_hook],
        "extractor_args": {
            "youtube": {"player_client": ["android"]}
        },
        "outtmpl": f"{save_folder}/%(title)s.%(ext)s",
        "format": format_str,
        "merge_output_format": "mp4",
        "writethumbnail": True,
        "postprocessors": [
            {"key": "EmbedThumbnail"}
        ],
        "retries": 5,
        "fragment_retries": 5,
    }


def download_video(video_url, save_folder, progress_hook, postprocessor_hook, format_str="bestvideo+bestaudio/best"):
    """Downloads a video. Raises on failure — the caller decides how to report it."""
    os.makedirs(save_folder, exist_ok=True)
    ytdown_optn = build_options(save_folder, progress_hook, postprocessor_hook, format_str)
    downloader = yt_dlp.YoutubeDL(ytdown_optn)
    downloader.download([video_url])


def fetch_thumbnail(video_url):
    """Fetches video metadata and returns the thumbnail as a PIL Image. Raises on failure."""
    info = yt_dlp.YoutubeDL({"quiet": True, "retries": 5}).extract_info(video_url, download=False)
    thumbnail_url = info.get("thumbnail")

    if not thumbnail_url:
        raise ValueError("Thumbnail URL not found for the provided video.")

    response = requests.get(thumbnail_url, timeout=10)
    response.raise_for_status()

    pil_image = Image.open(BytesIO(response.content))
    return pil_image
