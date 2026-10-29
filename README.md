# Universal Video Downloader

Paste a link, pick video or audio, click download. A small local web app built on [yt-dlp](https://github.com/yt-dlp/yt-dlp), so it works with YouTube, TikTok, Instagram, Facebook, X/Twitter, Dailymotion, Vimeo, Reddit, Twitch and [1000+ other sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

## Features

- Video formats: MP4, MKV, WebM, with a max-quality picker (best, 1080p, 720p, ...)
- Audio-only formats: MP3, M4A, Opus, WAV, FLAC, AAC
- Thumbnail and title preview before downloading
- Live progress with speed and ETA
- ffmpeg is bundled through `imageio-ffmpeg`, so no separate install is needed
- Runs only on your machine (127.0.0.1)

## Windows: one-click start

1. Install [Python 3.9+](https://www.python.org/downloads/) (tick "Add python.exe to PATH").
2. Download this repo (green **Code** button, then **Download ZIP**) and unzip it somewhere with a short path, e.g. `C:\video-downloader`.
3. Double-click `run.bat`. It sets itself up on first run, updates the downloader engine each time, and opens the app in your browser.

No exe is offered: unsigned single-file Python executables are often flagged by antivirus software (false positives), and `run.bat` avoids that.

## Run from source (any OS)


Requires Python 3.9+.

```bash
git clone https://github.com/abhisanGhimire/video-downloader.git
cd video-downloader
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Your browser opens at http://127.0.0.1:5000. Files are saved in the `downloads/` folder and also sent to your browser.

Optional: you can build your own exe with `build.bat` (activate the venv first). Your antivirus may still flag it.

## Keep it working

Sites change often. If a site stops working, update yt-dlp:

```bash
pip install -U yt-dlp
```

## Notes

- Private, age-restricted or login-only videos may need cookies, which this app does not handle yet.
- Only download content you own or have permission to save. Respect copyright and each site's terms of service. You are responsible for how you use this tool.

## License

MIT
