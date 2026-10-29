@echo off
REM One-click launcher: sets up Python environment on first run, then starts the app.
cd /d "%~dp0"

REM A broken certificate setting (e.g. from other software) can make pip fail
set CURL_CA_BUNDLE=
set SSL_CERT_FILE=
set REQUESTS_CA_BUNDLE=

where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed. Get it from https://www.python.org/downloads/
  echo Tick "Add python.exe to PATH" during install, then run this again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo First run: setting things up, this takes a minute...
  python -m venv .venv
)

echo Checking for updates to the downloader engine...
".venv\Scripts\python.exe" -m pip install -q -U -r requirements.txt
if errorlevel 1 (
  echo Setup failed. Check your internet connection and try again.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" app.py
pause
