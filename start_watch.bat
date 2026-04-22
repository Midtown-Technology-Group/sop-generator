@echo off
cd /d "%~dp0"
echo Starting SOP Generator in watch mode...
echo.
python sop_generator.py --watch
pause
