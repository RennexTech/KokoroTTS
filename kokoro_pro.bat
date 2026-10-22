@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================
echo   Kokoro Studio Pro
echo ============================================
echo.

set PY=.venv\Scripts\python.exe

if not exist "%PY%" (
    echo [*] Creating virtual environment...
    where py >nul 2>nul
    if errorlevel 1 (
        echo [X] Python launcher "py" not found. Install Python 3.12 first.
        pause & exit /b 1
    )
    py -3.12 -m venv .venv
    "%PY%" -m pip install --upgrade pip
    "%PY%" -m pip install kokoro-onnx soundfile numpy pygame onnxruntime-directml
    echo.
)

"%PY%" -c "import kokoro_onnx, soundfile, numpy, pygame, onnxruntime" 2>nul
if errorlevel 1 (
    echo [!] Some packages missing. Installing...
    "%PY%" -m pip install kokoro-onnx soundfile numpy pygame onnxruntime-directml
)

if not exist "kokoro-v1.0.onnx" (
    echo [X] kokoro-v1.0.onnx missing next to this .bat
    pause & exit /b 1
)
if not exist "voices-v1.0.bin" (
    echo [X] voices-v1.0.bin missing next to this .bat
    pause & exit /b 1
)
if not exist "kokoro_studio_pro.py" (
    echo [X] kokoro_studio_pro.py missing next to this .bat
    pause & exit /b 1
)

where ffmpeg >nul 2>nul
if errorlevel 1 (
    if exist "ffmpeg.exe" (echo [*] ffmpeg.exe found locally.) else (echo [!] ffmpeg not found - WAV only.)
) else (
    echo [*] ffmpeg found on PATH.
)

echo.
echo [*] Launching Kokoro Studio Pro...
"%PY%" kokoro_studio_pro.py
if errorlevel 1 (
    echo.
    echo [X] GUI crashed. Scroll up for details.
    pause
)