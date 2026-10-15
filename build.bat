@echo off
REM Builds dist\VideoDownloader.exe (run inside the activated venv)
pip install pyinstaller
pyinstaller --noconfirm --onefile --name VideoDownloader ^
  --add-data "templates;templates" ^
  --collect-all imageio_ffmpeg ^
  --collect-all yt_dlp ^
  --collect-all curl_cffi ^
  app.py
echo.
echo Done: dist\VideoDownloader.exe
