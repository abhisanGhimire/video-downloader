"""Universal Video Downloader - paste a link, get video or audio.

Powered by yt-dlp (1000+ supported sites) and a bundled ffmpeg.
"""
import os
import threading
import uuid
import webbrowser
from pathlib import Path

import yt_dlp
from flask import Flask, jsonify, render_template, request, send_file

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:  # fall back to ffmpeg on PATH
    FFMPEG = None

BASE = Path(__file__).parent
DOWNLOADS = BASE / "downloads"
DOWNLOADS.mkdir(exist_ok=True)

app = Flask(__name__)
jobs = {}  # job_id -> dict(status, progress, filename, error, title)

VIDEO_FORMATS = ["mp4", "mkv", "webm"]
AUDIO_FORMATS = ["mp3", "m4a", "opus", "wav", "flac", "aac"]


def base_opts():
    opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
    if FFMPEG:
        opts["ffmpeg_location"] = FFMPEG
    return opts


def clean_error(e):
    msg = str(e)
    return msg.replace("ERROR: ", "").split("\n")[0][:300]


@app.route("/")
def index():
    return render_template("index.html", video_formats=VIDEO_FORMATS, audio_formats=AUDIO_FORMATS)


@app.post("/api/info")
def info():
    url = (request.json or {}).get("url", "").strip()
    if not url:
        return jsonify(error="Please paste a link."), 400
    try:
        with yt_dlp.YoutubeDL(base_opts()) as ydl:
            data = ydl.extract_info(url, download=False)
    except Exception as e:
        return jsonify(error=clean_error(e)), 400
    heights = sorted(
        {f["height"] for f in data.get("formats", []) if f.get("height") and f.get("vcodec") != "none"},
        reverse=True,
    )
    return jsonify(
        title=data.get("title"),
        thumbnail=data.get("thumbnail"),
        uploader=data.get("uploader"),
        duration=data.get("duration"),
        site=data.get("extractor_key"),
        heights=heights,
    )


def run_job(job_id, url, mode, fmt, height):
    job = jobs[job_id]
    out_dir = DOWNLOADS / job_id
    out_dir.mkdir(exist_ok=True)

    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            if total:
                job["progress"] = round(d["downloaded_bytes"] / total * 100, 1)
            job["speed"] = d.get("_speed_str", "").strip()
            job["eta"] = d.get("_eta_str", "").strip()
        elif d["status"] == "finished":
            job["progress"] = 100
            job["status"] = "processing"

    opts = base_opts()
    opts.update(outtmpl=str(out_dir / "%(title).150B.%(ext)s"), progress_hooks=[hook])

    if mode == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": fmt, "preferredquality": "192"}
        ]
    else:
        h = f"[height<={height}]" if height else ""
        opts["format"] = f"bestvideo{h}+bestaudio/best{h}/best"
        opts["merge_output_format"] = fmt

    try:
        job["status"] = "downloading"
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=True)
            job["title"] = data.get("title")
        files = [p for p in out_dir.iterdir() if p.is_file()]
        if not files:
            raise RuntimeError("No file was produced.")
        job["filename"] = max(files, key=lambda p: p.stat().st_size).name
        job["status"] = "done"
    except Exception as e:
        job["status"] = "error"
        job["error"] = clean_error(e)


@app.post("/api/download")
def download():
    body = request.json or {}
    url = body.get("url", "").strip()
    mode = body.get("mode", "video")
    fmt = body.get("format") or ("mp4" if mode == "video" else "mp3")
    allowed = AUDIO_FORMATS if mode == "audio" else VIDEO_FORMATS
    if not url or fmt not in allowed:
        return jsonify(error="Invalid request."), 400
    height = body.get("height")
    height = int(height) if str(height).isdigit() else None
    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {"status": "queued", "progress": 0}
    threading.Thread(target=run_job, args=(job_id, url, mode, fmt, height), daemon=True).start()
    return jsonify(job_id=job_id)


@app.get("/api/progress/<job_id>")
def progress(job_id):
    job = jobs.get(job_id)
    return (jsonify(job), 200) if job else (jsonify(error="Unknown job"), 404)


@app.get("/api/file/<job_id>")
def get_file(job_id):
    job = jobs.get(job_id)
    if not job or job.get("status") != "done":
        return jsonify(error="Not ready"), 404
    return send_file(DOWNLOADS / job_id / job["filename"], as_attachment=True)


if __name__ == "__main__":
    import socket

    def free(p):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", p))
                return True
            except OSError:
                return False

    # Port 5000 is sometimes busy or reserved on Windows; fall back to the next free one.
    start = int(os.environ.get("PORT", 5000))
    port = next((p for p in range(start, start + 50) if free(p)), start)
    url = f"http://127.0.0.1:{port}"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"Video Downloader running at {url}")
    app.run(host="127.0.0.1", port=port)
