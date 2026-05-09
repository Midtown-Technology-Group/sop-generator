@echo off
cd /d "%~dp0"
echo Starting SOP Generator companion service...
echo.

python -m sop_generator init-style
if ERRORLEVEL 1 (
    echo Failed to initialize SOP Generator house style.
    pause
    exit /b %ERRORLEVEL%
)

python -m sop_generator serve --host 127.0.0.1 --port 8765
if ERRORLEVEL 1 (
    echo SOP Generator companion service exited with an error.
    pause
    exit /b %ERRORLEVEL%
)
